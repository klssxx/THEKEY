"""Verifier gate tests (section 31: VERIFIER)."""

import pytest

from thekey.gates import GateRunner
from thekey.policies import PolicyEngine
from thekey.roles.verifier import Verifier
from thekey.roles.executor import Executor
from thekey.roles.planner import build_demo_plan
from thekey.config import WORKSPACES_DIR


def _prepare_repaired(run_id):
    ex = Executor(run_id, WORKSPACES_DIR)
    ex.prepare_workspace()
    plan = build_demo_plan(run_id)
    plan.approved = True
    ex.apply_operation(plan.operations[0], plan.to_dict())
    return ex


def test_verifier_runs_all_four_gates():
    policy = PolicyEngine().load_default()
    ex = _prepare_repaired("R1")
    verifier = Verifier("R1", policy)
    results = verifier.run_gates()
    codes = {r.gate for r in results}
    assert "BUILD_PASSED" in codes
    assert "UNIT_TESTS_PASSED" in codes
    assert "SECURITY_GATE_PASSED" in codes
    assert "DOCUMENTATION_GATE_PASSED" in codes


def test_verifier_all_pass_on_repaired_workspace():
    policy = PolicyEngine().load_default()
    _prepare_repaired("R1")
    verifier = Verifier("R1", policy)
    results = verifier.run_gates()
    assert all(r.passed for r in results)


def test_verifier_blocks_on_failed_gate():
    policy = PolicyEngine().load_default()
    # Workspace prepared but NOT repaired -> unit tests fail.
    ex = Executor("R1", WORKSPACES_DIR)
    ex.prepare_workspace()
    verifier = Verifier("R1", policy)
    results = verifier.run_gates()
    failed = [r for r in results if not r.passed]
    assert failed  # at least UNIT_TESTS_PASSED fails
    assert not all(r.passed for r in results)


def test_verifier_does_not_modify_product_code():
    policy = PolicyEngine().load_default()
    ex = _prepare_repaired("R1")
    before = (ex.ws / "src/demo_app/calculator.py").read_text(encoding="utf-8")
    Verifier("R1", policy).run_gates()
    after = (ex.ws / "src/demo_app/calculator.py").read_text(encoding="utf-8")
    assert before == after
