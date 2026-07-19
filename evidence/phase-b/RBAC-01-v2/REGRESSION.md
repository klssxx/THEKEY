# Regression — FASE-B-v2

Generated at `2026-07-19T14:36:16.059Z`.

| Scope | Result |
|---|---|
| Baseline canonical suite before implementation | `113 passed, 1 skipped` |
| Final focused RBAC/roles/verifier suite | `47 passed in 5.45s` |
| Final workspace suite | `148 passed, 1 skipped in 30.50s` |
| Clean clone, deep path with spaces | `149 passed in 30.25s` |
| Clean clone, short path with spaces | `148 passed, 1 skipped in 30.95s` |
| External Phase-B pack | `44 passed, 1 skipped`, 100% guard coverage |
| Ruff on every modified Python file | PASS |
| Compileall | PASS |

The skip is the existing Windows/filesystem-dependent symlink test. A separate
clean clone supported the symlink and therefore reported 149 passes.

Three earlier runs reported fixture setup errors because their temporary roots
were removed by the suite or inaccessible to the sandbox identity. They
produced no assertion failures and were superseded by the valid runs above.
