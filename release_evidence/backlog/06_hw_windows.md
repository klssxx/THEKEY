---
title: "Windows 11 and path-with-spaces hardening in auxiliary tooling"
type: help-wanted
labels: [help wanted, windows, ci]
---

## Context
The primary Quick Start runs on Windows 11 from a path that may contain
spaces. `scripts/demo.ps1` already sets `THEKEY_REPO_ROOT` to isolate run
state, but other auxiliary scripts (bootstrap*.ps1, run-demo.ps1) were written
before that fix and are not uniform.

## Problem
Auxiliary tooling is inconsistent: some scripts use `[dev]` install, some rely
on shortcuts that break under spaces, and none share a single, tested harness.

## Scope
- Audit `scripts/*.ps1` for space-safe, admin-free, non-`Set-ExecutionPolicy`
  behavior.
- Normalize on the `demo.ps1` pattern (create/reuse `.venv`, `pip install -e
  .`, set `THEKEY_REPO_ROOT`, propagate exit code).
- Add a CI job that runs at least one script from a path containing spaces
  (already partially covered by `demo.ps1`).

## Out of scope
- Changing the core or the demo logic.
- Supporting non-Windows platforms as primary (CI may stay Windows-first).

## Acceptance criteria
- Every `scripts/*.ps1` is space-safe and admin-free; none calls
  `Set-ExecutionPolicy`.
- A documented test proves one script runs from a "C:\Path With Spaces\..."
  clone.
- CI green.

## Validation notes
- Copy the repo to `C:\Temp\THEKEY Test 0.2\` and run a script → exit 0.
