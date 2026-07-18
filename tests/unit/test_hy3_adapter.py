"""Unit tests for the HY3 turn adapter (improvement C).

Verifies the closed loop ContextBuilder -> build_hy3_turn -> OutputValidator
without invoking a model or touching the deterministic coordinator.
"""

import json

from thekey.adapters.npsc_adapter import build_hy3_turn
from thekey.context_builder import ContextBuilder
from thekey.output_validator import OutputValidator, parse_operator_turn
from thekey.state_machine import StateMachine


def _build_context_and_state():
    sm = StateMachine()
    cb = ContextBuilder(sm)
    contract = {"output_schema": "schemas/operator-turn-v1.yaml"}
    ctx = cb.build(
        phase_contract=contract,
        phase_type="WORK",
        turn_index=0,
        turns_remaining=1,
    )
    state = sm.load()
    return ctx, state


def test_build_hy3_turn_parses_as_operator_turn():
    ctx, state = _build_context_and_state()
    turn = build_hy3_turn(
        ctx,
        state_version=state.state_version,
        state_hash=state.current_state_hash,
        phase_contract_hash=state.phase_contract_hash or "x",
        phase="WORK",
        evidence_index=["EVID-BASELINE"],
    )
    # Must parse under the restricted parser.
    parsed = parse_operator_turn(turn)
    assert parsed["status"] == "NEXT_PHASE_READY"
    assert parsed["phase"] == "WORK"


def test_build_hy3_turn_passes_full_validation():
    ctx, state = _build_context_and_state()
    turn = build_hy3_turn(
        ctx,
        state_version=state.state_version,
        state_hash=state.current_state_hash,
        phase_contract_hash=state.phase_contract_hash or "x",
        phase="WORK",
        evidence_index=["EVID-BASELINE"],
    )
    validator = OutputValidator()
    result = validator.validate(
        turn,
        expected_phase="WORK",
        expected_state_version=state.state_version,
        expected_state_hash=state.current_state_hash,
        expected_contract_hash=state.phase_contract_hash or "x",
        role="WORK",
        state=state,
        allowed_transitions=[],
        evidence_index=["EVID-BASELINE"],
    )
    assert result["phase"] == "WORK"
    # Evidence reference must be in the supplied index.
    assert result["evidence"][0]["evidence"] == "EVID-BASELINE"
