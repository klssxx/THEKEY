"""Entry point for the Windows 10/11 portable THEKEY bundle.

The source package keeps its normal CLI.  This wrapper adds only packaging
commands and the two bounded Python-module invocations used by Judge Mode's
real build and unit-test gates.
"""

from __future__ import annotations

import contextlib
import io
import json
import sys
from pathlib import Path
from uuid import uuid4


def _configure_console() -> None:
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            reconfigure(encoding="utf-8", errors="replace")


def _run_bounded_module(arguments: list[str]) -> int:
    if len(arguments) < 2:
        print("error: -m requires a module", file=sys.stderr)
        return 2
    module = arguments[1]
    module_args = arguments[2:]
    # A normal ``python -m`` invocation places the working directory on
    # ``sys.path``.  PyInstaller's bootloader does not, so restore that narrow
    # interpreter behavior for the bundled build/test gates.
    working_directory = str(Path.cwd())
    if working_directory not in sys.path:
        sys.path.insert(0, working_directory)
    if module == "pytest":
        import pytest

        return int(pytest.main(module_args))
    if module == "compileall":
        import compileall

        previous = sys.argv
        try:
            sys.argv = ["compileall", *module_args]
            return 0 if compileall.main() else 1
        finally:
            sys.argv = previous
    print(f"error: bundled module is not allowed: {module}", file=sys.stderr)
    return 2


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def verify_evidence(evidence_path: Path) -> dict:
    evidence_path = evidence_path.resolve()
    _require(evidence_path.is_file(), f"evidence file missing: {evidence_path}")
    evidence = _load_json(evidence_path)

    _require(evidence.get("judge_mode") == "THEKEY Build Week Judge Mode", "kind")
    _require(evidence.get("allow", {}).get("status") == "APPLIED", "ALLOW status")
    _require(evidence.get("allow", {}).get("handler_call_count") == 1, "ALLOW handlers")
    _require(evidence.get("deny", {}).get("reason_code") == "ROLE_NOT_ALLOWED", "DENY")
    _require(evidence.get("deny", {}).get("handler_call_count") == 0, "DENY handlers")
    _require(bool(evidence.get("deny", {}).get("workspace_hash_unchanged")), "DENY hash")
    _require(bool(evidence.get("source", {}).get("hash_unchanged")), "source hash")
    bindings = evidence.get("receipt_binding", {})
    _require(
        all(bindings.get(name) is True for name in (
            "run_id_match", "transaction_id_match", "plan_sha256_match"
        )),
        "receipt binding",
    )
    _require(evidence.get("production_reuse") is False, "production reuse")
    gates = evidence.get("gates", [])
    _require(len(gates) == 4 and all(gate.get("passed") is True for gate in gates), "gates")
    _require(evidence.get("release_decision") == "RELEASE_ELIGIBLE", "decision")

    run_path = Path(evidence["run_path"]).resolve()
    review = _load_json(run_path / "checkmate-review-receipt.json")
    authorization = _load_json(run_path / "sovereign-authorization-receipt.json")
    decision = _load_json(run_path / "decision.json")
    for receipt in (review, authorization):
        _require(receipt.get("run_id") == evidence.get("run_id"), "persisted run ID")
        _require(
            receipt.get("transaction_id") == evidence.get("transaction_id"),
            "persisted transaction ID",
        )
        _require(receipt.get("plan_sha256") == evidence.get("plan_sha256"), "plan hash")
    _require(authorization.get("production_reuse") is False, "persisted reuse")
    _require(decision.get("decision") == "RELEASE_ELIGIBLE", "persisted decision")
    _require(
        all(gate.get("passed") is True for gate in decision.get("gates", [])),
        "persisted gates",
    )
    return evidence


def _latest_evidence(thekey_dir: Path) -> Path:
    candidates = list(thekey_dir.glob("**/judge-mode-evidence.json"))
    if not candidates:
        raise FileNotFoundError("No Judge Mode evidence found. Run the governed demo first.")
    return max(candidates, key=lambda path: path.stat().st_mtime_ns)


def _print_verified_summary(evidence: dict, evidence_path: Path) -> None:
    print("THEKEY - THE KING OF CHECKMATE")
    print("Governed Codex Transactions for Coding Agents")
    print()
    print("ALLOW: APPLIED, handlers=1")
    print("DENY: ROLE_NOT_ALLOWED, handlers=0")
    print("GATES: 4/4 PASS")
    print("DECISION: RELEASE_ELIGIBLE")
    print("SOURCE: unchanged=True")
    print("RECEIPTS: bound=True")
    print("PRODUCTION REUSE: False")
    print(f"RUN ID: {evidence['run_id']}")
    print(f"EVIDENCE: {evidence_path}")


def portable_demo() -> int:
    from thekey.cli import main as cli_main
    from thekey.config import DEMO_APP_SOURCE, THEKEY_DIR

    output_dir = THEKEY_DIR / "portable" / f"Portable Demo {uuid4().hex}"
    evidence_path = output_dir / "judge-mode-evidence.json"
    captured = io.StringIO()
    with contextlib.redirect_stdout(captured):
        result = cli_main([
            "judge-mode",
            "--source",
            str(DEMO_APP_SOURCE),
            "--output",
            str(evidence_path),
            "--json",
        ])
    if result != 0:
        print(captured.getvalue(), file=sys.stderr)
        return int(result)
    evidence = verify_evidence(evidence_path)
    _print_verified_summary(evidence, evidence_path)
    return 0


def portable_verify(arguments: list[str]) -> int:
    from thekey.config import THEKEY_DIR

    evidence_path = Path(arguments[0]) if arguments else _latest_evidence(THEKEY_DIR)
    evidence = verify_evidence(evidence_path)
    print("EVIDENCE VERIFY: VALID")
    _print_verified_summary(evidence, evidence_path.resolve())
    return 0


def main() -> int:
    _configure_console()
    arguments = sys.argv[1:]
    try:
        if arguments[:1] == ["-m"]:
            return _run_bounded_module(arguments)
        if arguments[:1] == ["portable-demo"]:
            return portable_demo()
        if arguments[:1] == ["portable-verify"]:
            return portable_verify(arguments[1:])

        from thekey.cli import main as cli_main

        return int(cli_main(arguments))
    except Exception as exc:
        print(f"error: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
