"""End-to-end deterministic run tests (section 31: END-TO-END)."""

import pytest

from thekey.main import RunCoordinator
from thekey.config import DEMO_APP_SOURCE


def _full_positive():
    c = RunCoordinator()
    c.create("Canonical governed demo", "Fix calculator.add")
    c.baseline()
    c.plan()
    c.approve_plan()
    c.execute()
    c.verify()
    decision = c.decide()
    return c, decision


def test_e2e_positive_reaches_release_eligible():
    c, decision = _full_positive()
    assert decision.decision == "RELEASE_ELIGIBLE"
    assert c.sm.load().run_state == "RELEASE_ELIGIBLE"


def test_e2e_original_demo_unchanged():
    _full_positive()
    # Original source still defective.
    assert "return a - b" in DEMO_APP_SOURCE.read_text(encoding="utf-8")


def test_e2e_workspace_repaired():
    c, _ = _full_positive()
    ws_file = c.run.dir.parent.parent / "workspaces" / c.run.run_id / "src/demo_app/calculator.py"
    # Use the canonical workspace path.
    from thekey.config import WORKSPACES_DIR

    ws_file = WORKSPACES_DIR / c.run.run_id / "src/demo_app/calculator.py"
    assert "return a + b" in ws_file.read_text(encoding="utf-8")


def test_e2e_evidence_verify_passes():
    c, _ = _full_positive()
    from thekey.evidence import sha256_file

    data = __import__("json").loads((c.run.dir / "artifact-hashes.json").read_text(encoding="utf-8"))
    for name, expected in data["hashes"].items():
        p = c.run.dir / name
        assert sha256_file(p) == expected


def test_e2e_blocked_invalid_policy():
    c = RunCoordinator()
    decision = c.run_blocked("invalid_policy")
    assert decision.decision == "BLOCKED"


def test_e2e_blocked_failed_gate():
    c = RunCoordinator()
    decision = c.run_blocked("failed_gate")
    assert decision.decision == "BLOCKED"
    failed = [g for g in decision.gates if not g["passed"]]
    assert failed


def test_e2e_blocked_tampered_evidence():
    c = RunCoordinator()
    decision = c.run_blocked("tampered_evidence")
    assert decision.decision == "BLOCKED"


def test_e2e_blocked_missing_input():
    c = RunCoordinator()
    decision = c.run_blocked("missing_input")
    assert decision.decision == "BLOCKED"
    assert "Missing required input" in decision.reason
