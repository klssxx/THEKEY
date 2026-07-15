"""VERIFIER role.

Reads the approved plan, workspace, and diff. Runs build, tests, secret scan,
and documentation checks. Produces gate results. Does NOT modify product code,
weaken tests, or repair the implementation (sections 5, 17). The actual gate
execution is delegated to gates.GateRunner + actions dispatch; this module owns
the deterministic orchestration of those checks and the gate JSON artifact.
"""

from __future__ import annotations

from pathlib import Path

from ..gates import GateResult, GateRunner
from ..policies import Policy


class Verifier:
    def __init__(self, run_id: str, policy: Policy):
        self.run_id = run_id
        self.policy = policy

    def run_gates(self) -> list[GateResult]:
        runner = GateRunner(self.policy)
        return runner.run(self.run_id)

    def gates_json(self, results: list[GateResult]) -> dict:
        runner = GateRunner(self.policy)
        return runner.gates_json(results)

    def read_diff(self, diff_path: Path) -> str:
        if not diff_path.exists():
            return ""
        return diff_path.read_text(encoding="utf-8")
