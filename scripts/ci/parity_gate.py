"""ES/EN parity gate for THEKEY normative documentation.

Compares paired documents on NORMATIVE invariants only (not sentence-by-
sentence). Fails the build if a material divergence is detected.

Pairs and their invariants:
  README.md / README.en.md:
    version, quickstart_clone, quickstart_cd, demo_ps1, main_demo_cmd,
    workflow_isolation, no_os_sandbox_claim, deterministic_policy_auth,
    mutual_link
  THREAT_MODEL.md / THREAT_MODEL.en.md:
    version, workflow_isolation, no_os_sandbox_claim, deterministic_policy_auth,
    mutual_link (links to README / SECURITY)
  CONTRIBUTING.md / CONTRIBUTING.en.md:
    version, workflow_isolation, no_os_sandbox_claim, deterministic_policy_auth,
    mutual_link (links to README / SECURITY)

Exit code 0 = PASS, 1 = FAIL. Prints a readable report.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

VERSION = "0.2.0"

NEGATION = re.compile(
    r"\b(no|not|never|sin|without|does not|doesn't|isn't|aren't|is not|are not|"
    r"no proporciona|no promete|no garantiza|no afirma|no es|no provee)\b",
    re.IGNORECASE,
)

PAIRS = {
    ("README.md", "README.en.md"): [
        ("version", re.compile(r"0\.2\.0")),
        ("quickstart_clone", re.compile(r"git clone")),
        ("quickstart_cd", re.compile(r"cd THEKEY", re.IGNORECASE)),
        ("demo_ps1", re.compile(r"demo\.ps1")),
        ("main_demo_cmd", re.compile(r"python -m thekey demo")),
        ("workflow_isolation", re.compile(r"aislamiento de flujo de trabajo|workflow isolation", re.IGNORECASE)),
        ("deterministic_policy_auth", re.compile(r"autorizaci.n de pol.tica|deterministic policy authorization", re.IGNORECASE)),
        ("mutual_link", re.compile(r"README\.en\.md|README\.md")),
    ],
    ("THREAT_MODEL.md", "THREAT_MODEL.en.md"): [
        ("version", re.compile(r"0\.2\.0")),
        ("workflow_isolation", re.compile(r"aislamiento de flujo de trabajo|workflow isolation", re.IGNORECASE)),
        ("deterministic_policy_auth", re.compile(r"autorizaci.n de pol.tica|deterministic policy authorization", re.IGNORECASE)),
        ("mutual_link", re.compile(r"README\.md|SECURITY\.md")),
    ],
    ("CONTRIBUTING.md", "CONTRIBUTING.en.md"): [
        ("version", re.compile(r"0\.2\.0")),
        ("workflow_isolation", re.compile(r"aislamiento de flujo de trabajo|workflow isolation", re.IGNORECASE)),
        ("deterministic_policy_auth", re.compile(r"autorizaci.n de pol.tica|deterministic policy authorization", re.IGNORECASE)),
        ("mutual_link", re.compile(r"README\.md|SECURITY\.md")),
    ],
}

# Affirmative OS-sandbox claims must be ABSENT in both sides.
FORBIDDEN_SANDBOX = [
    re.compile(r"sandbox(ing)? (a nivel de|at the level of|de) sistema operativo", re.IGNORECASE),
    re.compile(r"os[- ]level sandbox", re.IGNORECASE),
    re.compile(r"operating[- ]system sandbox", re.IGNORECASE),
]


def has_positive(rx: re.Pattern, text: str) -> bool:
    for line in text.splitlines():
        if rx.search(line) and not NEGATION.search(line):
            return True
    return False


def main() -> int:
    problems: list[str] = []
    for (es_name, en_name), invariants in PAIRS.items():
        es_path = ROOT / es_name
        en_path = ROOT / en_name
        if not es_path.exists():
            problems.append(f"missing {es_name}")
            continue
        if not en_path.exists():
            problems.append(f"missing {en_name}")
            continue
        es = es_path.read_text(encoding="utf-8")
        en = en_path.read_text(encoding="utf-8")
        for label, rx in invariants:
            if not rx.search(es):
                problems.append(f"{es_name}: missing invariant '{label}'")
            if not rx.search(en):
                problems.append(f"{en_name}: missing invariant '{label}'")
        for srx in FORBIDDEN_SANDBOX:
            if has_positive(srx, es):
                problems.append(f"{es_name}: affirmative OS-sandbox claim present")
            if has_positive(srx, en):
                problems.append(f"{en_name}: affirmative OS-sandbox claim present")

    print("=" * 60)
    print("THEKEY ES/EN PARITY GATE")
    print("=" * 60)
    if problems:
        print("RESULT: FAIL")
        for p in problems:
            print(f"  - {p}")
        return 1
    print("RESULT: PASS")
    print(f"Checked {len(PAIRS)} pairs on normative invariants.")
    print("Version 0.2.0 consistent; no affirmative OS-sandbox claim; "
          "workflow isolation + deterministic policy authorization present.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
