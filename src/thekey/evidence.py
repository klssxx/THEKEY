"""Evidence manager: atomic writes and SHA-256 verification.

Evidence is created ONLY from observed execution results - never from model
output. Each evidence record carries the producing command/action, its result
hash, and the path it validates. Missing evidence resolves to NO_VERIFICABLE,
never PASS (section 16 of kernel rules).
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .errors import InvalidEvidenceError, TheKeyError


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with Path(path).open("rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


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
        return {
            "evidence_id": self.evidence_id,
            "kind": self.kind,
            "producer": self.producer,
            "artifact_path": self.artifact_path,
            "artifact_hash": self.artifact_hash,
            "summary": self.summary,
            "verified": self.verified,
        }


class EvidenceManager:
    """Writes evidence atomically into a run's evidence/ directory and verifies
    artifact hashes."""

    def __init__(self, run_evidence_dir: Path):
        self.dir = Path(run_evidence_dir)
        self.dir.mkdir(parents=True, exist_ok=True)

    def write_atomic(self, name: str, payload: dict) -> Path:
        path = self.dir / name
        text = json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True)
        tmp = path.with_suffix(path.suffix + ".tmp")
        tmp.write_text(text, encoding="utf-8")
        tmp.replace(path)
        return path

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
        return json.loads(path.read_text(encoding="utf-8"))

    def index(self) -> list[str]:
        return sorted(p.name for p in self.dir.glob("*.json"))
