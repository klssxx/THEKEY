# TDD GREEN — FASE-B-v2 / RBAC-01-v2

Generated at `2026-07-19T14:36:16.059Z` from branch
`implementation/phase-b-rbac-v2`, parent commit
`3a8456416ed9ae9183840585b488cec04e9a069d`.

## Security boundary

- Initial RED: three collection errors with `ModuleNotFoundError: thekey.models`.
- Demo-grant hardening RED: `12 failed, 6 passed`; the repository grant could
  authorize two distinct sources.
- Final focused result: `47 passed in 5.45s`.
- Modified-Python Ruff result: `All checks passed!`.
- `python -m compileall -q src/thekey`: exit code `0`.

## Adversarial grant result after repair

- Canonical demo: `JUDGE_MODE_DEMO_ONLY`, one `REPLACE_EXACT_TEXT` handler.
- Distinct source: `DEMO_AUTHORIZATION_SUBJECT_MISMATCH`.
- Authorization receipt created for distinct source: `false`.
- Workspace created for distinct source: `false`.
- Handler delta for denied attempt: `0`.

The grant is bound in code and receipt to the canonical normalized-text hash,
canonical or exact ephemeral Judge Mode location, isolated output scope, and
`production_reuse=false`.
