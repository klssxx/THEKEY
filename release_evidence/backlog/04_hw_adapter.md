---
title: "Additional example read-only adapter, separate from the core, with a verifiable contract"
type: help-wanted
labels: [help wanted, adapter, enhancement]
---

## Context
THEKEY consumes external providers (e.g. NPSC) only through optional,
read-only adapters. The core must not depend on any adapter to exist.
`src/thekey/adapters/npsc_adapter.py` is the reference example.

## Problem
There is only one example adapter. More examples make the "external provider"
boundary concrete and lower the bar for contributions.

## Scope
- Add a second example adapter under `src/thekey/adapters/` (e.g. a static
  prompt-linter or a second compiler stub) that maps an external output into
  the core's `ActorContext` without executing the provider.
- The adapter must be importable and unit-tested against a fixture output.
- Document it as optional and external in README / CONTRIBUTING.

## Out of scope
- Integrating the provider into the core transaction flow.
- Network calls or model execution inside the adapter.

## Acceptance criteria
- New adapter module + a test that feeds a sample external payload and asserts
  a valid `ActorContext` (no provider execution).
- README mentions adapters as optional/read-only; NPSC stays the example.
- CI tests pass.

## Validation notes
- `python -m pytest -q` includes the new adapter test (green).
- `python -m thekey demo` unaffected (adapter is not on the core path).
