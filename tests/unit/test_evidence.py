"""Evidence + hash verification tests (section 31: EVIDENCE)."""

import json

import pytest

from thekey.evidence import EvidenceManager, sha256_file, sha256_text
from thekey.config import RUNS_DIR
from thekey.runs import RunManager


def test_correct_hashes():
    rm = RunManager(RUNS_DIR)
    run = rm.create_run(__import__("thekey.runs", fromlist=["RunRequest"]).RunRequest(title="t"))
    em = EvidenceManager(run.evidence_dir)
    p = run.dir / "artifact.txt"
    p.write_text("hello", encoding="utf-8")
    h = sha256_file(p)
    assert em.verify_artifact(p, h)
    assert not em.verify_artifact(p, "deadbeef")


def test_tampered_hash_detected():
    rm = RunManager(RUNS_DIR)
    run = rm.create_run(__import__("thekey.runs", fromlist=["RunRequest"]).RunRequest(title="t"))
    em = EvidenceManager(run.evidence_dir)
    p = run.dir / "artifact.txt"
    p.write_text("hello", encoding="utf-8")
    rec = em.record(__import__("thekey.evidence", fromlist=["EvidenceRecord"]).EvidenceRecord(
        evidence_id="E1", kind="state-file", producer="x",
        artifact_path="artifact.txt", artifact_hash=sha256_file(p), summary="s",
    ))
    # Tamper with the artifact after recording.
    p.write_text("tampered", encoding="utf-8")
    # The recorded hash no longer matches on disk.
    assert sha256_file(p) != json.loads(rec.read_text(encoding="utf-8"))["artifact_hash"]


def test_missing_artifact():
    em = EvidenceManager(RUNS_DIR / "nonexistent-run" / "evidence")
    with pytest.raises(Exception):
        em.load_record("E1")


def test_sha256_text_stable():
    assert sha256_text("abc") == sha256_text("abc")
    assert sha256_text("abc") != sha256_text("abd")
