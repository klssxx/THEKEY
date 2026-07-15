"""Recovery protocol tests (section 31: RECOVERY)."""

import pytest

from thekey.recovery import RecoveryController
from thekey.state_machine import StateMachine


def test_truncated_output_recovers_no_change():
    sm = StateMachine()
    sm.reset_to_submitted("R1")
    sm.apply_transition("BASELINED", run_id="R1", role="orchestrator", reason="t")
    rc = RecoveryController(sm)
    res = rc.reconcile("R1")
    # No unrecorded changes -> no change.
    assert res.outcome in ("RECOVERED_NO_CHANGE", "RECOVERED_ACTION_NOT_APPLIED")


def test_stale_output_reconciliation_idempotent():
    sm = StateMachine()
    sm.reset_to_submitted("R1")
    sm.apply_transition("BASELINED", run_id="R1", role="orchestrator", reason="t")
    rc = RecoveryController(sm)
    r1 = rc.reconcile("R1")
    r2 = rc.reconcile("R1")
    # Idempotent: same deterministic outcome.
    assert r1.outcome == r2.outcome


def test_ambiguous_recovery_blocks():
    sm = StateMachine()
    sm.reset_to_submitted("R1")
    # Advance to IMPLEMENTED but create no workspace artifacts -> ambiguous.
    for to in ("BASELINED", "ANALYZED", "PLAN_PROPOSED", "PLAN_APPROVED", "IMPLEMENTED"):
        sm.apply_transition(to, run_id="R1", role="orchestrator", reason="t")
    rc = RecoveryController(sm)
    res = rc.reconcile("R1")
    assert res.outcome == "RECOVERY_BLOCKED_AMBIGUOUS"
    with pytest.raises(Exception):
        rc.require_blocked(res)


def test_unrecorded_change_detected():
    sm = StateMachine()
    sm.reset_to_submitted("R1")
    sm.apply_transition("BASELINED", run_id="R1", role="orchestrator", reason="t")
    rc = RecoveryController(sm)
    # Suspected action with no recorded command result -> not applied.
    res = rc.reconcile("R1", suspected_action="REPLACE_EXACT_TEXT")
    assert res.outcome == "RECOVERED_ACTION_NOT_APPLIED"
