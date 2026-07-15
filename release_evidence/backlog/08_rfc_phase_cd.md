---
title: "RFC: preliminary design for Phase C/D without implementation in 0.2.0"
type: rfc
labels: [rfc, phase-c, phase-d]
---

## Context
THEKEY 0.2.0 is intentionally small. Future work (Phase C: stronger identities,
evidence signing, concurrency, exceptions, RFC policy; Phase D: OSS
attractiveness) is planned but must not start before the public launch.

## Problem
There is no single, reviewed design note that scopes Phase C/D, lists what
stays out of the core, and defines the gates that would let a Phase C change
land without breaking the "small, serious" principle.

## Scope (design only — no implementation in 0.2.0)
- Enumerate candidate Phase C/D work items with explicit "in core" vs "external
  adapter" classification.
- Define the acceptance bar for any Phase C change (security/product/OSS veto,
  no core bloat, deterministic gates preserved).
- Sketch the evidence-signing and concurrency models as options, not decisions.

## Out of scope
- Writing Phase C code now.
- Changing 0.2.0 behavior.

## Acceptance criteria (for the RFC)
- A design note under `docs/rfc/phase-c-d.md` approved by maintainers.
- Each item tagged `phase-c` or `phase-d` with scope boundaries.
- Confirmed that Phase C does not begin before public launch.

## Validation notes
- RFC merged as docs; the 0.2.0 release remains unchanged and publishable.
