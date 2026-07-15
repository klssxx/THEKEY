"""Run Coordinator: the deterministic control plane that executes one complete
governed run lifecycle.

Flow (section 15):
  SUBMITTED -> BASELINED -> ANALYZED -> PLAN_PROPOSED -> PLAN_APPROVED ->
  IMPLEMENTED -> TESTED -> RELEASE_ELIGIBLE

The coordinator validates every path, permission, action, state, and output,
and changes authoritative state only via StateMachine.apply_transition. HY3 is
optional; in the MVP the four roles run deterministically. The coordinator can
also drive a "blocked" scenario (invalid policy / failed gate / tampered
evidence / missing input).
"""

from __future__ import annotations

import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

from .config import (
    DEFAULT_POLICY_FILE,
    DEMO_APP_SOURCE,
    RUNS_DIR,
    WORKSPACES_DIR,
)
from .decisions import ReleaseDecision
from .errors import (
    GateFailureError,
    InvalidEvidenceError,
    InvalidPolicyError,
    TheKeyError,
)
from .evidence import EvidenceManager, sha256_file
from .gates import GateResult
from .history import index_run as _history_index_run
from .event_store import EventStore
from .policies import Policy, PolicyEngine
from .roles.approver import Approval, Approver
from .roles.executor import Executor
from .roles.planner import Plan, build_demo_plan
from .roles.verifier import Verifier
from .runs import Run, RunManager, RunRequest
from .state_machine import StateMachine, is_legal


def _utcnow() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


