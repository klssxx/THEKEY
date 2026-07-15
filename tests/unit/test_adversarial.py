"""Adversarial tests (task 9, optional but value-demonstrating).

These do NOT trust the happy path. They assert THEKEY Core *resists* the
attacks a serious reviewer would try:

  1. Tampering with a sealed artifact after execution -> BLOCKED (never silent).
  2. A forged decision.json with a fake review_token -> BLOCKED on verify.
  3. The autonomous launcher guard refuses to run if the runtime root sits
     inside a protected historical path.
  4. An empty/zero-gate plan can NEVER reach RELEASE_ELIGIBLE.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from thekey import decisions
from thekey.launchers import mimo_launcher as ml
from thekey.main import RunCoordinator


def test_tampered_evidence_blocks_run():
    coord = RunCoordinator()
    coord.create("adv-tamper", "tamper sealed artifact")
    coord.baseline()
    coord.plan()
    coord.approve_plan()
    coord.execute()
    # Adversary tampers with a sealed artifact AFTER execution.
    (coord.run.dir / "changes.diff").write_text("TAMPERED", encoding="utf-8")
    decision = coord.decide()
    assert decision.decision == "BLOCKED"
    coord.close()


def test_forged_review_token_fails_verify():
    forged = {
        "run_id": "R-X",
        "decision": "RELEASE_ELIGIBLE",
        "policy_id": "local-python-demo",
        "approver_identity": "attacker",
        "gates": [{"passed": True}, {"passed": True}, {"passed": True}, {"passed": True}],
        "review_token": "rt-" + "0" * 48,  # fake
        "approved_plan_hash": "abc",
    }
    assert decisions.verify_review_token(forged) is False


def test_guard_refuses_protected_root(monkeypatch: pytest.MonkeyPatch):
    # Point REAL_ROOT at a protected historical path -> guard must hard-refuse.
    prot = Path(r"E:\KLSX PROYECTS\KlsxMaker\TheKey\Thekey")
    monkeypatch.setattr(ml, "REAL_ROOT", prot)
    with pytest.raises(SystemExit) as exc:
        ml._guard_allowed_root()
    assert exc.value.code == 8  # UNAUTHORIZED_PATH


def test_empty_plan_never_releases():
    coord = RunCoordinator()
    coord.create("adv-empty", "empty plan")
    coord.baseline()
    plan = coord.plan()
    plan.operations = []  # adversay empties the plan
    coord._write_artifact("plan.json", plan.to_dict())
    coord.approve_plan()
    coord.execute()
    results = coord.verify()
    decision = coord.decide()
    # With no operations there is no fix -> the build/unit gate fails -> BLOCKED.
    assert decision.decision == "BLOCKED"
    coord.close()
