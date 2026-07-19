from __future__ import annotations

import ast
import json
import shutil
import subprocess
from pathlib import Path
from types import SimpleNamespace
from uuid import uuid4

import pytest

from thekey.actions import handler_call_count
from thekey.cli import cmd_judge_mode
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


def test_judge_mode_evidence_binds_receipts_and_preserves_source(request):
    root = Path(__file__).resolve().parents[1]
    session_root = root / ".thekey" / "judge-mode" / f"Judge Mode {uuid4().hex}"
    request.addfinalizer(lambda: shutil.rmtree(session_root, ignore_errors=True))
    source_dir = session_root / "Temporary Sample Repository"
    source_dir.mkdir(parents=True)
    shutil.copy2(root / "examples/demo_app/calculator.py", source_dir / "calculator.py")
    shutil.copy2(
        root / "examples/demo_app/test_calculator.py",
        source_dir / "test_calculator.py",
    )
    subprocess.run(
        ["git", "init", "--quiet", str(source_dir)],
        check=True,
        capture_output=True,
        text=True,
    )
    source = source_dir / "calculator.py"
    output = session_root / "judge-mode-evidence.json"

    exit_code = cmd_judge_mode(
        SimpleNamespace(source=str(source), output=str(output), json=True)
    )

    assert exit_code == 0
    payload = json.loads(output.read_text(encoding="utf-8"))
    assert payload["allow"]["status"] == "APPLIED"
    assert payload["allow"]["handler_call_count"] == 1
    assert payload["deny"] == {
        "reason_code": "ROLE_NOT_ALLOWED",
        "handler_call_count": 0,
        "workspace_hash_unchanged": True,
    }
    assert payload["source"]["hash_unchanged"] is True
    assert payload["source"]["sha256_before"] == payload["source"]["sha256_after"]
    assert all(payload["receipt_binding"].values())
    assert payload["production_reuse"] is False
    assert len(payload["gates"]) == 4
    assert all(gate["passed"] for gate in payload["gates"])
    assert payload["release_decision"] == "RELEASE_ELIGIBLE"

    run_path = Path(payload["run_path"])
    review = json.loads(
        (run_path / "checkmate-review-receipt.json").read_text(encoding="utf-8")
    )
    authorization = json.loads(
        (run_path / "sovereign-authorization-receipt.json").read_text(
            encoding="utf-8"
        )
    )
    for field in ("run_id", "transaction_id", "plan_sha256"):
        assert review[field] == authorization[field] == payload[field]
