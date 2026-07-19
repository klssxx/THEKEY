# Build Week evidence handling

## Status vocabulary

- `VERIFIED_GIT_OBJECT`: the commit/tree exists locally and is reachable in the
  inspected Git graph.
- `VERIFIED_PUBLIC_RULE`: the value is taken from the linked official rules.
- `VERIFIED_SESSION_METADATA`: the identifier was found in real local Codex
  session metadata without publishing the raw log.
- `PUBLIC_SANITIZED_RECORD`: a public summary derived from private metadata;
  it is intentionally not the raw source.
- `CLAIM_RECORDED`: the owner supplied the statement, but independent evidence
  has not established it.
- `PENDING_EVIDENCE_IMPORT`: a possible source has not yet been imported,
  hashed, reviewed, or accepted as evidence.
- `BOUND_TO_FINAL_HEAD`: the value is the checked-out final commit resolved by
  `git rev-parse HEAD` after the non-amended candidate commit is created.

These labels must not be silently promoted. In particular,
`PENDING_EVIDENCE_IMPORT` and `CLAIM_RECORDED` are never described as verified
pre-cutoff proof.

## Public/private separation

Raw pre-public chat exports belong only under the ignored directory
`evidence-private/build-week/chat-exports/`. The public repository may contain
only sanitized descriptions, hashes after an actual import, evidence status,
and paths that do not disclose a private source location.

`.gitignore` also excludes the private import manifest. Before every candidate
commit, inspect `git status --short` and the staged write-set to ensure neither
raw evidence nor the private manifest is staged.

## Import procedure

1. Run `scripts/collect-preexisting-evidence.ps1` with explicit source files.
2. The script copies each file to the ignored private directory, uses a
   content-hash suffix, and records SHA-256, size, and the actual import time in
   a private manifest. It does not publish the source path.
3. Review the private artifact for credentials, personal data, third-party
   rights, and relevance.
4. If a public derivative is justified, create a separate sanitized record and
   add only its hash/status to the public index.
5. Keep the historical assertion at `CLAIM_RECORDED` until the evidence is
   actually imported and reviewed. An import alone does not prove authenticity
   or date.

## Session metadata

The primary `/feedback` Session ID
`019f79f2-6a7e-74f0-b1fa-d65335b29a7c` and the labels `gpt-5.6-luna` and
`gpt-5.6-sol` were found in local metadata. The public sanitized record is
[CODEX_SESSION_EVIDENCE.md](CODEX_SESSION_EVIDENCE.md). No raw session log is
committed, no exact per-model work split is claimed, and GPT-5.6 is not
presented as a THEKEY runtime dependency.

## Candidate binding

A Git commit cannot embed its own literal commit SHA in its tree: changing the
file would change the tree and therefore the commit. Candidate documents bind
to symbolic `HEAD`; the exact SHA and tree are recorded by the required
post-commit commands and final handoff. Video recording must visibly run
`git rev-parse HEAD` from that verified checkout.
