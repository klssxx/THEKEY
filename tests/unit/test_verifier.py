"""Verifier gate tests (section 31: VERIFIER)."""


from thekey.config import WORKSPACES_DIR
from thekey.roles.executor import Executor
from thekey.roles.verifier import Verifier


def _prepare(repair=True):
    from thekey.main import RunCoordinator

    coordinator = RunCoordinator()
    coordinator.create("verifier unit test")
    coordinator.baseline()
    plan = coordinator.plan()
    coordinator.approve_plan()
    context = coordinator.load_action_context()
    ex = Executor(coordinator.run.run_id, WORKSPACES_DIR, action_context=context)
    ex.prepare_workspace()
    plan.approved = True
    if repair:
        ex.apply_operation(plan.operations[0], plan.to_dict())
    return ex, Verifier(coordinator.run.run_id, coordinator.policy, action_context=context)


def test_verifier_runs_all_four_gates():
    ex, verifier = _prepare()
    results = verifier.run_gates()
    codes = {r.gate for r in results}
    assert "BUILD_PASSED" in codes
    assert "UNIT_TESTS_PASSED" in codes
    assert "SECURITY_GATE_PASSED" in codes
    assert "DOCUMENTATION_GATE_PASSED" in codes


def test_verifier_all_pass_on_repaired_workspace():
    _, verifier = _prepare()
    results = verifier.run_gates()
    assert all(r.passed for r in results)


def test_verifier_blocks_on_failed_gate():
    # Workspace prepared but NOT repaired -> unit tests fail.
    _, verifier = _prepare(repair=False)
    results = verifier.run_gates()
    failed = [r for r in results if not r.passed]
    assert failed  # at least UNIT_TESTS_PASSED fails
    assert not all(r.passed for r in results)


def test_verifier_does_not_modify_product_code():
    ex, verifier = _prepare()
    before = (ex.ws / "src/demo_app/calculator.py").read_text(encoding="utf-8")
    verifier.run_gates()
    after = (ex.ws / "src/demo_app/calculator.py").read_text(encoding="utf-8")
    assert before == after
