---
title: "Improved exportable evidence / auditable artifact format without changing the transactional core"
type: help-wanted
labels: [help wanted, enhancement, documentation]
---

## Context
Every run writes artifacts under `runs/<RUN_ID>/` (manifest, plan, approvals,
changes.diff, gates.json, decision.json, artifact-hashes.json, evidence/). The
event store is append-only and hash-chained.

## Problem
The artifact format is ad hoc and not trivially portable or machine-checkable
by external tooling. A stable, documented export format would help auditors
and downstream consumers.

## Scope
- Define a versioned, documented evidence bundle schema (JSON) that wraps the
  existing artifacts + event-chain tail.
- Add an export command (e.g. `thekey evidence export --run-id <ID>`) that
  emits the bundle without altering how the core records evidence.
- Keep `thekey evidence verify` working against both old and new formats.

## Out of scope
- Changing the state machine, gates, or event-store internals.
- Adding cryptographic signing (tracked separately as a future mitigation).

## Acceptance criteria
- New schema file under `governance/schemas/` + a test that validates a real
  bundle.
- Export command produces a parseable bundle; `evidence verify` still passes.
- Docs note the format is additive (no core behavior change).

## Validation notes
- Run a demo, then `python -m thekey evidence export --run-id <ID>` and
  `python -m thekey evidence verify --run-id <ID>` → both succeed.
