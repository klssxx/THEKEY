"""Read-only intake and isolated verification for local Python projects."""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from .config import THEKEY_DIR
from .errors import UnsupportedProjectProfileError
from .policies import PolicyEngine
from .project_loader import inspect_project
from .project_profiler import profile_project

PROJECT_TEST_CONSENT = "execute_trusted_tests"
MAX_PROCESS_OUTPUT_CHARS = 24_000


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _canonical_sha256(value: dict) -> str:
    body = json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(body).hexdigest()


def _verification_id() -> str:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    return f"PV-{stamp}-{uuid4().hex[:8]}"


def _external_tests_for(source: Path, local_test_roots: list[str]) -> Path | None:
    """Return a conventional sibling monorepo test root when one is present."""
    if local_test_roots:
        return None
    candidate = source.parent / "tests" / source.name
    if not candidate.is_dir():
        return None
    try:
        if any(candidate.rglob("test_*.py")):
            return candidate.resolve()
    except OSError:
        return None
    return None


def _combined_input_hash(source_hash: str, external_test_hash: str | None) -> str:
    if external_test_hash is None:
        return source_hash
    return _canonical_sha256({
        "source_tree_sha256": source_hash,
        "external_tests_tree_sha256": external_test_hash,
    })


def inspect_application(source: str | Path, *, output: Path | None = None) -> dict:
    source_path = Path(source).expanduser().resolve()
    inspection = inspect_project(source_path)
    external_test_path = _external_tests_for(source_path, inspection.test_roots)
    external_test_inspection = (
        inspect_project(external_test_path) if external_test_path else None
    )
    try:
        profile = profile_project(source_path).to_dict()
        profile_supported = profile["detected_profile"] != "unsupported"
        profile_error = None
    except UnsupportedProjectProfileError as exc:
        profile = {
            "project_name": source_path.name,
            "source_root": str(source_path),
            "source_access": "READ_ONLY",
            "detected_profile": "unsupported",
            "profile_confidence": 0.0,
            "test_configuration": {"test_roots": inspection.test_roots},
        }
        profile_supported = False
        profile_error = str(exc)

    unsafe_findings = [*inspection.symlink_findings, *inspection.reparse_findings]
    if external_test_inspection:
        unsafe_findings.extend(
            f"external-tests:{item}"
            for item in [
                *external_test_inspection.symlink_findings,
                *external_test_inspection.reparse_findings,
            ]
        )
    checkmate_verdict = "PASS" if profile_supported and not unsafe_findings else "FAIL"
    risk = "LOW"
    tests_detected = bool(inspection.test_roots or external_test_inspection)
    if inspection.warnings or not tests_detected:
        risk = "MEDIUM"
    if unsafe_findings or not profile_supported:
        risk = "HIGH"

    verification_input_hash = _combined_input_hash(
        inspection.baseline_tree_hash,
        (
            external_test_inspection.baseline_tree_hash
            if external_test_inspection
            else None
        ),
    )
    plan_material = {
        "operation": "READ_ONLY_PROJECT_INSPECTION",
        "source_tree_hash": verification_input_hash,
        "profile": profile["detected_profile"],
        "access_mode": "READ_ONLY",
        "output_scope": "THEKEY_ISOLATED_VERIFICATION_ONLY",
    }
    plan_sha256 = _canonical_sha256(plan_material)
    run_id = _verification_id()
    policy = PolicyEngine()
    policy_decision = policy.authorize_project_verification({
        "source_tree_hash": verification_input_hash,
        "profile": profile["detected_profile"],
        "access_mode": "READ_ONLY",
        "output_scope": "THEKEY_ISOLATED_VERIFICATION_ONLY",
        "checkmate_verdict": checkmate_verdict,
    })
    result = {
        "schema_version": "v1",
        "verification_id": run_id,
        "created_at": _utc_now(),
        "source": {
            "path": str(source_path),
            "access_mode": "READ_ONLY",
            "file_count": inspection.included_file_count,
            "tree_sha256": inspection.baseline_tree_hash,
            "verification_input_sha256": verification_input_hash,
            "git_detected": inspection.git_detected,
            "git_head": inspection.git_head,
            "git_dirty": inspection.git_dirty,
        },
        "profile": profile,
        "inspection": {
            "entrypoints": inspection.detected_entrypoints,
            "test_roots": inspection.test_roots,
            "external_tests": (
                {
                    "path": str(external_test_path),
                    "file_count": external_test_inspection.included_file_count,
                    "tree_sha256": external_test_inspection.baseline_tree_hash,
                }
                if external_test_inspection
                else None
            ),
            "metadata_files": inspection.metadata_files,
            "binary_files": inspection.binary_files,
            "warnings": inspection.warnings,
            "unsafe_findings": unsafe_findings,
            "profile_error": profile_error,
        },
        "plan_sha256": plan_sha256,
        "checkmate_review": {
            "verdict": checkmate_verdict,
            "risk": risk,
            "physical_writes_to_source": False,
            "reasons": [
                "supported project profile" if profile_supported else "unsupported profile",
                "no unsafe links" if not unsafe_findings else "unsafe links detected",
                "tests detected" if tests_detected else "no tests detected",
            ],
        },
        "policy_decision": policy_decision,
        "next_action": (
            (
                "VERIFY_ISOLATED_DOTNET_BUILD_WITH_EXPLICIT_TEST_CONSENT"
                if profile["detected_profile"] == "dotnet-windows"
                else "VERIFY_ISOLATED_COPY_WITH_EXPLICIT_TEST_CONSENT"
            )
            if policy_decision["allowed"]
            else "BLOCKED"
        ),
    }
    destination = output or (
        THEKEY_DIR / "project-verification" / run_id / "inspection.json"
    )
    destination = Path(destination).resolve()
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    result["evidence_path"] = str(destination)
    return result