class RunCoordinator:
    """Executes a single governed run end to end (deterministic MVP)."""

    def __init__(
        self,
        run: Run | None = None,
        policy: Policy | None = None,
        state_machine: StateMachine | None = None,
        runs_dir: Path = RUNS_DIR,
        workspaces_dir: Path = WORKSPACES_DIR,
    ):
        self.runs = RunManager(runs_dir)
        self.run = run or self.runs.create_run(
            RunRequest(title="Untitled governed run")
        )
        # Authoritative state is repo-level; for a fresh run we reset it to the
        # initial SUBMITTED binding so each run starts deterministically.
        self.sm = state_machine or StateMachine()
        if run is None:
            self.sm.reset_to_submitted(self.run.run_id)
        self.policy_engine = PolicyEngine()
        self.policy = policy or self.policy_engine.load_default()
        self.evidence = EvidenceManager(self.run.evidence_dir)
        self.approver = Approver()
        self._plan: Plan | None = None
        # Append-only audit event store (SQLite, hash-chained).
        from .config import THEKEY_DIR
        self._events = EventStore(THEKEY_DIR / "events.db")

    def close(self) -> None:
        try:
            self._events.close()
        except Exception:
            pass
    def _snapshot_policy(self) -> None:
        self.policy_engine.snapshot(self.policy, self.run.policy_snapshot_dir)

    def _write_artifact(self, name: str, payload: dict) -> Path:
        return self.run.write_json(name, payload)

    def _record_evidence(self, evidence_id: str, kind: str, producer: str,
                         artifact_path: str, summary: str) -> None:
        from .evidence import EvidenceRecord

        path = self.run.dir / artifact_path
        h = sha256_file(path) if Path(path).exists() else ""
        rec = EvidenceRecord(
            evidence_id=evidence_id,
            kind=kind,
            producer=producer,
            artifact_path=artifact_path,
            artifact_hash=h,
            summary=summary,
            verified=False,
        )
        self.evidence.record(rec)

    def _transition(self, to_state: str, role: str, reason: str,
                    related_evidence: list[str] | None = None,
                    extra: dict | None = None) -> None:
        from_state = self.sm.load().run_state
        self.sm.apply_transition(
            to_state,
            run_id=self.run.run_id,
            role=role,
            reason=reason,
            related_evidence=related_evidence,
            extra=extra,
        )
        # Append-only audit event (hash-chained SQLite). Best-effort: a failure
        # here must never break the deterministic transition above.
        try:
            self._events.append(
                "transition", self.run.run_id, role,
                {
                    "from": from_state,
                    "to": to_state,
                    "reason": reason,
                    "related_evidence": related_evidence or [],
                },
            )
        except Exception:
            pass

    def _index(self) -> None:
        """Index the current run in the derived run-history (section 40)."""
        try:
            _history_index_run(self.run.run_id)
        except Exception:
            # History indexing is best-effort and never blocks the run.
            pass

    # ---- lifecycle steps ----------------------------------------------
    def create(self, title: str, description: str = "") -> "RunCoordinator":
        self._write_artifact(
            "request.json",
            {
                "created_at": _utcnow(),
                "title": title,
                "description": description,
                "source_inputs": [{"input_id": "APP_SOURCE", "path": str(DEMO_APP_SOURCE)}],
            },
        )
        if self.sm.load().run_state == "SUBMITTED":
            self._transition("BASELINED", "orchestrator", "Run created and baselined")
        return self

    def baseline(self) -> dict:
        """Capture baseline: hash the original demo source and store it."""
        original_hash = sha256_file(DEMO_APP_SOURCE)
        payload = {
            "baseline_at": _utcnow(),
            "original_source": str(DEMO_APP_SOURCE),
            "original_hash": original_hash,
        }
        self._write_artifact("baseline.json", payload)
        self._record_evidence(
            "EVID-BASELINE", "state-file", "orchestrator",
            "baseline.json", f"Original demo hash {original_hash[:12]}",
        )
        self._transition("ANALYZED", "orchestrator", "Baseline captured", ["EVID-BASELINE"])
        return payload

    def plan(self) -> Plan:
        """Deterministic planner detects the defect and proposes one op."""
        self._plan = build_demo_plan(self.run.run_id)
        self._write_artifact("plan.json", self._plan.to_dict())
        plan_hash = self._plan.compute_hash()
        self.sm.update_fields(
            approved_plan_hash=plan_hash,
            last_completed_action="PLAN_PROPOSED",
        )
        self._record_evidence(
            "EVID-PLAN", "generated-proposal", "planner",
            "plan.json", f"Plan with {len(self._plan.operations)} operation(s)",
        )
        self._transition("PLAN_PROPOSED", "planner", "Plan proposed", ["EVID-PLAN"], extra={"approved_plan_hash": plan_hash})
        self._index()
        return self._plan

    def approve_plan(self) -> Approval:
        if self._plan is None:
            raise TheKeyError("No plan to approve", code="NO_PLAN")
        self._snapshot_policy()
        # 100% AUTOMATED approval (default): the governed run does not pause
        # for human input. The approver is a deterministic local identity bound
        # to the plan hash; a human-in-the-loop mode MAY later route through
        # WAITING_FOR_HUMAN_APPROVAL, but that is not the default flow.
        approval = self.approver.approve_plan(self.run.run_id, self._plan.to_dict(), self.policy)
        self._write_artifact("approvals.json", approval.to_dict())
        self._record_evidence(
            "EVID-APPROVAL", "state-file", "approver",
            "approvals.json", f"Plan auto-approved by {approval.approved_by}",
        )
        self._transition("PLAN_APPROVED", "approver", "Plan approved (automated)", ["EVID-APPROVAL"])
        self._plan.approved = True
        self._write_artifact("plan.json", self._plan.to_dict())
        self._index()
        return approval

    def execute(self) -> dict:
        if self._plan is None or not self._plan.approved:
            raise TheKeyError("Executor requires an approved plan", code="INCOMPATIBLE_RUN_STATE")
        executor = Executor(self.run.run_id, WORKSPACES_DIR)
        prep = executor.prepare_workspace()
        results = []
        for op in self._plan.operations:
            res = executor.apply_operation(op, self._plan.to_dict())
            results.append(res)
        diff = executor.generate_diff()
        self._write_artifact("changes.diff", {"diff": diff})
        # Ensure changes.diff exists as a raw file too (for evidence/hash checks).
        (self.run.dir / "changes.diff").write_text(diff, encoding="utf-8")
        self._record_evidence(
            "EVID-EXEC", "command-result", "executor",
            "changes.diff", f"Applied {len(results)} operation(s) in workspace",
        )
        self._transition("IMPLEMENTED", "executor", "Plan executed in workspace", ["EVID-EXEC"])
        self._index()
        return {"prep": prep, "results": results, "diff": diff}

    def verify(self) -> list[GateResult]:
        verifier = Verifier(self.run.run_id, self.policy)
        results = verifier.run_gates()
        gates_json = verifier.gates_json(results)
        self._write_artifact("gates.json", gates_json)
        self._record_evidence(
            "EVID-GATES", "command-result", "verifier",
            "gates.json", f"{sum(r.passed for r in results)}/{len(results)} gates passed",
        )
        self._transition("TESTED", "verifier", "Gates executed", ["EVID-GATES"])
        self._index()
        return results

    def decide(self) -> ReleaseDecision:
        # Tamper check: compare principal artifacts against their recorded
        # evidence hashes. A mismatch means evidence was altered after it was
        # produced -> block deterministically (section 16 kernel rule 14).
        tampered = self._detect_tampered_evidence()
        if tampered:
            decision = ReleaseDecision(
                run_id=self.run.run_id,
                decision="BLOCKED",
                policy_id=self.policy.policy_id,
                reason=f"Tampered evidence detected: {tampered}",
                gates=[],
                evidence_missing=[],
                approver_identity="n/a",
            )
            self._write_artifact("decision.json", decision.to_dict())
            self._transition("BLOCKED", "approver", f"Tampered evidence: {tampered}")
            return decision
        verifier = Verifier(self.run.run_id, self.policy)
        gates = verifier.run_gates()
        # Write the other principal artifacts so required-evidence check can pass.
        # (decision.json is written after the decision is computed, then hashed.)
        self._write_artifact("gates.json", verifier.gates_json(gates))
        # Compute hashes of everything EXCEPT decision.json + artifact-hashes.json.
        self._write_artifact_hashes()
        # Required evidence: the artifact files must exist.
        decision = self.approver.decide(
            self.run.run_id, gates, self.run.dir, self.policy,
            approved_plan_hash=self.sm.load().approved_plan_hash,
        )
        self._write_artifact("decision.json", decision.to_dict())
        # Recompute hashes to include decision.json, then assert all present.
        self._write_artifact_hashes()
        self._record_evidence(
            "EVID-DECISION", "state-file", "approver",
            "decision.json", f"Decision: {decision.decision}",
        )
        target = "RELEASE_ELIGIBLE" if decision.decision == "RELEASE_ELIGIBLE" else "BLOCKED"
        self._transition(
            target,
            "approver",
            f"Release decision: {decision.decision}",
            ["EVID-DECISION"],
        )
        self._index()
        return decision

    def _detect_tampered_evidence(self) -> list[str]:
        """Verify on-disk sealed artifacts match the hashes recorded in their
        evidence records. Only 'sealed' artifacts (never rewritten after
        recording: changes.diff, baseline.json, approvals.json) are checked, so
        that legitimately rewritten artifacts (plan.json, gates.json) do not
        produce false positives. Returns the list of tampered artifacts."""
        sealed = {"changes.diff", "baseline.json", "approvals.json"}
        tampered = []
        for ev_file in self.run.evidence_dir.glob("*.json"):
            try:
                rec = json.loads(ev_file.read_text(encoding="utf-8"))
            except Exception:
                continue
            artifact = rec.get("artifact_path")
            recorded = rec.get("artifact_hash")
            if not artifact or not recorded:
                continue
            if artifact not in sealed:
                continue
            p = self.run.dir / artifact
            if p.exists() and sha256_file(p) != recorded:
                tampered.append(artifact)
        return tampered

    def _write_artifact_hashes(self) -> dict:
        names = ["plan.json", "approvals.json", "changes.diff", "gates.json",
                 "decision.json", "baseline.json", "manifest.json", "request.json"]
        hashes = {}
        for n in names:
            p = self.run.dir / n
            if p.exists():
                hashes[n] = sha256_file(p)
        self._write_artifact("artifact-hashes.json", {
            "generated_at": _utcnow(),
            "hashes": hashes,
        })
        return hashes

    # ---- blocked scenarios --------------------------------------------
    def run_blocked(self, mode: str) -> ReleaseDecision:
        """Run a deliberately blocked scenario.

        modes:
          'invalid_policy'  - load a policy that fails schema validation.
          'failed_gate'     - execute with a broken workspace so a gate fails.
          'tampered_evidence' - tamper with a written artifact before deciding.
          'missing_input'   - plan against a missing source input.
        """
        self.create("Blocked scenario", f"mode={mode}")
        if mode == "invalid_policy":
            bad = {
                "policy_id": "broken",
                # missing required fields on purpose
                "max_files_changed": -1,
            }
            self._write_artifact("policy-broken.json", bad)
            try:
                self.policy_engine.validate_dict(bad)
                raise TheKeyError("Policy unexpectedly valid", code="INVALID_POLICY")
            except InvalidPolicyError as exc:
                # Deterministic: stop, move to BLOCKED, non-zero exit.
                self._transition("BLOCKED", "orchestrator", f"Invalid policy: {exc.detail}")
                decision = ReleaseDecision(
                    run_id=self.run.run_id,
                    decision="BLOCKED",
                    policy_id="broken",
                    reason=f"Invalid policy: {exc.detail}",
                    gates=[],
                    evidence_missing=[],
                    approver_identity="n/a",
                )
                self._write_artifact("decision.json", decision.to_dict())
                return decision
        if mode == "missing_input":
            # Remove the source input reference and force planner to fail.
            broken_source = DEMO_APP_SOURCE.with_name("__does_not_exist__.py")
            try:
                build_demo_plan(self.run.run_id, broken_source)
            except TheKeyError as exc:
                self._transition("BLOCKED", "orchestrator", f"Missing input: {exc.detail}")
                decision = ReleaseDecision(
                    run_id=self.run.run_id, decision="BLOCKED",
                    policy_id=self.policy.policy_id,
                    reason=f"Missing required input: {exc.detail}",
                    gates=[], evidence_missing=["APP_SOURCE"],
                    approver_identity="n/a",
                )
                self._write_artifact("decision.json", decision.to_dict())
                return decision
        if mode == "failed_gate":
            # Follow the real lifecycle but execute a PLAN THAT APPLIES NO FIX,
            # so the workspace copy stays defective and the UNIT_TESTS gate fails
            # deterministically (a genuine mandatory-gate failure).
            self.baseline()
            self.plan()
            self.approve_plan()
            # Neutralize the fix so the workspace remains defective.
            self._plan.operations = []
            self._write_artifact("plan.json", self._plan.to_dict())
            self.execute()
            results = self.verify()
            decision = self.decide()
            return decision
        if mode == "tampered_evidence":
            self.baseline()
            self.plan()
            self.approve_plan()
            self.execute()
            # Tamper with a written artifact after execution.
            (self.run.dir / "changes.diff").write_text("TAMPERED", encoding="utf-8")
            results = self.verify()
            decision = self.decide()
            return decision
        raise TheKeyError(f"Unknown blocked mode: {mode}", code="UNKNOWN_MODE")

    def summary(self) -> dict:
        state = self.sm.load()
        return {
            "run_id": self.run.run_id,
            "run_path": str(self.run.dir),
            "workspace": str(WORKSPACES_DIR / self.run.run_id),
            "state": state.run_state,
            "state_version": state.state_version,
            "policy_id": self.policy.policy_id,
            "evidence_dir": str(self.run.evidence_dir),
            "decision_path": str(self.run.dir / "decision.json"),
        }
