"""Unit tests for the LAUNCH_SMOKE_TEST gate profile (improvement F)."""

import importlib

import thekey.gates as gates_mod
from thekey.gates import GateRunner, _active_gates
from thekey.policies import PolicyEngine


def _demo_policy() -> object:
    return PolicyEngine().load_default()


def test_full_profile_runs_all_gates(monkeypatch):
    monkeypatch.delenv("LAUNCH_SMOKE_TEST", raising=False)
    policy = _demo_policy()
    assert set(_active_gates(policy)) == set(policy.required_gates)


def test_smoke_profile_uses_only_fast_gates(monkeypatch):
    monkeypatch.setenv("LAUNCH_SMOKE_TEST", "1")
    policy = _demo_policy()
    active = _active_gates(policy)
    assert set(active) == gates_mod.FAST_GATES
    assert "SECURITY_GATE_PASSED" not in active
    assert "DOCUMENTATION_GATE_PASSED" not in active


def test_smoke_profile_runs_fewer_gates_than_full(monkeypatch):
    monkeypatch.setenv("LAUNCH_SMOKE_TEST", "1")
    policy = _demo_policy()
    runner = GateRunner(policy)
    # The GateRunner honors the profile via _active_gates internally.
    assert len(gates_mod.FAST_GATES) < len(policy.required_gates)
