# Build Week video script

Target runtime: **2:40–2:55**. Hard stop before **3:00**. Spoken language:
English.

## 0:00–0:18 — The problem

**On screen:** title card, then the repository README.

**Narration:**

> Coding agents can patch a repository quickly. The harder question is whether
> anyone can prove which plan was reviewed, who authorized it, what actually
> executed, and why the result was allowed to move forward.

## 0:18–0:40 — The product

**On screen:** the authorization flow in `README.en.md`.

**Narration:**

> THEKEY turns an agentic change into a governed transaction. One plan identity
> connects pre-action CHECKMATE review, explicit scoped human authority, a
> deterministic policy decision, the physical action, four release gates, and
> reviewable evidence. Authorization happens before the handler is resolved,
> and only the EXECUTOR role can cross that boundary.

## 0:40–1:32 — Live Judge Mode

**On screen:** a clean PowerShell 7 terminal at the repository root. Run:

```powershell
pwsh -NoProfile -File .\scripts\build-week-demo.ps1
```

Keep the final summary visible and point to each result.

**Narration:**

> Judge Mode creates a temporary Git repository and an isolated workflow
> workspace. It applies one bounded calculator repair through the governed
> path, then attempts an adversarial action using a disallowed role. The ALLOW
> path reports APPLIED and exactly one handler. The DENY path reports
> ROLE_NOT_ALLOWED and zero handlers. Build, unit tests, limited secret scan,
> and documentation all pass: four out of four. The resulting decision is
> RELEASE_ELIGIBLE.

## 1:32–2:02 — Evidence, not just output

**On screen:** show only the safe fields from the generated
`judge-mode-evidence.json`: `run_id`, `transaction_id`, `plan_sha256`,
`policy_bundle_hash`, `allow`, `deny`, `gates`, and `release_decision`. Do not
show the absolute `run_path` or `workspace_path` fields.

**Narration:**

> This is structural evidence, not a screenshot-only claim. The receipts share
> the same run, transaction, and plan hash. The policy bundle is recorded. The
> evidence confirms one ALLOW handler, zero DENY handlers, and that the denied
> attempt left the workspace hash unchanged. The demo grant is bound to this
> bounded source and explicitly rejects production reuse.

## 2:02–2:30 — Build Week contribution and Codex

**On screen:** run `git rev-parse HEAD`, then show `BUILD_WEEK_DELTA.md` and the
sanitized `CODEX_SESSION_EVIDENCE.md` record. The displayed commit must match
the final candidate handoff.

**Narration:**

> THEKEY is a declared preexisting project, and its public Git history begins
> after the cutoff. Only the verified post-baseline delta is submitted. During
> Build Week it was significantly extended with bound double receipts, a
> fail-closed physical guard, five
> governed callers, adversarial security tests, Judge Mode, and reproducibility
> evidence. Codex with GPT-5.6 compared the five caller paths, designed denial
> cases, implemented the governed boundary, and drove regression and clean-clone
> checks. I, moli, retained authority, scope, and publication decisions. GPT-5.6
> is development tooling here, not a runtime dependency.

## 2:30–2:48 — Limits and close

**On screen:** the README limitations, then the project title.

**Narration:**

> The boundaries are deliberate: this is workflow isolation, not an operating-
> system sandbox; the local grant is not a cryptographic human signature; and
> the built-in secret scan and action set are bounded. Within those limits,
> THEKEY gives every agentic change a plan identity, explicit authorization,
> deterministic gates, and reviewable evidence.

## Timing discipline

- Rehearse once at a conversational pace before recording.
- Let the real command finish; do not speed up or splice its output.
- If the take exceeds 2:55, shorten pauses rather than removing limitations or
  provenance.
- Never submit a cut that reaches 3:00.
