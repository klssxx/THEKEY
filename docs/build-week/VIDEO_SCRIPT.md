# Build Week video script — 2:50 maximum
**0:00–0:20 — Problem.** “Coding agents patch quickly, but which plan was
authorized, what handler ran, and can a reviewer verify the result?”
**0:20–0:40 — Product.** “THEKEY requires a CHECKMATE PASS, explicit scoped
moli authorization, matching run/transaction/plan identities, and a fail-closed
policy decision before resolving a handler.”
**0:40–1:50 — Live demo.** Run:

```powershell
pwsh -NoProfile -File .\scripts\build-week-demo.ps1
```
Show the temporary Git repo, workflow workspace, controlled repair, JSON
evidence, and output: `ALLOW handlers=1`, `DENY handlers=0`, `4/4 PASS`,
`RELEASE_ELIGIBLE`.
**1:50–2:20 — Gates/evidence.** Open the governed transaction and both receipts;
show the shared plan hash and transaction ID. State clearly that this is
workflow isolation, not an OS sandbox.
**2:20–2:45 — Codex/GPT-5.6.** “Codex inspected the AST, designed adversarial
cases, implemented the five-caller rebase, and drove RED→GREEN tests. I, moli,
retained authority and publication decisions. The submission links genuine
`/feedback` evidence; GPT-5.6 is not a runtime dependency.”
**2:45–2:50 — Close.** “THEKEY: a key, a receipt, and evidence for every agentic
change.”
