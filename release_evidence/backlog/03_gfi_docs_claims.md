---
title: "CI validation for forbidden language and disallowed claims in normative docs"
type: good-first-issue
labels: [good first issue, documentation, ci, security]
---

## Context
The project forbids the term "auto-approval" and any claim of OS-level
sandboxing, total security, tamper-proofing, invulnerability, risk-free
operation, or impossibility of manipulation. These must never reappear in
normative docs.

## Problem
Today `scripts/ci/docs_claims.py` does a basic scan, but it can be fooled by
line-wrapped negations and does not cover all phrasing variants.

## Scope
- Harden `scripts/ci/docs_claims.py` to skip negated contexts reliably
  (multi-line negation window, not just per-line).
- Add coverage for "auto-approval" / "auto-approve" / "autoaprobación" in ES
  and EN.
- Treat the check as a required CI gate with clear file:line output.

## Out of scope
- Rewriting the docs.
- Enforcing claims in code comments (docs only, per contract).

## Acceptance criteria
- `scripts/ci/docs_claims.py` exits 0 on current docs.
- A seeded affirmative claim (e.g. "THEKEY is a tamper-proof sandbox")
  produces a non-zero exit with the file:line.
- CI job `docs-gates` runs it on every PR.

## Validation notes
- Run locally: `python scripts/ci/docs_claims.py` → exit 0.
- Negative test: add a forbidden phrase to a scratch doc, confirm exit 1,
  then remove it.
