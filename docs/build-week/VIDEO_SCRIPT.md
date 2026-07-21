# Build Week video script

Target runtime: **2:40–2:55**. Hard stop before **3:00**. Spoken language:
English.

## 0:00–0:15 — Brand and problem

**On screen:** launch `THEKEY.exe` and hold briefly on the canonical home view.

**Narration:**

> Coding agents and project tests can change or execute code quickly. The hard
> question is whether we can prove what was inspected, who authorized the next
> step, what actually ran, and whether the original stayed unchanged.

## 0:15–0:35 — The governed roles

**On screen:** the application header and three-step guidance.

**Narration:**

> THEKEY is the governed-transaction core. THE KING coordinates phases and
> context, but cannot self-approve or bypass the PolicyEngine. CHECKMATE reviews
> risk and emits a pre-execution verdict without physical writes.

## 0:35–1:20 — Detect and repair a real application defect

**On screen:** select **Seleccionar y analizar / Select & Analyze**, choose the bundled
`SAMPLE-REPAIRABLE-PYTHON-APP`, and keep the read-only inspection visible. Then
select **Reparar / Repair**, read the warning, and consent.

**Narration:**

> First, THEKEY only reads the selected Python application. It identifies the
> profile and tests, records CHECKMATE PASS, and obtains a narrow read-only,
> isolated-output PolicyEngine authorization. The second click is separate
> because tests execute trusted project code. They expose a real arithmetic
> failure. THEKEY tries only bounded single-point mutations in the copy. One
> candidate passes compileall, the full pytest suite, the secret scan, and the
> documentation gate. After separate consent, it rechecks the baseline, saves
> a backup, applies the exact verified bytes, and verifies again. The result is
> REPAIRED_AND_VERIFIED — not a prerecorded claim.

## 1:20–1:55 — Adversarial judge scenario

**On screen:** select **Demo para jueces** and hold on its final summary.

**Narration:**

> The reproducible Judge Mode also shows the enforcement boundary. One bounded
> repair reaches exactly one handler. An adversarial request using a disallowed
> role is denied with zero handlers. All four release gates pass and the result
> is RELEASE_ELIGIBLE.

## 1:55–2:18 — Evidence

**On screen:** select **Ver resultados / View results** and show safe fields from the
latest project `verification-evidence.json`, then the judge summary. Hide local
absolute paths.

**Narration:**

> These are persisted JSON records, not prerecorded output. The application
> record contains the diagnostic, exact diff and repair hash, source hashes
> before and after, backup, CHECKMATE and policy decisions, both gate runs, and
> the final verdict. The Judge Mode receipts bind
> run, transaction, plan, and policy bundle, including one ALLOW handler and
> zero DENY handlers.

## 2:18–2:40 — Build Week contribution and Codex

**On screen:** show `git rev-parse HEAD`, `BUILD_WEEK_DELTA.md`, and the
sanitized `CODEX_SESSION_EVIDENCE.md`.

**Narration:**

> THEKEY is a declared preexisting project and only its verified post-baseline
> delta is submitted. Codex with GPT-5.6 helped analyze, build, test, and improve
> the governed boundary, security cases, evidence and portable interface. The
> user retained authority, scope and publication decisions. GPT-5.6 is
> development tooling, not a runtime dependency.

## 2:40–2:55 — Limits and close

**On screen:** the warning text, then the canonical title.

**Narration:**

> Project tests must be trusted. THEKEY uses a read-only intake and isolated
> copy, not an operating-system sandbox. Repair uses a closed candidate set,
> never edits tests or installs dependencies, and blocks anything it cannot
> prove fixed. THEKEY — THE KING OF CHECKMATE. Governed
> Codex Transactions for Coding Agents.

## Timing discipline

- Rehearse once at a conversational pace before recording.
- Use the bundled sample so the displayed result is deterministic.
- Show the real runs continuously; do not replace output with prerecorded
  results.
- Never submit a cut that reaches three minutes.
