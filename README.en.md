# THEKEY

Governed software transactions for coding agents.

> **One-sentence value:** THEKEY lets a coding agent change an isolated
> workspace only after the plan, review, human authority, policy decision, and
> evidence all agree on the same transaction.

[Spanish README](README.md) · [Build Week contribution](BUILD_WEEK_CONTRIBUTION.md) · [Security](SECURITY.md) · [MIT License](LICENSE)

THEKEY addresses a concrete developer-tools problem: agentic changes are fast,
but it is often difficult to prove which plan was authorized, what crossed the
physical execution boundary, and why the result was eligible for release. It
is intended for coding-agent builders, CI/CD maintainers, and teams that need a
small, inspectable governance layer.

THEKEY provides workflow isolation, deterministic gates, and tamper-evident
evidence within documented limits. It is not an operating-system sandbox.

## OpenAI Build Week Judge Mode

The fastest way to evaluate the Build Week addition on Windows 11 is:

```powershell
git clone https://github.com/klssxx/THEKEY.git
cd THEKEY
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e .
pwsh -NoProfile -File .\scripts\build-week-demo.ps1
```

Judge Mode creates a small temporary Git repository, starts a real governed
transaction, copies the target into a workflow-isolated runtime, applies one
controlled repair, executes four gates, demonstrates an authorized ALLOW and
an adversarial DENY, and writes JSON evidence. It requires no secret, paid
service, Docker, WSL, or GPU.

Verified output shape:

```text
THEKEY BUILD WEEK JUDGE MODE
ALLOW: APPLIED, handlers=1
DENY: ROLE_NOT_ALLOWED, handlers=0
GATES: 4/4 PASS
DECISION: RELEASE_ELIGIBLE
EVIDENCE: ...\judge-mode-evidence.json
Isolation: workflow workspace only; this is not an OS sandbox.
```

The verified local run completed in under ten seconds and included paths with
spaces. Runtime varies with hardware and dependency state.

## How authorization works

```text
Mission plan
  → CHECKMATE pre-action review receipt
  → explicit scoped moli authorization receipt
  → deterministic PolicyEngine decision
  → THEKEY physical dispatch guard
  → exactly one declared handler
  → build, tests, secret scan, documentation gates
  → release decision and evidence
```

Before a physical handler is even resolved, THEKEY validates a strict Pydantic
`ActionContext`. Both persisted receipts must agree on the run ID, transaction
ID and plan SHA-256. The authorization ID, policy version, policy bundle hash,
role, verdict, and action scope must also match. Only `Role.EXECUTOR` can cross
the boundary. Missing fields, extra fields, mismatches, `SYSTEM`, `PENDING`,
`DEFER`, `FAIL`, policy exceptions, invalid responses, or an ALLOW without a
decision ID all fail closed.

`ActionReviewVerdict` is a pre-execution CHECKMATE result. `ReleaseDecision` is
created after gates. A later release decision is never reused retroactively as
authorization.

## Architecture

- **Coordinator:** persists run artifacts and rehydrates a transaction across
  CLI processes.
- **CHECKMATE reviewer:** emits the pre-action review receipt for the bounded
  plan.
- **Sovereign grant binder:** binds moli's explicit, repository-visible grant
  to one real run and transaction.
- **PolicyEngine:** validates the complete context and emits `allowed`, a reason
  code, a decision ID, and the preserved policy bundle hash.
- **Physical dispatch guard:** authorizes before handler lookup; no arbitrary
  shell command or path is exposed.
- **Workspace manager:** confines declared changes to a workflow workspace.
- **Verifier:** runs build, unit-test, limited secret-scan, and documentation
  gates.
- **Evidence/state:** hashes artifacts, records transitions, and verifies the
  persisted state projection on load.

## Requirements and supported platform

- Windows 11 — verified
- PowerShell 7 (`pwsh`) — verified
- Python 3.11 or newer
- Git

The core is Python. Judge Mode is currently verified only on Windows 11. The
project does not describe workflow isolation as an OS sandbox.

## Commands

```powershell
# Build Week judge path
pwsh -NoProfile -File .\scripts\build-week-demo.ps1

# Canonical demo
python -m thekey demo

# Focused and full tests
python -m pytest -q tests\test_phase_b_rbac_v2_models.py `
  tests\test_phase_b_rbac_v2_guard.py `
  tests\test_phase_b_rbac_v2_integration.py
python -m pytest -q

# Separate-process lifecycle
python -m thekey run create --title "Fix calculator.add"
python -m thekey run plan --run-id <RUN_ID>
python -m thekey run approve-plan --run-id <RUN_ID>
python -m thekey run execute --run-id <RUN_ID>
python -m thekey run verify --run-id <RUN_ID>
python -m thekey evidence verify --run-id <RUN_ID>
```

## Build Week provenance and use of Codex

The public repository begins after the event cutoff even though the owner says
the project existed earlier. [BUILD_WEEK_CONTRIBUTION.md](BUILD_WEEK_CONTRIBUTION.md)
therefore separates verified work in this Codex thread from unresolved earlier
provenance instead of presenting the first public commit as entirely new.

Codex was used for codebase inspection, architecture and adversarial analysis,
implementation, AST caller verification, RED→GREEN testing, regression,
rollback preparation, and documentation. moli retained the decisions about
authority, scope, LIVE_E, push, merge, release, video publication, and final
submission.

- GPT-5.6 development evidence: `PENDING_SESSION_METADATA_VERIFICATION`
- Primary Codex `/feedback` Session ID: `PENDING_REAL_FEEDBACK_SESSION_ID`
- Public YouTube video: `PENDING_PUBLIC_YOUTUBE_URL`

These placeholders must be replaced with real evidence. THEKEY does not claim
a GPT-5.6 runtime integration.

## Security boundaries and limitations

- Workflow isolation is not process or OS isolation.
- The included sovereign grant is not production authorization: the binder
  requires `JUDGE_MODE_DEMO_ONLY`, the canonical demo's exact path and normalized-text SHA-256,
  isolated-workspace-only output, and `production_reuse=false`. It remains a
  transparent local grant, not a cryptographic human signature.
- SHA-256 evidence is tamper-evident within the implemented chain; it is not
  invulnerable or a substitute for external attestation.
- The built-in secret scan is deliberately limited.
- The action registry and Judge Mode cover a bounded demonstration, not
  arbitrary repository repair.
- `CANONICAL_SOURCE_STATUS` remains `UNRESOLVED`; `FULL_CHECKMATE` is `FALSE`.

See [THREAT_MODEL.en.md](THREAT_MODEL.en.md) and [SECURITY.md](SECURITY.md).

## License

THEKEY is distributed under the [MIT License](LICENSE).
