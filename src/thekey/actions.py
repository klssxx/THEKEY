"""Concrete safe action handlers.

These execute only *declared*, bounded operations resolved from input IDs and
workspace-relative paths. They never run arbitrary shell strings. Every handler
returns a deterministic result dict with a stable ``status`` and (where
relevant) a sha256 of the observed output.
"""

from __future__ import annotations

import ast
import hashlib
import subprocess
import sys
from pathlib import Path

from .errors import TheKeyError
from .workspaces import WorkspaceManager

_wm = WorkspaceManager()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _resolve_declared(workspace: Path, target_id: str) -> Path:
    """Resolve a declared target id to a workspace file.

    Declared ids follow the convention TARGET_FILE -> <workspace>/src/<name>.
    For the canonical demo, target ids map to the copied demo app.
    """
    workspace = Path(workspace)
    # Accept either a bare relative id or an explicit relative path.
    candidate = (workspace / target_id).resolve()
    try:
        candidate.relative_to(workspace.resolve())
    except ValueError as exc:
        raise TheKeyError(
            f"Declared target outside workspace: {target_id!r}",
            code="PATH_OUTSIDE_ALLOWED_ROOTS",
        ) from exc
    return candidate


# --------------------------------------------------------------------------
# Read-only handlers (PLANNER / EXECUTOR / VERIFIER).
# --------------------------------------------------------------------------
def list_declared_files(run_id: str, parameters: dict) -> dict:
    ws = _wm.root / run_id
    if not ws.exists():
        return {"status": "MISSING_WORKSPACE", "files": []}
    files = sorted(str(p.relative_to(ws)) for p in ws.rglob("*") if p.is_file())
    return {"status": "OK", "files": files}


def read_declared_file(run_id: str, parameters: dict) -> dict:
    target = _resolve_declared(_wm.root / run_id, parameters["target_id"])
    if not target.exists():
        return {"status": "NOT_FOUND", "path": str(target)}
    content = target.read_text(encoding="utf-8")
    return {
        "status": "OK",
        "path": str(target),
        "sha256": sha256_file(target),
        "content": content,
    }


def compute_declared_file_hash(run_id: str, parameters: dict) -> dict:
    target = _resolve_declared(_wm.root / run_id, parameters["target_id"])
    if not target.exists():
        return {"status": "NOT_FOUND", "path": str(target)}
    return {"status": "OK", "path": str(target), "sha256": sha256_file(target)}


def check_declared_python_syntax(run_id: str, parameters: dict) -> dict:
    target = _resolve_declared(_wm.root / run_id, parameters["target_id"])
    if not target.exists():
        return {"status": "NOT_FOUND", "path": str(target)}
    try:
        with target.open("r", encoding="utf-8") as fh:
            source = fh.read()
        ast.parse(source)
        return {"status": "SYNTAX_OK", "path": str(target)}
    except SyntaxError as exc:
        return {
            "status": "SYNTAX_ERROR",
            "path": str(target),
            "error": f"{exc.msg} (line {exc.lineno})",
        }
    except Exception as exc:  # pragma: no cover
        return {"status": "ERROR", "path": str(target), "error": str(exc)}


# --------------------------------------------------------------------------
# Write handlers (EXECUTOR only, orchestrator-authorized).
# --------------------------------------------------------------------------
def replace_exact_text(run_id: str, parameters: dict) -> dict:
    """Apply an exact-text replacement inside the isolated workspace.

    Parameters:
        target_id: declared file id inside the workspace.
        expected: exact text that must currently be present.
        replacement: exact replacement text.
    Refuses ambiguous replacement (expected not present exactly once).
    """
    target = _resolve_declared(_wm.root / run_id, parameters["target_id"])
    if not target.exists():
        return {"status": "NOT_FOUND", "path": str(target)}
    expected = parameters["expected"]
    replacement = parameters["replacement"]
    before = target.read_text(encoding="utf-8")
    count = before.count(expected)
    if count != 1:
        return {
            "status": "AMBIGUOUS_OR_MISSING",
            "path": str(target),
            "count": count,
        }
    after = before.replace(expected, replacement, 1)
    # Atomic write.
    tmp = target.with_suffix(target.suffix + ".tmp")
    tmp.write_text(after, encoding="utf-8")
    tmp.replace(target)
    return {
        "status": "APPLIED",
        "path": str(target),
        "sha256_before": hashlib.sha256(before.encode()).hexdigest(),
        "sha256_after": sha256_file(target),
    }


def create_declared_file(run_id: str, parameters: dict) -> dict:
    target = _wm.authorize_write(run_id, parameters["target_id"])
    content = parameters.get("content", "")
    tmp = target.with_suffix(target.suffix + ".tmp")
    tmp.write_text(content, encoding="utf-8")
    tmp.replace(target)
    return {"status": "CREATED", "path": str(target), "sha256": sha256_file(target)}


