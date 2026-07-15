"""Integration tests for the demo app and CLI surface."""

import json

import pytest

from thekey.main import RunCoordinator
from thekey.config import DEMO_APP_SOURCE


def test_demo_app_original_is_defective():
    src = DEMO_APP_SOURCE.read_text(encoding="utf-8")
    assert "return a - b" in src
    # The ORIGINAL intentionally fails the test expectation.
    import subprocess, sys

    result = subprocess.run(
        [sys.executable, "-c",
         "import sys; sys.path.insert(0, r'%s'); from calculator import add; "
         "sys.exit(0 if add(2,3)==5 else 1)" % str(DEMO_APP_SOURCE.parent)],
        capture_output=True, text=True,
    )
    assert result.returncode == 1, result.stderr


def test_cli_demo_help():
    from thekey.cli import build_parser
    parser = build_parser()
    # Must not raise; help text available.
    assert parser.prog == "thekey"


def test_integration_full_run_artifacts_present():
    c = RunCoordinator()
    c.create("t", "t")
    c.baseline()
    c.plan()
    c.approve_plan()
    c.execute()
    c.verify()
    c.decide()
    for name in ("manifest.json", "request.json", "plan.json", "approvals.json",
                 "changes.diff", "gates.json", "decision.json", "artifact-hashes.json"):
        assert (c.run.dir / name).exists(), f"missing {name}"
    # The transition log lives at the repo-level .thekey directory.
    from thekey.config import THEKEY_DIR

    assert (THEKEY_DIR / "state-transitions.jsonl").exists()
