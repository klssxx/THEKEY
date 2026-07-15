"""Forbidden-language and disallowed-claim gate for THEKEY normative docs.

Scans README*, THREAT_MODEL*, CONTRIBUTING*, SECURITY.md for:
  - the forbidden term "auto-approval" / "auto-approve" / "autoaprobaci"
  - ABSOLUTE security claims (tamper-proof, invulnerable, risk-free,
    impossible to manipulate, total security, full OS sandbox)

Negated contexts are NOT flagged. A line is only a violation when it asserts
the claim positively (no nearby negation token such as "no", "not", "never",
"sin", "does not", "isn't", "without").

Exit code 0 = PASS, 1 = FAIL. Prints findings with file:line.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

TARGETS = [
    "README.md", "README.en.md",
    "THREAT_MODEL.md", "THREAT_MODEL.en.md",
    "CONTRIBUTING.md", "CONTRIBUTING.en.md",
    "SECURITY.md",
]

NEGATION = re.compile(
    r"\b(no|not|never|sin|without|does not|doesn't|isn't|aren't|is not|are not|"
    r"no proporciona|no promete|no garantiza|no afirma|no es|no provee|ni)\b",
    re.IGNORECASE,
)

FORBIDDEN_TERMS = [
    re.compile(r"auto[- ]?approval|auto[- ]?approve|autoaprobaci", re.IGNORECASE),
]

FORBIDDEN_CLAIMS = [
    re.compile(r"a prueba de manipulaci[oó]n|tamper[- ]proof", re.IGNORECASE),
    re.compile(r"invulnerab", re.IGNORECASE),
    re.compile(r"sin riesgo|risk[- ]free", re.IGNORECASE),
    re.compile(r"imposible de manipular|impossible to manipulate", re.IGNORECASE),
    re.compile(r"seguridad total|total security|full security", re.IGNORECASE),
    re.compile(r"sandbox(ing)? (a nivel de |at the level of |de )?sistema operativo|os[- ]level sandbox|operating[- ]system sandbox", re.IGNORECASE),
]


def line_violates(rx: re.Pattern, line: str) -> bool:
    if not rx.search(line):
        return False
    # Allow if the whole line is a negation of the claim.
    return not NEGATION.search(line)


def main() -> int:
    problems: list[str] = []
    for name in TARGETS:
        p = ROOT / name
        if not p.exists():
            continue
        for i, line in enumerate(p.read_text(encoding="utf-8").splitlines(), 1):
            for rx in FORBIDDEN_TERMS:
                if line_violates(rx, line):
                    problems.append(f"{name}:{i}: forbidden term '{rx.pattern}'")
            for rx in FORBIDDEN_CLAIMS:
                if line_violates(rx, line):
                    problems.append(f"{name}:{i}: disallowed claim '{rx.pattern}'")
    print("=" * 60)
    print("THEKEY DOCS CLAIMS GATE")
    print("=" * 60)
    if problems:
        print("RESULT: FAIL")
        for pr in problems:
            print(f"  - {pr}")
        return 1
    print("RESULT: PASS")
    print("No forbidden 'auto-approval' term and no affirmative absolute/sandbox claims.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
