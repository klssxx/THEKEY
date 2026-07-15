---
title: "Improved error messages and exit codes in scripts/demo.ps1"
type: good-first-issue
labels: [good first issue, windows, documentation]
---

## Context
`scripts/demo.ps1` is the primary Quick Start entry point on Windows 11. It
must fail clearly when prerequisites are missing and must never mask the real
exit code from `python -m thekey demo`.

## Problem
Current error handling is minimal: some missing-prerequisite cases print a
generic message, and the propagation path for the demo exit code could be
made explicit and testable.

## Scope
- Detect missing Python / wrong version with a clear, single-line message and
  a distinct non-zero exit code.
- Ensure `exit $LASTEXITCODE` from the demo is the script's final exit code.
- Add a short comment block at the top describing each failure mode.
- Keep the script idempotent, admin-free, and without `Set-ExecutionPolicy`.

## Out of scope
- Changing the demo itself or the core.
- Adding new install steps.

## Acceptance criteria
- When Python is absent, the script prints one clear error and exits non-zero.
- When `python -m thekey demo` exits non-zero, `demo.ps1` propagates exactly
  that code (verified by forcing a BLOCKED demo in a test clone).
- No `Set-ExecutionPolicy` call remains in the file.

## Validation notes
- In a clean clone: `pwsh -NoProfile -File .\scripts\demo.ps1` → exit 0.
- Temporarily rename python on PATH (or use a shim) → script exits non-zero
  with a clear message.
