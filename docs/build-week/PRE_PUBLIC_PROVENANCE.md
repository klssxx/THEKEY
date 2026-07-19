# Pre-public provenance declaration

## Project classification

**THEKEY is a PREEXISTING PROJECT.** The owner records that development began
before the OpenAI Build Week submission period. That statement is deliberately
classified as `CLAIM_RECORDED`: the current public repository does not contain
pre-cutoff Git history that independently proves when the earlier work began.

The public GitHub history must not be read as an earlier history than it is.
The first commit reachable from the configured public `origin/main` is
`b7b6c32cf3a2621d29ef2c5856db50d116d8dff6`, dated
`2026-07-15T06:34:40+02:00`. This is after the official submission-period start
of July 13, 2026 at 09:00 Pacific Time. No commit is backdated and no synthetic
pre-GitHub history is asserted.

## Evidence status

| Statement or artifact | Status | What it establishes |
| --- | --- | --- |
| Owner statement that THEKEY existed before the submission period | `CLAIM_RECORDED` | Project classification supplied by the owner; not independent date proof. |
| Earliest commit reachable from `origin/main` | `VERIFIED_GIT_OBJECT` | The accessible public Git graph begins after the cutoff. |
| Pre-GitHub chat exports, backups, or local snapshots not yet imported | `PENDING_EVIDENCE_IMPORT` | Potential historical evidence exists as a collection task, not as verified public proof. |
| Session baseline `3a8456416ed9ae9183840585b488cec04e9a069d` | `VERIFIED_GIT_OBJECT` | Exact state already present when the primary Build Week implementation session was baselined. |
| Phase-B commit `c0410feaf869e0ac08c9e637b70e30ebac8085c8` | `VERIFIED_GIT_OBJECT` | Exact governed-authorization implementation produced after the baseline. |
| Primary Codex Session ID and local GPT-5.6 labels | `VERIFIED_SESSION_METADATA` | The identifiers occur in local session metadata; raw logs remain private. |

## Evaluation boundary

Only the verifiable delta after session baseline
`3a8456416ed9ae9183840585b488cec04e9a069d` is presented for Build Week
evaluation. Preexisting functionality is context, not newly claimed event work.
The exact split is in [BUILD_WEEK_DELTA.md](BUILD_WEEK_DELTA.md).

## Non-claims

- The public GitHub repository is not presented as if it existed before its
  visible history.
- `CLAIM_RECORDED` is not equivalent to independently verified provenance.
- `PENDING_EVIDENCE_IMPORT` is not evidence until a real artifact is imported,
  hashed, reviewed, and classified.
- Local session metadata verifies observed identifiers only. It does not prove
  a runtime GPT-5.6 integration or an exact allocation of work between model
  labels.
- No private chat export, credential, personal path, or raw session log is
  committed to the public candidate.

See [EVIDENCE_HANDLING.md](EVIDENCE_HANDLING.md) and the public
[provenance manifest](../../evidence/build-week/provenance/PROVENANCE_MANIFEST.json).
