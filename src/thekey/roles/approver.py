"""APPROVER / RELEASE CONTROLLER role.

Approves the plan through a simplified local identity and evaluates mandatory
gates against policy to produce RELEASE_ELIGIBLE or BLOCKED. Does NOT implement
product changes and does NOT fabricate evidence (sections 5, 17). The decision
itself is produced by decisions.DecisionEngine; this module models the local
identity and the approval record.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from ..decisions import DecisionEngine, ReleaseDecision
from ..errors import TheKeyError
from ..gates import GateResult
from ..models import SovereignAuthorizationReceipt
from ..policies import Policy

DEMO_GRANT_ID = "build-week-judge-mode-v1"
DEMO_AUTHORIZATION_SCOPE = "JUDGE_MODE_DEMO_ONLY"
DEMO_SUBJECT_RELATIVE_PATH = "examples/demo_app/calculator.py"
DEMO_SUBJECT_SHA256 = "ca3d99f787cb349aa2acff2c31ac6cad9ef9a8c68152e48ace7d4c32dafda7b7"
DEMO_TEST_SHA256 = "9509d66836dbfe680882ba83e2876b2f192d9d6004ed9c30471f19f7a378429b"
DEMO_OUTPUT_SCOPE = "ISOLATED_RUN_WORKSPACE_ONLY"
DEMO_AUTHORITY_SOURCE_SHA256 = (
    "6c7a03a76c9bf43e923ee2b5ef47e0543c5aafd2da29c5c1bcf5863d358883fe"
)


def canonical_grant_sha256(grant: dict) -> str:
    body = json.dumps(
        grant,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(body).hexdigest()


def normalized_text_sha256(path: Path) -> str:
    """Hash UTF-8 text after universal-newline normalization."""
    normalized = path.read_text(encoding="utf-8").replace("\r\n", "\n")
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def validate_demo_subject(subject_path: Path, canonical_subject_path: Path) -> None:
    """Allow only the canonical demo or Judge Mode's exact ephemeral copy."""
    actual_subject = Path(subject_path).resolve()
    canonical_subject = Path(canonical_subject_path).resolve()
    if actual_subject != canonical_subject:
        repository_root = canonical_subject.parents[2]
        judge_root = (repository_root / ".thekey" / "judge-mode").resolve()
        try:
            relative = actual_subject.relative_to(judge_root)
        except ValueError as exc:
            raise TheKeyError(
                "Demo grant cannot authorize another source",
                code="DEMO_AUTHORIZATION_SUBJECT_MISMATCH",
            ) from exc
        parts = relative.parts
        is_ephemeral_judge_copy = (
            len(parts) == 3
            and parts[0].startswith("Judge Mode ")
            and len(parts[0]) > len("Judge Mode ")
            and parts[1] == "Temporary Sample Repository"
            and parts[2] == "calculator.py"
            and (actual_subject.parent / ".git").is_dir()
        )
        companion_test = actual_subject.parent / "test_calculator.py"
        if not is_ephemeral_judge_copy:
            raise TheKeyError(
                "Demo grant cannot authorize another source",
                code="DEMO_AUTHORIZATION_SUBJECT_MISMATCH",
            )
        if (
            not companion_test.is_file()
            or normalized_text_sha256(companion_test) != DEMO_TEST_SHA256
        ):
            raise TheKeyError(
                "Judge Mode companion test hash mismatch",
                code="DEMO_AUTHORIZATION_SUBJECT_HASH_MISMATCH",
            )
    if (
        not actual_subject.is_file()
        or normalized_text_sha256(actual_subject) != DEMO_SUBJECT_SHA256
    ):
        raise TheKeyError(
            "Canonical demo source hash mismatch",
            code="DEMO_AUTHORIZATION_SUBJECT_HASH_MISMATCH",
        )


@dataclass
class Approval:
    run_id: str
    approved_by: str
    policy_id: str
    approved_at: str
    note: str = ""
    transaction_id: str = ""
    authorization_id: str = ""
    plan_sha256: str = ""

    def to_dict(self) -> dict:
        return {
            "run_id": self.run_id,
            "approved_by": self.approved_by,
            "policy_id": self.policy_id,
            "approved_at": self.approved_at,
            "note": self.note,
            "transaction_id": self.transaction_id,
            "authorization_id": self.authorization_id,
            "plan_sha256": self.plan_sha256,
        }


