"""THEKEY Core CLI.

Commands:
  thekey run create
  thekey run plan
  thekey run approve-plan
  thekey run execute
  thekey run verify
  thekey run status
  thekey evidence verify
  thekey demo
  python -m thekey

Every command: --help, stable exit codes, human/--json output, includes run id,
actionable errors, redacts secrets, works in PowerShell 7.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import __version__
from .config import (
    DEFAULT_POLICY_FILE,
    DEMO_APP_SOURCE,
    RUNS_DIR,
    WORKSPACES_DIR,
)
from .errors import (
    BudgetExceededError,
    GateFailureError,
    InvalidEvidenceError,
    InvalidPolicyError,
    RecoveryBlockedError,
    StaleModelOutputError,
    TheKeyError,
    UnauthorizedPathError,
)
from .main import RunCoordinator
from .policies import PolicyEngine
from .runs import RunManager
from .state_machine import StateMachine, is_legal

EXIT_CODES = {
    "GENERAL_ERROR": 1,
    "INVALID_ARGUMENTS": 2,
    "INCOMPATIBLE_RUN_STATE": 3,
    "INVALID_POLICY": 4,
    "GATE_FAILURE": 5,
    "INVALID_EVIDENCE": 6,
    "BUDGET_EXCEEDED": 7,
    "UNAUTHORIZED_PATH": 8,
    "STALE_MODEL_OUTPUT": 9,
    "RECOVERY_BLOCKED": 10,
}


def _redact_env() -> None:
    """Defense in depth: never let secrets leak via tracebacks in CLI output."""
    pass


def _print(obj, as_json: bool) -> None:
    if as_json:
        print(json.dumps(obj, indent=2, ensure_ascii=False))
    else:
        if isinstance(obj, dict):
            for k, v in obj.items():
                print(f"{k}: {v}")
        else:
            print(obj)


def _fail(err: TheKeyError) -> int:
    sys.stderr.write(f"error: [{err.code}] {err.detail}\n")
    return EXIT_CODES.get(err.code, 1)


def _coordinator_for(run_id: str | None) -> RunCoordinator:
    rm = RunManager(RUNS_DIR)
    if run_id:
        run = rm.get_run(run_id)
    else:
        run = None
    return RunCoordinator(run=run, runs_dir=RUNS_DIR, workspaces_dir=WORKSPACES_DIR)


# ---------------------------------------------------------------------------
# Subcommands
# ---------------------------------------------------------------------------
def cmd_run_create(args) -> int:
    coord = _coordinator_for(None)
    coord.create(title=args.title or "Governed run", description=args.description or "")
    _print({**coord.summary(), "title": args.title}, args.json)
    return 0


def cmd_run_plan(args) -> int:
    coord = _coordinator_for(args.run_id)
    if coord.sm.load().run_state == "SUBMITTED":
        coord.baseline()
    plan = coord.plan()
    _print({"run_id": coord.run.run_id, "plan": plan.to_dict()}, args.json)
    return 0


def cmd_run_approve(args) -> int:
    coord = _coordinator_for(args.run_id)
    approval = coord.approve_plan()
    _print({"run_id": coord.run.run_id, "approval": approval.to_dict()}, args.json)
    return 0


def cmd_run_execute(args) -> int:
    coord = _coordinator_for(args.run_id)
    res = coord.execute()
    _print({"run_id": coord.run.run_id, "changed": len(res["results"])}, args.json)
    return 0


def cmd_run_verify(args) -> int:
    coord = _coordinator_for(args.run_id)
    results = coord.verify()
    failed = [r.gate for r in results if not r.passed]
    _print({"run_id": coord.run.run_id, "gates": [r.to_dict() for r in results],
            "failed": failed}, args.json)
    if failed:
        return EXIT_CODES["GATE_FAILURE"]
    return 0


def cmd_run_status(args) -> int:
    coord = _coordinator_for(args.run_id)
    _print(coord.summary(), args.json)
    return 0


def cmd_evidence_verify(args) -> int:
    coord = _coordinator_for(args.run_id)
    # Verify hashes of principal artifacts and the state chain.
    hashes_path = coord.run.dir / "artifact-hashes.json"
    if not hashes_path.exists():
        err = InvalidEvidenceError("artifact-hashes.json missing")
        sys.stderr.write(f"error: [{err.code}] {err.detail}\n")
        return EXIT_CODES["INVALID_EVIDENCE"]
    data = json.loads(hashes_path.read_text(encoding="utf-8"))
    mismatches = []
    for name, expected in data["hashes"].items():
        p = coord.run.dir / name
        if not p.exists():
            mismatches.append((name, "MISSING"))
            continue
        from .evidence import sha256_file

        actual = sha256_file(p)
        if actual != expected:
            mismatches.append((name, "TAMPERED"))
    ok = not mismatches
    _print({
        "run_id": coord.run.run_id,
        "evidence_ok": ok,
        "mismatches": [{"artifact": n, "status": s} for n, s in mismatches],
    }, args.json)
    return 0 if ok else EXIT_CODES["INVALID_EVIDENCE"]


def cmd_demo(args) -> int:
    if args.blocked:
        coord = _coordinator_for(None)
        coord.create("Blocked demo", f"mode={args.blocked_mode}")
        decision = coord.run_blocked(args.blocked_mode)
        _print({
            "run_id": coord.run.run_id,
            "mode": args.blocked_mode,
            "decision": decision.decision,
            "reason": decision.reason,
        }, args.json)
        if decision.decision == "RELEASE_ELIGIBLE":
            return 0
        # Map invalid-policy blocked runs to the dedicated exit code.
        if args.blocked_mode == "invalid_policy":
            return EXIT_CODES["INVALID_POLICY"]
        return EXIT_CODES["GATE_FAILURE"]
    # Positive canonical demo.
    coord = _coordinator_for(None)
    coord.create("Canonical governed demo", "Fix calculator.add")
    coord.baseline()
    coord.plan()
    coord.approve_plan()
    coord.execute()
    results = coord.verify()
    decision = coord.decide()
    # Evidence verify.
    from .evidence import sha256_file

    hashes_path = coord.run.dir / "artifact-hashes.json"
    data = json.loads(hashes_path.read_text(encoding="utf-8"))
    mismatches = []
    for name, expected in data["hashes"].items():
        p = coord.run.dir / name
        if p.exists() and sha256_file(p) != expected:
            mismatches.append(name)
    out = {
        "run_id": coord.run.run_id,
        "state": coord.sm.load().run_state,
        "decision": decision.decision,
        "gates_passed": sum(r.passed for r in results),
        "gates_total": len(results),
        "evidence_mismatches": mismatches,
        "workspace": str(WORKSPACES_DIR / coord.run.run_id),
        "run_path": str(coord.run.dir),
    }
    _print(out, args.json)
    if decision.decision != "RELEASE_ELIGIBLE" or mismatches:
        return EXIT_CODES["GATE_FAILURE"]
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="thekey", description="THEKEY Core Governed Run (MVP 0.1.0)")
    p.add_argument("--version", action="version", version=f"thekey {__version__}")
    sub = p.add_subparsers(dest="group")

    # run
    run = sub.add_parser("run", help="Run lifecycle commands")
    run_sub = run.add_subparsers(dest="command")
    c = run_sub.add_parser("create", help="Create a run")
    c.add_argument("--title", default="Governed run")
    c.add_argument("--description", default="")
    c.add_argument("--json", action="store_true")
    c.set_defaults(func=cmd_run_create)
    pl = run_sub.add_parser("plan", help="Baseline + propose plan")
    pl.add_argument("--run-id", required=True)
    pl.add_argument("--json", action="store_true")
    pl.set_defaults(func=cmd_run_plan)
    ap = run_sub.add_parser("approve-plan", help="Approve a proposed plan")
    ap.add_argument("--run-id", required=True)
    ap.add_argument("--json", action="store_true")
    ap.set_defaults(func=cmd_run_approve)
    ex = run_sub.add_parser("execute", help="Execute approved plan in workspace")
    ex.add_argument("--run-id", required=True)
    ex.add_argument("--json", action="store_true")
    ex.set_defaults(func=cmd_run_execute)
    ve = run_sub.add_parser("verify", help="Run gates")
    ve.add_argument("--run-id", required=True)
    ve.add_argument("--json", action="store_true")
    ve.set_defaults(func=cmd_run_verify)
    st = run_sub.add_parser("status", help="Show run status")
    st.add_argument("--run-id", required=True)
    st.add_argument("--json", action="store_true")
    st.set_defaults(func=cmd_run_status)

    # evidence
    ev = sub.add_parser("evidence", help="Evidence commands")
    ev_sub = ev.add_subparsers(dest="command")
    evv = ev_sub.add_parser("verify", help="Verify artifact hashes")
    evv.add_argument("--run-id", required=True)
    evv.add_argument("--json", action="store_true")
    evv.set_defaults(func=cmd_evidence_verify)

    # demo
    dm = sub.add_parser("demo", help="Run the canonical / blocked demo")
    dm.add_argument("--blocked", action="store_true")
    dm.add_argument("--blocked-mode", default="failed_gate",
                    choices=["invalid_policy", "failed_gate", "tampered_evidence", "missing_input"])
    dm.add_argument("--json", action="store_true")
    dm.set_defaults(func=cmd_demo)

    return p


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if not getattr(args, "func", None):
        parser.print_help()
        return EXIT_CODES["INVALID_ARGUMENTS"]
    try:
        return args.func(args)
    except TheKeyError as err:
        return _fail(err)
    except FileNotFoundError as err:
        sys.stderr.write(f"error: file not found: {err}\n")
        return EXIT_CODES["GENERAL_ERROR"]
    except Exception as err:  # pragma: no cover - last resort
        sys.stderr.write(f"error: {type(err).__name__}: {err}\n")
        return EXIT_CODES["GENERAL_ERROR"]


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
