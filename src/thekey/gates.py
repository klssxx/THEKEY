"""Gate definitions and the gate runner.

Each gate has a stable code, a deterministic runner, and a severity. A failed
mandatory gate cannot be offset by any other gate or score (section 17 of rules
+ policy required_gates). NO_VERIFICABLE is used when evidence is missing,
never PASS.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

from .actions import dispatch
from .config import DEFAULT_POLICY_FILE
from .errors import GateFailureError, TheKeyError
from .policies import Policy, PolicyEngine


@dataclass
class GateResult:
    gate: str
    passed: bool
    status: str  # PASSED | FAILED | NO_VERIFICABLE
    detail: str = ""

    def to_dict(self) -> dict:
        return {
            "gate": self.gate,
            "passed": self.passed,
            "status": self.status,
            "detail": self.detail,
        }


def _gate_build(run_id: str, policy: Policy, ctx: dict) -> GateResult:
    res = dispatch("RUN_BUILD", run_id, {})
    ok = res.get("status") == "OK"
    return GateResult(
        "BUILD_PASSED",
        ok,
        "PASSED" if ok else "FAILED",
        f"compileall returncode={res.get('returncode')}",
    )


def _gate_unit_tests(run_id: str, policy: Policy, ctx: dict) -> GateResult:
    res = dispatch("RUN_UNIT_TESTS", run_id, {})
    ok = res.get("status") == "OK"
    return GateResult(
        "UNIT_TESTS_PASSED",
        ok,
        "PASSED" if ok else "FAILED",
        f"pytest returncode={res.get('returncode')}",
    )


def _gate_security(run_id: str, policy: Policy, ctx: dict) -> GateResult:
    res = dispatch("SCAN_SECRETS", run_id, {"policy": policy})
    clean = res.get("status") == "CLEAN"
    return GateResult(
        "SECURITY_GATE_PASSED",
        clean,
        "PASSED" if clean else "FAILED",
        f"findings={len(res.get('findings', []))}",
    )


def _gate_documentation(run_id: str, policy: Policy, ctx: dict) -> GateResult:
    res = dispatch("CHECK_REQUIRED_DOCUMENTATION", run_id, {})
    ok = res.get("status") == "DOC_OK"
    return GateResult(
        "DOCUMENTATION_GATE_PASSED",
        ok,
        "PASSED" if ok else "FAILED",
        f"missing={res.get('missing')}",
    )


GATE_RUNNERS = {
    "BUILD_PASSED": _gate_build,
    "UNIT_TESTS_PASSED": _gate_unit_tests,
    "SECURITY_GATE_PASSED": _gate_security,
    "DOCUMENTATION_GATE_PASSED": _gate_documentation,
}


class GateRunner:
    """Runs the mandatory gates declared by the policy and records results."""

    def __init__(self, policy: Policy):
        self.policy = policy

    def run(self, run_id: str, ctx: dict | None = None) -> list[GateResult]:
        results: list[GateResult] = []
        for gate in self.policy.required_gates:
            runner = GATE_RUNNERS.get(gate)
            if runner is None:
                results.append(
                    GateResult(gate, False, "NO_VERIFICABLE", "no runner for gate")
                )
                continue
            try:
                results.append(runner(run_id, self.policy, ctx or {}))
            except Exception as exc:  # never mask a gate failure as pass
                results.append(
                    GateResult(gate, False, "FAILED", f"runner error: {exc}")
                )
        return results

    def all_passed(self, results: list[GateResult]) -> bool:
        return all(r.passed for r in results)

    def gates_json(self, results: list[GateResult]) -> dict:
        return {
            "policy_id": self.policy.policy_id,
            "required_gates": self.policy.required_gates,
            "results": [r.to_dict() for r in results],
            "all_passed": self.all_passed(results),
        }
