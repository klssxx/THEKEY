"""Release decision engine.

Evaluates mandatory gates against policy and produces RELEASE_ELIGIBLE or
BLOCKED. The decision is deterministic: any failed mandatory gate blocks; a
missing artifact resolves to BLOCKED. The approver owns the decision; the engine
is the deterministic evaluator.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from .config import DEFAULT_POLICY_FILE
from .errors import GateFailureError
from .gates import GateResult, GateRunner
from .policies import Policy, PolicyEngine


@dataclass
class ReleaseDecision:
    run_id: str
    decision: str  # RELEASE_ELIGIBLE | BLOCKED
    policy_id: str
    reason: str
    gates: list[dict]
    evidence_missing: list[str]
    approver_identity: str

    def to_dict(self) -> dict:
        return {
            "run_id": self.run_id,
            "decision": self.decision,
            "policy_id": self.policy_id,
            "approver_identity": self.approver_identity,
            "reason": self.reason,
            "gates": self.gates,
            "evidence_missing": self.evidence_missing,
        }


class DecisionEngine:
    def __init__(self, policy: Policy, evidence_dir: Path):
        self.policy = policy
        self.evidence_dir = Path(evidence_dir)

    def decide(
        self,
        run_id: str,
        gates: list[GateResult],
        approver_identity: str = "local-approver@governed-run",
        required_evidence: list[str] | None = None,
    ) -> ReleaseDecision:
        required_evidence = required_evidence or self.policy.required_evidence
        missing = [e for e in required_evidence if not (self.evidence_dir / e).exists()]
        if missing:
            return ReleaseDecision(
                run_id=run_id,
                decision="BLOCKED",
                policy_id=self.policy.policy_id,
                reason=f"Missing required evidence: {missing}",
                gates=[g.to_dict() for g in gates],
                evidence_missing=missing,
                approver_identity=approver_identity,
            )
        failed = [g for g in gates if not g.passed]
        if failed:
            return ReleaseDecision(
                run_id=run_id,
                decision="BLOCKED",
                policy_id=self.policy.policy_id,
                reason=f"Failed mandatory gate(s): {[g.gate for g in failed]}",
                gates=[g.to_dict() for g in gates],
                evidence_missing=[],
                approver_identity=approver_identity,
            )
        return ReleaseDecision(
            run_id=run_id,
            decision="RELEASE_ELIGIBLE",
            policy_id=self.policy.policy_id,
            reason="All mandatory gates passed and required evidence present.",
            gates=[g.to_dict() for g in gates],
            evidence_missing=[],
            approver_identity=approver_identity,
        )
