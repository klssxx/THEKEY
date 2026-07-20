# Status

| Item | Status |
|------|--------|
| Release version | 0.2.0 |
| Canonical demo | PASS (RELEASE_ELIGIBLE) |
| Blocked demos | PASS (invalid_policy / failed_gate / tampered_evidence / missing_input) |
| Tests | 170 passed, 1 skipped (symlink unsupported on test filesystem) |
| Original demo | Intentionally broken, unchanged |
| Historical THEKEY path | Read-only, unmodified |
| Evidence verification | Enforced (tamper detected) |
| CLI | Implemented with stable exit codes |
| Application inspection | PASS (read-only profile + CHECKMATE + policy) |
| Application diagnostics | PASS (compile/pytest findings, redacted output) |
| Bounded repair | PASS (isolated gates, consent, backup, reverify, rollback) |
| Frozen Windows repair E2E | PASS (`REPAIRED_AND_VERIFIED`) |
| Portable package manifest | PASS (123/123 file hashes) |

This file is a human-readable snapshot; authoritative state is in
`.thekey/state.json` and per-run artifacts under `runs/`.
