# Verifiable Build Week delta

Only changes verifiable after the session baseline are presented for judging.
This file does not retroactively classify the public repository history as
pre-cutoff evidence.

## PREEXISTING PROJECT

THEKEY is explicitly declared a preexisting project. Before the session
baseline it already contained the governed lifecycle, workflow workspaces,
policy and gates, evidence/state machinery, CLI, history/event components, and
the bounded calculator demo.

The declaration that this work existed before the event is `CLAIM_RECORDED`.
The accessible public Git history begins after the submission cutoff, and
historical records not yet imported remain `PENDING_EVIDENCE_IMPORT`.

## SESSION BASELINE

`3a8456416ed9ae9183840585b488cec04e9a069d`

Tree: `06ff07e3482ff8443d4cbebddb270aed15da1712`.

This is the fixed comparison point for the primary Build Week implementation
session. Functionality present at this commit is context, not submitted as new
work.

## PHASE-B COMMIT

`c0410feaf869e0ac08c9e637b70e30ebac8085c8`

Tree: `5d9ac9693c1f58ae80314e114e291b0738c70255`.

Verified post-baseline technical delta:

- strict action context and bound CHECKMATE/sovereign receipts;
- fail-closed physical authorization restricted to `Role.EXECUTOR`;
- deterministic production policy adapter and five governed dispatch callers;
- demo-grant subject/output binding with production reuse denied;
- adversarial models, guard, integration, caller, rollback, and clean-clone
  verification;
- reproducible Judge Mode with one-handler ALLOW, zero-handler DENY, four gates,
  and persisted evidence.

The original Phase-B commit remains unchanged and is not duplicated or amended.

## FINAL CANDIDATE

Pre-commit literal SHA: `<SHA pending until the final local commit>`.

Authoritative binding after commit: `HEAD`, resolved by:

```powershell
git rev-parse HEAD
git show -s --format=%T HEAD
```

The exact SHA and tree are recorded in the post-commit verification and final
candidate handoff. This symbolic binding avoids inventing a self-referential
hash. The final candidate adds the submission-safe README and Judge Mode
evidence contract, independent evidence verifier, tests, video/Devpost package,
and this provenance dossier.

## Evaluation command

Review only the verifiable post-baseline range:

```powershell
git diff --stat 3a8456416ed9ae9183840585b488cec04e9a069d..HEAD
git diff --name-status 3a8456416ed9ae9183840585b488cec04e9a069d..HEAD
```

The preexisting project provides context; only this bounded range is presented
for Build Week evaluation.
