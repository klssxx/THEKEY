"""Governed state machine and authoritative atomic state.

The state machine is the single source of truth for *legal* transitions
between run states. The orchestrator consults it before applying any
transition request (whether from a deterministic role or the HY3 operator).

Authoritative state lives in .thekey/state.json at the repo root and is updated
atomically: write tmp -> validate -> canonicalize -> sha256 -> rename ->
preserve previous -> append event. No model output may update state directly.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from .config import THEKEY_DIR
from .errors import (
    InvalidTransitionError,
    TheKeyError,
)
from .io_atomic import atomic_write_text

STATE_FILE = THEKEY_DIR / "state.json"
STATE_PREV_FILE = THEKEY_DIR / "state.previous.json"
TRANSITIONS_FILE = THEKEY_DIR / "state-transitions.jsonl"
HISTORY_FILE = THEKEY_DIR / "state-history.jsonl"

# MVP run states (section 15).
STATES = {
    "SUBMITTED",
    "BASELINED",
    "ANALYZED",
    "PLAN_PROPOSED",
    "WAITING_FOR_HUMAN_APPROVAL",
    "PLAN_APPROVED",
    "PLAN_REJECTED",
    "IMPLEMENTED",
    "TESTED",
    "RELEASE_ELIGIBLE",
    "BLOCKED",
    "FAILED",
    "ROLLED_BACK",
}

# Legal main-flow + recovery transitions (section 15).
LEGAL_TRANSITIONS: dict[str, set[str]] = {
    "SUBMITTED": {"BASELINED", "BLOCKED", "FAILED"},
    "BASELINED": {"ANALYZED", "BLOCKED", "FAILED"},
    "ANALYZED": {"PLAN_PROPOSED", "BLOCKED", "FAILED"},
    "PLAN_PROPOSED": {"WAITING_FOR_HUMAN_APPROVAL", "PLAN_APPROVED", "BLOCKED", "FAILED"},
    "WAITING_FOR_HUMAN_APPROVAL": {"PLAN_APPROVED", "PLAN_REJECTED", "BLOCKED", "FAILED"},
    "PLAN_REJECTED": {"WAITING_FOR_HUMAN_APPROVAL", "BLOCKED", "FAILED"},
    "PLAN_APPROVED": {"IMPLEMENTED", "TESTED", "WAITING_FOR_HUMAN_APPROVAL", "BLOCKED", "FAILED"},
    "IMPLEMENTED": {"TESTED", "BLOCKED", "FAILED"},
    "TESTED": {"RELEASE_ELIGIBLE", "BLOCKED", "FAILED"},
    "RELEASE_ELIGIBLE": {"ROLLED_BACK", "BLOCKED"},
    "BLOCKED": {"ROLLED_BACK", "FAILED"},
    "FAILED": {"ROLLED_BACK"},
    "ROLLED_BACK": set(),
}


def is_legal(from_state: str, to_state: str) -> bool:
    return from_state in LEGAL_TRANSITIONS and to_state in LEGAL_TRANSITIONS[from_state]


def _utcnow() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S%z")


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


@dataclass
class StateSnapshot:
    """The complete authoritative state projection (section 13)."""

    state_version: int = 1
    previous_state_hash: str = ""
    current_state_hash: str = ""
    run_id: str = ""
    run_state: str = "SUBMITTED"
    active_phase: str = ""
    active_role: str = ""
    phase_contract_hash: str = ""
    approved_plan_hash: str = ""
    active_transaction_id: str = ""
    active_authorization_id: str = ""
    action_context_path: str = ""
    internal_mode: str = "NORMAL"  # orchestrator-only, never exposed to HY3
    last_completed_action: str = ""
    last_verified_command_result: str = ""
    blockers: list[str] = field(default_factory=list)
    next_action: str = ""
    updated_at: str = ""

    def canonical(self) -> dict:
        return {
            "state_version": self.state_version,
            "previous_state_hash": self.previous_state_hash,
            "current_state_hash": self.current_state_hash,
            "run_id": self.run_id,
            "run_state": self.run_state,
            "active_phase": self.active_phase,
            "active_role": self.active_role,
            "phase_contract_hash": self.phase_contract_hash,
            "approved_plan_hash": self.approved_plan_hash,
            "active_transaction_id": self.active_transaction_id,
            "active_authorization_id": self.active_authorization_id,
            "action_context_path": self.action_context_path,
            "internal_mode": self.internal_mode,
            "last_completed_action": self.last_completed_action,
            "last_verified_command_result": self.last_verified_command_result,
            "blockers": self.blockers,
            "next_action": self.next_action,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "StateSnapshot":
        known = {f for f in cls.__dataclass_fields__}
        filtered = {k: v for k, v in data.items() if k in known}
        return cls(**filtered)

    def recompute_hash(self) -> str:
        """Recompute current_state_hash from the canonical body (excluding the
        hash fields themselves)."""
        body = self.canonical()
        body["current_state_hash"] = ""
        body["previous_state_hash"] = ""
        text = json.dumps(body, sort_keys=True, ensure_ascii=False)
        return sha256_text(text)


class StateMachine:
    """Owns the authoritative state file and transition log.

    State is per-run: pass a ``state_file`` inside the run directory
    (improvement D) so multiple RunCoordinators can execute concurrently
    without sharing a single repo-level state file. The default keeps the
    historical repo-level location for backward compatibility with scripts
    that construct a StateMachine without arguments.
    """

    def __init__(self, state_file: Path = STATE_FILE, *, transitions_file: Path | None = None,
                 history_file: Path | None = None, prev_file: Path | None = None):
        self.state_file = Path(state_file)
        self.dir = self.state_file.parent
        self.dir.mkdir(parents=True, exist_ok=True)
        # Per-run log locations derived from the state file's directory.
        self.prev_file = Path(prev_file) if prev_file else self.dir / "state.previous.json"
        self.transitions_file = (
            Path(transitions_file)
            if transitions_file
            else self.dir / "state-transitions.jsonl"
        )
        self.history_file = (
            Path(history_file) if history_file else self.dir / "state-history.jsonl"
        )
        self._seq = 0
        self._load_seq()

    def reset_to_submitted(self, run_id: str) -> StateSnapshot:
        """Reset the authoritative state to a fresh SUBMITTED binding for a new
        run. Used by the coordinator when it creates a new run. Preserves
        previous copy within the run directory (no cross-run leakage)."""
        self._seq = 0
        snap = StateSnapshot(
            state_version=1,
            previous_state_hash="",
            run_id=run_id,
            run_state="SUBMITTED",
            active_phase="",
            active_role="",
            phase_contract_hash="",
            internal_mode="NORMAL",
            last_completed_action="",
            last_verified_command_result="",
            blockers=[],
            next_action="",
            updated_at=_utcnow(),
        )
        snap.current_state_hash = snap.recompute_hash()
        if self.state_file.exists():
            self.state_file.replace(self.prev_file)
        atomic_write_text(
            self.state_file,
            json.dumps(snap.canonical(), indent=2, sort_keys=True, ensure_ascii=False),
        )
        # Reset transition + history logs for this run's directory.
        self.transitions_file.write_text("", encoding="utf-8")
        self.history_file.write_text("", encoding="utf-8")
        return snap

    # ---- read ----------------------------------------------------------
    def load(self) -> StateSnapshot:
        if not self.state_file.exists():
            snap = StateSnapshot()
            snap.updated_at = _utcnow()
            snap.current_state_hash = snap.recompute_hash()
            return snap
        data = json.loads(self.state_file.read_text(encoding="utf-8"))
        snapshot = StateSnapshot.from_dict(data)
        if snapshot.run_state not in STATES:
            raise TheKeyError("Unknown persisted run state", code="STATE_INTEGRITY_FAILURE")
        if (
            not snapshot.current_state_hash
            or snapshot.recompute_hash() != snapshot.current_state_hash
        ):
            raise TheKeyError("Persisted state hash mismatch", code="STATE_INTEGRITY_FAILURE")
        return snapshot

    def _load_seq(self) -> None:
        if self.transitions_file.exists():
            last = None
            for line in self.transitions_file.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if not line:
                    continue
                last = json.loads(line)
            if last and "sequence" in last:
                self._seq = int(last["sequence"])

    # ---- validate ------------------------------------------------------
    def validate_transition(
        self,
        from_state: str,
        to_state: str,
        role: str,
        phase_contract_hash: str,
        current: StateSnapshot,
    ) -> None:
        if from_state != current.run_state:
            raise InvalidTransitionError(
                f"Transition source {from_state!r} != current {current.run_state!r}"
            )
        if to_state not in STATES:
            raise InvalidTransitionError(f"Unknown target state {to_state!r}")
        if not is_legal(from_state, to_state):
            raise InvalidTransitionError(
                f"Illegal transition {from_state!r} -> {to_state!r}"
            )
        # Stale contract / hash check is the caller's job via output validator;
        # here we ensure the run id binding matches.
        if current.phase_contract_hash and phase_contract_hash and \
           current.phase_contract_hash != phase_contract_hash:
            raise InvalidTransitionError("Phase contract hash mismatch")

    # ---- apply ---------------------------------------------------------
    def apply_transition(
        self,
        to_state: str,
        *,
        run_id: str,
        role: str,
        reason: str,
        actor: str = "orchestrator",
        related_evidence: list[str] | None = None,
        extra: dict | None = None,
    ) -> StateSnapshot:
        """Atomically validate, apply, and record a transition.

        Raises InvalidTransitionError if illegal. Never leaves a partial write.
        """
        current = self.load()
        from_state = current.run_state
        self.validate_transition(
            from_state, to_state, role, current.phase_contract_hash, current
        )

        # Build next snapshot.
        self._seq += 1
        prev_hash = current.current_state_hash
        next_snap = StateSnapshot(
            state_version=current.state_version + 1,
            previous_state_hash=prev_hash,
            run_id=run_id,
            run_state=to_state,
            active_phase=current.active_phase,
            active_role=current.active_role,
            phase_contract_hash=current.phase_contract_hash,
            approved_plan_hash=current.approved_plan_hash,
            active_transaction_id=current.active_transaction_id,
            active_authorization_id=current.active_authorization_id,
            action_context_path=current.action_context_path,
            internal_mode=current.internal_mode,
            last_completed_action=current.last_completed_action,
            last_verified_command_result=(extra or {}).get(
                "last_verified_command_result", current.last_verified_command_result
            ),
            blockers=(extra or {}).get("blockers", current.blockers),
            next_action=(extra or {}).get("next_action", ""),
            updated_at=_utcnow(),
        )
        if extra:
            for k in (
                "active_phase",
                "active_role",
                "phase_contract_hash",
                "last_completed_action",
                "approved_plan_hash",
                "active_transaction_id",
                "active_authorization_id",
                "action_context_path",
            ):
                if k in extra:
                    setattr(next_snap, k, extra[k])
        next_snap.current_state_hash = next_snap.recompute_hash()

        # Preserve previous copy, then atomic write.
        if self.state_file.exists():
            self.state_file.replace(self.prev_file)
        atomic_write_text(
            self.state_file,
            json.dumps(next_snap.canonical(), indent=2, sort_keys=True, ensure_ascii=False),
        )

        # Append transition record (jsonl).
        record = {
            "sequence": self._seq,
            "run_id": run_id,
            "from": from_state,
            "to": to_state,
            "actor": actor,
            "role": role,
            "timestamp": next_snap.updated_at,
            "reason": reason,
            "related_evidence": related_evidence or [],
        }
        with self.transitions_file.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(record, ensure_ascii=False) + "\n")

        # Append validated event to history.
        with self.history_file.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps({
                "kind": "transition",
                "sequence": self._seq,
                "run_id": run_id,
                "state": to_state,
                "role": role,
                "timestamp": next_snap.updated_at,
            }, ensure_ascii=False) + "\n")

        return next_snap

    def update_fields(self, **fields) -> StateSnapshot:
        """Apply non-transition field updates atomically (e.g. active_phase)."""
        current = self.load()
        for k, v in fields.items():
            if not hasattr(current, k):
                raise TheKeyError(f"Unknown state field: {k}", code="INVALID_STATE_FIELD")
            setattr(current, k, v)
        current.state_version += 1
        current.previous_state_hash = current.current_state_hash
        current.updated_at = _utcnow()
        current.current_state_hash = current.recompute_hash()
        if self.state_file.exists():
            self.state_file.replace(self.prev_file)
        atomic_write_text(
            self.state_file,
            json.dumps(current.canonical(), indent=2, sort_keys=True, ensure_ascii=False),
        )
        return current

    def recent_events(self, limit: int = 3) -> list[dict]:
        """Deterministically derive recent validated events from the history
        log (NOT from chat history)."""
        if not self.history_file.exists():
            return []
        lines = [
            json.loads(line)
            for line in self.history_file.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        return lines[-limit:]