# --------------------------------------------------------------------------
# Command handlers (orchestrator executes; deterministic, no network).
# --------------------------------------------------------------------------
def _run_python(args: list[str], cwd: Path) -> dict:
    try:
        proc = subprocess.run(
            [sys.executable, *args],
            cwd=str(cwd),
            capture_output=True,
            text=True,
            timeout=300,
        )
    except subprocess.TimeoutExpired:
        return {"status": "TIMEOUT", "returncode": None, "stdout": "", "stderr": "timeout"}
    return {
        "status": "OK" if proc.returncode == 0 else "FAILED",
        "returncode": proc.returncode,
        "stdout": proc.stdout,
        "stderr": proc.stderr,
    }


def run_build(run_id: str, parameters: dict) -> dict:
    ws = _wm.root / run_id
    if not ws.exists():
        return {"status": "MISSING_WORKSPACE"}
    # Build = compileall over the workspace project sources.
    return _run_python(["-m", "compileall", "-q", "src"], cwd=ws)


def run_unit_tests(run_id: str, parameters: dict) -> dict:
    ws = _wm.root / run_id
    if not ws.exists():
        return {"status": "MISSING_WORKSPACE"}
    return _run_python(["-m", "pytest", "-q", "tests"], cwd=ws)


def run_targeted_tests(run_id: str, parameters: dict) -> dict:
    ws = _wm.root / run_id
    if not ws.exists():
        return {"status": "MISSING_WORKSPACE"}
    node = parameters.get("node", "tests")
    return _run_python(["-m", "pytest", "-q", node], cwd=ws)


def scan_secrets(run_id: str, parameters: dict) -> dict:
    """Limited, honest secret scan over the workspace using regex patterns.

    Returns FOUND only on non-excluded, in-scope matches. Never claims a full
    sandbox or exhaustive coverage.
    """
    from .policies import PolicyEngine

    ws = _wm.root / run_id
    if not ws.exists():
        return {"status": "MISSING_WORKSPACE"}
    policy = parameters.get("policy")
    if policy is None:
        policy = PolicyEngine().load_default()
    patterns = [__import__("re").compile(p) for p in policy.secret_scan_scope["patterns"]]
    excluded = set(policy.excluded_directories)

    findings = []
    for p in ws.rglob("*"):
        if not p.is_file():
            continue
        try:
            rel = p.relative_to(ws)
        except ValueError:  # pragma: no cover
            continue
        if any(part in excluded for part in rel.parts):
            continue
        try:
            text = p.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for pat in patterns:
            for m in pat.finditer(text):
                findings.append({"file": str(rel), "match": m.group(0)[:32]})
    return {
        "status": "FOUND" if findings else "CLEAN",
        "findings": findings,
    }


def check_required_documentation(run_id: str, parameters: dict) -> dict:
    """Documentation gate: the workspace project must ship README + a doc that
    describes the repaired behavior, and the tests docstring must reference the
    fixed function."""
    ws = _wm.root / run_id
    required = ["README.md"]
    missing = [r for r in required if not (ws / r).exists()]
    # Also require the test file to exist.
    test_exists = any((ws / "tests").rglob("test_*.py"))
    ok = (not missing) and test_exists
    return {
        "status": "DOC_OK" if ok else "DOC_MISSING",
        "missing": missing,
        "test_exists": test_exists,
    }


# Handler lookup.
HANDLERS = {
    "list_declared_files": list_declared_files,
    "read_declared_file": read_declared_file,
    "compute_declared_file_hash": compute_declared_file_hash,
    "check_declared_python_syntax": check_declared_python_syntax,
    "replace_exact_text": replace_exact_text,
    "create_declared_file": create_declared_file,
    "run_build": run_build,
    "run_unit_tests": run_unit_tests,
    "run_targeted_tests": run_targeted_tests,
    "scan_secrets": scan_secrets,
    "check_required_documentation": check_required_documentation,
}

_HANDLER_CALL_COUNTS: dict[tuple[str, str], int] = {}


def handler_call_count(transaction_id: str, action_id: str) -> int:
    return _HANDLER_CALL_COUNTS.get((transaction_id, action_id), 0)


def dispatch(
    action_id: str,
    run_id: str,
    parameters: dict,
    *,
    context,
) -> dict:
    """Authorize, then resolve and execute exactly one declared handler."""
    from .rbac_guard import enforce_action_context

    authorized = enforce_action_context(
        raw_context=context,
        action_id=action_id,
        run_id=run_id,
        parameters=parameters,
    )
    from .command_registry import get_spec

    spec = get_spec(action_id)
    if spec is None:
        raise TheKeyError(f"Unknown action: {action_id!r}", code="UNAUTHORIZED_ACTION")
    handler = HANDLERS[spec.handler]
    key = (authorized.context.transaction_id, action_id)
    _HANDLER_CALL_COUNTS[key] = _HANDLER_CALL_COUNTS.get(key, 0) + 1
    result = handler(run_id, parameters)
    result = dict(result)
    result["authorization"] = authorized.decision.model_dump(mode="json")
    result["transaction_id"] = authorized.context.transaction_id
    return result