def _copy_inspected_files(source: Path, target: Path, canonical_hashes: dict[str, str]) -> None:
    target.mkdir(parents=True, exist_ok=False)
    resolved_target = target.resolve()
    for relative in sorted(canonical_hashes):
        source_file = (source / relative).resolve()
        target_file = (target / relative).resolve()
        try:
            target_file.relative_to(resolved_target)
        except ValueError as exc:
            raise ValueError(f"unsafe project path: {relative}") from exc
        target_file.parent.mkdir(parents=True, exist_ok=True)
        target_file.write_bytes(source_file.read_bytes())


def _copy_dotnet_build_state(source: Path, target: Path) -> None:
    """Copy only local NuGet/MSBuild state needed by a no-restore build.

    ``obj`` is generated state and is intentionally not part of the immutable
    source baseline.  It is copied into the disposable workspace solely so a
    no-network .NET build can report the real SDK/dependency problem.
    """
    source_obj = source / "obj"
    if source_obj.is_dir():
        shutil.copytree(source_obj, target / "obj", dirs_exist_ok=True)


def _persist_result(result: dict, destination: Path) -> dict:
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        json.dumps(result, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    result["evidence_path"] = str(destination)
    return result


def _redact_process_output(text: str, workspace: Path) -> str:
    """Return bounded diagnostic text without obvious credential values."""
    normalized = text.replace(str(workspace), "<isolated-workspace>")
    normalized = normalized.replace(str(workspace).replace("\\", "/"), "<isolated-workspace>")
    redactions = (
        (re.compile(r"\bsk-[A-Za-z0-9_-]{12,}\b"), "<redacted-openai-key>"),
        (
            re.compile(
                r"(?i)(api[_-]?key|access[_-]?token|auth[_-]?token|password)"
                r"(\s*[:=]\s*)[^\s,;]+"
            ),
            r"\1\2<redacted>",
        ),
        (re.compile(r"(?i)\bBearer\s+[A-Za-z0-9._~+/-]{12,}"), "Bearer <redacted>"),
    )
    for pattern, replacement in redactions:
        normalized = pattern.sub(replacement, normalized)
    if len(normalized) <= MAX_PROCESS_OUTPUT_CHARS:
        return normalized.strip()
    half = MAX_PROCESS_OUTPUT_CHARS // 2
    return (
        normalized[:half].rstrip()
        + "\n... <diagnostic output truncated> ...\n"
        + normalized[-half:].lstrip()
    )


def _run_bounded_python(
    arguments: list[str],
    workspace: Path,
    *,
    timeout_seconds: int = 300,
) -> dict:
    return _run_bounded_command(
        [sys.executable, *arguments],
        workspace,
        timeout_seconds=timeout_seconds,
        extra_environment={
            "PYTHONDONTWRITEBYTECODE": "1",
            "PYTHONHASHSEED": "0",
            **({"PYINSTALLER_RESET_ENVIRONMENT": "1"} if getattr(sys, "frozen", False) else {}),
        },
    )


def _run_bounded_command(
    command: list[str],
    workspace: Path,
    *,
    timeout_seconds: int = 300,
    extra_environment: dict[str, str] | None = None,
) -> dict:
    """Run a fixed, audited command in an isolated workspace."""
    env = os.environ.copy()
    env.update(extra_environment or {})
    started = time.monotonic()
    timed_out = False
    try:
        process = subprocess.run(
            command,
            cwd=str(workspace),
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
            env=env,
        )
        returncode = process.returncode
        stdout = process.stdout
        stderr = process.stderr
    except subprocess.TimeoutExpired as exc:
        timed_out = True
        returncode = None
        stdout = exc.stdout or ""
        stderr = exc.stderr or ""
        if isinstance(stdout, bytes):
            stdout = stdout.decode("utf-8", errors="replace")
        if isinstance(stderr, bytes):
            stderr = stderr.decode("utf-8", errors="replace")
        stderr += f"\nTimed out after {timeout_seconds} seconds."
    except FileNotFoundError as exc:
        returncode = None
        stdout = ""
        stderr = f"Required command is unavailable: {exc.filename}"
    combined_text = stdout + "\n" + stderr
    combined = combined_text.encode("utf-8", errors="replace")
    return {
        "returncode": returncode,
        "timed_out": timed_out,
        "duration_ms": round((time.monotonic() - started) * 1000),
        "output_sha256": hashlib.sha256(combined).hexdigest(),
        "output_bytes": len(combined),
        "output_excerpt": _redact_process_output(combined_text, workspace),
    }


def _diagnostics_for(
    compile_result: dict,
    tests_result: dict | None,
    secret_result: dict,
    documentation_present: bool,
    *,
    language: str = "python",
) -> list[dict]:
    """Translate raw gate evidence into concise, actionable findings."""
    findings: list[dict] = []
    if compile_result["returncode"] != 0:
        excerpt = compile_result.get("output_excerpt", "")
        if "Required command is unavailable" in excerpt:
            code = "TOOLCHAIN_UNAVAILABLE"
            summary = "The required local language toolchain is not installed or not on PATH."
            repair_class = "REQUIRES_ENVIRONMENT_SETUP"
        elif language == "csharp":
            if "NETSDK1112" in excerpt:
                code = "DOTNET_RUNTIME_REFERENCE_MISSING"
                summary = (
                    "The .NET SDK runtime reference package is missing "
                    "from the local restore state."
                )
            elif "NETSDK1004" in excerpt or "project.assets.json" in excerpt:
                code = "DOTNET_RESTORE_REQUIRED"
                summary = "The isolated .NET build requires a completed NuGet restore."
            elif "NU1301" in excerpt:
                code = "DOTNET_NUGET_SOURCE_UNAVAILABLE"
                summary = "NuGet could not reach a configured package source."
            else:
                code = "DOTNET_BUILD_FAILURE"
                summary = "The .NET project did not build in the isolated copy."
            repair_class = "REQUIRES_DEPENDENCY_OR_HUMAN_REVIEW"
        elif language == "javascript":
            code = "NODE_BUILD_FAILURE"
            summary = "The Node.js build script failed in the isolated copy."
            repair_class = "REQUIRES_HUMAN_REVIEW"
        elif language == "rust":
            code = "RUST_CHECK_FAILURE"
            summary = "Cargo could not check the Rust project in the isolated copy."
            repair_class = "REQUIRES_HUMAN_REVIEW"
        elif language == "go":
            code = "GO_TEST_OR_BUILD_FAILURE"
            summary = "Go could not compile or test the module in the isolated copy."
            repair_class = "REQUIRES_HUMAN_REVIEW"
        elif language == "java":
            code = "MAVEN_BUILD_FAILURE"
            summary = "Maven could not compile the project in offline isolated mode."
            repair_class = "REQUIRES_DEPENDENCY_OR_HUMAN_REVIEW"
        else:
            code = "PYTHON_COMPILE_FAILURE"
            summary = "One or more Python files do not compile."
            repair_class = "SAFE_SYNTAX_CANDIDATE"
        findings.append({
            "code": code,
            "severity": "ERROR",
            "summary": summary,
            "evidence": excerpt,
            "repair_class": repair_class,
        })
    if tests_result is None:
        findings.append({
            "code": "TESTS_NOT_FOUND",
            "severity": "ERROR",
            "summary": (
                "No .NET test project was detected; an automatic repair cannot be proven."
                if language == "csharp" else
                "No pytest tests were detected; an automatic repair cannot be proven."
            ),
            "evidence": "",
            "repair_class": "NOT_AUTOMATICALLY_REPAIRABLE",
        })
    elif tests_result["returncode"] != 0:
        excerpt = tests_result.get("output_excerpt", "")
        if language == "rust" and ("link.exe" in excerpt or "linker" in excerpt):
            code = "RUST_LINKER_UNAVAILABLE"
            summary = "Rust tests need the local C/C++ linker toolchain."
            repair_class = "REQUIRES_ENVIRONMENT_SETUP"
        elif "ModuleNotFoundError" in excerpt or "ImportError" in excerpt:
            code = "TEST_DEPENDENCY_OR_IMPORT_FAILURE"
            summary = "The test suite has a missing dependency or import."
            repair_class = "NOT_AUTOMATICALLY_REPAIRABLE"
        elif tests_result.get("timed_out"):
            code = "TEST_TIMEOUT"
            summary = "The test suite exceeded its time limit."
            repair_class = "NOT_AUTOMATICALLY_REPAIRABLE"
        else:
            code = "TEST_FAILURE" if language == "python" else f"{language.upper()}_TEST_FAILURE"
            summary = "The project's test suite failed in the isolated copy."
            repair_class = "BOUNDED_LOGIC_MUTATION_CANDIDATE"
        failed_nodes = sorted(set(re.findall(r"(?m)^FAILED\s+([^\s]+)", excerpt)))
        findings.append({
            "code": code,
            "severity": "ERROR",
            "summary": summary,
            "failed_tests": failed_nodes[:50],
            "evidence": excerpt,
            "repair_class": repair_class,
        })
    if not secret_result["passed"]:
        findings.append({
            "code": "POTENTIAL_SECRET_EXPOSURE",
            "severity": "ERROR",
            "summary": "The bounded secret scan found credential-like material.",
            "evidence": secret_result["findings"],
            "repair_class": "REQUIRES_HUMAN_REVIEW",
        })
    if not documentation_present:
        findings.append({
            "code": "DOCUMENTATION_MISSING",
            "severity": "ERROR",
            "summary": "README.md, README.rst, or README.txt is required.",
            "evidence": "",
            "repair_class": "REQUIRES_HUMAN_CONTENT",
        })
    return findings


def _limited_secret_scan(workspace: Path, policy) -> dict:
    patterns = [re.compile(item) for item in policy.secret_scan_scope["patterns"]]
    excluded = {item.casefold() for item in policy.excluded_directories}
    # Build output is not authored application source.  In particular .NET
    # cache files are high-entropy hashes and must never become false secret
    # findings after we copy local restore state into an isolated workspace.
    excluded.update({"bin", "obj", "dist", "build", "artifacts", "publish", "target"})
    findings: list[dict] = []
    for path in workspace.rglob("*"):
        if not path.is_file() or any(part.casefold() in excluded for part in path.parts):
            continue
        try:
            if path.stat().st_size > 1_048_576:
                continue
            raw = path.read_bytes()
            if b"\x00" in raw[:1024]:
                continue
            text = raw.decode("utf-8", errors="ignore")
        except OSError:
            continue
        for index, line in enumerate(text.splitlines(), 1):
            if any(pattern.search(line) for pattern in patterns):
                findings.append({"path": str(path.relative_to(workspace)), "line": index})
    return {"passed": not findings, "finding_count": len(findings), "findings": findings[:50]}


def _run_dotnet_test_projects(
    projects: list[str], workspace: Path, *, timeout_seconds: int = 300
) -> dict | None:
    if not projects:
        return None
    runs = [
        _run_bounded_command(
            ["dotnet", "test", project, "--no-restore", "--configuration", "Release", "--nologo"],
            workspace,
            timeout_seconds=timeout_seconds,
        )
        for project in projects
    ]
    text = "\n".join(run["output_excerpt"] for run in runs)
    encoded = text.encode("utf-8", errors="replace")
    return {
        "returncode": 0 if all(run["returncode"] == 0 for run in runs) else 1,
        "timed_out": any(run["timed_out"] for run in runs),
        "duration_ms": sum(run["duration_ms"] for run in runs),
        "output_sha256": hashlib.sha256(encoded).hexdigest(),
        "output_bytes": len(encoded),
        "output_excerpt": _redact_process_output(text, workspace),
        "projects": projects,
    }


def verify_application(
    source: str | Path,
    *,
    consent: str,
    output: Path | None = None,
) -> dict:
    if consent != PROJECT_TEST_CONSENT:
        raise PermissionError(
            "Explicit consent is required because project tests execute trusted local code "
            "without an operating-system sandbox."
        )
    source_path = Path(source).expanduser().resolve()
    inspection_before = inspect_project(source_path)
    external_test_path = _external_tests_for(source_path, inspection_before.test_roots)
    external_test_before = (
        inspect_project(external_test_path) if external_test_path else None
    )
    inspection_result = inspect_application(source_path)
    if not inspection_result["policy_decision"]["allowed"]:
        inspection_result["final_verdict"] = "BLOCKED"
        return inspection_result

    verification_id = _verification_id()
    run_root = THEKEY_DIR / "project-verification" / verification_id
    workspace = run_root / "isolated-workspace"
    profile = inspection_result["profile"]
    profile_name = profile["detected_profile"]
    is_dotnet = profile_name.startswith("dotnet-")
    try:
        if external_test_before:
            _copy_inspected_files(
                source_path,
                workspace / source_path.name,
                inspection_before.canonical_hashes,
            )
            _copy_inspected_files(
                external_test_path,
                workspace / "tests" / source_path.name,
                external_test_before.canonical_hashes,
            )
            project_workspace = workspace / source_path.name
            test_arguments = ["-m", "pytest", "-q", str(Path("tests") / source_path.name)]
        else:
            _copy_inspected_files(
                source_path,
                workspace,
                inspection_before.canonical_hashes,
            )
            project_workspace = workspace
            test_arguments = ["-m", "pytest", "-q"]
        if is_dotnet:
            _copy_dotnet_build_state(source_path, project_workspace)
    except OSError as exc:
        inspection_after = inspect_project(source_path)
        external_test_after = (
            inspect_project(external_test_path) if external_test_path else None
        )
        source_unchanged = (
            inspection_before.baseline_tree_hash == inspection_after.baseline_tree_hash
            and (
                external_test_before is None
                or (
                    external_test_after is not None
                    and external_test_before.baseline_tree_hash
                    == external_test_after.baseline_tree_hash
                )
            )
        )
        result = {
            "schema_version": "v1",
            "verification_id": verification_id,
            "created_at": _utc_now(),
            "source": {
                "path": str(source_path),
                "access_mode": "READ_ONLY",
                "tree_sha256_before": inspection_before.baseline_tree_hash,
                "tree_sha256_after": inspection_after.baseline_tree_hash,
                "unchanged": source_unchanged,
            },
            "profile": inspection_result["profile"],
            "plan_sha256": inspection_result["plan_sha256"],
            "checkmate_review": inspection_result["checkmate_review"],
            "policy_decision": inspection_result["policy_decision"],
            "test_execution": {
                "explicit_consent": True,
                "operating_system_sandbox": False,
                "network_install_performed": False,
                "workspace": str(workspace),
            },
            "gates": [
                {
                    "gate": "ISOLATED_COPY_CREATED",
                    "passed": False,
                    "status": "FAILED",
                    "reason": f"{type(exc).__name__}: {exc}",
                },
                {
                    "gate": "SOURCE_UNCHANGED",
                    "passed": source_unchanged,
                    "status": "PASSED" if source_unchanged else "FAILED",
                },
            ],
            "final_verdict": "BLOCKED",
        }
        destination = (
            Path(output).resolve()
            if output
            else run_root / "verification-evidence.json"
        )
        return _persist_result(result, destination)

    if is_dotnet:
        csproj = profile["packaging"]["csproj"]
        compile_result = _run_bounded_command(
            ["dotnet", "build", csproj, "--no-restore", "--configuration", "Release", "--nologo"],
            workspace,
        )
        test_projects = list(profile["test_configuration"].get("test_projects", []))
        tests_present = bool(test_projects)
        tests_result = (
            _run_dotnet_test_projects(test_projects, workspace)
            if compile_result["returncode"] == 0 else None
        )
        compile_gate = "DOTNET_BUILD_PASSED"
    elif profile_name == "node-javascript":
        # On Windows npm is a command script. Invoke the explicit `.cmd`
        # entrypoint so subprocess does not depend on shell resolution or an
        # incidental `npm` shim being present on PATH.
        npm = "npm.cmd" if os.name == "nt" else "npm"
        compile_result = _run_bounded_command(
            [npm, "run", "build", "--if-present"], workspace,
        )
        tests_present = bool(profile["test_configuration"].get("has_test_script"))
        tests_result = (
            _run_bounded_command([npm, "test"], workspace)
            if compile_result["returncode"] == 0 and tests_present else None
        )
        compile_gate = "NODE_BUILD_PASSED"
    elif profile_name == "rust-cargo":
        compile_result = _run_bounded_command(
            ["cargo", "check", "--offline"], workspace,
        )
        tests_present = bool(profile["test_configuration"].get("has_tests"))
        tests_result = (
            _run_bounded_command(["cargo", "test", "--offline"], workspace)
            if compile_result["returncode"] == 0 and tests_present else None
        )
        compile_gate = "RUST_CHECK_PASSED"
    elif profile_name == "go-module":
        compile_result = _run_bounded_command(["go", "test", "./..."], workspace)
        tests_present = bool(profile["test_configuration"].get("has_tests"))
        tests_result = compile_result if tests_present else None
        compile_gate = "GO_BUILD_PASSED"
    elif profile_name == "java-maven":
        compile_result = _run_bounded_command(
            ["mvn", "--offline", "--quiet", "-DskipTests", "compile"], workspace,
        )
        tests_present = bool(profile["test_configuration"].get("has_tests"))
        tests_result = (
            _run_bounded_command(["mvn", "--offline", "--quiet", "test"], workspace)
            if compile_result["returncode"] == 0 and tests_present else None
        )
        compile_gate = "MAVEN_COMPILE_PASSED"
    else:
        # ``-b`` keeps bytecode beside the copied sources.  Besides making the
        # generated artifact easy to discard with the workspace, this avoids
        # the extra ``__pycache__`` path depth that can trigger Windows error 206.
        compile_result = _run_bounded_python(
            ["-m", "compileall", "-q", "-b", "."], workspace
        )
        tests_present = bool(inspection_before.test_roots or external_test_before)
        tests_result = (
            _run_bounded_python(test_arguments, workspace)
            if tests_present
            else None
        )
        compile_gate = "PYTHON_COMPILE_PASSED"
    policy_engine = PolicyEngine()
    policy = policy_engine.load_default()
    secret_result = _limited_secret_scan(workspace, policy)
    documentation_present = any(
        (project_workspace / name).is_file()
        for name in ("README.md", "README.rst", "README.txt")
    )
    inspection_after = inspect_project(source_path)
    external_test_after = (
        inspect_project(external_test_path) if external_test_path else None
    )
    source_unchanged = (
        inspection_before.baseline_tree_hash == inspection_after.baseline_tree_hash
        and (
            external_test_before is None
            or (
                external_test_after is not None
                and external_test_before.baseline_tree_hash
                == external_test_after.baseline_tree_hash
            )
        )
    )

    gates = [
        {
            "gate": "CHECKMATE_PRECHECK_PASSED",
            "passed": inspection_result["checkmate_review"]["verdict"] == "PASS",
            "status": inspection_result["checkmate_review"]["verdict"],
        },
        {
            "gate": compile_gate,
            "passed": compile_result["returncode"] == 0,
            "status": "PASSED" if compile_result["returncode"] == 0 else "FAILED",
            "evidence": compile_result,
        },
        {
            "gate": "UNIT_TESTS_PASSED",
            "passed": bool(tests_result and tests_result["returncode"] == 0),
            "status": (
                "PASSED"
                if tests_result and tests_result["returncode"] == 0
                else "FAILED" if tests_result else "NO_VERIFICABLE"
            ),
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
        {
            "gate": "SOURCE_UNCHANGED",
            "passed": source_unchanged,
            "status": "PASSED" if source_unchanged else "FAILED",
        },
    ]
    if not tests_present:
        final_verdict = "NO_VERIFICABLE"
    elif all(gate["passed"] for gate in gates):
        final_verdict = "VERIFIED"
    else:
        final_verdict = "BLOCKED"

    result = {
        "schema_version": "v1",
        "verification_id": verification_id,
        "created_at": _utc_now(),
        "source": {
            "path": str(source_path),
            "access_mode": "READ_ONLY",
            "tree_sha256_before": inspection_before.baseline_tree_hash,
            "tree_sha256_after": inspection_after.baseline_tree_hash,
            "unchanged": source_unchanged,
            "external_tests": (
                {
                    "path": str(external_test_path),
                    "tree_sha256_before": external_test_before.baseline_tree_hash,
                    "tree_sha256_after": external_test_after.baseline_tree_hash,
                    "unchanged": (
                        external_test_before.baseline_tree_hash
                        == external_test_after.baseline_tree_hash
                    ),
                }
                if external_test_before and external_test_after
                else None
            ),
        },
        "profile": inspection_result["profile"],
        "plan_sha256": inspection_result["plan_sha256"],
        "checkmate_review": inspection_result["checkmate_review"],
        "policy_decision": inspection_result["policy_decision"],
        "test_execution": {
            "explicit_consent": True,
            "operating_system_sandbox": False,
            "network_install_performed": False,
            "workspace": str(workspace),
        },
        "gates": gates,
        "diagnostics": _diagnostics_for(
            compile_result,
            tests_result,
            secret_result,
            documentation_present,
            language=profile["language"],
        ),
        "final_verdict": final_verdict,
    }
    destination = Path(output).resolve() if output else run_root / "verification-evidence.json"
    return _persist_result(result, destination)
