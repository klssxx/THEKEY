# Final adversarial audit — Phase B RBAC v2

Audit date: 2026-07-19. Audited commit:
`c0410feaf869e0ac08c9e637b70e30ebac8085c8`.

## Result

`PASS` for the bounded Phase-B physical-authorization scope. This result does
not claim `FULL_CHECKMATE`, operating-system isolation, external attestation,
or production authorization from the local Judge Mode grant.

## Security properties checked

- Strict Pydantic contracts reject missing, extra, malformed, or mismatched
  action-context and receipt fields.
- CHECKMATE review and sovereign authorization receipts bind the same run,
  transaction, plan SHA-256, authorization, policy version, and policy-bundle
  hash.
- Only `Role.EXECUTOR` reaches the policy backend or physical handler lookup.
- `SYSTEM`, absent/invalid roles, CHECKMATE `PENDING`, `DEFER`, or `FAIL`, policy
  exceptions, malformed policy responses, scope mismatches, and ALLOW without
  a decision ID fail closed.
- The action must be present in the explicit sovereign scope.
- The repository-visible demo grant accepts only the canonical source or its
  exact ephemeral Judge Mode copy, requires the companion-test hash and
  isolated output, and sets `production_reuse=false`.
- All five live physical dispatch callers pass the persisted context
  explicitly; no production bypass was added.
- Judge Mode proves one authorized handler, zero handlers for the adversarial
  denial, unchanged denied-workspace and source hashes, four passing gates,
  bound receipts, and `RELEASE_ELIGIBLE`.

## Verification record

The Phase-B checkpoint recorded:

- focused RBAC/roles/verifier suite: `47 passed`;
- full workspace suite: `148 passed, 1 skipped`;
- clean-clone reproduction: `148 passed, 1 skipped`;
- external Phase-B pack: `44 passed, 1 skipped`, with 100% guard coverage;
- modified-Python Ruff check, rollback, secret scan, and Judge Mode: `PASS`.

The filesystem-dependent skip and superseded temporary-fixture setup errors are
documented in the regression record; they were not assertion failures.

The recovered submission-package checkpoint was then revalidated with `151
passed, 1 skipped`, all three documentation gates, the entropy scan, Ruff,
compileall, a live Judge Mode run, and the independent evidence verifier. All
completed successfully; the same filesystem-dependent symlink test was skipped.

## Residual boundaries

- Workflow isolation is not a process or operating-system sandbox.
- The local grant is not a cryptographic human signature.
- SHA-256 is tamper-evident within the implemented chain, not external
  attestation.
- Secret scanning and the action registry are deliberately bounded.
- The pre-public owner statement is `CLAIM_RECORDED`; historical records not
  imported are `PENDING_EVIDENCE_IMPORT`. The Phase-B manifest retains its
  legacy `PROVENANCE_UNRESOLVED` canonical-source flag.
- `FULL_CHECKMATE=false` and `MACRO_PACK_2=NOT_STARTED`.

## Evidence

- [Final manifest](../../evidence/phase-b/RBAC-01-v2/FINAL_MANIFEST.json)
- [Regression](../../evidence/phase-b/RBAC-01-v2/REGRESSION.md)
- [Security gate](../../evidence/phase-b/RBAC-01-v2/GATE_SEC_01.json)
- [Caller analysis](../../evidence/phase-b/RBAC-01-v2/CALLER_ANALYSIS.json)
- [Secret scan](../../evidence/phase-b/RBAC-01-v2/SECRET_SCAN.md)
- [Rollback bundle](../../evidence/phase-b/RBAC-01-v2/ROLLBACK_BUNDLE.json)
