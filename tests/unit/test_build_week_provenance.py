from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASELINE = "3a8456416ed9ae9183840585b488cec04e9a069d"
PHASE_B = "c0410feaf869e0ac08c9e637b70e30ebac8085c8"
SESSION_ID = "019f79f2-6a7e-74f0-b1fa-d65335b29a7c"

REQUIRED = (
    "docs/build-week/PRE_PUBLIC_PROVENANCE.md",
    "docs/build-week/PROVENANCE_TIMELINE.md",
    "docs/build-week/EVIDENCE_HANDLING.md",
    "docs/build-week/BUILD_WEEK_DELTA.md",
    "evidence/build-week/provenance/PROVENANCE_MANIFEST.json",
    "evidence/build-week/provenance/PUBLIC_EVIDENCE_INDEX.json",
    "scripts/collect-preexisting-evidence.ps1",
)

ALLOWED_PUBLIC_STATUSES = {
    "BOUND_TO_FINAL_HEAD",
    "CLAIM_RECORDED",
    "PENDING_EVIDENCE_IMPORT",
    "VERIFIED_GIT_OBJECT",
    "VERIFIED_SESSION_METADATA",
}


def _load(relative: str) -> dict:
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def test_required_provenance_dossier_exists_and_private_path_is_ignored():
    assert all((ROOT / relative).is_file() for relative in REQUIRED)
    gitignore = (ROOT / ".gitignore").read_text(encoding="utf-8")
    assert "/evidence-private/build-week/chat-exports/" in gitignore


def test_provenance_manifest_preserves_claim_boundaries():
    manifest = _load("evidence/build-week/provenance/PROVENANCE_MANIFEST.json")
    assert manifest["project"] == {
        "name": "THEKEY",
        "classification": "PREEXISTING_PROJECT",
        "classification_status": "CLAIM_RECORDED",
    }
    boundaries = manifest["candidate_boundaries"]
    assert boundaries["session_baseline"]["commit"] == BASELINE
    assert boundaries["phase_b_commit"]["commit"] == PHASE_B
    assert boundaries["final_candidate"]["ref"] == "HEAD"
    assert boundaries["final_candidate"]["status"] == "BOUND_TO_FINAL_HEAD"
    assert manifest["codex_session"]["feedback_session_id"] == SESSION_ID
    assert manifest["codex_session"]["status"] == "VERIFIED_SESSION_METADATA"
    assert manifest["pre_public_history"][0]["status"] == "CLAIM_RECORDED"
    assert manifest["pre_public_history"][1]["status"] == "PENDING_EVIDENCE_IMPORT"


def test_public_index_uses_only_explicit_evidence_statuses():
    index = _load("evidence/build-week/provenance/PUBLIC_EVIDENCE_INDEX.json")
    statuses = {entry["status"] for entry in index["entries"]}
    assert statuses <= ALLOWED_PUBLIC_STATUSES
    pending = next(
        entry
        for entry in index["entries"]
        if entry["evidence_id"] == "PREPUBLIC-CHAT-EXPORTS"
    )
    assert pending["status"] == "PENDING_EVIDENCE_IMPORT"
    assert pending["public_path"] is None
    assert pending["published"] is False


def test_build_week_delta_names_all_four_boundaries():
    delta = (ROOT / "docs/build-week/BUILD_WEEK_DELTA.md").read_text(encoding="utf-8")
    markers = (
        "PREEXISTING PROJECT",
        "SESSION BASELINE",
        "PHASE-B COMMIT",
        "FINAL CANDIDATE",
    )
    for marker in markers:
        assert marker in delta
    assert BASELINE in delta
    assert PHASE_B in delta
    assert "Only changes verifiable after the session baseline" in delta
