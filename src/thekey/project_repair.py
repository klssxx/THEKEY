"""Bounded automatic diagnosis and repair for trusted local Python projects.

The repair engine never invents shell commands or installs dependencies.  It
searches a closed set of single-token/source-line mutations in an isolated
copy, accepts a candidate only when compile, the complete existing pytest
suite, the secret scan, and documentation gate all pass, and writes the exact
verified bytes to the source only after separate explicit consent.
"""

from __future__ import annotations

import difflib
import hashlib
import io
import json
import os
import re
import shutil
import tokenize
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from .config import THEKEY_DIR
from .policies import PolicyEngine
from .project_loader import inspect_project
from .project_models import compute_tree_hash
from .project_verification import (
    PROJECT_TEST_CONSENT,
    _external_tests_for,
    _limited_secret_scan,
    _persist_result,
    _run_bounded_command,
    _run_bounded_python,
    verify_application,
)

PROJECT_REPAIR_APPLY_CONSENT = "apply_verified_repairs"
DEFAULT_MAX_CANDIDATES = 60
DEFAULT_CANDIDATE_TIMEOUT_SECONDS = 60

_TOKEN_REPLACEMENTS: dict[str, tuple[str, ...]] = {
    "+": ("-", "*"),
    "-": ("+", "*"),
    "*": ("+", "-", "/"),
    "/": ("//", "*"),
    "//": ("/", "%"),
    "%": ("//", "/"),
    "==": ("!=",),
    "!=": ("==",),
    "<": ("<=", ">", ">="),
    "<=": ("<", ">=", ">"),
    ">": (">=", "<", "<="),
    ">=": (">", "<=", "<"),
    "and": ("or",),
    "or": ("and",),
    "True": ("False",),
    "False": ("True",),
    "is": ("==",),
    "in": ("not in",),
}
_COMMON_NAME_TYPOS: dict[str, str] = {
    "flase": "False",
    "pritn": "print",
    "ture": "True",
}
_JAVASCRIPT_REPLACEMENTS: dict[str, tuple[str, ...]] = {
    "+": ("-", "*"), "-": ("+", "*"), "*": ("+", "-"), "/": ("*",),
    "===": ("!==",), "!==": ("===",), "&&": ("||",), "||": ("&&",),
    "true": ("false",), "false": ("true",),
}
_JAVASCRIPT_TOKEN = re.compile(r"===|!==|&&|\|\||\+|-|\*|/|\btrue\b|\bfalse\b")
_BLOCK_HEADER = re.compile(
    r"^(?P<indent>\s*)(?:async\s+def|def|class|if|elif|else|for|while|try|except|"
    r"finally|with|async\s+with|async\s+for|match|case)\b.*[^:\s]\s*(?:#.*)?$"
)


@dataclass(frozen=True)
class RepairCandidate:
    relative_path: str
    line: int
    column: int
    before: str
    after: str
    original_text: str
    repaired_text: str
    strategy: str

    @property
    def candidate_id(self) -> str:
        body = (
            f"{self.relative_path}:{self.line}:{self.column}:"
            f"{self.before!r}:{self.after!r}:{self.strategy}"
        )
        return "candidate-" + hashlib.sha256(body.encode("utf-8")).hexdigest()[:16]

    def evidence(self) -> dict:
        return {
            "candidate_id": self.candidate_id,
            "path": self.relative_path,
            "line": self.line,
            "column": self.column,
            "before": self.before,
            "after": self.after,
            "strategy": self.strategy,
            "sha256_before": hashlib.sha256(self.original_text.encode("utf-8")).hexdigest(),
            "sha256_after": hashlib.sha256(self.repaired_text.encode("utf-8")).hexdigest(),
        }


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _repair_id() -> str:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    return f"PR-{stamp}-{uuid4().hex[:8]}"


def _canonical_sha256(value: dict) -> str:
    body = json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(body).hexdigest()


def _is_product_python_file(relative: str) -> bool:
    path = Path(relative)
    return (
        path.suffix.casefold() == ".py"
        and not path.name.startswith("test_")
        and not any(part.casefold() in {"test", "tests"} for part in path.parts)
    )


def _is_product_javascript_file(relative: str) -> bool:
    path = Path(relative)
    return (
        path.suffix.casefold() in {".js", ".mjs", ".cjs"}
        and not path.name.casefold().endswith((".test.js", ".spec.js"))
        and not any(part.casefold() in {"test", "tests"} for part in path.parts)
    )


