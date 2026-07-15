"""Token budget profiles and a conservative estimator.

Uses a simple, deterministic word/punctuation estimate when the real HY3
tokenizer is unavailable. Never truncates Kernel, Output schema, or the required
state binding (section 12). When the input is too large, it prunes events,
minifies evidence, drops irrelevant state fields, narrows project excerpts, or
splits the phase.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


# Conservative estimate: ~4 chars per token for mixed content.
_CHARS_PER_TOKEN = 4


def estimate_tokens(text: str) -> int:
    if not text:
        return 0
    return max(1, len(text) // _CHARS_PER_TOKEN)


@dataclass
class BudgetProfile:
    name: str
    kernel_max_tokens: int
    state_max_tokens: int
    phase_max_tokens: int
    recent_events_max_tokens: int
    evidence_index_max_tokens: int
    project_data_max_tokens: int
    output_schema_max_tokens: int
    total_input_max_tokens: int
    max_output_tokens_per_turn: int
    max_turns: int
    max_cumulative_output_tokens: int
    max_invalid_outputs: int

    def fits(self, used: int) -> bool:
        return used <= self.total_input_max_tokens

    def over_budget_sections(self, sizes: dict[str, int]) -> list[str]:
        over = []
        mapping = {
            "kernel": self.kernel_max_tokens,
            "state": self.state_max_tokens,
            "phase": self.phase_max_tokens,
            "events": self.recent_events_max_tokens,
            "evidence": self.evidence_index_max_tokens,
            "project": self.project_data_max_tokens,
            "schema": self.output_schema_max_tokens,
        }
        for section, limit in mapping.items():
            if limit and sizes.get(section, 0) > limit:
                over.append(section)
        return over


CONTROL_PROFILE = BudgetProfile(
    name="CONTROL",
    kernel_max_tokens=150, state_max_tokens=250, phase_max_tokens=300,
    recent_events_max_tokens=150, evidence_index_max_tokens=150,
    project_data_max_tokens=0, output_schema_max_tokens=150,
    total_input_max_tokens=1200, max_output_tokens_per_turn=300,
    max_turns=4, max_cumulative_output_tokens=900, max_invalid_outputs=1,
)

WORK_PROFILE = BudgetProfile(
    name="WORK",
    kernel_max_tokens=150, state_max_tokens=250, phase_max_tokens=400,
    recent_events_max_tokens=150, evidence_index_max_tokens=200,
    project_data_max_tokens=800, output_schema_max_tokens=150,
    total_input_max_tokens=2200, max_output_tokens_per_turn=500,
    max_turns=3, max_cumulative_output_tokens=1500, max_invalid_outputs=1,
)

RECOVERY_PROFILE = BudgetProfile(
    name="RECOVERY",
    kernel_max_tokens=150, state_max_tokens=350, phase_max_tokens=300,
    recent_events_max_tokens=250, evidence_index_max_tokens=300,
    project_data_max_tokens=200, output_schema_max_tokens=150,
    total_input_max_tokens=1900, max_output_tokens_per_turn=400,
    max_turns=1, max_cumulative_output_tokens=400, max_invalid_outputs=0,
)

PROFILES = {
    "CONTROL": CONTROL_PROFILE,
    "WORK": WORK_PROFILE,
    "RECOVERY": RECOVERY_PROFILE,
}


def get_profile(name: str) -> BudgetProfile:
    return PROFILES[name]
