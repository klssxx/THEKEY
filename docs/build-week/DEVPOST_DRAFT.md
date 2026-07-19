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
THEKEY is explicitly declared a preexisting project. Its accessible public Git
history begins after the cutoff: the owner statement is `CLAIM_RECORDED`, and
unimported historical records remain `PENDING_EVIDENCE_IMPORT`. The session
baseline contained the lifecycle, isolation, gates, evidence, CLI, and
canonical demo. Only the verifiable delta after baseline
`3a8456416ed9ae9183840585b488cec04e9a069d` is submitted for evaluation; see
`docs/build-week/BUILD_WEEK_DELTA.md`. This Codex thread added bound double
receipts, the production policy decision API, 5/5 governed callers,
state-provenance fixes, security tests, Judge Mode, and submission
documentation. Codex drove inspection, adversarial design,
implementation and RED→GREEN verification; moli retained product, authority,
and publication decisions. Codex with GPT-5.6 compared the physical caller
paths, helped design adversarial cases, implemented the governed boundary, and
supported regression and clean-clone verification. GPT-5.6 was development
tooling, not a runtime dependency; the sanitized session record is in
`docs/build-week/CODEX_SESSION_EVIDENCE.md`.
## Judge instructions
```powershell
git clone https://github.com/klssxx/THEKEY.git
cd THEKEY
git rev-parse HEAD
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -e .
pwsh -NoProfile -File .\scripts\build-week-demo.ps1
pwsh -NoProfile -File .\scripts\verify-build-week-evidence.ps1
```

The displayed `git rev-parse HEAD` must equal the exact `FINAL_CANDIDATE` SHA in
the post-commit handoff and submission. The repository cannot embed its own
commit hash; this check binds the instructions to the checked-out candidate.

Expected: ALLOW `handlers=1`, DENY `handlers=0`, `4/4 PASS`, and
`RELEASE_ELIGIBLE`, plus unchanged source, bound receipts, and
`production_reuse=False`. Repository: https://github.com/klssxx/THEKEY.
Platform: Windows 11. Public YouTube: `PENDING_PUBLIC_YOUTUBE_URL`.
`/feedback`: `019f79f2-6a7e-74f0-b1fa-d65335b29a7c`.
Limits: workflow isolation is not an OS sandbox. The local grant is hard-bound
to the canonical demo path/hash and isolated output, with production reuse
denied; it is not a cryptographic signature. Secret scanning is limited; no
paid service or secret is required for the main demo.
