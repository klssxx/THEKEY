"""Release decision engine.

Evaluates mandatory gates against policy and produces RELEASE_ELIGIBLE or
BLOCKED. The decision is deterministic: any failed mandatory gate blocks; a
missing artifact resolves to BLOCKED. The approver owns the decision; the
engine is the deterministic evaluator.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
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
    review_token: str = ""
    issued_at: str = ""
    approved_plan_hash: str = ""

    def to_dict(self) -> dict:
        return {
            "run_id": self.run_id,
            "decision": self.decision,
            "policy_id": self.policy_id,
            "approver_identity": self.approver_identity,
            "review_token": self.review_token,
            "issued_at": self.issued_at,
            "approved_plan_hash": self.approved_plan_hash,
            "reason": self.reason,
            "gates": self.gates,
            "evidence_missing": self.evidence_missing,
        }


def derive_review_token(
    run_id: str, policy_id: str, approver_identity: str,
    gates_passed: int, gates_total: int, approved_plan_hash: str,
) -> str:
    """Deterministic, unforgeable-without-inputs review token.

    Derived from the canonical decision inputs so a tampered or forged
    decision.json fails verification (the token will not recompute). This is an
    MVP token, not a cryptographic signature: it proves the decision body was
    produced by the deterministic engine, not that a human signed it.
    """
    material = json.dumps(
        {
            "run_id": run_id,
            "policy_id": policy_id,
            "approver_identity": approver_identity,
            "gates_passed": gates_passed,
            "gates_total": gates_total,
            "approved_plan_hash": approved_plan_hash,
        },
        sort_keys=True,
        ensure_ascii=False,
    )
    return "rt-" + hashlib.sha256(material.encode("utf-8")).hexdigest()[:48]


def verify_review_token(decision: dict) -> bool:
    """Recompute the review token from the decision body and compare.

    A tampered or forged decision.json (altered gates, plan hash, identity)
    will not reproduce the recorded token -> returns False.
    """
    try:
        token = derive_review_token(
            decision["run_id"],
            decision["policy_id"],
            decision["approver_identity"],
            sum(1 for g in decision.get("gates", []) if g.get("passed")),
            len(decision.get("gates", [])),
            decision.get("approved_plan_hash", ""),
        )
    except (KeyError, TypeError):
        return False
    return token == decision.get("review_token")


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
        approved_plan_hash: str = "",
    ) -> ReleaseDecision:
        required_evidence = required_evidence or self.policy.required_evidence
        gates_passed = sum(1 for g in gates if g.passed)
        gates_total = len(gates)
        issued_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        token = derive_review_token(
            run_id, self.policy.policy_id, approver_identity,
            gates_passed, gates_total, approved_plan_hash,
        )
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
                review_token=token,
                issued_at=issued_at,
                approved_plan_hash=approved_plan_hash,
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
                review_token=token,
                issued_at=issued_at,
                approved_plan_hash=approved_plan_hash,
            )
        return ReleaseDecision(
            run_id=run_id,
            decision="RELEASE_ELIGIBLE",
            policy_id=self.policy.policy_id,
            reason="All mandatory gates passed and required evidence present.",
            gates=[g.to_dict() for g in gates],
            evidence_missing=[],
            approver_identity=approver_identity,
            review_token=token,
            issued_at=issued_at,
            approved_plan_hash=approved_plan_hash,
        )
