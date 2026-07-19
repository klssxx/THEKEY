"""Role separation tests (section 31: PLANNER / EXECUTOR / VERIFIER).

These verify the non-negotiable role rules: the planner never writes, the
executor changes only the workspace, the verifier never modifies product code,
and permission matrices reject out-of-role actions.
"""

import pytest

from thekey.command_registry import assert_role_allowed, get_spec
from thekey.config import DEMO_APP_SOURCE, WORKSPACES_DIR
from thekey.errors import UnauthorizedActionError
from thekey.roles.executor import Executor
from thekey.roles.planner import build_demo_plan, detect_demo_defect


def _authorized_executor():
    from thekey.main import RunCoordinator

    coordinator = RunCoordinator()
    coordinator.create("executor unit test")
    coordinator.baseline()
    plan = coordinator.plan()
    coordinator.approve_plan()
    return (
        Executor(
            coordinator.run.run_id,
            WORKSPACES_DIR,
            action_context=coordinator.load_action_context(),
        ),
        plan,
    )


def test_planner_detects_defect():
    defect = detect_demo_defect()
    assert defect is not None
    assert "return a + b" in defect["replacement"]


def test_planner_produces_plan_with_one_op():
    plan = build_demo_plan("R1")
    assert len(plan.operations) == 1
    assert plan.operations[0]["action_id"] == "REPLACE_EXACT_TEXT"


def test_planner_does_not_modify_source():
    before = DEMO_APP_SOURCE.read_text(encoding="utf-8")
    build_demo_plan("R1")
    after = DEMO_APP_SOURCE.read_text(encoding="utf-8")
    assert before == after  # planner never writes


def test_executor_rejects_unapproved_plan():
    ex = Executor("R1", WORKSPACES_DIR)
    ex.prepare_workspace()
    plan = build_demo_plan("R1")
    plan.approved = False
    with pytest.raises(Exception):
        ex.apply_operation(plan.operations[0], plan.to_dict())


def test_executor_modifies_only_workspace():
    ex, plan = _authorized_executor()
    ex.prepare_workspace()
    plan.approved = True
    ex.apply_operation(plan.operations[0], plan.to_dict())
    # Original untouched.
    assert "return a - b" in DEMO_APP_SOURCE.read_text(encoding="utf-8")
    # Workspace repaired.
    ws_file = ex.ws / "src" / "demo_app" / "calculator.py"
    assert "return a + b" in ws_file.read_text(encoding="utf-8")
    ex.generate_diff()


def test_executor_rejects_operation_not_in_plan():
    ex = Executor("R1", WORKSPACES_DIR)
    ex.prepare_workspace()
    plan = build_demo_plan("R1")
    plan.approved = True
    rogue = {"op_id": "OP-NOT-IN-PLAN", "action_id": "REPLACE_EXACT_TEXT",
             "target_id": "DEMO_CALCULATOR", "expected": "x", "replacement": "y"}
    with pytest.raises(UnauthorizedActionError):
        ex.apply_operation(rogue, plan.to_dict())


def test_executor_rejects_ambiguous_replacement():
    ex, plan = _authorized_executor()
    ex.prepare_workspace()
    plan.approved = True
    op = dict(plan.operations[0])
    op["expected"] = "def"  # appears multiple times -> ambiguous
    res = ex.apply_operation(op, plan.to_dict())
    assert res["result"]["status"] == "AMBIGUOUS_OR_MISSING"


def test_role_action_matrix():
    assert_role_allowed("READ_DECLARED_FILE", "PLANNER")
    with pytest.raises(UnauthorizedActionError):
        assert_role_allowed("RUN_BUILD", "PLANNER")
    assert_role_allowed("REPLACE_EXACT_TEXT", "EXECUTOR")
    with pytest.raises(UnauthorizedActionError):
        assert_role_allowed("SCAN_SECRETS", "EXECUTOR")
    assert_role_allowed("SCAN_SECRETS", "VERIFIER")
    with pytest.raises(UnauthorizedActionError):
        assert_role_allowed("REPLACE_EXACT_TEXT", "VERIFIER")
    assert get_spec("RUN_BUILD").allowed_roles == frozenset({"VERIFIER"})
