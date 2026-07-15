"""EXECUTOR role.

Requires an approved plan. Works ONLY inside workspaces/<RUN_ID>/. Applies
approved structured operations (never arbitrary shell). Produces change
evidence and a diff. Does NOT modify the original project, THEKEY, policies, or
approvals. Rejects unapproved plans, ambiguous replacements, operations not in
the plan, and exceeded budgets (sections 5, 17).
"""

from __future__ import annotations

import difflib
from pathlib import Path

from ..actions import dispatch
from ..config import DEMO_APP_SOURCE, WORKSPACES_DIR
from ..errors import IncompatibleRunStateError, TheKeyError, UnauthorizedActionError
from ..workspaces import WorkspaceManager


class Executor:
    def __init__(self, run_id: str, workspace_root: Path = WORKSPACES_DIR):
        self.run_id = run_id
        self.wm = WorkspaceManager(workspace_root)
        self.ws = self.wm.create(run_id)

    def _assert_approved(self, plan: dict) -> None:
        if not plan.get("approved"):
            raise IncompatibleRunStateError(
                "Executor requires an approved plan", code="INCOMPATIBLE_RUN_STATE"
            )

    def prepare_workspace(self, demo_source: Path = DEMO_APP_SOURCE) -> dict:
        """Copy the original demo into the isolated workspace (read-only copy of
        the original; the workspace copy is the only thing ever modified)."""
        self.ws.mkdir(parents=True, exist_ok=True)
        src_dir = self.ws / "src" / "demo_app"
        src_dir.mkdir(parents=True, exist_ok=True)
        dest = src_dir / "calculator.py"
        dest.write_text(demo_source.read_text(encoding="utf-8"), encoding="utf-8")

        tests_dir = self.ws / "tests"
        tests_dir.mkdir(parents=True, exist_ok=True)
        # Minimal test module referencing the fixed behavior.
        (self.ws / "README.md").write_text(
            "# Demo App (governed workspace copy)\n\n"
            "This workspace copy is repaired by the governed run.\n"
            "Original source at examples/demo_app remains intentionally broken.\n",
            encoding="utf-8",
        )
        test_file = tests_dir / "test_calculator.py"
        test_file.write_text(
            "from src.demo_app.calculator import add\n\n"
            "def test_add_uses_addition():\n"
            "    assert add(2, 3) == 5\n",
            encoding="utf-8",
        )
        # Make src importable.
        (self.ws / "src" / "__init__.py").write_text("", encoding="utf-8")
        (self.ws / "src" / "demo_app" / "__init__.py").write_text("", encoding="utf-8")
        return {
            "status": "PREPARED",
            "workspace": str(self.ws),
            "copied_from": str(demo_source),
        }

    def apply_operation(self, operation: dict, plan: dict) -> dict:
        self._assert_approved(plan)
        # Operation must be in the approved plan.
        approved_ids = {op["op_id"] for op in plan.get("operations", [])}
        if operation.get("op_id") not in approved_ids:
            raise UnauthorizedActionError(
                f"Operation {operation.get('op_id')!r} not in approved plan",
                code="UNAUTHORIZED_ACTION",
            )
        action_id = operation.get("action_id")
        target_id = operation.get("target_id")
        # Map declared target id -> workspace relative path.
        ws_relative = {
            "DEMO_CALCULATOR": "src/demo_app/calculator.py",
        }.get(target_id)
        if ws_relative is None:
            raise TheKeyError(f"Unknown target id: {target_id!r}", code="UNKNOWN_TARGET")
        params = dict(operation.get("parameters", {}))
        params.setdefault("target_id", ws_relative)
        if action_id == "REPLACE_EXACT_TEXT":
            params["target_id"] = ws_relative
            params["expected"] = operation["expected"]
            params["replacement"] = operation["replacement"]
        result = dispatch(action_id, self.run_id, params)
        return {"status": result.get("status"), "action_id": action_id, "result": result}

    def generate_diff(self, demo_source: Path = DEMO_APP_SOURCE) -> str:
        original = demo_source.read_text(encoding="utf-8").splitlines()
        workspace_file = self.ws / "src" / "demo_app" / "calculator.py"
        modified = workspace_file.read_text(encoding="utf-8").splitlines()
        diff = difflib.unified_diff(
            original,
            modified,
            fromfile="examples/demo_app/calculator.py (original, untouched)",
            tofile="workspaces/{}/src/demo_app/calculator.py (repaired)".format(self.run_id),
            lineterm="",
        )
        return "\n".join(diff)
