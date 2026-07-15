"""Tests for the 0.2.0 automation surface: schemas, NPSC adapter,
review_token, and the MiMo autonomous launcher.

These lock in the new components added for the autonomous, contributor-ready
release. They are deterministic and do not touch the protected historical
THEKEY framework.
"""

from __future__ import annotations

import json
from pathlib import Path

import jsonschema
import pytest

from thekey import decisions
from thekey.adapters import npsc_adapter as npsc
from thekey.mimo_profile import as_actor_context, CONTRACT

SCHEMAS_DIR = Path(__file__).resolve().parents[2] / "governance" / "schemas"


def _load_schema(name: str) -> dict:
    return json.loads((SCHEMAS_DIR / name).read_text(encoding="utf-8"))


def test_mission_schema_accepts_valid():
    schema = _load_schema("mission.schema.json")
    valid = {
        "mission_id": "M1",
        "title": "Fix add",
        "description": "d",
        "actor_profile": "MiMo",
        "target": {"kind": "demo"},
        "policy_id": "local-python-demo",
    }
    jsonschema.validate(valid, schema)


def test_mission_schema_rejects_missing_fields():
    schema = _load_schema("mission.schema.json")
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate({"mission_id": "M1"}, schema)


def test_review_decision_schema_requires_token():
    schema = _load_schema("review_decision.schema.json")
    bad = {
        "run_id": "R1",
        "decision": "RELEASE_ELIGIBLE",
        "policy_id": "p",
        "gates_passed": 4,
        "gates_total": 4,
        # missing review_token + approver_identity
    }
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(bad, schema)


def test_actor_context_schema_ok():
    schema = _load_schema("actor_context.schema.json")
    ctx = as_actor_context("M1")
    jsonschema.validate(ctx, schema)
    assert ctx["actor"] == "MiMo"
    assert ctx["constraints"]["never_mutates_original_source"] is True


def test_npsc_adapter_recommended_output_contract_shape():
    # The drifted NPSC shape from the 2026-07-15 audit.
    art = {
        "recommended_output_contract": {"tone": "formal"},
        "constraints": ["no_secrets", "max_200_tokens"],
    }
    ctx = npsc.map_npsc_to_context(art, mission_id="M1", actor="MiMo")
    assert ctx["read_only"] is True
    assert "no_secrets" in ctx["constraints"]["constraints"]
    assert ctx["constraints"]["tone"] == "formal"


def test_npsc_adapter_output_contract_shape():
    art = {
        "output_contract": {"constraints": ["x"], "tone": "casual"},
    }
    ctx = npsc.map_npsc_to_context(art, mission_id="M1")
    assert "x" in ctx["constraints"]["constraints"]
    assert ctx["constraints"]["tone"] == "casual"


def test_npsc_adapter_file_roundtrip(tmp_path: Path):
    art = {"constraints": ["a", "b"], "recommended_output_contract": {"k": "v"}}
    p = tmp_path / "npsc.json"
    p.write_text(json.dumps(art), encoding="utf-8")
    ctx = npsc.map_npsc_to_context(p, mission_id="M1")
    assert ctx["evidence_scope"] == ["npsc_artifact_hash"]
    h = npsc.npsc_artifact_hash(p)
    assert len(h) == 64


def test_review_token_deterministic_and_tamper_evident():
    good = decisions.derive_review_token("R1", "p", "id", 4, 4, "hashabc")
    # Same inputs -> same token.
    again = decisions.derive_review_token("R1", "p", "id", 4, 4, "hashabc")
    assert good == again
    # Forged decision body must not verify.
    decision = {
        "run_id": "R1",
        "policy_id": "p",
        "approver_identity": "id",
        "gates": [{"passed": True}, {"passed": True}, {"passed": True}, {"passed": True}],
        "review_token": good,
        "approved_plan_hash": "hashabc",
    }
    assert decisions.verify_review_token(decision) is True
    # Tamper: change a gate result.
    decision["gates"] = [{"passed": True}, {"passed": False}, {"passed": True}, {"passed": True}]
    assert decisions.verify_review_token(decision) is False


def test_mimo_launcher_runs_autonomously():
    """The autonomous launcher must run the full governed pipeline with no
    prompts and exit 0 on RELEASE_ELIGIBLE."""
    from thekey.launchers import mimo_launcher as ml

    rc = ml.run("test-mimo", "autonomous")
    assert rc == 0