class Approver:
    """Simplified local identity approver. NOT a cryptographic identity."""

    def __init__(self, identity: str = "local-approver@governed-run"):
        self.identity = identity

    def approve_plan(self, run_id: str, plan: dict, policy: Policy) -> Approval:
        raise TheKeyError(
            "A persisted explicit sovereign grant is required",
            code="MISSING_AUTHORIZATION",
        )

    def authorize_plan(
        self,
        *,
        run_id: str,
        transaction_id: str,
        plan_sha256: str,
        requested_action_ids: list[str],
        grant: dict,
        policy: Policy,
        subject_path: Path,
        canonical_subject_path: Path,
        workspace_root: Path,
    ) -> tuple[Approval, SovereignAuthorizationReceipt]:
        """Bind the explicit demo grant to one real, isolated transaction."""
        required = {
            "schema_version",
            "protocol_version",
            "grant_id",
            "sovereign_identity_id",
            "allowed_action_ids",
            "authority_basis",
            "authority_source_sha256",
            "authorization_scope",
            "subject_relative_path",
            "subject_sha256",
            "output_scope",
            "production_reuse",
        }
        if not isinstance(grant, dict) or set(grant) != required:
            raise TheKeyError("Invalid sovereign grant", code="INVALID_AUTHORIZATION_GRANT")
        if grant["schema_version"] != "v1" or grant["protocol_version"] != "v1":
            raise TheKeyError("Incompatible sovereign grant", code="INVALID_AUTHORIZATION_GRANT")
        if grant["sovereign_identity_id"] != "usuario":
            raise TheKeyError("Unexpected sovereign identity", code="INVALID_AUTHORIZATION_GRANT")
        fixed_fields = {
            "grant_id": DEMO_GRANT_ID,
            "authority_source_sha256": DEMO_AUTHORITY_SOURCE_SHA256,
            "authorization_scope": DEMO_AUTHORIZATION_SCOPE,
            "subject_relative_path": DEMO_SUBJECT_RELATIVE_PATH,
            "subject_sha256": DEMO_SUBJECT_SHA256,
            "output_scope": DEMO_OUTPUT_SCOPE,
            "production_reuse": False,
        }
        if any(grant.get(name) != value for name, value in fixed_fields.items()):
            raise TheKeyError("Demo grant scope mismatch", code="INVALID_AUTHORIZATION_GRANT")

        canonical_subject = Path(canonical_subject_path).resolve()
        validate_demo_subject(subject_path, canonical_subject)
        resolved_workspace = Path(workspace_root).resolve()
        if (
            resolved_workspace.name.casefold() != "workspaces"
            or resolved_workspace == canonical_subject.parent
            or canonical_subject.is_relative_to(resolved_workspace)
        ):
            raise TheKeyError(
                "Demo grant requires an isolated run workspace",
                code="DEMO_AUTHORIZATION_OUTPUT_SCOPE_MISMATCH",
            )

        allowed_raw = grant["allowed_action_ids"]
        if (
            not isinstance(allowed_raw, list)
            or not allowed_raw
            or any(not isinstance(item, str) or not item for item in allowed_raw)
            or len(set(allowed_raw)) != len(allowed_raw)
        ):
            raise TheKeyError("Invalid allowed actions", code="INVALID_AUTHORIZATION_GRANT")
        allowed = list(allowed_raw)
        if not requested_action_ids or not set(requested_action_ids).issubset(set(allowed)):
            raise TheKeyError("Action outside sovereign grant", code="UNAUTHORIZED_ACTION")
        grant_sha256 = canonical_grant_sha256(grant)
        authorization_id = f"auth-{uuid4().hex}"
        now = datetime.now(timezone.utc)
        receipt = SovereignAuthorizationReceipt(
            schema_version="v1",
            protocol_version="v1",
            authorization_id=authorization_id,
            grant_id=grant["grant_id"],
            grant_sha256=grant_sha256,
            sovereign_identity_id="usuario",
            run_id=run_id,
            transaction_id=transaction_id,
            plan_sha256=plan_sha256,
            allowed_action_ids=requested_action_ids,
            issued_at=now,
            authority_basis=grant["authority_basis"],
            authorization_scope=grant["authorization_scope"],
            subject_relative_path=grant["subject_relative_path"],
            subject_sha256=grant["subject_sha256"],
            output_scope=grant["output_scope"],
            production_reuse=grant["production_reuse"],
        )
        approval = Approval(
            run_id=run_id,
            approved_by="usuario (persisted explicit grant)",
            policy_id=policy.policy_id,
            approved_at=now.strftime("%Y-%m-%dT%H:%M:%SZ"),
            note=f"Bound to sovereign grant {grant['grant_id']}.",
            transaction_id=transaction_id,
            authorization_id=authorization_id,
            plan_sha256=plan_sha256,
        )
        return approval, receipt

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
