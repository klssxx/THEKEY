---
title: "RFC: formal contract for read-only adapters for external providers"
type: rfc
labels: [rfc, adapter, phase-c]
---

## Context
THEKEY may consume outputs from external providers (compilers, linters, prompt
optimizers) without executing them. NPSC is the reference read-only adapter.
There is no formal, versioned contract for what an adapter must guarantee.

## Problem
Without a contract, each adapter reinvents input validation, error handling,
and the `ActorContext` mapping. Contributors cannot tell what "read-only" and
"optional" mean in practice.

## Scope (design only — no implementation in 0.2.0)
- Define `AdapterContract`: input shape, required read-only guarantee (no
  provider execution, no writes outside a scratch dir), `ActorContext` output
  schema, error taxonomy, and a self-test fixture.
- Specify how the core discovers/loads adapters (entry point or explicit
  import) without coupling to any provider.
- State explicitly that adapters are optional: the core works with zero
  adapters.

## Out of scope
- Implementing the contract in code during 0.2.0.
- Integrating any specific provider into the core.

## Acceptance criteria (for the RFC, not the code)
- A written contract under `docs/rfc/` covering the above.
- A reviewed example (`npsc_adapter.py`) annotated against the contract.
- Maintainer approval as an RFC; implementation deferred to a later phase.

## Validation notes
- RFC reviewed and merged as documentation; no runtime change required for
  the 0.2.0 public preview.
