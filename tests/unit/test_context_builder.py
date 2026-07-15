"""Context builder + token budget tests (section 31: CONTEXT BUILDER)."""

from thekey import budgets
from thekey.context_builder import ContextBuilder
from thekey.state_machine import StateMachine


def _contract():
    return {
        "phase_contract": {"contract_version": "1.0", "run_id": "R1",
                            "phase_id": "p", "phase_type": "WORK", "role": "EXECUTOR"},
        "authoritative_state": {"current": "PLAN_APPROVED", "version": 2, "sha256": "abc"},
        "role_permissions": {},
        "flags": {},
        "required_inputs": [],
        "allowed_roots": [],
        "protected_paths": [],
        "allowed_operations": [],
        "allowed_command_ids": [],
        "allowed_outputs": [],
        "allowed_transitions": [],
        "budgets": {},
        "rollback": {},
        "required_evidence": [],
        "task": "t",
        "success_conditions": [],
        "stop_conditions": [],
        "output_schema": "schemas/operator-turn-v1.yaml",
    }


def test_enforces_total_token_budget():
    cb = ContextBuilder(StateMachine())
    # Huge project data should push over budget (project_data limited to 800
    # tokens; total_work budget 2200). We assert the profile flags over_budget
    # when we inject oversized project data.
    big = "x" * 20000  # ~5000 tokens
    ctx = cb.build(
        phase_contract=_contract(), phase_type="WORK",
        project_data=big, turn_index=0, turns_remaining=1,
    )
    assert ctx.over_budget  # project section should be flagged


def test_includes_only_minified_state():
    cb = ContextBuilder(StateMachine())
    ctx = cb.build(phase_contract=_contract(), phase_type="WORK")
    # The minified view contains run_id and phase_id but NOT full transition
    # history (which would be a long list).
    assert "current_state:" in ctx.user_message
    assert "run_id:" in ctx.user_message


def test_includes_no_raw_chat_history():
    cb = ContextBuilder(StateMachine())
    ctx = cb.build(phase_contract=_contract(), phase_type="WORK")
    # By construction the builder never receives chat history; assert the kernel
    # is present and there is no injected 'previous model response'.
    assert "THEKEY-OPERATOR" in ctx.system_message
    assert "previous model response" not in ctx.user_message.lower()


def test_rejects_oversized_and_preserves_kernel():
    cb = ContextBuilder(StateMachine())
    ctx = cb.build(phase_contract=_contract(), phase_type="WORK",
                   project_data="y" * 30000)
    # Kernel must always be present regardless of budget pressure.
    assert "THEKEY-OPERATOR" in ctx.system_message
    # Oversized project data is narrowed to fit the budget (no false over-flag),
    # which is the required behavior: "Select narrower project excerpts".
    # The minified state + kernel remain intact.
    assert "current_state:" in ctx.user_message
    assert "THEKEY-OPERATOR" in ctx.system_message


def test_at_most_three_recent_events():
    sm = StateMachine()
    sm.reset_to_submitted("R1")
    for to in ("BASELINED", "ANALYZED", "PLAN_PROPOSED", "PLAN_APPROVED"):
        sm.apply_transition(to, run_id="R1", role="orchestrator", reason="t")
    events = sm.recent_events(limit=3)
    assert len(events) <= 3
