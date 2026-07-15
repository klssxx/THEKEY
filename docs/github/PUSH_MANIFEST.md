# THEKEY Core — Push Manifest (generated locally, pre-approval)

Generated: 2026-07-15
Repo working copy: E:\PROYECTS\GovernedOSS
Branch to publish: feature/universal-python-missions-0.2  ->  GitHub `main`
Push status: **NOT EXECUTED** (awaiting operator approval + gate 1).

## Commits that would be pushed

| Hash | Subject | Files | Notes |
|------|---------|-------|-------|
| b7b6c32 | THEKEY Core Governed Run MVP 0.1.0 | ~60 | baseline, 63-test suite |
| 3cc3950 | 0.2.0: autonomous governed run + contributor-ready surface | +38 | auto-approval, event store, review_token, NPSC adapter, MiMo profile, schemas, 9+4 tests |
| cc31b7b | chore: stop tracking runtime state (.thekey/) — push hygiene | 1 | removes runtime state from tracked tree |

## Integrity hashes (publish tree HEAD = cc31b7b)

- `git rev-parse HEAD` = cc31b7b
- Tracked file count (excl. .thekey/, runs/, workspaces/, development-audit/) = 129
- Frozen baseline (development-audit/automation-baseline/, gitignored):
  - file_hashes.sha256: 107 source+doc+test files
  - pytest_count.txt: "102 passed"
  - git_head.txt: b7b6c32 (original 0.1.0 anchor; working tree is cc31b7b)

## Test results on the exact publish tree

- `python -m pytest -q` => **102 passed** (89 baseline + 9 automation-surface + 4 adversarial)
- `python -m compileall src` => OK
- `python -m thekey demo` => RELEASE_ELIGIBLE, exit 0, 4/4 gates, review_token emitted
- `python -m thekey-mimo` => exit 0 (autonomous)
- `python -m thekey history verify` => integrity_status VALID
- `python -m thekey evidence verify` => evidence_ok true

## Planned push content (gates 4–5 satisfied on this tree)

- 129 source/governance/test/doc/fixture files
- NO runtime state (.thekey/, runs/, workspaces/ gitignored)
- NO secrets / tokens / private paths in tracked tree
- License: MIT; CI: .github/workflows/tests.yml runs pytest

## Blocker

Push is frozen until:
1. GPT_HARDENING produces verifiable output (background task complete).
2. NPSC diff + patched package validated via read-only adapter.
3. `--strict` blocks for real; `redacted_review` leaks nothing; contract aligned.
4. (this manifest + PUSH_PLAN.md committed locally)
5. **Operator explicit approval to run the push.**

Nothing has been pushed. The protected original NPSC is unmodified.
