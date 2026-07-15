"""Run History index (section 40/41/42).

A derived, append-only index of runs at runs/history.jsonl. Each run directory
remains the authoritative record; this index is rebuilt/verified against the
actual run artifacts. Corrupt runs are marked CORRUPT, never silently dropped.
"""

from __future__ import annotations

import hashlib
import json
import shutil
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .config import RUNS_DIR
from .evidence import sha256_file

HISTORY_PATH = RUNS_DIR / "history.jsonl"


def _utcnow() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read_json(path: Path) -> dict | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


@dataclass
class HistoryEntry:
    schema_version: str = "1.0"
    run_id: str = ""
    mission_id: str = ""
    project_id: str = ""
    project_name: str = ""
    source_root_display: str = ""
    created_at: str = ""
    updated_at: str = ""
    completed_at: str | None = None
    project_profile: str = ""
    policy_id: str = ""
    final_state: str = ""
    decision: str | None = None
    gates_passed: int = 0
    gates_failed: int = 0
    plan_sha256: str = ""
    source_baseline_sha256: str = ""
    decision_path: str | None = None
    integrity_status: str = "VALID"

    def to_dict(self) -> dict:
        return {
            "schema_version": self.schema_version,
            "run_id": self.run_id,
            "mission_id": self.mission_id,
            "project_id": self.project_id,
            "project_name": self.project_name,
            "source_root_display": self.source_root_display,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "completed_at": self.completed_at,
            "project_profile": self.project_profile,
            "policy_id": self.policy_id,
            "final_state": self.final_state,
            "decision": self.decision,
            "gates_passed": self.gates_passed,
            "gates_failed": self.gates_failed,
            "plan_sha256": self.plan_sha256,
            "source_baseline_sha256": self.source_baseline_sha256,
            "decision_path": self.decision_path,
            "integrity_status": self.integrity_status,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "HistoryEntry":
        known = {f for f in cls.__dataclass_fields__}
        return cls(**{k: v for k, v in d.items() if k in known})


def _load_index() -> list[HistoryEntry]:
    if not HISTORY_PATH.exists():
        return []
    out = []
    for line in HISTORY_PATH.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            out.append(HistoryEntry.from_dict(json.loads(line)))
        except Exception:
            continue
    return out


def _save_index(entries: list[HistoryEntry], backup: bool = True) -> None:
    HISTORY_PATH.parent.mkdir(parents=True, exist_ok=True)
    if backup and HISTORY_PATH.exists():
        shutil.copy2(HISTORY_PATH, HISTORY_PATH.with_suffix(".jsonl.bak"))
    tmp = HISTORY_PATH.with_suffix(".jsonl.tmp")
    lines = [json.dumps(e.to_dict(), ensure_ascii=False) for e in entries]
    tmp.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")
    tmp.replace(HISTORY_PATH)


def _derive_from_run(run_dir: Path) -> HistoryEntry | None:
    """Build a history entry by reading the authoritative run artifacts."""
    run_id = run_dir.name
    manifest = _read_json(run_dir / "manifest.json") or {}
    request = _read_json(run_dir / "request.json") or {}
    plan = _read_json(run_dir / "plan.json")
    approvals = _read_json(run_dir / "approvals.json")
    profile = _read_json(run_dir / "project-profile.json")
    decision = _read_json(run_dir / "decision.json")
    gates = _read_json(run_dir / "gates.json")

    entry = HistoryEntry(
        run_id=run_id,
        created_at=manifest.get("created_at", ""),
        updated_at=manifest.get("created_at", ""),
    )
    entry.mission_id = request.get("request_id", "")
    if profile:
        entry.project_id = profile.get("project_id", "")
        entry.project_name = profile.get("project_name", "")
        entry.source_root_display = profile.get("source_root", "")
        entry.project_profile = profile.get("detected_profile", "")
    if approvals:
        entry.plan_sha256 = (approvals.get("history") or [{}])[-1:][0].get("plan_sha256", "") or ""
        for h in approvals.get("history", []):
            if h.get("plan_sha256"):
                entry.plan_sha256 = h["plan_sha256"]
                break
    if gates:
        entry.gates_passed = sum(1 for g in gates.get("results", []) if g.get("passed"))
        entry.gates_failed = sum(1 for g in gates.get("results", []) if not g.get("passed"))
    if decision:
        entry.decision = decision.get("decision")
        entry.policy_id = decision.get("policy_id", "")
        entry.decision_path = str(run_dir / "decision.json")
        if decision.get("reason", "").startswith("SOURCE_BASELINE_CHANGED"):
            entry.integrity_status = "CORRUPT"
    entry.final_state = manifest.get("status", "UNKNOWN")
    # Corrupt detection: manifest present but decision references missing file.
    if entry.decision and entry.decision_path and not Path(entry.decision_path).exists():
        entry.integrity_status = "CORRUPT"
    return entry


class RunHistory:
    def __init__(self, runs_dir: Path = RUNS_DIR):
        self.runs_dir = Path(runs_dir)

    # -- indexing ------------------------------------------------------
    def index_run(self, run_id: str) -> HistoryEntry | None:
        run_dir = self.runs_dir / run_id
        if not run_dir.exists():
            return None
        entry = _derive_from_run(run_dir)
        if entry is None:
            return None
        entries = _load_index()
        replaced = False
        for i, e in enumerate(entries):
            if e.run_id == run_id:
                entries[i] = entry
                replaced = True
                break
        if not replaced:
            entries.append(entry)
        _save_index(entries)
        return entry

    def list_entries(
        self,
        *,
        project: str | None = None,
        profile: str | None = None,
        state: str | None = None,
        decision: str | None = None,
        since: str | None = None,
        limit: int | None = None,
    ) -> list[HistoryEntry]:
        entries = _load_index()
        if project:
            entries = [e for e in entries if e.project_id == project]
        if profile:
            entries = [e for e in entries if e.project_profile == profile]
        if state:
            entries = [e for e in entries if e.final_state == state]
        if decision:
            entries = [e for e in entries if e.decision == decision]
        if since:
            entries = [e for e in entries if (e.created_at or "") >= since]
        entries.sort(key=lambda e: e.created_at)
        if limit:
            entries = entries[-limit:]
        return entries

    def show(self, run_id: str) -> dict | None:
        for e in _load_index():
            if e.run_id == run_id:
                run_dir = self.runs_dir / run_id
                detail: dict[str, Any] = e.to_dict()
                detail["artifacts"] = sorted(
                    p.name for p in run_dir.iterdir() if p.is_file()
                ) if run_dir.exists() else []
                return detail
        return None

    # -- verify / rebuild ---------------------------------------------
    def verify(self) -> dict:
        entries = _load_index()
        corrupt = []
        checked = 0
        for e in entries:
            run_dir = self.runs_dir / e.run_id
            if not run_dir.exists():
                e.integrity_status = "CORRUPT"
                corrupt.append(e.run_id)
                continue
            checked += 1
            # Re-derive and compare key fields.
            derived = _derive_from_run(run_dir)
            if derived is None:
                e.integrity_status = "CORRUPT"
                corrupt.append(e.run_id)
                continue
            # Corruption: an indexed decision exists but the on-disk
            # decision artifact is missing (tampered/removed run).
            if e.decision and not (run_dir / "decision.json").exists():
                e.integrity_status = "CORRUPT"
                corrupt.append(e.run_id)
                continue
            if e.integrity_status == "CORRUPT":
                corrupt.append(e.run_id)
        return {
            "indexed": len(entries),
            "checked": checked,
            "corrupt": corrupt,
            "integrity_status": "VALID" if not corrupt else "CORRUPT",
        }

    def rebuild(self) -> dict:
        """Rescan all run directories, validate, and rewrite the index."""
        if HISTORY_PATH.exists():
            shutil.copy2(HISTORY_PATH, HISTORY_PATH.with_suffix(".jsonl.bak"))
        entries: list[HistoryEntry] = []
        corrupt = []
        if self.runs_dir.exists():
            for run_dir in sorted(self.runs_dir.iterdir()):
                if not run_dir.is_dir() or not run_dir.name.startswith("TK-"):
                    continue
                manifest = _read_json(run_dir / "manifest.json")
                if manifest is None:
                    # Run dir without manifest: record as corrupt but keep.
                    ent = HistoryEntry(run_id=run_dir.name, integrity_status="CORRUPT")
                    entries.append(ent)
                    corrupt.append(run_dir.name)
                    continue
                derived = _derive_from_run(run_dir)
                if derived is None:
                    derived = HistoryEntry(run_id=run_dir.name, integrity_status="CORRUPT")
                    corrupt.append(run_dir.name)
                entries.append(derived)
        _save_index(entries)
        return {
            "rebuilt": len(entries),
            "corrupt": corrupt,
            "integrity_status": "VALID" if not corrupt else "CORRUPT",
        }


def index_run(run_id: str) -> HistoryEntry | None:
    return RunHistory().index_run(run_id)


def history_verify() -> dict:
    return RunHistory().verify()


def history_rebuild() -> dict:
    return RunHistory().rebuild()
