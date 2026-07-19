"""VERIFIER role.

Reads the approved plan, workspace, and diff. Runs build, tests, secret scan,
and documentation checks. Produces gate results. Does NOT modify product code,
weaken tests, or repair the implementation (sections 5, 17). The actual gate
execution is delegated to gates.GateRunner + actions dispatch; this module owns
the deterministic orchestration of those checks and the gate JSON artifact.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from ..gates import GateResult, GateRunner
from ..models import ActionReviewVerdict, CheckmateReviewReceipt
from ..policies import Policy


class Verifier:
    def __init__(self, run_id: str, policy: Policy, action_context=None):
        self.run_id = run_id
        self.policy = policy
        self.action_context = action_context

    def run_gates(self) -> list[GateResult]:
        runner = GateRunner(self.policy)
        return runner.run(self.run_id, {"action_context": self.action_context})

    def gates_json(self, results: list[GateResult]) -> dict:
        runner = GateRunner(self.policy)
        return runner.gates_json(results)

    def read_diff(self, diff_path: Path) -> str:
        if not diff_path.exists():
            return ""
        return diff_path.read_text(encoding="utf-8")

    def review_plan(
        self,
        *,
        transaction_id: str,
        plan: dict,
        plan_sha256: str,
    ) -> CheckmateReviewReceipt:
        """Issue a real pre-action CHECKMATE receipt for the bounded demo plan."""
        operations = plan.get("operations") if isinstance(plan, dict) else None
        safe = bool(
            operations
            and plan.get("run_id") == self.run_id
            and plan_sha256 != "0" * 64
            and all(
                op.get("action_id") in {"REPLACE_EXACT_TEXT", "CREATE_DECLARED_FILE"}
                for op in operations
            )
        )
        verdict = ActionReviewVerdict.PASS if safe else ActionReviewVerdict.FAIL
        return CheckmateReviewReceipt(
            schema_version="v1",
            protocol_version="v1",
            receipt_id=f"review-{uuid4().hex}",
            reviewer_id="checkmate-local-v1",
            run_id=self.run_id,
            transaction_id=transaction_id,
            plan_sha256=plan_sha256,
            verdict=verdict,
            issued_at=datetime.now(timezone.utc),
        )
