# THEKEY judge demo — under three minutes

## 0:00–0:20 — Problem

“Coding agents can modify projects quickly, but teams need a deterministic,
auditable way to decide what may run, what changed, and whether the result is
safe to release.”

## 0:20–0:45 — Product

Open `THEKEY.exe`. Point out the native desktop UI, the local-mode label and
the four real operations. Explain that the home screen reports no synthetic
health or activity data.

## 0:45–1:50 — Real demo

Click **Demo para jueces / Judge demo**. THEKEY uses its bundled deterministic
calculator sample, creates an isolated workspace, demonstrates an allowed
operation and a denied operation, runs four gates and persists bound receipts.
Show the real output and then **Resultados / Results**.

## 1:50–2:30 — Safety

Select `SAMPLE-REPAIRABLE-PYTHON-APP`, explain that initial intake is read
only, and show that verification requires explicit consent. Explain that repair
first creates a verified isolated preview; applying it requires a separate
confirmation, stale-source check, backup and post-apply re-test.

## 2:30–3:00 — Close

“THEKEY is a developer tool for governed coding-agent operations: isolated
workspaces, deterministic gates and auditable evidence. Codex assisted the
Build Week implementation; no model is a hidden runtime authority.”

### Repeatable source command

```powershell
pwsh -NoProfile -File .\scripts\build-week-demo.ps1
```

Expected duration on the validated machine: under three minutes, typically
well under one minute. It uses no private data or API key and leaves the source
repository unchanged.
