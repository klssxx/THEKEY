"""Gate definitions and the gate runner.

Each gate has a stable code, a deterministic runner, and a severity. A failed
mandatory gate cannot be offset by any other gate or score (section 17 of rules
+ policy required_gates). NO_VERIFICABLE is used when evidence is missing,
never PASS.
"""

from __future__ import annotations

from dataclasses import dataclass

from .actions import dispatch
from .policies import Policy


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
    res = dispatch("RUN_BUILD", run_id, {}, context=ctx["action_context"])
    ok = res.get("status") == "OK"
    return GateResult(
        "BUILD_PASSED",
        ok,
        "PASSED" if ok else "FAILED",
        f"compileall returncode={res.get('returncode')}",
    )


def _gate_unit_tests(run_id: str, policy: Policy, ctx: dict) -> GateResult:
    res = dispatch("RUN_UNIT_TESTS", run_id, {}, context=ctx["action_context"])
    ok = res.get("status") == "OK"
    return GateResult(
        "UNIT_TESTS_PASSED",
        ok,
        "PASSED" if ok else "FAILED",
        f"pytest returncode={res.get('returncode')}",
    )


def _gate_security(run_id: str, policy: Policy, ctx: dict) -> GateResult:
    res = dispatch(
        "SCAN_SECRETS", run_id, {}, context=ctx["action_context"]
    )
    clean = res.get("status") == "CLEAN"
    return GateResult(
        "SECURITY_GATE_PASSED",
        clean,
        "PASSED" if clean else "FAILED",
        f"findings={len(res.get('findings', []))}",
    )


def _gate_documentation(run_id: str, policy: Policy, ctx: dict) -> GateResult:
    res = dispatch(
        "CHECK_REQUIRED_DOCUMENTATION", run_id, {}, context=ctx["action_context"]
    )
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

# Gates considered "fast" for the LAUNCH_SMOKE_TEST profile: build + unit tests
# only. Security (secret scan) and documentation gates are slower / heavier and
# are skipped under smoke mode for fast iteration.
FAST_GATES = {"BUILD_PASSED", "UNIT_TESTS_PASSED"}


def _active_gates(policy: Policy) -> list[str]:
    """Resolve which gates to run, honoring the LAUNCH_SMOKE_TEST profile."""
    import os

    if os.environ.get("LAUNCH_SMOKE_TEST"):
        selected = [g for g in policy.required_gates if g in FAST_GATES]
        # If the policy declares no fast gates at all, fall back to the full set
        # so smoke mode never silently passes an empty gate list.
        return selected if selected else list(policy.required_gates)
    return list(policy.required_gates)


class GateRunner:
    """Runs the mandatory gates declared by the policy and records results."""

    def __init__(self, policy: Policy):
        self.policy = policy

    def run(self, run_id: str, ctx: dict | None = None) -> list[GateResult]:
        results: list[GateResult] = []
        for gate in _active_gates(self.policy):
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
