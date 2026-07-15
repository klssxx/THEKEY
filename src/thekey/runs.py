"""Run identifiers, manifests, and request records.

A *run* is the authoritative record of one governed change attempt. The run id
is globally unique (TK-YYYYMMDD-HHMMSS-XXXXXX) and every artifact for the run
lives under runs/<RUN_ID>/.
"""

from __future__ import annotations

import json
import secrets
import string
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from .config import RUNS_DIR
from .errors import InvalidArgumentsError, TheKeyError


def _utcnow() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _rand_suffix(n: int = 6) -> str:
    alphabet = string.ascii_uppercase + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(n))


def generate_run_id() -> str:
    """TK-YYYYMMDD-HHMMSS-XXXXXX - deterministic format, random suffix."""
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    return f"TK-{stamp}-{_rand_suffix(6)}"


@dataclass
class RunRequest:
    """The submitted change request."""

    title: str
    description: str = ""
    source_inputs: list[dict] = field(default_factory=list)
    request_id: str = field(default_factory=lambda: f"REQ-{uuid.uuid4().hex[:8]}")

    def to_dict(self) -> dict:
        return {
            "request_id": self.request_id,
            "title": self.title,
            "description": self.description,
            "source_inputs": self.source_inputs,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "RunRequest":
        return cls(
            title=data["title"],
            description=data.get("description", ""),
            source_inputs=data.get("source_inputs", []),
            request_id=data.get("request_id", f"REQ-{uuid.uuid4().hex[:8]}"),
        )


class RunManager:
    """Creates and reads run directories under runs/.

    The manager only deals with filesystem layout and atomic JSON writes for
    run-level artifacts. It does NOT own authoritative state transitions (see
    state_machine.py). Every action is logged via an explicit audit trail.
    """

    def __init__(self, runs_dir: Path = RUNS_DIR):
        self.runs_dir = Path(runs_dir)
        self.runs_dir.mkdir(parents=True, exist_ok=True)

    def create_run(self, request: RunRequest) -> "Run":
        run = Run(run_id=generate_run_id(), runs_dir=self.runs_dir)
        run.ensure_dirs()
        run.write_json(
            "request.json",
            {"created_at": _utcnow(), **request.to_dict()},
        )
        run.write_json(
            "manifest.json",
            {
                "run_id": run.run_id,
                "schema_version": "1.0",
                "created_at": _utcnow(),
                "engine_version": "0.1.0",
                "status": "CREATED",
            },
        )
        return run

    def get_run(self, run_id: str) -> "Run":
        if not run_id or not run_id.startswith("TK-"):
            raise InvalidArgumentsError(f"Malformed run id: {run_id!r}")
        run = Run(run_id=run_id, runs_dir=self.runs_dir)
        if not run.dir.exists():
            raise InvalidArgumentsError(f"Run does not exist: {run_id}")
        return run


class Run:
    """A single run's artifact directory."""

    def __init__(self, run_id: str, runs_dir: Path = RUNS_DIR):
        self.run_id = run_id
        self.dir = Path(runs_dir) / run_id
        self.evidence_dir = self.dir / "evidence"
        self.logs_dir = self.dir / "logs"
        self.policy_snapshot_dir = self.dir / "policy-snapshot"

    def ensure_dirs(self) -> None:
        self.dir.mkdir(parents=True, exist_ok=True)
        self.evidence_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        self.policy_snapshot_dir.mkdir(parents=True, exist_ok=True)

    def write_json(self, name: str, payload: dict, *, atomic: bool = True) -> Path:
        path = self.dir / name
        self._write_payload(path, payload, atomic=atomic)
        return path

    def read_json(self, name: str) -> dict:
        path = self.dir / name
        if not path.exists():
            raise TheKeyError(f"Missing run artifact: {name}", code="MISSING_ARTIFACT")
        return json.loads(path.read_text(encoding="utf-8"))

    def append_line(self, name: str, line: str) -> None:
        path = self.dir / name
        with path.open("a", encoding="utf-8") as fh:
            fh.write(line.rstrip("\n") + "\n")

    @staticmethod
    def _write_payload(path: Path, payload: dict, *, atomic: bool) -> None:
        text = json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True)
        if atomic:
            tmp = path.with_suffix(path.suffix + ".tmp")
            tmp.write_text(text, encoding="utf-8")
            tmp.replace(path)
        else:
            path.write_text(text, encoding="utf-8")
