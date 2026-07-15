---
title: "Automated ES/EN README parity gate for version, commands, and essential links"
type: good-first-issue
labels: [good first issue, documentation, ci, windows]
---

## Context
THEKEY ships normative docs in Spanish (README.md, THREAT_MODEL.md,
CONTRIBUTING.md) and English (README.en.md, THREAT_MODEL.en.md,
CONTRIBUTING.en.md). A divergence in version, commands, or essential links
would be a publication blocker.

## Problem
Today a manual review is needed to keep ES/EN in sync. The parity gate
(`scripts/ci/parity_gate.py`) exists but only covers a few invariants and is
not yet wired as a required check with clear failure output.

## Scope
- Extend `scripts/ci/parity_gate.py` to assert: project version 0.2.0,
  Quick Start commands (git clone / cd THEKEY / demo.ps1), main demo command
  (`python -m thekey demo`), guarantee claims (workflow isolation present,
  no OS-sandbox claim), deterministic policy authorization present, and
  essential links to related docs.
- Emit a readable PASS/FAIL report (already partially done).
- Document the gate in CONTRIBUTING.

## Out of scope
- Rewriting the docs.
- Adding new gates beyond ES/EN parity.

## Acceptance criteria
- `scripts/ci/parity_gate.py` exits 0 on the current docs and non-zero on a
  seeded divergence (add a temporary test fixture proving it fails).
- CI job `docs-gates` runs it on every PR.
- A short README/CONTRIBUTING note explains the parity requirement.

## Validation notes
- Run locally: `python scripts/ci/parity_gate.py` → exit 0.
- Negative test: temporarily edit README.en.md to drop the demo command,
  confirm exit 1, then revert.
