from __future__ import annotations

import ast
import shutil
from pathlib import Path

import pytest

from thekey.actions import handler_call_count
from thekey.errors import TheKeyError
from thekey.main import RunCoordinator
from thekey.models import ActionContext


def test_live_coordinator_persists_real_context_and_executes_once():
    coordinator = RunCoordinator()
    coordinator.create("RBAC v2 integration", "Bound double receipt")
    coordinator.baseline()
    coordinator.plan()
    coordinator.approve_plan()

    for name in (
        "checkmate-review-receipt.json",
        "sovereign-authorization-receipt.json",
        "governed-transaction.json",
    ):
        assert (coordinator.run.dir / name).exists()

    context = coordinator.load_action_context()
    assert isinstance(context, ActionContext)
    assert context.run_id == coordinator.run.run_id
    assert context.transaction_id == context.checkmate_receipt.transaction_id
    assert context.transaction_id == context.sovereign_receipt.transaction_id
    assert context.plan_sha256 == coordinator.sm.load().approved_plan_hash
    assert context.sovereign_receipt.authorization_scope == "JUDGE_MODE_DEMO_ONLY"
    assert context.sovereign_receipt.output_scope == "ISOLATED_RUN_WORKSPACE_ONLY"
    assert context.sovereign_receipt.production_reuse is False

    execution = coordinator.execute()
    assert len(execution["results"]) == 1
    assert execution["results"][0]["authorization"]["allowed"] is True
    assert execution["results"][0]["authorization"]["decision_id"]


def test_demo_grant_cannot_authorize_a_distinct_source(tmp_path):
    source_dir = tmp_path / "product-like-source"
    source_dir.mkdir()
    root = Path(__file__).resolve().parents[1]
    shutil.copy2(root / "examples/demo_app/calculator.py", source_dir / "calculator.py")
    shutil.copy2(
        root / "examples/demo_app/test_calculator.py",
        source_dir / "test_calculator.py",
    )
    source = source_dir / "calculator.py"
    source.write_text(
        source.read_text(encoding="utf-8") + "\n# distinct production-like source\n",
        encoding="utf-8",
    )

    coordinator = RunCoordinator(demo_source=source)
    coordinator.create("adversarial grant reuse")
    coordinator.baseline()
    coordinator.plan()
    with pytest.raises(TheKeyError) as exc:
        coordinator.approve_plan()

    assert exc.value.code == "DEMO_AUTHORIZATION_SUBJECT_MISMATCH"
    assert not (coordinator.run.dir / "sovereign-authorization-receipt.json").exists()
    assert handler_call_count("unissued-transaction", "REPLACE_EXACT_TEXT") == 0


def test_all_five_live_callers_pass_explicit_context_keyword():
    from pathlib import Path

    import thekey.gates
    import thekey.roles.executor

    targets = [(Path(thekey.gates.__file__), 4), (Path(thekey.roles.executor.__file__), 1)]
    total = 0
    for path, expected in targets:
        tree = ast.parse(path.read_text(encoding="utf-8"))
        calls = [
            node
            for node in ast.walk(tree)
            if isinstance(node, ast.Call)
            and ((isinstance(node.func, ast.Name) and node.func.id == "dispatch")
                 or (isinstance(node.func, ast.Attribute) and node.func.attr == "dispatch"))
        ]
        assert len(calls) == expected
        assert all(any(kw.arg == "context" for kw in call.keywords) for call in calls)
        total += len(calls)
    assert total == 5
