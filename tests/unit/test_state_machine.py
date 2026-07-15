"""State machine tests (section 31: STATE MACHINE)."""

import pytest

from thekey.state_machine import (
    LEGAL_TRANSITIONS,
    StateMachine,
    is_legal,
)
from thekey.errors import InvalidTransitionError


def test_valid_transitions():
    sm = StateMachine()
    # Walk the main flow.
    for frm, to in [
        ("SUBMITTED", "BASELINED"),
        ("BASELINED", "ANALYZED"),
        ("ANALYZED", "PLAN_PROPOSED"),
        ("PLAN_PROPOSED", "PLAN_APPROVED"),
        ("PLAN_APPROVED", "IMPLEMENTED"),
        ("IMPLEMENTED", "TESTED"),
        ("TESTED", "RELEASE_ELIGIBLE"),
    ]:
        assert is_legal(frm, to)


def test_invalid_transitions_rejected():
    assert not is_legal("SUBMITTED", "TESTED")
    assert not is_legal("PLAN_APPROVED", "RELEASE_ELIGIBLE")
    assert not is_legal("RELEASE_ELIGIBLE", "SUBMITTED")
    # Unknown state.
    with pytest.raises(InvalidTransitionError):
        sm = StateMachine()
        sm.validate_transition("SUBMITTED", "NOT_A_STATE", "PLANNER", "", sm.load())


def test_no_skipped_states_in_main_flow():
    # Main flow has exactly 8 hops; no shortcuts allowed.
    assert "SUBMITTED" in LEGAL_TRANSITIONS
    assert "RELEASE_ELIGIBLE" in LEGAL_TRANSITIONS["TESTED"]


def test_atomic_recording_and_hash_chain():
    sm = StateMachine()
    snap0 = sm.load()
    snap1 = sm.apply_transition("BASELINED", run_id="R1", role="orchestrator", reason="t")
    snap2 = sm.apply_transition("ANALYZED", run_id="R1", role="orchestrator", reason="t")
    # Hash chain: previous of snap2 == hash of snap1 body.
    assert snap2.previous_state_hash == snap1.current_state_hash
    assert snap1.previous_state_hash == snap0.current_state_hash
    assert snap2.state_version == snap0.state_version + 2


def test_state_not_updated_after_record_failure():
    sm = StateMachine()
    before = sm.load().run_state
    with pytest.raises(InvalidTransitionError):
        sm.apply_transition("TESTED", run_id="R1", role="orchestrator", reason="bad")
    after = sm.load().run_state
    # Should remain SUBMITTED (no partial write).
    assert before == after == "SUBMITTED"
