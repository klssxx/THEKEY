"""Output validator tests (section 31: OUTPUT VALIDATOR)."""

import pytest

from thekey.output_validator import OutputValidator, parse_operator_turn
from thekey.errors import (
    InvalidModelOutputError,
    OutputTruncatedError,
    StaleModelOutputError,
)


def _good(state_version=1, state_hash="h", contract_hash="c", status="PASSED"):
    return f"""phase: "phase-03-plan"
status: "{status}"
context_binding:
  state_version: {state_version}
  state_hash: "{state_hash}"
  phase_contract_hash: "{contract_hash}"
observed:
  - fact: "defect found"
    source: "filesystem"
    evidence: "EVID-BASELINE"
actions: []
files_changed: []
evidence: []
state_change_requested:
  from: "ANALYZED"
  to: "PLAN_PROPOSED"
next: ""
error_code: ""
---END_TURN---"""


def test_missing_terminator():
    with pytest.raises(OutputTruncatedError):
        parse_operator_turn("phase: x\nstatus: PASSED")


def test_invalid_yaml():
    with pytest.raises(InvalidModelOutputError):
        parse_operator_turn("phase: x\nstatus: PASSED\n---END_TURN---")


def test_unknown_keys():
    bad = _good().replace('next: ""', 'next: ""\nextra_unknown: 1')
    with pytest.raises(InvalidModelOutputError):
        parse_operator_turn(bad)


def test_invalid_status():
    with pytest.raises(InvalidModelOutputError):
        parse_operator_turn(_good(status="NOT_A_STATUS"))


def test_stale_state_hash():
    v = OutputValidator()
    with pytest.raises(StaleModelOutputError):
        v.validate(
            _good(state_hash="wrong"),
            expected_phase="phase-03-plan",
            expected_state_version=1,
            expected_state_hash="h",
            expected_contract_hash="c",
            role="PLANNER",
            state=None,
            allowed_transitions=["ANALYZED->PLAN_PROPOSED"],
        )


def test_wrong_phase_contract_hash():
    v = OutputValidator()
    with pytest.raises(StaleModelOutputError):
        v.validate(
            _good(contract_hash="wrong"),
            expected_phase="phase-03-plan",
            expected_state_version=1,
            expected_state_hash="h",
            expected_contract_hash="c",
            role="PLANNER",
            state=None,
            allowed_transitions=["ANALYZED->PLAN_PROPOVED"],
        )


def test_unauthorized_action():
    from thekey.errors import UnauthorizedActionError

    v = OutputValidator()
    malicious = _good().replace("actions: []", """actions:
  - action_id: "RUN_BUILD"
    parameters: {}
    reason: "x" """)
    with pytest.raises(UnauthorizedActionError):
        v.validate(
            malicious,
            expected_phase="phase-03-plan",
            expected_state_version=1,
            expected_state_hash="h",
            expected_contract_hash="c",
            role="PLANNER",  # PLANNER may not request RUN_BUILD
            state=None,
            allowed_transitions=["ANALYZED->PLAN_PROPOSED"],
        )


def test_invalid_transition():
    v = OutputValidator()
    with pytest.raises(InvalidModelOutputError):
        v.validate(
            _good(),
            expected_phase="phase-03-plan",
            expected_state_version=1,
            expected_state_hash="h",
            expected_contract_hash="c",
            role="PLANNER",
            state=None,
            allowed_transitions=["BASELINED->ANALYZED"],  # not the requested one
        )


def test_evidence_without_source():
    v = OutputValidator()
    bad = _good().replace("evidence: []", """evidence:
  - fact: "x"
    source: "filesystem"
    evidence: "" """)
    with pytest.raises(InvalidModelOutputError):
        v.validate(
            bad,
            expected_phase="phase-03-plan",
            expected_state_version=1,
            expected_state_hash="h",
            expected_contract_hash="c",
            role="PLANNER",
            state=None,
            allowed_transitions=["ANALYZED->PLAN_PROPOSED"],
        )


def test_valid_output_passes():
    v = OutputValidator()
    parsed = v.validate(
        _good(),
        expected_phase="phase-03-plan",
        expected_state_version=1,
        expected_state_hash="h",
        expected_contract_hash="c",
        role="PLANNER",
        state=None,
        allowed_transitions=["ANALYZED->PLAN_PROPOSED"],
    )
    assert parsed["status"] == "PASSED"
