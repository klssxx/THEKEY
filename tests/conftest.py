"""Pytest fixtures: reset repo-local state before each test so runs are
deterministic and isolated (single active run at a time in the MVP).

Each test starts from an identical, clean runtime state by removing the four
known mutable state files and wiping runs/ + workspaces/. We deliberately do
NOT rmtree the whole .thekey directory, because on Windows that triggered a
directory-level lock race with StateMachine's atomic writes.
"""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest

from thekey.config import RUNS_DIR, THEKEY_DIR, WORKSPACES_DIR
from thekey.state_machine import (
    HISTORY_FILE,
    STATE_FILE,
    STATE_PREV_FILE,
    TRANSITIONS_FILE,
)

THEKEY_HISTORICAL = Path("E:/KLSX PROYECTS/KlsxMaker/TheKey/Thekey")


def _wipe_dir(d: Path):
    if d.exists():
        for child in d.iterdir():
            if child.is_dir():
                shutil.rmtree(child, ignore_errors=True)
            else:
                child.unlink()


@pytest.fixture(autouse=True)
def _reset_state():
    THEKEY_DIR.mkdir(parents=True, exist_ok=True)
    # Remove the entire mutable state set (not just two files), so lingering
    # artifacts (state.previous.json, state-history.jsonl) cannot cause
    # non-reproducible baselines. We delete files only -- never rmtree the
    # .thekey directory -- to avoid Windows lock races.
    for f in (STATE_FILE, STATE_PREV_FILE, TRANSITIONS_FILE, HISTORY_FILE):
        if f.exists():
            f.unlink()
    for f in THEKEY_DIR.glob("*.jsonl"):
        f.unlink()
    for f in THEKEY_DIR.glob("*.json"):
        f.unlink()
    _wipe_dir(RUNS_DIR)
    _wipe_dir(WORKSPACES_DIR)
    yield
    # No teardown needed; each test cleans its own run.


@pytest.fixture
def coordinator():
    from thekey.main import RunCoordinator

    return RunCoordinator()
