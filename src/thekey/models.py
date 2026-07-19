"""Strict contracts for the governed physical-action boundary."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class Role(str, Enum):
    AUTHOR = "AUTHOR"
    EXECUTOR = "EXECUTOR"
    REVIEWER = "REVIEWER"
    APPROVER = "APPROVER"
    SOVEREIGN = "SOVEREIGN"
    SYSTEM = "SYSTEM"


class ActionReviewVerdict(str, Enum):
    PASS = "PASS"
    DEFER = "DEFER"
    FAIL = "FAIL"
    PENDING = "PENDING"


class CheckmateReviewReceipt(StrictModel):
    schema_version: Literal["v1"]
    protocol_version: Literal["v1"]
    receipt_id: str = Field(min_length=3, max_length=128)
    reviewer_id: str = Field(min_length=3, max_length=128)
    run_id: str = Field(min_length=3, max_length=128)
    transaction_id: str = Field(min_length=3, max_length=128)
    plan_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    verdict: ActionReviewVerdict
    issued_at: datetime

    @field_validator("plan_sha256")
    @classmethod
    def reject_zero_plan_hash(cls, value: str) -> str:
        if value == "0" * 64:
            raise ValueError("ZERO_PLAN_HASH_DENIED")
        return value


class SovereignAuthorizationReceipt(StrictModel):
    schema_version: Literal["v1"]
    protocol_version: Literal["v1"]
    authorization_id: str = Field(min_length=3, max_length=128)
    grant_id: str = Field(min_length=3, max_length=128)
    grant_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    sovereign_identity_id: str = Field(min_length=1, max_length=128)
    run_id: str = Field(min_length=3, max_length=128)
    transaction_id: str = Field(min_length=3, max_length=128)
    plan_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    allowed_action_ids: list[str] = Field(min_length=1, max_length=32)
    issued_at: datetime
    authority_basis: str = Field(min_length=12, max_length=512)
    authorization_scope: Literal["JUDGE_MODE_DEMO_ONLY"]
    subject_relative_path: Literal["examples/demo_app/calculator.py"]
    subject_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    output_scope: Literal["ISOLATED_RUN_WORKSPACE_ONLY"]
    production_reuse: Literal[False]

    @field_validator("plan_sha256", "grant_sha256", "subject_sha256")
    @classmethod
    def reject_zero_hash(cls, value: str) -> str:
        if value == "0" * 64:
            raise ValueError("ZERO_HASH_DENIED")
        return value

    @field_validator("allowed_action_ids")
    @classmethod
    def unique_actions(cls, value: list[str]) -> list[str]:
        if any(not item.strip() for item in value) or len(set(value)) != len(value):
            raise ValueError("INVALID_ALLOWED_ACTIONS")
        return value


class ActionContext(StrictModel):
    """Complete, pre-execution context containing both persisted receipts."""

    schema_version: Literal["v1"]
    protocol_version: Literal["v1"]
    actor_id: str = Field(min_length=1, max_length=128)
    role: Role
    transaction_id: str = Field(min_length=3, max_length=128)
    authorization_id: str = Field(min_length=3, max_length=128)
    run_id: str = Field(min_length=3, max_length=128)
    plan_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    policy_version: str = Field(min_length=1, max_length=64)
    policy_bundle_hash: str = Field(pattern=r"^[0-9a-f]{64}$")
    requested_at: datetime
    review_verdict: ActionReviewVerdict
    checkmate_receipt: CheckmateReviewReceipt
    sovereign_receipt: SovereignAuthorizationReceipt

    @field_validator("plan_sha256", "policy_bundle_hash")
    @classmethod
    def reject_zero_hash(cls, value: str) -> str:
        if value == "0" * 64:
            raise ValueError("ZERO_HASH_DENIED")
        return value

    @model_validator(mode="after")
    def bind_receipts(self) -> "ActionContext":
        review = self.checkmate_receipt
        authorization = self.sovereign_receipt
        for name in ("run_id", "transaction_id", "plan_sha256"):
            expected = getattr(self, name)
            if getattr(review, name) != expected or getattr(authorization, name) != expected:
                raise ValueError(f"{name.upper()}_RECEIPT_MISMATCH")
        if authorization.authorization_id != self.authorization_id:
            raise ValueError("AUTHORIZATION_ID_RECEIPT_MISMATCH")
        if review.verdict is not self.review_verdict:
            raise ValueError("REVIEW_VERDICT_RECEIPT_MISMATCH")
        return self


class AuthorizationDecision(StrictModel):
    allowed: bool
    reason_code: str = Field(min_length=1, max_length=128)
    decision_id: str | None = Field(default=None, min_length=3, max_length=128)
    policy_bundle_hash: str | None = Field(default=None, pattern=r"^[0-9a-f]{64}$")

    @model_validator(mode="after")
    def require_allow_evidence(self) -> "AuthorizationDecision":
        if self.allowed and (not self.decision_id or not self.policy_bundle_hash):
            raise ValueError("ALLOW_REQUIRES_DECISION_ID_AND_POLICY_HASH")
        return self


class GovernedTransaction(StrictModel):
    schema_version: Literal["v1"]
    protocol_version: Literal["v1"]
    transaction_id: str = Field(min_length=3, max_length=128)
    run_id: str = Field(min_length=3, max_length=128)
    plan_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    actor_id: str = Field(min_length=1, max_length=128)
    authorization_id: str = Field(min_length=3, max_length=128)
    review_receipt_id: str = Field(min_length=3, max_length=128)
    policy_version: str = Field(min_length=1, max_length=64)
    policy_bundle_hash: str = Field(pattern=r"^[0-9a-f]{64}$")
    requested_at: datetime
