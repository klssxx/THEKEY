# Build Week provenance timeline

This timeline distinguishes owner claims, public Git facts, and the bounded
post-baseline contribution. Dates below come from the cited rule or Git object;
unknown pre-public dates remain unknown.

| Time | Event | Evidence status |
| --- | --- | --- |
| Before the public repository history; exact date not established | The owner states that THEKEY already existed. | `CLAIM_RECORDED` |
| 2026-07-13 09:00 PT | OpenAI Build Week submission period begins under the [official rules](https://openai.devpost.com/rules). | `VERIFIED_PUBLIC_RULE` |
| 2026-07-15T06:34:40+02:00 | Earliest commit reachable from configured `origin/main`: `b7b6c32cf3a2621d29ef2c5856db50d116d8dff6`. | `VERIFIED_GIT_OBJECT` |
| 2026-07-18T23:12:31+02:00 | Session baseline: `3a8456416ed9ae9183840585b488cec04e9a069d`. | `VERIFIED_GIT_OBJECT` |
| 2026-07-19T18:01:30+02:00 | Phase-B governed physical authorization: `c0410feaf869e0ac08c9e637b70e30ebac8085c8`. | `VERIFIED_GIT_OBJECT` |
| Final local closure | Candidate documentation, evidence verifier, provenance dossier, and reproducibility checks are committed after Phase B. The exact commit is resolved by `git rev-parse HEAD` in the post-commit handoff. | `BOUND_TO_FINAL_HEAD` |
| Not yet imported | Any historical pre-GitHub chat exports, backups, or snapshots. | `PENDING_EVIDENCE_IMPORT` |

## Interpretation

The public Git graph verifies the baseline and later changes; it does not verify
the start date of work that predates that graph. The submission therefore says
both things plainly: THEKEY is declared preexisting, and the visible public
history begins after the cutoff. Only the post-baseline delta is submitted for
evaluation.
