# Provenance index

## Plain statement for judges

The owner reports that THEKEY existed before OpenAI Build Week. The reachable Git history in this working copy starts after the Submission Period began, so Git cannot independently prove that earlier history. Under the Build Week rules, only meaningful extensions made during the Submission Period are offered for evaluation; this repository does not relabel unverified prior work as new.

| Evidence | Status | What it supports |
| --- | --- | --- |
| [Pre-period Git audit](PRE_BUILD_WEEK_GIT_HISTORY.md) | `BLOCKED_NO_PRE_PERIOD_COMMIT` | Honest limit of the accessible history. |
| [Reachable Build Week range](BUILD_WEEK_COMMIT_RANGE.md) | reproducible | Dated commits and visible changes after July 15. |
| [Technical delta](../BUILD_WEEK_DELTA.md) | documented | Bounded implementation work after the Build Week baseline. |
| [Codex session register](../CODEX_SESSIONS.md) | primary ID recorded | Codex/GPT-5.6 development contribution during the period. |
| [Chat evidence](chat-evidence/README.md) | owner-supplied supplementary evidence published | Saved ChatGPT conversation about an existing THEKEY ZIP, paired with the visible `5 jul` history-search label and explicit evidentiary limits. |

## Capability boundary

| Capability | Before July 13 | Added or meaningfully extended during Build Week | Evidence |
| --- | --- | --- | --- |
| Project history | Owner-reported, not Git-verified in this checkout | Public, dated reachable history begins July 15 | [pre-period audit](PRE_BUILD_WEEK_GIT_HISTORY.md) |
| Governed lifecycle, policy, evidence, CLI | Present at the documented Build Week baseline; not verified pre-period | Reused and hardened | [new-work boundary](../../BUILD_WEEK_NEW_WORK.md) |
| Strict physical authorization and receipt binding | Not classified as pre-period | Implemented and tested in the recorded core delta | [delta](../BUILD_WEEK_DELTA.md) |
| Windows portable, WPF judge experience, samples, smoke evidence | Not classified as pre-period | Documented Build Week delivery work | [final report](../../../artifacts/build-week/FINAL_REPORT.md) |
| Chat records | Owner-supplied saved conversation shows an existing THEKEY ZIP, architecture, tests and agents; date is corroborated by the companion `5 jul` UI screenshot | Supplementary only; the browser-saved HTML does not independently expose a creation timestamp | [chat evidence](chat-evidence/CHAT_EVIDENCE_INDEX.md) |

Never infer an earlier timestamp from prose, file modification time, or a recreated transcript. Git is the primary evidence when present; chats are supplementary.
