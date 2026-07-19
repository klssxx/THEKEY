from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

import pytest
from jsonschema import Draft202012Validator
from pydantic import ValidationError

from thekey.models import (
    ActionContext,
    ActionReviewVerdict,
    CheckmateReviewReceipt,
    Role,
    SovereignAuthorizationReceipt,
)

PLAN = "a1" * 32
POLICY = "b2" * 32


def _ids() -> tuple[str, str, str, str]:
    suffix = uuid4().hex
    return f"run-{suffix}", f"tx-{suffix}", f"review-{suffix}", f"auth-{suffix}"


def valid_context(**changes) -> dict:
    run_id, transaction_id, review_id, authorization_id = _ids()
    now = datetime.now(timezone.utc)
    review = CheckmateReviewReceipt(
        schema_version="v1",
        protocol_version="v1",
        receipt_id=review_id,
        reviewer_id="checkmate-local-v1",
        run_id=run_id,
        transaction_id=transaction_id,
        plan_sha256=PLAN,
        verdict=ActionReviewVerdict.PASS,
        issued_at=now,
    )
    authorization = SovereignAuthorizationReceipt(
        schema_version="v1",
        protocol_version="v1",
        authorization_id=authorization_id,
        grant_id="build-week-judge-mode-v1",
        grant_sha256="d4" * 32,
        sovereign_identity_id="moli",
        run_id=run_id,
        transaction_id=transaction_id,
        plan_sha256=PLAN,
        allowed_action_ids=["REPLACE_EXACT_TEXT", "RUN_BUILD"],
        issued_at=now,
        authority_basis="Explicit Build Week Judge Mode authorization.",
        authorization_scope="JUDGE_MODE_DEMO_ONLY",
        subject_relative_path="examples/demo_app/calculator.py",
        subject_sha256="ca3d99f787cb349aa2acff2c31ac6cad9ef9a8c68152e48ace7d4c32dafda7b7",
        output_scope="ISOLATED_RUN_WORKSPACE_ONLY",
        production_reuse=False,
    )
    value = {
        "schema_version": "v1",
        "protocol_version": "v1",
        "actor_id": "thekey-executor-v1",
        "role": Role.EXECUTOR,
        "transaction_id": transaction_id,
        "authorization_id": authorization_id,
        "run_id": run_id,
        "plan_sha256": PLAN,
        "policy_version": "1.0",
        "policy_bundle_hash": POLICY,
        "requested_at": now,
        "review_verdict": ActionReviewVerdict.PASS,
        "checkmate_receipt": review,
        "sovereign_receipt": authorization,
    }
    value.update(changes)
    return value


def test_action_context_accepts_bound_double_receipt():
    context = ActionContext.model_validate(valid_context())
    assert context.role is Role.EXECUTOR
    assert context.checkmate_receipt.plan_sha256 == context.plan_sha256
    assert context.sovereign_receipt.authorization_id == context.authorization_id


@pytest.mark.parametrize(
    "field,value",
    [
        ("schema_version", "v2"),
        ("protocol_version", "v2"),
        ("plan_sha256", "0" * 64),
        ("actor_id", ""),
    ],
)
def test_action_context_rejects_invalid_security_fields(field, value):
    with pytest.raises(ValidationError):
        ActionContext.model_validate(valid_context(**{field: value}))


def test_action_context_rejects_extra_fields():
    with pytest.raises(ValidationError):
        ActionContext.model_validate(valid_context(unexpected=True))


@pytest.mark.parametrize(
    "field,value",
    [
        ("authorization_scope", "PRODUCTION"),
        ("subject_relative_path", "src/thekey/actions.py"),
        ("output_scope", "REPOSITORY"),
        ("production_reuse", True),
    ],
)
def test_sovereign_receipt_rejects_productive_reuse(field, value):
    receipt = valid_context()["sovereign_receipt"]
    payload = receipt.model_dump(mode="json")
    payload[field] = value
    with pytest.raises(ValidationError):
        SovereignAuthorizationReceipt.model_validate(payload)


def test_versioned_action_context_schema_accepts_model_and_rejects_extra():
    root = Path(__file__).resolve().parents[1]
    schema = json.loads(
        (root / "governance/schemas/action-context.schema.json").read_text(encoding="utf-8")
    )
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema)
    payload = ActionContext.model_validate(valid_context()).model_dump(mode="json")
    validator.validate(payload)
    payload["unexpected"] = True
    assert list(validator.iter_errors(payload))


def test_sovereign_receipt_schema_denies_productive_reuse():
    root = Path(__file__).resolve().parents[1]
    schema = json.loads(
        (root / "governance/schemas/sovereign-authorization-receipt.schema.json")
        .read_text(encoding="utf-8")
    )
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema)
    payload = valid_context()["sovereign_receipt"].model_dump(mode="json")
    validator.validate(payload)
    payload["production_reuse"] = True
    assert list(validator.iter_errors(payload))


@pytest.mark.parametrize(
    "mismatch", ["run_id", "transaction_id", "authorization_id", "plan_sha256"]
)
def test_action_context_rejects_receipt_mismatch(mismatch):
    value = valid_context()
    if mismatch == "authorization_id":
        value[mismatch] = f"auth-{uuid4().hex}"
    elif mismatch == "plan_sha256":
        value[mismatch] = "c3" * 32
    else:
        value[mismatch] = f"{mismatch}-{uuid4().hex}"
    with pytest.raises(ValidationError):
        ActionContext.model_validate(value)
