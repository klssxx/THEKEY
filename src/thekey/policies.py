"""Policy engine: load, validate, snapshot, and gate against policy as code.

An invalid policy STOPS the run with a deterministic decision, a non-zero exit
code, and never executes the plan (section 26).
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft7Validator

from .config import (
    DEFAULT_POLICY_FILE,
    DEFAULT_POLICY_ID,
    POLICY_SCHEMA_FILE,
)
from .errors import InvalidPolicyError
from .io_atomic import atomic_write_text
from .models import ActionContext, AuthorizationDecision, Role


@dataclass
class Policy:
    """A validated, frozen policy document."""

    policy_id: str
    policy_version: str
    description: str
    max_files_changed: int
    max_lines_changed: int
    max_new_dependencies: int
    required_gates: list[str]
    required_evidence: list[str]
    secret_scan_scope: dict
    excluded_directories: list[str]
    raw: dict = field(default_factory=dict, repr=False)

    def to_dict(self) -> dict:
        return {
            "policy_id": self.policy_id,
            "policy_version": self.policy_version,
            "description": self.description,
            "max_files_changed": self.max_files_changed,
            "max_lines_changed": self.max_lines_changed,
            "max_new_dependencies": self.max_new_dependencies,
            "required_gates": self.required_gates,
            "required_evidence": self.required_evidence,
            "secret_scan_scope": self.secret_scan_scope,
            "excluded_directories": self.excluded_directories,
        }


class PolicyEngine:
    """Loads and validates policies against the JSON Schema."""

    def __init__(self, schema_file: Path = POLICY_SCHEMA_FILE):
        self.schema_file = Path(schema_file)
        self._schema = yaml.safe_load if False else None  # placeholder
        self._schema = self._load_schema()

    def _load_schema(self) -> dict:
        if not self.schema_file.exists():
            raise InvalidPolicyError(f"Missing schema: {self.schema_file}")
        return yaml.safe_load(self.schema_file.read_text(encoding="utf-8"))

    def load_file(self, path: Path) -> Policy:
        path = Path(path)
        if not path.exists():
            raise InvalidPolicyError(f"Policy file not found: {path}")
        try:
            raw = yaml.safe_load(path.read_text(encoding="utf-8"))
        except yaml.YAMLError as exc:
            raise InvalidPolicyError(f"Invalid YAML in {path}: {exc}") from exc
        return self.validate_dict(raw)

    def load_default(self) -> Policy:
        return self.load_file(DEFAULT_POLICY_FILE)

    def validate_dict(self, raw: Any) -> Policy:
        if not isinstance(raw, dict):
            raise InvalidPolicyError("Policy root must be a mapping")
        validator = Draft7Validator(self._schema)
        errors = sorted(validator.iter_errors(raw), key=lambda e: e.path)
        if errors:
            msgs = [f"{list(e.path)}: {e.message}" for e in errors]
            raise InvalidPolicyError("Policy failed schema validation:\n" + "\n".join(msgs))
        # Negative-limit guard (schema enforces minimum, but keep explicit).
        for key in ("max_files_changed", "max_lines_changed", "max_new_dependencies"):
            if raw[key] < 0:
                raise InvalidPolicyError(f"Policy field {key} must not be negative")
        # Unknown gate guard.
        allowed_gates = {
            "BUILD_PASSED",
            "UNIT_TESTS_PASSED",
            "SECURITY_GATE_PASSED",
            "DOCUMENTATION_GATE_PASSED",
        }
        for g in raw["required_gates"]:
            if g not in allowed_gates:
                raise InvalidPolicyError(f"Unknown gate in policy: {g!r}")
        return Policy(
            policy_id=raw["policy_id"],
            policy_version=str(raw["policy_version"]),
            description=raw.get("description", ""),
            max_files_changed=int(raw["max_files_changed"]),
            max_lines_changed=int(raw["max_lines_changed"]),
            max_new_dependencies=int(raw["max_new_dependencies"]),
            required_gates=list(raw["required_gates"]),
            required_evidence=list(raw.get("required_evidence", [])),
            secret_scan_scope=raw["secret_scan_scope"],
            excluded_directories=list(raw.get("excluded_directories", [])),
            raw=raw,
        )

    def snapshot(self, policy: Policy, run_policy_dir: Path) -> Path:
        """Write a frozen copy of the policy into the run's policy-snapshot dir
        for auditability. Returns the snapshot path."""
        run_policy_dir = Path(run_policy_dir)
        run_policy_dir.mkdir(parents=True, exist_ok=True)
        dest = run_policy_dir / f"{policy.policy_id}.yaml"
        atomic_write_text(
            dest,
            yaml.safe_dump(policy.raw, sort_keys=True, allow_unicode=True),
        )
        return dest

    def default_policy_path(self) -> Path:
        return DEFAULT_POLICY_FILE

    def policy_id(self) -> str:
        return DEFAULT_POLICY_ID

    @staticmethod
    def bundle_hash(policy: Policy) -> str:
        """Hash the complete validated policy using canonical JSON."""
        body = json.dumps(
            policy.to_dict(),
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        ).encode("utf-8")
        return hashlib.sha256(body).hexdigest()

    def authorize_action(self, request: dict[str, Any]) -> dict[str, Any]:
        """Evaluate a bound physical-action request deterministically.

        Invalid inputs never raise into the handler path: every branch returns
        an explicit denial carrying the currently loaded policy bundle hash.
        """
        policy = self.load_default()
        bundle_hash = self.bundle_hash(policy)

        def deny(reason: str) -> dict[str, Any]:
            return AuthorizationDecision(
                allowed=False,
                reason_code=reason,
                policy_bundle_hash=bundle_hash,
            ).model_dump(mode="json")

        if not isinstance(request, dict):
            return deny("POLICY_REQUEST_INVALID")
        expected = set(ActionContext.model_fields) | {"action_id", "parameters_sha256"}
        if set(request) != expected:
            return deny("POLICY_REQUEST_FIELDS_INVALID")
        try:
            context = ActionContext.model_validate(
                {key: request[key] for key in ActionContext.model_fields}
            )
        except Exception:
            return deny("POLICY_CONTEXT_INVALID")
        if context.role is not Role.EXECUTOR:
            return deny("POLICY_ROLE_DENIED")
        if context.policy_version != policy.policy_version:
            return deny("POLICY_VERSION_MISMATCH")
        if context.policy_bundle_hash != bundle_hash:
            return deny("POLICY_BUNDLE_HASH_MISMATCH")
        if context.sovereign_receipt.sovereign_identity_id != "moli":
            return deny("SOVEREIGN_IDENTITY_MISMATCH")
        if (
            context.sovereign_receipt.authorization_scope != "JUDGE_MODE_DEMO_ONLY"
            or context.sovereign_receipt.output_scope != "ISOLATED_RUN_WORKSPACE_ONLY"
            or context.sovereign_receipt.production_reuse is not False
        ):
            return deny("SOVEREIGN_SCOPE_DENIED")
        if request["action_id"] not in context.sovereign_receipt.allowed_action_ids:
            return deny("ACTION_NOT_SOVEREIGN_AUTHORIZED")
        parameters_hash = request.get("parameters_sha256")
        if not isinstance(parameters_hash, str) or len(parameters_hash) != 64:
            return deny("PARAMETERS_HASH_INVALID")
        decision_material = json.dumps(
            request,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        ).encode("utf-8")
        decision_id = "policy-decision-" + hashlib.sha256(decision_material).hexdigest()[:32]
        return AuthorizationDecision(
            allowed=True,
            reason_code="AUTHORIZED_BY_BOUND_RECEIPTS",
            decision_id=decision_id,
            policy_bundle_hash=bundle_hash,
        ).model_dump(mode="json")
