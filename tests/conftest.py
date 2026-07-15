"""Pytest fixtures: reset repo-local state before each test so runs are
deterministic and isolated (single active run at a time in the MVP)."""

from __future__ import annotations

from pathlib import Path

import pytest

from thekey.config import REPO_ROOT, RUNS_DIR, WORKSPACES_DIR
from thekey.state_machine import STATE_FILE, TRANSITIONS_FILE

THEKEY_HISTORICAL = Path("E:/KLSX PROYECTS/KlsxMaker/TheKey/Thekey")


@pytest.fixture(autouse=True)
def _reset_state():
    # Remove repo-local run state + runtime artifacts before each test.
    for p in (STATE_FILE, TRANSITIONS_FILE):
        if p.exists():
            p.unlink()
    for d in (RUNS_DIR, WORKSPACES_DIR):
        if d.exists():
            for child in d.iterdir():
                if child.is_dir():
                    import shutil

                    shutil.rmtree(child, ignore_errors=True)
                else:
                    child.unlink()
    yield
    # No teardown needed; each test cleans its own run.


@pytest.fixture
def coordinator():
    from thekey.main import RunCoordinator

    return RunCoordinator()