def _line_offsets(text: str) -> list[int]:
    offsets = [0]
    for line in text.splitlines(keepends=True):
        offsets.append(offsets[-1] + len(line))
    return offsets


def _token_candidates(relative: str, text: str) -> list[RepairCandidate]:
    candidates: list[RepairCandidate] = []
    offsets = _line_offsets(text)
    try:
        tokens = tokenize.generate_tokens(io.StringIO(text).readline)
        for token in tokens:
            replacements = _TOKEN_REPLACEMENTS.get(token.string)
            strategy = "SINGLE_TOKEN_LOGIC_MUTATION"
            if token.type == tokenize.NUMBER and token.string in {"0", "1"}:
                replacements = ("1" if token.string == "0" else "0",)
                strategy = "SINGLE_LITERAL_BOUNDARY_MUTATION"
            elif token.type == tokenize.NAME and token.string in _COMMON_NAME_TYPOS:
                replacements = (_COMMON_NAME_TYPOS[token.string],)
                strategy = "COMMON_IDENTIFIER_TYPO"
            if not replacements:
                continue
            start_line, start_column = token.start
            end_line, end_column = token.end
            if start_line != end_line or start_line >= len(offsets):
                continue
            start = offsets[start_line - 1] + start_column
            end = offsets[end_line - 1] + end_column
            for replacement in replacements:
                candidates.append(RepairCandidate(
                    relative_path=relative,
                    line=start_line,
                    column=start_column + 1,
                    before=token.string,
                    after=replacement,
                    original_text=text,
                    repaired_text=text[:start] + replacement + text[end:],
                    strategy=strategy,
                ))
    except (IndentationError, SyntaxError, tokenize.TokenError):
        return []
    return candidates


def _syntax_candidates(relative: str, text: str) -> list[RepairCandidate]:
    candidates: list[RepairCandidate] = []
    offset = 0
    for line_number, line in enumerate(text.splitlines(keepends=True), 1):
        content = line.rstrip("\r\n")
        ending = line[len(content):]
        match = _BLOCK_HEADER.match(content)
        if match and not content.rstrip().endswith(":"):
            comment_at = content.find("#")
            insertion = comment_at if comment_at >= 0 else len(content)
            while insertion > 0 and content[insertion - 1].isspace():
                insertion -= 1
            repaired_line = content[:insertion] + ":" + content[insertion:] + ending
            candidates.append(RepairCandidate(
                relative_path=relative,
                line=line_number,
                column=insertion + 1,
                before="<missing colon>",
                after=":",
                original_text=text,
                repaired_text=text[:offset] + repaired_line + text[offset + len(line):],
                strategy="MISSING_BLOCK_COLON",
            ))
        offset += len(line)
    return candidates


def _javascript_candidates(relative: str, text: str) -> list[RepairCandidate]:
    candidates: list[RepairCandidate] = []
    for match in _JAVASCRIPT_TOKEN.finditer(text):
        for replacement in _JAVASCRIPT_REPLACEMENTS.get(match.group(), ()):
            line = text.count("\n", 0, match.start()) + 1
            column = match.start() - text.rfind("\n", 0, match.start())
            candidates.append(RepairCandidate(
                relative_path=relative,
                line=line,
                column=column,
                before=match.group(),
                after=replacement,
                original_text=text,
                repaired_text=text[:match.start()] + replacement + text[match.end():],
                strategy="JAVASCRIPT_SINGLE_TOKEN_LOGIC_MUTATION",
            ))
    return candidates


def _unclosed_delimiter_candidates(relative: str, text: str) -> list[RepairCandidate]:
    """Offer one EOF delimiter only when tokenization proves it is missing."""
    opening = {"(": ")", "[": "]", "{": "}"}
    closing = {value: key for key, value in opening.items()}
    stack: list[str] = []
    try:
        tokens = tokenize.generate_tokens(io.StringIO(text).readline)
        for token in tokens:
            if token.string in opening:
                stack.append(token.string)
            elif token.string in closing and stack and stack[-1] == closing[token.string]:
                stack.pop()
    except (IndentationError, SyntaxError, tokenize.TokenError):
        pass
    if not stack:
        return []
    missing = opening[stack[-1]]
    suffix = "\n"
    return [RepairCandidate(
        relative_path=relative,
        line=text.count("\n") + 1,
        column=len(text.rsplit("\n", 1)[-1]) + 1,
        before="<missing closing delimiter>",
        after=missing,
        original_text=text,
        repaired_text=text + missing + suffix,
        strategy="MISSING_CLOSING_DELIMITER",
    )]


