# Decisions

This document records architecture decisions for THEKEY Core Governed Run.

## ADR-001: Deterministic MVP without mandatory AI
The MVP runs the canonical demo and all blocked scenarios **deterministically**
with no external AI. HY3 is designed as a stateless phase operator behind the
same context builder + output validator, so the control plane is AI-optional.
Rationale: a governed pipeline must be auditable and reproducible without
depending on a model's nondeterminism.

## ADR-002: Single active run, repo-level state
The authoritative state (`.thekey/state.json`) is repo-level and a single run is
active at a time in the MVP. Each new run resets the binding to SUBMITTED.
Rationale: keeps the state machine simple and the transition log legible;
concurrency is a post-0.1.0 item (see ROADMAP).

## ADR-003: Evidence from observed results only
Evidence records are created only from observed execution results (command
output, file hashes). The orchestrator — not any model output — writes
authoritative evidence and state. Rationale: prevents fabricated or hallucinated
evidence from becoming authoritative.

## ADR-004: Tamper detection via sealed-artifact hashes
Sealed artifacts (changes.diff, baseline.json, approvals.json) are hashed at
production time and re-checked before the decision. Tampering blocks the run.
Rationale: honest, cheap verification that evidence was not edited after
production.

## ADR-005: Closed action IDs, no arbitrary shell
The model may only request a fixed set of action IDs with declared parameters.
No shell strings, no free-form paths. Rationale: removes the largest attack
surface (arbitrary command execution) by construction.
