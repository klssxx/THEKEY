"""Evidence manager: atomic writes and SHA-256 verification.

Evidence is created ONLY from observed execution results - never from model
output. Each evidence record carries the producing command/action, its result
hash, and the path it validates. Missing evidence resolves to NO_VERIFICABLE,
never PASS (section 16 of kernel rules).

Integrity (improvement A): every evidence record is signed with HMAC-SHA256
using a local deterministic key stored at THEKEY_DIR/evidence.key. The
signature binds the canonical record payload, so a record edited in place (not
just the referenced artifact) is detected on verify.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .errors import InvalidEvidenceError, TheKeyError
from .io_atomic import atomic_write_json


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with Path(path).open("rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _key_path() -> Path:
    from .config import THEKEY_DIR

    return THEKEY_DIR / "evidence.key"


def _load_or_create_key() -> bytes:
    """Return the local evidence-signing key, creating it deterministically
    if absent. The key is repo-local and never committed (see .gitignore)."""
    kp = _key_path()
    if kp.exists():
        return kp.read_bytes()
    # Deterministic seed from the repo root path so a fresh clone on the same
    # machine reproduces the same key without a secrets store. This is evidence
    # integrity, not confidentiality: it prevents silent edits, not disclosure.
    from .config import REAL_ROOT

    seed = sha256_text(f"thekey-evidence:{REAL_ROOT}").encode("utf-8")
    kp.parent.mkdir(parents=True, exist_ok=True)
    # Defensive: avoid world-readable key file where the OS supports it.
    try:
        os.chmod(kp.parent, 0o700)
    except OSError:
        pass
    kp.write_bytes(seed)
    try:
        os.chmod(kp, 0o600)
    except OSError:
        pass
    return seed


def _sign(payload: dict) -> str:
    key = _load_or_create_key()
    canonical = json.dumps(payload, sort_keys=True, ensure_ascii=False)
    return hmac.new(key, canonical.encode("utf-8"), hashlib.sha256).hexdigest()


def verify_record_signature(rec: dict) -> bool:
    """Recompute the HMAC over the stored payload and compare to 'signature'."""
    if "signature" not in rec:
        return False
    signed = dict(rec)
    stored = signed.pop("signature")
    return hmac.compare_digest(_sign(signed), stored)


@dataclass
class EvidenceRecord:
    evidence_id: str
    kind: str  # 'command-result' | 'state-file' | 'policy-file' | 'generated-proposal'
    producer: str  # action id / orchestrator op
    artifact_path: str
    artifact_hash: str
    summary: str
    verified: bool = False

    def to_dict(self) -> dict:
        d = {
            "evidence_id": self.evidence_id,
            "kind": self.kind,
            "producer": self.producer,
            "artifact_path": self.artifact_path,
            "artifact_hash": self.artifact_hash,
            "summary": self.summary,
            "verified": self.verified,
        }
        # Signature binds the canonical payload; computed last and excluded
        # from the signed content.
        d["signature"] = _sign(d)
        return d


class EvidenceManager:
    """Writes evidence atomically into a run's evidence/ directory and verifies
    artifact hashes and record signatures."""

    def __init__(self, run_evidence_dir: Path):
        self.dir = Path(run_evidence_dir)
        self.dir.mkdir(parents=True, exist_ok=True)

    def write_atomic(self, name: str, payload: dict) -> Path:
        return atomic_write_json(self.dir / name, payload)

    def record(self, rec: EvidenceRecord) -> Path:
        return self.write_atomic(f"{rec.evidence_id}.json", rec.to_dict())

    def verify_artifact(self, path: Path, expected_hash: str) -> bool:
        path = Path(path)
        if not path.exists():
            return False
        return sha256_file(path) == expected_hash

    def load_record(self, evidence_id: str) -> dict:
        path = self.dir / f"{evidence_id}.json"
        if not path.exists():
            raise InvalidEvidenceError(f"Missing evidence: {evidence_id}")
        rec = json.loads(path.read_text(encoding="utf-8"))
        if not verify_record_signature(rec):
            raise InvalidEvidenceError(
                f"Evidence signature mismatch: {evidence_id} (record tampered)"
            )
        return rec

    def index(self) -> list[str]:
        return sorted(p.name for p in self.dir.glob("*.json"))
