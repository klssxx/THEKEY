# Rollback plan — THEKEY 0.2.0 publication prep

Date: 2026-07-15

## Created / modified files in this preparation

Documentation (normative):
- README.md (rewritten, ES normative)
- README.en.md (new, complete EN)
- THREAT_MODEL.md (rewritten)
- THREAT_MODEL.en.md (new)
- CONTRIBUTING.md (rewritten)
- CONTRIBUTING.en.md (new)
- SECURITY.md (rewritten)

Automation / CI:
- .github/workflows/tests.yml (demo.ps1 entry, parity + claims + secret scan)
- .github/PULL_REQUEST_TEMPLATE.md (structured)
- .github/ISSUE_TEMPLATE/config.yml, bug_report.yml, feature_request.yml, good-first-issue.yml
- scripts/demo.ps1 (new definitive demo bootstrap)
- scripts/ci/parity_gate.py (new)
- scripts/ci/docs_claims.py (new)
- scripts/ci/generate_evidence.py (new)

Core (minimal, justified):
- pyproject.toml (pytest>=7.4 added to runtime deps so `pip install -e .`
  reproduces a green demo from a clean clone)

Evidence:
- release_evidence/01..08_*.md
- release_evidence/backlog/01..08_*.md
- release_evidence/rollback_plan.md (this file)

## Revert criteria

Revert to a clean previous state if:
- Any CI gate is red after a change and cannot be fixed within the release
  scope.
- A prohibited claim (auto-approval, OS sandbox, total security) reappears.
- The demo stops reaching RELEASE_ELIGIBLE from a clean clone.

## Revert procedure (local only — no push performed)

1. Determine the last good commit:
   `git log --oneline` and identify the commit before this preparation batch.
2. Revert documentation/automation only first (do NOT touch product code
   unless proven necessary):
   `git checkout <good_commit> -- README.md README.en.md THREAT_MODEL.md THREAT_MODEL.en.md CONTRIBUTING.md CONTRIBUTING.en.md SECURITY.md .github scripts/ci scripts/demo.ps1`
3. If the pyproject change must be reverted:
   `git checkout <good_commit> -- pyproject.toml`
4. Re-run `python scripts/ci/generate_evidence.py`; confirm all gates green
   before any further step.
5. Never restructure or alter the core transactional logic to "fix" a docs/CI
   gate; fix the docs/CI or revert them.

## Notes

- The repository is kept PRIVATE until all gates are green and the owner
  approves switching public.
- Nothing in this prep performs a push, a remote creation, or a release.
