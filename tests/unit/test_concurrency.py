"""Concurrency test for per-run state isolation (improvement D).

Two RunCoordinators must not share state; each writes to its own
runs/<RUN_ID>/state.json and completes independently.
"""

import os
import tempfile
import threading
from pathlib import Path

from thekey.main import RunCoordinator
from thekey.runs import RunManager, RunRequest
from thekey.state_machine import StateMachine


def _run_once():
    coord = RunCoordinator()
    coord.create("concurrent run", "demo")
    coord.baseline()
    coord.plan()
    coord.approve_plan()
    coord.execute()
    coord.verify()
    decision = coord.decide()
    coord.close()
    return decision


def test_two_concurrent_runs_isolated():
    results = {}

    def worker(tag):
        d = _run_once()
        results[tag] = d.decision

    t1 = threading.Thread(target=worker, args=("a",))
    t2 = threading.Thread(target=worker, args=("b",))
    t1.start()
    t2.start()
    t1.join()
    t2.join()

    assert results["a"] == "RELEASE_ELIGIBLE"
    assert results["b"] == "RELEASE_ELIGIBLE"


def test_state_files_are_per_run():
    root = Path(tempfile.mkdtemp())
    os.environ["THEKEY_REPO_ROOT"] = str(root)
    try:
        rm = RunManager(root / "runs")
        r1 = rm.create_run(RunRequest(title="r1"))
        r2 = rm.create_run(RunRequest(title="r2"))
        sm1 = StateMachine(state_file=r1.dir / "state.json")
        sm2 = StateMachine(state_file=r2.dir / "state.json")
        sm1.reset_to_submitted(r1.run_id)
        sm2.reset_to_submitted(r2.run_id)
        sm1.apply_transition("BASELINED", run_id=r1.run_id, role="orchestrator", reason="x")
        # r2 must still be SUBMITTED; no leakage.
        assert sm2.load().run_state == "SUBMITTED"
        assert sm1.load().run_state == "BASELINED"
    finally:
        os.environ.pop("THEKEY_REPO_ROOT", None)
