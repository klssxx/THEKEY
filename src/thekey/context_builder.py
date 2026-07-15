"""Context builder for the stateless HY3 operator.

It renders ONLY:
  1. Fixed system kernel.
  2. Minified authoritative state (never full state during normal ops).
  3. Active phase contract.
  4. Up to three recent validated events (derived from state transitions, not chat).
  5. Relevant evidence index.
  6. Only required project data excerpts.
  7. Closed output contract / schema.

It enforces token budgets and NEVER injects raw chat history or previous model
responses (section 10, 14, 7).
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from . import budgets
from .config import (
    CYCLE_PROTOCOL_FILE,
    SYSTEM_KERNEL_FILE,
)
from .state_machine import StateMachine


@dataclass
class BuiltContext:
    system_message: str
    user_message: str
    profile_name: str
    total_tokens_est: int
    over_budget: list[str]

    def to_dict(self) -> dict:
        return {
            "system_message": self.system_message,
            "user_message": self.user_message,
            "profile_name": self.profile_name,
            "total_tokens_est": self.total_tokens_est,
            "over_budget": self.over_budget,
        }


def _load_kernel() -> str:
    return SYSTEM_KERNEL_FILE.read_text(encoding="utf-8").strip()


def _load_cycle_protocol() -> str:
    if CYCLE_PROTOCOL_FILE.exists():
        return CYCLE_PROTOCOL_FILE.read_text(encoding="utf-8").strip()
    return ""


def minify_state(state: dict, turn_index: int, turns_remaining: int, blockers: list) -> str:
    """Render the minified state view (section 14)."""
    return (
        "current_state:\n"
        'view_version: "1.0"\n'
        f'run_id: "{state.get("run_id", "")}"\n'
        f'phase_id: "{state.get("active_phase", "")}"\n'
        f'run_state: "{state.get("run_state", "")}"\n'
        f'previous_state: "{state.get("previous_state_hash", "")}"\n'
        f'state_version: {state.get("state_version", 1)}\n'
        f'state_hash: "{state.get("current_state_hash", "")}"\n'
        f'phase_contract_hash: "{state.get("phase_contract_hash", "")}"\n'
        f'workspace: "workspaces/{state.get("run_id", "")}/"\n'
        f'approved_plan_hash: "{state.get("approved_plan_hash", "")}"\n'
        f'last_validated_action_id: "{state.get("last_completed_action", "")}"\n'
        f"phase_turn_index: {turn_index}\n"
        f"phase_turns_remaining: {turns_remaining}\n"
        f"blockers: {json.dumps(blockers, ensure_ascii=False)}"
    )


def _events_to_text(events: list[dict]) -> str:
    if not events:
        return "  (none)"
    lines = []
    for ev in events[-3:]:
        lines.append(
            f"  - {ev.get('kind','event')}:{ev.get('state', ev.get('role',''))} "
            f"@{ev.get('timestamp','')}"
        )
    return "\n".join(lines)


def _evidence_index(evidence_ids: list[str]) -> str:
    if not evidence_ids:
        return "  (none)"
    return "\n".join(f"  - {eid}" for eid in evidence_ids)


class ContextBuilder:
    def __init__(self, state_machine: StateMachine):
        self.sm = state_machine

    def build(
        self,
        *,
        phase_contract: dict,
        phase_type: str,
        recent_events: list[dict] | None = None,
        evidence_index: list[str] | None = None,
        project_data: str = "",
        turn_index: int = 0,
        turns_remaining: int = 1,
        include_cycle_protocol: bool = False,
    ) -> BuiltContext:
        profile = budgets.get_profile(phase_type)
        kernel = _load_kernel()

        state = self.sm.load().canonical()
        state_view = minify_state(state, turn_index, turns_remaining, state.get("blockers", []))

        contract_text = json.dumps(phase_contract, ensure_ascii=False, indent=2)
        events_text = _events_to_text(recent_events or self.sm.recent_events(3))
        evidence_text = _evidence_index(evidence_index or [])
        # Output schema is referenced by name; the validator loads it.
        schema_text = f"schema: {phase_contract.get('output_schema', 'schemas/operator-turn-v1.yaml')}"

        # Project data is bounded; trim if over budget.
        if budgets.estimate_tokens(project_data) > profile.project_data_max_tokens:
            # Narrow excerpt: keep first/last chunks within budget.
            limit_chars = profile.project_data_max_tokens * 4
            if len(project_data) > limit_chars:
                half = limit_chars // 2 - 20
                project_data = (
                    project_data[:half]
                    + "\n...[TRUNCATED FOR BUDGET]...\n"
                    + project_data[-half:]
                )

        user_parts = [state_view]
        if include_cycle_protocol:
            user_parts.append("CYCLE PROTOCOL:\n" + _load_cycle_protocol())
        user_parts.append("<ACTIVE_PHASE>\n" + contract_text + "\n</ACTIVE_PHASE>")
        user_parts.append("<RECENT_VALIDATED_EVENTS>\n" + events_text + "\n</RECENT_VALIDATED_EVENTS>")
        user_parts.append("<AVAILABLE_EVIDENCE>\n" + evidence_text + "\n</AVAILABLE_EVIDENCE>")
        if project_data:
            user_parts.append("<UNTRUSTED_PROJECT_DATA>\n" + project_data + "\n</UNTRUSTED_PROJECT_DATA>")
        user_parts.append(
            "<OUTPUT_CONTRACT>\nReturn only the required restricted YAML. "
            "Use exactly the declared keys. Do not add commentary. "
            "End with ---END_TURN---.\n" + schema_text + "\n</OUTPUT_CONTRACT>"
        )
        user_message = "\n\n".join(user_parts)

        sizes = {
            "kernel": budgets.estimate_tokens(kernel),
            "state": budgets.estimate_tokens(state_view),
            "phase": budgets.estimate_tokens(contract_text),
            "events": budgets.estimate_tokens(events_text),
            "evidence": budgets.estimate_tokens(evidence_text),
            "project": budgets.estimate_tokens(project_data),
            "schema": budgets.estimate_tokens(schema_text),
        }
        total = sum(sizes.values())
        over = profile.over_budget_sections(sizes)

        # Preserve mandatory sections: kernel + schema are never dropped.
        # If over budget, the caller is responsible for splitting the phase.
        return BuiltContext(
            system_message=kernel,
            user_message=user_message,
            profile_name=phase_type,
            total_tokens_est=total,
            over_budget=over,
        )
