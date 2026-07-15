# THEKEY Core — Push Manifest (generated locally, pre-approval)

Generated: 2026-07-15 (updated after NPSC hardening Fase A/B)
Repo working copy: E:\PROYECTS\GovernedOSS
Branch to publish: feature/universal-python-missions-0.2  ->  GitHub `main`
Push status: **NOT EXECUTED** (awaiting operator approval + gate 7).

## Commits that would be pushed

| Hash | Subject | Files | Notes |
|------|---------|-------|-------|
| b7b6c32 | THEKEY Core Governed Run MVP 0.1.0 | ~60 | baseline, 63-test suite |
| 3cc3950 | 0.2.0: autonomous governed run + contributor-ready surface | +38 | auto-approval, event store, review_token, NPSC adapter, MiMo profile, schemas, 9+4 tests |
| cc31b7b | chore: stop tracking runtime state (.thekey/) — push hygiene | 1 | removes runtime state from tracked tree |
| ebb0770 | docs: add GitHub push plan + manifest (local prep, no push) | +2 | PUSH_PLAN.md, PUSH_MANIFEST.md |

## Integrity hashes (publish tree HEAD = ebb0770)

- `git rev-parse HEAD` = ebb0770
- Tracked file count (excl. .thekey/, runs/, workspaces/, development-audit/) = 131
- Frozen baseline (development-audit/automation-baseline/, gitignored):
  - file_hashes.sha256: 107 source+doc+test files
  - pytest_count.txt: "102 passed"
  - git_head.txt: b7b6c32 (original 0.1.0 anchor; working tree is ebb0770)

## Test results on the exact publish tree

- `python -m pytest -q` => **102 passed** (89 baseline + 9 automation-surface + 4 adversarial)
- `python -m compileall src` => OK
- `python -m thekey demo` => RELEASE_ELIGIBLE, exit 0, 4/4 gates, review_token emitted
- `python -m thekey-mimo` => exit 0 (autonomous)
- `python -m thekey history verify` => integrity_status VALID
- `python -m thekey evidence verify` => evidence_ok true

## NPSC hardening (Fase A/B) — evidence, NOT part of THEKEY Core push tree

Verified by coordinator (not assumed):
- B1 contract aligned (output_contract == recommended_output_contract, 6 targets) — PASS
- B2 --strict blocking (exit 2, 0 files) — PASS
- B3 no leak (redacted_preview/hash_only, 0 leaks in hybrid_markdown) — PASS
- NPSC core tests: 91 passed / 3 failed (pre-existing fixture) / 1 skipped / 4 subtests
- Deliverables on disk: GPT_HARDENING/02_NPSC_HARDENING_DIFF.patch, GPT_HARDENING/NPSC_HARDENED/, GPT_HARDENING/01_HARDENING_REPORT.md
- Fase B: NPSC_HARDENED output consumed by THEKEY adapter read-only, schema-valid, read_only=True.
- Original NPSC protected path UNTOUCHED. Not integrated into THEKEY Core.

## Planned push content (gates 4–5 satisfied on this tree)

- 131 source/governance/test/doc/fixture files
- NO runtime state (.thekey/, runs/, workspaces/ gitignored)
- NO secrets / tokens / private paths in tracked tree
- License: MIT; CI: .github/workflows/tests.yml runs pytest

## Blocker

Push is frozen until:
1. [DONE] GPT_HARDENING verified (B1/B2/B3 + deliverables) — coordinator-verified
2. [DONE] NPSC diff + package validated via read-only adapter (Fase B)
3. [DONE] --strict blocks; redacted safe; contract aligned
4. [DONE] Tests+demo+regression on exact publish tree (102 passed)
5. [DONE] No secrets/artifacts in tree
6. [DONE] Manifest generated (this file)
7. [PENDING] Operator explicit approval to run the push.

Nothing has been pushed. The protected original NPSC is unmodified.
