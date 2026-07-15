"""Run History tests (section 48: HISTORY)."""

import json

from thekey.config import RUNS_DIR
from thekey.history import RunHistory, history_rebuild, history_verify
from thekey.main import RunCoordinator


def _clean_history():
    p = RUNS_DIR / "history.jsonl"
    if p.exists():
        p.unlink()
    b = RUNS_DIR / "history.jsonl.bak"
    if b.exists():
        b.unlink()


def test_append_new_run():
    _clean_history()
    c = RunCoordinator()
    c.create("t", "t")
    c.baseline()
    c.plan()
    c.approve_plan()
    c.execute()
    c.verify()
    c.decide()
    rh = RunHistory()
    entries = rh.list_entries()
    assert len(entries) == 1
    e = entries[0]
    assert e.run_id == c.run.run_id
    assert e.decision == "RELEASE_ELIGIBLE"
    assert e.integrity_status == "VALID"


def test_legacy_run_indexing():
    _clean_history()
    # A 0.1.0-style run dir with manifest + decision, no project-profile.
    from thekey.runs import RunManager
    from thekey.config import DEMO_APP_SOURCE
    rm = RunManager(RUNS_DIR)
    run = rm.create_run(__import__("thekey.runs", fromlist=["RunRequest"]).RunRequest(title="legacy"))
    # Minimal artifacts so history can derive something.
    run.write_json("manifest.json", {"run_id": run.run_id, "schema_version": "1.0",
                                      "created_at": "2026-07-01T00:00:00Z", "engine_version": "0.1.0",
                                      "status": "DONE"})
    run.write_json("decision.json", {"run_id": run.run_id, "decision": "RELEASE_ELIGIBLE",
                                     "policy_id": "local-python-demo", "approver_identity": "x",
                                     "reason": "ok", "gates": [], "evidence_missing": []})
    rh = RunHistory()
    rh.index_run(run.run_id)
    entries = rh.list_entries()
    assert any(e.run_id == run.run_id for e in entries)
    # Legacy run with no project-profile -> profile empty, still indexed VALID.
    e = [e for e in entries if e.run_id == run.run_id][0]
    assert e.project_profile == ""
    assert e.decision == "RELEASE_ELIGIBLE"


def test_verify_valid():
    _clean_history()
    c = RunCoordinator()
    c.create("t", "t")
    c.baseline()
    c.plan()
    c.approve_plan()
    c.execute()
    c.verify()
    c.decide()
    res = history_verify()
    assert res["integrity_status"] == "VALID"
    assert res["corrupt"] == []


def test_rebuild_preserves_valid_entries():
    _clean_history()
    c = RunCoordinator()
    c.create("t", "t")
    c.baseline()
    c.plan()
    c.approve_plan()
    c.execute()
    c.verify()
    c.decide()
    res = history_rebuild()
    assert res["rebuilt"] >= 1
    assert res["integrity_status"] == "VALID"


def test_corrupt_run_marked():
    _clean_history()
    # Build a valid run first.
    c = RunCoordinator()
    c.create("t", "t")
    c.baseline()
    c.plan()
    c.approve_plan()
    c.execute()
    c.verify()
    c.decide()
    # Now corrupt: add a run dir with manifest but missing decision file while
    # decision.json references it (simulate by writing a bad decision path).
    from thekey.runs import RunManager
    import thekey.runs as rn
    rm = RunManager(RUNS_DIR)
    run = rm.create_run(rn.RunRequest(title="corrupt"))
    run.write_json("manifest.json", {"run_id": run.run_id, "schema_version": "1.0",
                                      "created_at": "2026-07-02T00:00:00Z", "engine_version": "0.1.0",
                                      "status": "DONE"})
    # decision.json claims a missing file path indirectly: leave a dangling
    # decision that points at a non-existent artifact by writing decision.json
    # but removing it after indexing.
    run.write_json("decision.json", {"run_id": run.run_id, "decision": "RELEASE_ELIGIBLE",
                                     "policy_id": "local-python-demo", "approver_identity": "x",
                                     "reason": "ok", "gates": [], "evidence_missing": []})
    rh = RunHistory()
    rh.index_run(run.run_id)
    # Remove decision.json to simulate corruption, then verify should flag it.
    (run.dir / "decision.json").unlink()
    res = history_verify()
    assert run.run_id in res["corrupt"]
    assert res["integrity_status"] == "CORRUPT"
