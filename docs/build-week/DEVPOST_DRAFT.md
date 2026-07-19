# Devpost draft — not submitted
**Project:** THEKEY — Governed Transactions for Coding Agents
**Tagline:** Every agentic change gets a plan identity, explicit authorization,
deterministic gates, and reviewable evidence.
**Track:** Developer Tools
## Description
Agentic changes are fast, but teams often cannot prove which plan was
authorized, what executed, or why release was allowed. THEKEY turns a change
into a governed transaction. Before resolving a physical handler it requires a
CHECKMATE pre-action PASS and scoped moli authorization bound to the same run,
transaction, plan SHA-256, policy version, and policy bundle hash. Only
EXECUTOR crosses the boundary; malformed, mismatched, deferred, failed, or
unauthorized inputs fail closed.
Judge Mode creates a temporary Git repository, repairs one controlled defect
inside a workflow-isolated runtime, runs build/tests/secret-scan/documentation,
and emits JSON evidence. An adversarial `Role.SYSTEM` request then returns DENY,
executes zero handlers, and leaves the workspace hash unchanged.
**Technologies:** Python 3.11+, Pydantic v2, pytest, JSON Schema, PowerShell 7,
SQLite, Git, and Codex.
The owner says THEKEY predates Build Week, but public history begins after the
cutoff; earlier provenance remains unresolved. The starting commit contained
the lifecycle, isolation, gates, evidence, CLI, and canonical demo. This Codex
thread added bound double receipts, the production policy decision API, 5/5
governed callers, state-provenance fixes, security tests, Judge Mode, and
submission documentation. Codex drove inspection, adversarial design,
implementation and RED→GREEN verification; moli retained product, authority,
and publication decisions. GPT-5.6 evidence awaits genuine session metadata;
no runtime GPT-5.6 integration is claimed.
## Judge instructions
```powershell
git clone https://github.com/klssxx/THEKEY.git
cd THEKEY
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e .
pwsh -NoProfile -File .\scripts\build-week-demo.ps1
```

Expected: ALLOW `handlers=1`, DENY `handlers=0`, `4/4 PASS`, and
`RELEASE_ELIGIBLE`. Repository: https://github.com/klssxx/THEKEY. Platform:
Windows 11. YouTube: `PENDING_PUBLIC_YOUTUBE_URL`. `/feedback`:
`PENDING_REAL_FEEDBACK_SESSION_ID`.
Limits: workflow isolation is not an OS sandbox. The local grant is hard-bound
to the canonical demo path/hash and isolated output, with production reuse
denied; it is not a cryptographic signature. Secret scanning is limited; no
paid service or secret is required for the main demo.
