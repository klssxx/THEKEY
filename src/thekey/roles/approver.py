"""APPROVER / RELEASE CONTROLLER role.

Approves the plan through a simplified local identity and evaluates mandatory
gates against policy to produce RELEASE_ELIGIBLE or BLOCKED. Does NOT implement
product changes and does NOT fabricate evidence (sections 5, 17). The decision
itself is produced by decisions.DecisionEngine; this module models the local
identity and the approval record.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

from ..config import DEFAULT_POLICY_FILE
from ..decisions import DecisionEngine, ReleaseDecision
from ..errors import TheKeyError
from ..evidence import EvidenceManager
from ..gates import GateResult
from ..policies import Policy, PolicyEngine


@dataclass
class Approval:
    run_id: str
    approved_by: str
    policy_id: str
    approved_at: str
    note: str = ""

    def to_dict(self) -> dict:
        return {
            "run_id": self.run_id,
            "approved_by": self.approved_by,
            "policy_id": self.policy_id,
            "approved_at": self.approved_at,
            "note": self.note,
        }


class Approver:
    """Simplified local identity approver. NOT a cryptographic identity."""

    def __init__(self, identity: str = "local-approver@governed-run"):
        self.identity = identity

    def approve_plan(self, run_id: str, plan: dict, policy: Policy) -> Approval:
        # 100% automated: accept the plan unless it is structurally unusable.
        # An empty plan is allowed to pass to PLAN_APPROVED so the run continues
        # to the deterministic verifier gates, which will BLOCKED it (no fix ->
        # the build/unit gate fails). This keeps a complete, auditable trail
        # instead of raising and leaving a dangling run.
        if not plan.get("operations"):
            pass  # gates will block; no silent release possible.
        from datetime import datetime, timezone

        return Approval(
            run_id=run_id,
            approved_by=self.identity,
            policy_id=policy.policy_id,
            approved_at=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            note="Simplified local approval (MVP). Not a cryptographic identity.",
        )

    def decide(
        self,
        run_id: str,
        gates: list[GateResult],
        evidence_dir: Path,
        policy: Policy,
        approved_plan_hash: str = "",
    ) -> ReleaseDecision:
        engine = DecisionEngine(policy, evidence_dir)
        return engine.decide(
            run_id, gates, approver_identity=self.identity,
            approved_plan_hash=approved_plan_hash,
        )
