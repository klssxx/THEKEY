# Devpost draft — not submitted
**Project:** THEKEY — THE KING OF CHECKMATE
**Tagline:** Governed Codex Transactions for Coding Agents
**Value proposition:** Every agentic change gets a plan identity, explicit
authorization, deterministic gates, and reviewable evidence.
**Track:** Developer Tools
## Description
THEKEY is the product and governed-transaction core. THE KING orchestrates
phases and context, but cannot self-approve or bypass the `PolicyEngine`.
CHECKMATE performs adversarial pre-execution review: it analyzes risk and issues
a verdict, but performs no physical writes.

Agentic changes are fast, but teams often cannot prove which plan was
authorized, what executed, or why release was allowed. THEKEY turns a change
into a governed transaction. Before resolving a physical handler it requires a
CHECKMATE pre-action PASS and scoped usuario authorization bound to the same run,
transaction, plan SHA-256, policy version, and policy bundle hash. Only
EXECUTOR crosses the boundary; malformed, mismatched, deferred, failed, or
unauthorized inputs fail closed.

The Windows portable application turns that boundary into a two-click product
flow. A user selects a trusted local Python project; THEKEY performs a
read-only inspection, profiles it, records a CHECKMATE verdict and asks the
`PolicyEngine` for a narrowly scoped authorization. Only after explicit test-
execution consent does it copy inspected files to a short isolated workspace
and run compileall, existing pytest tests, a limited secret scan, and a
documentation gate. It then re-hashes the original and emits a final
`VERIFIED`, `BLOCKED`, or `NO_VERIFICABLE` verdict with JSON evidence. Generated
`bin`, `obj`, `publish`, `build`, and `dist` trees are excluded; dependencies
are never installed automatically.

The product now closes the loop instead of stopping at detection. **Scan and
repair** emits redacted actionable diagnostics and searches a closed set of
conservative single-point Python mutations in the isolated copy. It accepts a
candidate only after compileall, the complete pytest suite, secret scan, and
documentation gate pass. A separate consent authorizes the exact verified
bytes; THEKEY rejects stale source/test hashes, stores an out-of-tree backup,
re-verifies after applying, and rolls back on failure.

Judge Mode creates a temporary Git repository, repairs one controlled defect
inside a workflow-isolated runtime, runs build/tests/secret-scan/documentation,
and emits JSON evidence. An adversarial `Role.SYSTEM` request then returns DENY,
executes zero handlers, and leaves the workspace hash unchanged.
**Technologies:** Python 3.11+, Pydantic v2, pytest, JSON Schema, PowerShell 7,
SQLite, Git, WPF/.NET Framework, PyInstaller, and Codex.
THEKEY is explicitly declared a preexisting project. Its accessible public Git
history begins after the cutoff: the owner statement is `CLAIM_RECORDED`, and
unimported historical records remain `PENDING_EVIDENCE_IMPORT`. The session
baseline contained the lifecycle, isolation, gates, evidence, CLI, and
canonical demo. Only the verifiable delta after baseline
`3a8456416ed9ae9183840585b488cec04e9a069d` is submitted for evaluation; see
`docs/build-week/BUILD_WEEK_DELTA.md`. This Codex thread added bound double
receipts, the production policy decision API, 5/5 governed callers,
state-provenance fixes, security tests, Judge Mode, and submission
documentation. Codex drove inspection, adversarial design, implementation and
RED→GREEN verification; usuario retained product, authority, and publication
decisions. Codex with GPT-5.6 was the agent used to analyze, build, test, and
improve the project, including caller comparison, denial cases, the governed
boundary, regression, and clean-clone verification. GPT-5.6 was development
tooling, not a runtime dependency; the sanitized session record is in
`docs/build-week/CODEX_SESSION_EVIDENCE.md`.
## Judge instructions

Submission owner checklist: the repository must be public or, if private,
shared with `testing@devpost.com` and `build-week-event@openai.com`. This access
setting must be confirmed in GitHub before submission; the repository contents
and Git remote cannot prove it.

Portable path for Windows 10/11 x64: extract
`THEKEY-Portable-Windows-x64.zip`, open `THEKEY.exe`, and select **Demo para
jueces** for the deterministic competition scenario. To exercise the product
flow, select **SELECCIONAR Y ANALIZAR APLICACIÓN**, choose the included
`SAMPLE-REPAIRABLE-PYTHON-APP`, then select **Escanear y reparar** and approve
execution of that trusted sample's tests plus application of only a fully
verified repair. The visible result is `REPAIRED_AND_VERIFIED`, with the exact
diff, policy decision, backup, and post-apply gates in JSON. No Python, Git,
PowerShell, API key, account, or network installation is needed.

Source-install fallback:

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
Portable target: Windows 10 x64 and Windows 11 x64; current verification host:
Windows 11. Public YouTube: `PENDING_PUBLIC_YOUTUBE_URL`.
`/feedback`: `019f79f2-6a7e-74f0-b1fa-d65335b29a7c`.
Limits: workflow isolation is not an OS sandbox. The local grant is hard-bound
to the canonical demo path/hash and isolated output, with production reuse
denied; it is not a cryptographic signature. Secret scanning is limited; no
paid service or secret is required for the main demo.
Project verification recognizes Python, Node.js, Go, Rust, .NET, and Maven
profiles. The portable does not bundle third-party project toolchains: Rust can
report `RUST_LINKER_UNAVAILABLE` without a compatible linker, while Maven can
report `TOOLCHAIN_UNAVAILABLE` (and `TESTS_NOT_FOUND` when applicable) without
Java/Maven and detectable tests. These are intentional fail-closed diagnostics,
not successful verification. Consent runs trusted project tests in an isolated
copy, not an OS sandbox; unsupported projects or missing evidence do not
receive a VERIFIED verdict. Automatic repair covers only the documented closed
Python/JavaScript single-point candidate set, never changes tests or installs
dependencies, and blocks defects it cannot prove fixed.
