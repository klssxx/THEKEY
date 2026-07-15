"""PLANNER role.

Deterministic in the MVP: reads declared source inputs, detects the canonical
demo defect (return a - b vs expected a + b), and produces a structured plan
with exactly one REPLACE_EXACT_TEXT operation. The planner NEVER writes product
code and NEVER approves (sections 5, 17). It may read source and request
bounded actions, but the orchestrator applies writes.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path

from ..config import DEMO_APP_SOURCE
from ..errors import TheKeyError

# Canonical demo defect signature. Anchored to the `add` function so the
# replacement is unambiguous (the `subtract` function legitimately also uses
# `return a - b`). The executor rejects ambiguous matches by design.
DEMO_DEFECT_EXPECTED = "def add(a: int, b: int) -> int:\n    return a - b"
DEMO_DEFECT_REPLACEMENT = "def add(a: int, b: int) -> int:\n    return a + b"
DEMO_EXPECTED_TEST = "add(2, 3) == 5"


@dataclass
class Plan:
    run_id: str
    title: str
    problem: str
    risk: str
    change_size: str
    operations: list[dict] = field(default_factory=list)
    approved: bool = False

    def to_dict(self) -> dict:
        return {
            "run_id": self.run_id,
            "title": self.title,
            "problem": self.problem,
            "risk": self.risk,
            "change_size": self.change_size,
            "operations": self.operations,
            "approved": self.approved,
        }

    def compute_hash(self) -> str:
        body = json.dumps(self.to_dict(), sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(body.encode("utf-8")).hexdigest()


def detect_demo_defect(source_path: Path = DEMO_APP_SOURCE) -> dict | None:
    """Return a defect report if the canonical defect is present, else None."""
    if not source_path.exists():
        raise TheKeyError(f"Demo source missing: {source_path}", code="MISSING_INPUT")
    text = source_path.read_text(encoding="utf-8")
    if DEMO_DEFECT_EXPECTED not in text:
        return None
    # The test that requires the corrected behavior lives alongside the source.
    test_path = source_path.parent / "test_calculator.py"
    test_text = test_path.read_text(encoding="utf-8") if test_path.exists() else ""
    if DEMO_EXPECTED_TEST not in test_text:
        # Defect present but no confirming test -> still detectable as defect,
        # but we require the confirming test for the canonical demo.
        return None
    line_no = text.split(DEMO_DEFECT_EXPECTED)[0].count("\n") + 1
    return {
        "target_id": "DEMO_CALCULATOR",
        "line": line_no,
        "expected": DEMO_DEFECT_EXPECTED,
        "replacement": DEMO_DEFECT_REPLACEMENT,
        "test_expectation": DEMO_EXPECTED_TEST,
    }


def build_demo_plan(run_id: str, source_path: Path = DEMO_APP_SOURCE) -> Plan:
    defect = detect_demo_defect(source_path)
    if defect is None:
        # The planner refuses to fabricate an operation on a clean source.
        raise TheKeyError(
            "Planner could not detect a defect; no plan produced.",
            code="NO_DEFECT_DETECTED",
        )
    op = {
        "op_id": "OP-REPLACE-1",
        "action_id": "REPLACE_EXACT_TEXT",
        "target_id": defect["target_id"],
        "expected": defect["expected"],
        "replacement": defect["replacement"],
        "reason": "Fix subtraction used where addition is required by the test.",
    }
    return Plan(
        run_id=run_id,
        title="Fix calculator.add to use addition",
        problem=(
            f"calculator.add implements '{defect['expected']}' at line "
            f"{defect['line']}; the test requires {defect['test_expectation']}."
        ),
        risk="LOW",
        change_size="1 line, 1 file",
        operations=[op],
    )
