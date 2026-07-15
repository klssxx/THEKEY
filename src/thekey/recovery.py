"""Recovery protocol (orchestrator-controlled mode, not a normal run state).

Triggered on: truncated output, invalid YAML, stale binding, uncertain command
result, partial write, state/evidence contradiction, unrecorded file change,
invalid transition, or state hash mismatch (section 24).

During recovery NO new productive writes happen. We load the last valid state +
transition, re-run only idempotent read checks, reconcile deterministically,
and return one of the four recovery outcomes.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path

from .config import RUNS_DIR
from .errors import RecoveryBlockedError, TheKeyError
from .state_machine import STATE_FILE, TRANSITIONS_FILE, StateMachine
from .workspaces import WorkspaceManager


@dataclass
class RecoveryResult:
    outcome: str  # RECOVERED_NO_CHANGE | RECOVERED_ACTION_CONFIRMED |
    # RECOVERED_ACTION_NOT_APPLIED | RECOVERY_BLOCKED_AMBIGUOUS
    detail: str
    evidence: dict

    def to_dict(self) -> dict:
        return {
            "outcome": self.outcome,
            "detail": self.detail,
            "evidence": self.evidence,
        }


class RecoveryController:
    def __init__(self, state_machine: StateMachine | None = None):
        self.sm = state_machine or StateMachine()
        self.wm = WorkspaceManager()

    def last_valid_transition(self) -> dict | None:
        if not TRANSITIONS_FILE.exists():
            return None
        lines = [l for l in TRANSITIONS_FILE.read_text(encoding="utf-8").splitlines() if l.strip()]
        if not lines:
            return None
        return json.loads(lines[-1])

    def reconcile(self, run_id: str, suspected_action: str | None = None) -> RecoveryResult:
        """Deterministic idempotent reconciliation. Only read checks."""
        # Load last valid state.
        current = self.sm.load()
        last_tx = self.last_valid_transition()

        # Inspect command-result files in the run evidence/logs dir.
        run_dir = RUNS_DIR / run_id
        cmd_results = {}
        logs_dir = run_dir / "logs"
        if logs_dir.exists():
            for p in sorted(logs_dir.glob("*.json")):
                try:
                    cmd_results[p.name] = json.loads(p.read_text(encoding="utf-8"))
                except Exception:
                    cmd_results[p.name] = {"unreadable": True}

        # Inspect workspace hash of the produced file (if any).
        ws = self.wm.root / run_id
        workspace_files = {}
        if ws.exists():
            for p in ws.rglob("*"):
                if p.is_file():
                    try:
                        workspace_files[str(p.relative_to(ws))] = hashlib.sha256(
                            p.read_bytes()
                        ).hexdigest()
                    except OSError:
                        pass

        evidence = {
            "state_version": current.state_version,
            "state_hash": current.current_state_hash,
            "last_transition": last_tx,
            "command_results": cmd_results,
            "workspace_file_hashes": workspace_files,
        }

        # Decide outcome deterministically.
        # If state contradicts evidence (e.g. state claims IMPLEMENTED but no
        # workspace change recorded), block as ambiguous.
        if current.run_state in ("IMPLEMENTED", "TESTED", "RELEASE_ELIGIBLE"):
            if not workspace_files:
                return RecoveryResult(
                    "RECOVERY_BLOCKED_AMBIGUOUS",
                    "State advanced but no workspace artifacts found; cannot reconcile safely.",
                    evidence,
                )

        # If a suspected action exists but no command result backs it, mark
        # not applied (safe default: do not repeat non-idempotent writes).
        if suspected_action and suspected_action not in cmd_results:
            return RecoveryResult(
                "RECOVERED_ACTION_NOT_APPLIED",
                f"Suspected action {suspected_action!r} has no recorded result; treated as not applied.",
                evidence,
            )

        if not cmd_results and not workspace_files:
            return RecoveryResult(
                "RECOVERED_NO_CHANGE",
                "No unrecorded changes detected; state intact.",
                evidence,
            )

        # Default: confirmed no contradiction -> no change needed.
        return RecoveryResult(
            "RECOVERED_NO_CHANGE",
            "Reconciliation found no contradiction; no productive write performed.",
            evidence,
        )

    def require_blocked(self, result: RecoveryResult) -> None:
        if result.outcome == "RECOVERY_BLOCKED_AMBIGUOUS":
            raise RecoveryBlockedError(result.detail)