def _diagnostic_text(verification: dict) -> str:
    return "\n".join(
        str(item.get("evidence", "")) for item in verification.get("diagnostics", [])
    ).casefold()


def _generate_candidates(
    project_workspace: Path,
    canonical_hashes: dict[str, str],
    verification: dict,
) -> list[RepairCandidate]:
    profile_name = verification["profile"]["detected_profile"]
    compile_failed = any(
        gate["gate"] == "PYTHON_COMPILE_PASSED" and not gate["passed"]
        for gate in verification.get("gates", [])
    )
    diagnostics = _diagnostic_text(verification)
    ranked: list[tuple[int, RepairCandidate]] = []
    for relative in sorted(canonical_hashes):
        is_python = _is_product_python_file(relative)
        is_javascript = profile_name == "node-javascript" and _is_product_javascript_file(relative)
        if not is_python and not is_javascript:
            continue
        target = project_workspace / relative
        try:
            text = target.read_bytes().decode("utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        if is_javascript:
            generated = _javascript_candidates(relative, text)
        else:
            generated = (
                [
                    *_syntax_candidates(relative, text),
                    *_unclosed_delimiter_candidates(relative, text),
                ]
                if compile_failed else _token_candidates(relative, text)
            )
        normalized = relative.replace("\\", "/").casefold()
        mentioned = normalized in diagnostics or Path(relative).name.casefold() in diagnostics
        for candidate in generated:
            ranked.append((0 if mentioned else 1, candidate))
    ranked.sort(
        key=lambda item: (
            item[0],
            item[1].relative_path.casefold(),
            item[1].line,
            item[1].column,
            item[1].after,
        )
    )
    return [item[1] for item in ranked]


def _workspace_layout(source: Path, verification: dict) -> tuple[Path, Path, list[str]]:
    workspace = Path(verification["test_execution"]["workspace"])
    if verification["source"].get("external_tests"):
        project_workspace = workspace / source.name
        test_arguments = ["-m", "pytest", "-q", str(Path("tests") / source.name)]
    else:
        project_workspace = workspace
        test_arguments = ["-m", "pytest", "-q"]
    return workspace, project_workspace, test_arguments


def _try_candidate(
    candidate: RepairCandidate,
    workspace: Path,
    project_workspace: Path,
    test_arguments: list[str],
    timeout_seconds: int,
    profile_name: str,
) -> dict:
    target = project_workspace / candidate.relative_path
    target.write_bytes(candidate.repaired_text.encode("utf-8"))
    if profile_name == "node-javascript":
        npm = "npm.cmd" if os.name == "nt" and shutil.which("npm.cmd") else "npm"
        compile_result = _run_bounded_command(
            [npm, "run", "build", "--if-present"], workspace, timeout_seconds=timeout_seconds,
        )
    else:
        compiled_target = str(target.relative_to(workspace))
        compile_result = _run_bounded_python(
            ["-m", "compileall", "-q", "-b", compiled_target],
            workspace,
            timeout_seconds=timeout_seconds,
        )
    tests_result = None
    if compile_result["returncode"] == 0:
        tests_result = (
            _run_bounded_command([npm, "test"], workspace, timeout_seconds=timeout_seconds)
            if profile_name == "node-javascript" else _run_bounded_python(
                test_arguments, workspace, timeout_seconds=timeout_seconds,
            )
        )
    passed = bool(tests_result and tests_result["returncode"] == 0)
    if not passed:
        target.write_bytes(candidate.original_text.encode("utf-8"))
    def bounded_evidence(value: dict | None) -> dict | None:
        if value is None:
            return None
        summary = dict(value)
        excerpt = summary.get("output_excerpt", "")
        if len(excerpt) > 2_000:
            summary["output_excerpt"] = excerpt[:2_000] + "\n... <attempt excerpt truncated>"
        return summary

    return {
        "candidate_id": candidate.candidate_id,
        "passed": passed,
        "compile": bounded_evidence(compile_result),
        "tests": bounded_evidence(tests_result),
    }


def _verified_workspace_gates(
    workspace: Path,
    project_workspace: Path,
    test_arguments: list[str],
    profile_name: str,
) -> tuple[list[dict], bool]:
    if profile_name == "node-javascript":
        npm = "npm.cmd" if os.name == "nt" and shutil.which("npm.cmd") else "npm"
        compile_result = _run_bounded_command([npm, "run", "build", "--if-present"], workspace)
        tests_result = _run_bounded_command([npm, "test"], workspace)
        compile_gate = "NODE_BUILD_PASSED"
    else:
        compile_result = _run_bounded_python(["-m", "compileall", "-q", "-b", "."], workspace)
        tests_result = _run_bounded_python(test_arguments, workspace)
        compile_gate = "PYTHON_COMPILE_PASSED"
    policy = PolicyEngine().load_default()
    secret_result = _limited_secret_scan(workspace, policy)
    documentation_present = any(
        (project_workspace / name).is_file()
        for name in ("README.md", "README.rst", "README.txt")
    )
    gates = [
        {
            "gate": compile_gate,
            "passed": compile_result["returncode"] == 0,
            "status": "PASSED" if compile_result["returncode"] == 0 else "FAILED",
            "evidence": compile_result,
        },
        {
            "gate": "UNIT_TESTS_PASSED",
            "passed": tests_result["returncode"] == 0,
            "status": "PASSED" if tests_result["returncode"] == 0 else "FAILED",
            "evidence": tests_result,
        },
        {
            "gate": "LIMITED_SECRET_SCAN_PASSED",
            "passed": secret_result["passed"],
            "status": "PASSED" if secret_result["passed"] else "FAILED",
            "evidence": secret_result,
        },
        {
            "gate": "DOCUMENTATION_PRESENT",
            "passed": documentation_present,
            "status": "PASSED" if documentation_present else "FAILED",
        },
    ]
    return gates, all(gate["passed"] for gate in gates)


def _unified_diff(candidate: RepairCandidate) -> str:
    return "".join(difflib.unified_diff(
        candidate.original_text.splitlines(keepends=True),
        candidate.repaired_text.splitlines(keepends=True),
        fromfile=f"a/{candidate.relative_path}",
        tofile=f"b/{candidate.relative_path}",
    ))


def _atomic_replace(target: Path, content: bytes, repair_id: str) -> None:
    temporary = target.with_name(f".{target.name}.{repair_id}.tmp")
    try:
        temporary.write_bytes(content)
        os.chmod(temporary, target.stat().st_mode)
        os.replace(temporary, target)
    finally:
        if temporary.exists():
            temporary.unlink()


def _source_inputs_unchanged(
    source: Path,
    expected_source_hash: str,
    external_tests: Path | None,
    expected_external_hash: str | None,
) -> bool:
    if inspect_project(source).baseline_tree_hash != expected_source_hash:
        return False
    if external_tests and expected_external_hash:
        return inspect_project(external_tests).baseline_tree_hash == expected_external_hash
    return True


def repair_application(
    source: str | Path,
    *,
    consent: str,
    apply_consent: str | None = None,
    output: Path | None = None,
    max_candidates: int = DEFAULT_MAX_CANDIDATES,
    candidate_timeout_seconds: int = DEFAULT_CANDIDATE_TIMEOUT_SECONDS,
) -> dict:
    """Diagnose and attempt one evidence-bound automatic repair."""
    if consent != PROJECT_TEST_CONSENT:
        raise PermissionError(
            "Explicit consent is required because project tests execute trusted local code "
            "without an operating-system sandbox."
        )
    if apply_consent not in {None, PROJECT_REPAIR_APPLY_CONSENT}:
        raise PermissionError("The repair-application consent value is invalid.")
    if not 1 <= max_candidates <= 200:
        raise ValueError("max_candidates must be between 1 and 200")
    if not 1 <= candidate_timeout_seconds <= 300:
        raise ValueError("candidate_timeout_seconds must be between 1 and 300")

    source_path = Path(source).expanduser().resolve()
    source_before = inspect_project(source_path)
    external_path = _external_tests_for(source_path, source_before.test_roots)
    external_before = inspect_project(external_path) if external_path else None
    repair_id = _repair_id()
    run_root = THEKEY_DIR / "project-repair" / repair_id
    destination = Path(output).resolve() if output else run_root / "repair-evidence.json"

    initial = verify_application(source_path, consent=consent)
    base_result = {
        "schema_version": "v1",
        "repair_id": repair_id,
        "created_at": _utc_now(),
        "source": {
            "path": str(source_path),
            "tree_sha256_before": source_before.baseline_tree_hash,
            "external_tests_tree_sha256_before": (
                external_before.baseline_tree_hash if external_before else None
            ),
        },
        "initial_verification": {
            "verification_id": initial.get("verification_id"),
            "verdict": initial.get("final_verdict"),
            "gates": initial.get("gates", []),
            "diagnostics": initial.get("diagnostics", []),
            "evidence_path": initial.get("evidence_path"),
        },
        "test_execution": initial.get("test_execution"),
        "apply_requested": apply_consent == PROJECT_REPAIR_APPLY_CONSENT,
    }
    if initial.get("final_verdict") == "VERIFIED":
        base_result.update({
            "outcome": "NO_CHANGES_NEEDED",
            "source_changed": False,
            "message": "All mandatory gates already pass; no repair was applied.",
        })
        return _persist_result(base_result, destination)
    if not initial.get("test_execution") or initial.get("final_verdict") == "NO_VERIFICABLE":
        base_result.update({
            "outcome": "BLOCKED_NO_PROVABLE_REPAIR",
            "source_changed": False,
            "message": "THEKEY requires an executable test suite to prove an automatic repair.",
        })
        return _persist_result(base_result, destination)

    gate_map = {gate["gate"]: gate for gate in initial.get("gates", [])}
    profile_name = initial["profile"]["detected_profile"]
    compile_gate = (
        "NODE_BUILD_PASSED" if profile_name == "node-javascript"
        else "PYTHON_COMPILE_PASSED"
    )
    repairable_failure = (
        not gate_map.get(compile_gate, {}).get("passed", False)
        or not gate_map.get("UNIT_TESTS_PASSED", {}).get("passed", False)
    )
    non_repairable_failed = any(
        not gate_map.get(name, {}).get("passed", False)
        for name in ("LIMITED_SECRET_SCAN_PASSED", "DOCUMENTATION_PRESENT", "SOURCE_UNCHANGED")
    )
    if not repairable_failure or non_repairable_failed:
        base_result.update({
            "outcome": "BLOCKED_UNSUPPORTED_FAILURE",
            "source_changed": False,
            "message": "The observed gate failure requires human review and is not auto-repaired.",
        })
        return _persist_result(base_result, destination)

    workspace, project_workspace, test_arguments = _workspace_layout(source_path, initial)
    candidates = _generate_candidates(
        project_workspace,
        source_before.canonical_hashes,
        initial,
    )[:max_candidates]
    attempts: list[dict] = []
    accepted: RepairCandidate | None = None
    for candidate in candidates:
        attempt = _try_candidate(
            candidate,
            workspace,
            project_workspace,
            test_arguments,
            candidate_timeout_seconds,
            profile_name,
        )
        attempts.append(attempt)
        if attempt["passed"]:
            accepted = candidate
            break

    base_result["repair_search"] = {
        "strategy": "BOUNDED_SINGLE_MUTATION_SEARCH",
        "candidate_limit": max_candidates,
        "generated_candidates": len(candidates),
        "attempted_candidates": len(attempts),
        "attempts": attempts,
    }
    if accepted is None:
        base_result.update({
            "outcome": "BLOCKED_NO_VERIFIED_REPAIR",
            "source_changed": False,
            "message": "No candidate in the bounded repair set passed the complete test suite.",
        })
        return _persist_result(base_result, destination)

    repaired_gates, repaired_verified = _verified_workspace_gates(
        workspace,
        project_workspace,
        test_arguments,
        profile_name,
    )
    repair_evidence = accepted.evidence()
    repair_evidence["diff"] = _unified_diff(accepted)
    repair_sha256 = _canonical_sha256(repair_evidence)
    access_mode = (
        "APPLY_VERIFIED_CHANGE"
        if apply_consent == PROJECT_REPAIR_APPLY_CONSENT
        else "ISOLATED_ONLY"
    )
    repair_checkmate_review = {
        "verdict": "PASS" if repaired_verified else "FAIL",
        "risk": "MEDIUM",
        "physical_writes_to_source": access_mode == "APPLY_VERIFIED_CHANGE",
        "changed_files": [accepted.relative_path],
        "reasons": [
            "single product-source file in the verified adapter",
            "tests and project metadata remain immutable",
            "complete isolated gates passed" if repaired_verified else "repair gates failed",
            "stale-input check required immediately before source application",
            "backup and post-apply rollback are mandatory",
        ],
    }
    policy_request = {
        "source_tree_hash": source_before.baseline_tree_hash,
        "profile": initial["profile"]["detected_profile"],
        "checkmate_verdict": repair_checkmate_review["verdict"],
        "access_mode": access_mode,
        "output_scope": "SINGLE_FILE_DETERMINISTIC_MUTATION",
        "repair_sha256": repair_sha256,
        "changed_files": [accepted.relative_path],
        "verification_verdict": "VERIFIED" if repaired_verified else "BLOCKED",
    }
    policy_decision = PolicyEngine().authorize_verified_project_repair(policy_request)
    base_result.update({
        "repair": repair_evidence,
        "repair_sha256": repair_sha256,
        "repaired_workspace_gates": repaired_gates,
        "repair_checkmate_review": repair_checkmate_review,
        "repair_policy_decision": policy_decision,
    })
    if not repaired_verified or not policy_decision["allowed"]:
        base_result.update({
            "outcome": "BLOCKED_REPAIR_AUTHORIZATION",
            "source_changed": False,
            "message": "The candidate did not satisfy all repair gates and policy checks.",
        })
        return _persist_result(base_result, destination)

    if apply_consent is None:
        base_result.update({
            "outcome": "REPAIR_READY",
            "source_changed": False,
            "message": (
                "A verified repair is ready in isolation; "
                "source-application consent was absent."
            ),
        })
        return _persist_result(base_result, destination)

    expected_external_hash = external_before.baseline_tree_hash if external_before else None
    if not _source_inputs_unchanged(
        source_path,
        source_before.baseline_tree_hash,
        external_path,
        expected_external_hash,
    ):
        base_result.update({
            "outcome": "BLOCKED_SOURCE_CHANGED",
            "source_changed": False,
            "message": "The source or tests changed after diagnosis; the stale repair was refused.",
        })
        return _persist_result(base_result, destination)

    target = (source_path / accepted.relative_path).resolve()
    try:
        target.relative_to(source_path)
    except ValueError:
        base_result.update({
            "outcome": "BLOCKED_UNSAFE_TARGET",
            "source_changed": False,
            "message": "The verified repair target escaped the selected project.",
        })
        return _persist_result(base_result, destination)
    original_bytes = target.read_bytes()
    original_hash = hashlib.sha256(original_bytes).hexdigest()
    if original_hash != source_before.canonical_hashes.get(accepted.relative_path):
        base_result.update({
            "outcome": "BLOCKED_SOURCE_CHANGED",
            "source_changed": False,
            "message": "The target file no longer matches the inspected baseline.",
        })
        return _persist_result(base_result, destination)

    backup = run_root / "backups" / accepted.relative_path
    backup.parent.mkdir(parents=True, exist_ok=True)
    backup.write_bytes(original_bytes)
    repaired_bytes = accepted.repaired_text.encode("utf-8")
    applied = False
    rollback_performed = False
    try:
        _atomic_replace(target, repaired_bytes, repair_id)
        applied = True
        expected_hashes = dict(source_before.canonical_hashes)
        expected_hashes[accepted.relative_path] = hashlib.sha256(repaired_bytes).hexdigest()
        expected_tree_hash = compute_tree_hash(expected_hashes)
        observed_tree_hash = inspect_project(source_path).baseline_tree_hash
        if observed_tree_hash != expected_tree_hash:
            raise RuntimeError("post-apply source tree hash mismatch")
        post_apply = verify_application(source_path, consent=consent)
        if post_apply.get("final_verdict") != "VERIFIED":
            raise RuntimeError("post-apply verification failed")
    except Exception as exc:
        if applied:
            _atomic_replace(target, original_bytes, repair_id + "-rollback")
            rollback_performed = True
        restored = (
            inspect_project(source_path).baseline_tree_hash
            == source_before.baseline_tree_hash
        )
        base_result.update({
            "outcome": "ROLLED_BACK",
            "source_changed": not restored,
            "rollback_performed": rollback_performed,
            "rollback_verified": restored,
            "message": f"Repair application failed safely: {type(exc).__name__}: {exc}",
            "backup_path": str(backup),
        })
        return _persist_result(base_result, destination)

    source_after = inspect_project(source_path)
    base_result.update({
        "outcome": "REPAIRED_AND_VERIFIED",
        "source_changed": True,
        "source": {
            **base_result["source"],
            "tree_sha256_after": source_after.baseline_tree_hash,
            "target_sha256_after": hashlib.sha256(repaired_bytes).hexdigest(),
        },
        "backup_path": str(backup),
        "post_apply_verification": {
            "verification_id": post_apply["verification_id"],
            "verdict": post_apply["final_verdict"],
            "gates": post_apply["gates"],
            "evidence_path": post_apply["evidence_path"],
        },
        "message": "The exact isolated repair was applied and independently re-verified.",
    })
    return _persist_result(base_result, destination)
