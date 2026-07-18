"""Evidence + hash verification tests (section 31: EVIDENCE)."""

import json

import pytest

from thekey.evidence import (
    EvidenceManager,
    EvidenceRecord,
    sha256_file,
    sha256_text,
    verify_record_signature,
)
from thekey.errors import InvalidEvidenceError
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


def test_record_signature_valid_and_tamper_detected():
    em = EvidenceManager(RUNS_DIR / "sigtest-run" / "evidence")
    rec = EvidenceRecord(
        evidence_id="S1", kind="state-file", producer="x",
        artifact_path="a.txt", artifact_hash="deadbeef", summary="s",
    )
    p = em.record(rec)
    # Loaded record verifies its own signature.
    loaded = em.load_record("S1")
    assert loaded["evidence_id"] == "S1"
    assert "signature" in loaded
    # Tamper with the on-disk record (edit a field, keep old signature).
    tampered = json.loads(p.read_text(encoding="utf-8"))
    tampered["summary"] = "TAMPERED"
    p.write_text(json.dumps(tampered), encoding="utf-8")
    with pytest.raises(InvalidEvidenceError):
        em.load_record("S1")


def test_signature_depends_on_payload():
    r1 = EvidenceRecord("A", "state-file", "x", "a", "h1", "s1").to_dict()
    r2 = EvidenceRecord("A", "state-file", "x", "a", "h2", "s1").to_dict()
    assert r1["signature"] != r2["signature"]
    assert verify_record_signature(r1)
    assert verify_record_signature(r2)
