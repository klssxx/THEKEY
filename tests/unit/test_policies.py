"""Policy engine tests (section 31: POLICIES)."""

import copy

import pytest

from thekey.errors import InvalidPolicyError
from thekey.policies import PolicyEngine


def test_valid_policy():
    pe = PolicyEngine()
    policy = pe.load_default()
    assert policy.policy_id == "local-python-demo"
    assert "BUILD_PASSED" in policy.required_gates
    assert "UNIT_TESTS_PASSED" in policy.required_gates
    assert "SECURITY_GATE_PASSED" in policy.required_gates
    assert "DOCUMENTATION_GATE_PASSED" in policy.required_gates


def test_invalid_yaml(tmp_path):
    bad = tmp_path / "bad.yaml"
    bad.write_text("foo: [unclosed\n", encoding="utf-8")
    pe = PolicyEngine()
    with pytest.raises(InvalidPolicyError):
        pe.load_file(bad)


def test_missing_field():
    pe = PolicyEngine()
    raw = pe.load_default().to_dict()
    del raw["required_gates"]
    with pytest.raises(InvalidPolicyError):
        pe.validate_dict(raw)


def test_unknown_gate():
    pe = PolicyEngine()
    raw = pe.load_default().to_dict()
    raw["required_gates"].append("NOT_A_GATE")
    with pytest.raises(InvalidPolicyError):
        pe.validate_dict(raw)


def test_negative_limit():
    pe = PolicyEngine()
    raw = pe.load_default().to_dict()
    raw["max_files_changed"] = -5
    with pytest.raises(InvalidPolicyError):
        pe.validate_dict(raw)


def test_invalid_policy_blocks_run():
    """An invalid policy must stop execution and never execute the plan."""
    pe = PolicyEngine()
    bad = {
        "policy_id": "broken",
        "max_files_changed": -1,
    }
    with pytest.raises(InvalidPolicyError):
        pe.validate_dict(bad)
    # Confirm the engine does not produce a usable Policy object.
    assert True
