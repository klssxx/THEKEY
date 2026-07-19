# THEKEY
## THE KING OF CHECKMATE

**Governed Codex Transactions for Coding Agents**

Official public name: **THEKEY — THE KING OF CHECKMATE**.

> Every agentic change gets a plan identity, explicit authorization,
> deterministic gates, and reviewable evidence.

[Español](README.md) · [Judge quickstart](docs/build-week/JUDGE_QUICKSTART.md) ·
[Build Week contribution](BUILD_WEEK_CONTRIBUTION.md) ·
[Build Week delta](docs/build-week/BUILD_WEEK_DELTA.md) ·
[Security](SECURITY.md) · [MIT License](LICENSE)

Current release: `0.2.0`.

## The problem

Coding agents can change a repository quickly, but a team may still be unable
to answer four basic questions: which plan was approved, who authorized its
physical execution, what actually ran, and why the result was eligible for
release. THEKEY makes those questions part of the transaction instead of an
after-the-fact narrative.

## What THEKEY is — and is not

The canonical public hierarchy separates four responsibilities:

- **THEKEY:** the product and governed-transaction core.
- **THE KING:** the phase-and-context orchestrator; it cannot self-approve or
  bypass the `PolicyEngine`.
- **CHECKMATE:** adversarial pre-execution review; it analyzes risk and issues a
  verdict, but performs no physical writes.
- **Codex with GPT-5.6:** the agent used to analyze, build, test, and improve the
  project; it is not a runtime dependency.

THEKEY is a small Python governance layer for coding-agent changes. It binds a
plan, a CHECKMATE pre-action review, explicit human authority, a deterministic
policy decision, physical handlers, four verification gates, and persisted
evidence to one run and transaction.

It provides workflow isolation, deterministic policy authorization, and
fail-closed dispatch. It is not an operating-system sandbox. It is not a
general-purpose repair agent, a cryptographic human-signature system, or an
external attestation service.

## Judge Mode in about three minutes

Verified platform: Windows 11, PowerShell 7, Python 3.11 or newer, and Git.

```powershell
git clone https://github.com/klssxx/THEKEY.git
cd THEKEY
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -e .
pwsh -NoProfile -File .\scripts\build-week-demo.ps1
pwsh -NoProfile -File .\scripts\verify-build-week-evidence.ps1
```

No API key, paid service, Docker, WSL, GPU, private dependency, or test account
is required. Judge Mode creates a temporary Git repository under the ignored
`.thekey` directory, repairs one controlled defect only in an isolated runtime,
executes the real governance path, and leaves the source repository unchanged.

Expected summary:

```text
THEKEY BUILD WEEK JUDGE MODE
ALLOW: APPLIED, handlers=1
DENY: ROLE_NOT_ALLOWED, handlers=0
GATES: 4/4 PASS
DECISION: RELEASE_ELIGIBLE
SOURCE: unchanged=True
RECEIPTS: bound=True
PRODUCTION REUSE: False
```

The verifier parses the JSON and persisted receipts; it does not accept the
printed summary as proof. It checks one ALLOW handler, zero DENY handlers, an
unchanged source and denied-workspace hash, four passing gates, receipt binding,
`production_reuse=false`, and the persisted release decision. See the
[judge quickstart](docs/build-week/JUDGE_QUICKSTART.md) for troubleshooting and
cleanup.

## Transaction flow

```text
Mission plan
  → CHECKMATE pre-action receipt
  → scoped sovereign authorization receipt
  → PolicyEngine decision
  → physical dispatch guard
  → one declared handler
  → build, unit-test, secret-scan, documentation gates
  → release decision and reviewable evidence
```

The physical guard validates a strict Pydantic `ActionContext` before handler
lookup. Both persisted receipts must agree on run ID, transaction ID, and plan
SHA-256. Authorization ID, policy version, policy-bundle hash, role, verdict,
and action scope must also agree. Only `Role.EXECUTOR` may cross the boundary.
Missing or extra fields, mismatches, non-executor roles, `PENDING`, `DEFER`,
`FAIL`, policy exceptions, malformed decisions, or ALLOW without a decision ID
all fail closed.

`ActionReviewVerdict` is a pre-execution CHECKMATE result. `ReleaseDecision` is
created only after the gates and is never reused retroactively as authority.

## Architecture

- **THE KING (orchestrator):** coordinates phases and context, persists run
  artifacts, and rehydrates a transaction without self-approval or bypassing
  the `PolicyEngine`.
- **CHECKMATE reviewer:** analyzes risk and emits a pre-action receipt for the
  bounded plan; it performs no physical writes.
- **Sovereign grant binder:** binds moli's explicit, repository-visible Judge
  Mode grant to one source, run, transaction, and isolated output scope.
- **PolicyEngine:** returns `allowed`, a reason code, a decision ID, and the
  preserved policy-bundle hash.
- **Physical dispatch guard:** authorizes before handler lookup and exposes no
  arbitrary shell or path resolution.
- **Workspace manager:** confines declared changes to a workflow workspace.
- **Verifier:** runs build, unit-test, limited secret-scan, and documentation
  gates.
- **Evidence/state:** hashes artifacts, records transitions, and verifies the
  persisted state projection when it is loaded.

## Other commands

```powershell
# Full regression
.\.venv\Scripts\python.exe -m pytest -q

# Canonical lifecycle demo
.\.venv\Scripts\python.exe -m thekey demo

# Equivalent after activating the environment
python -m thekey demo

# Separate-process lifecycle
.\.venv\Scripts\python.exe -m thekey run create --title "Fix calculator.add"
.\.venv\Scripts\python.exe -m thekey run plan --run-id <RUN_ID>
.\.venv\Scripts\python.exe -m thekey run approve-plan --run-id <RUN_ID>
.\.venv\Scripts\python.exe -m thekey run execute --run-id <RUN_ID>
.\.venv\Scripts\python.exe -m thekey run verify --run-id <RUN_ID>
.\.venv\Scripts\python.exe -m thekey evidence verify --run-id <RUN_ID>
```

## OpenAI Build Week contribution and Codex collaboration

THEKEY is explicitly declared a preexisting project. The public Git graph
available from `origin/main` begins after the event cutoff, so the owner's
pre-public statement is `CLAIM_RECORDED` and historical records not yet
imported are `PENDING_EVIDENCE_IMPORT`, never verified pre-cutoff proof. The
repository baseline already contained the governed lifecycle, workflow
workspaces, policy and gates, evidence store, CLI, and calculator demo.

Only the verifiable post-baseline extension is presented for evaluation. See
[BUILD_WEEK_CONTRIBUTION.md](BUILD_WEEK_CONTRIBUTION.md), the
[delta](docs/build-week/BUILD_WEEK_DELTA.md), and the
[pre-public provenance declaration](docs/build-week/PRE_PUBLIC_PROVENANCE.md).

In the primary Codex thread, Codex with GPT-5.6 was used to inspect the
codebase, design and implement strict receipts and the fail-closed physical
guard, rebase all five physical callers, create adversarial tests, harden the
non-reusable demo grant, run RED→GREEN and regression cycles, verify rollback
and clean-clone reproduction, and prepare judge materials. GPT-5.6 accelerated
the security analysis and implementation work; it is development tooling, not
a runtime dependency of THEKEY.

moli retained the product and authority decisions: human sovereignty, bounded
scope, no production reuse of the demo grant, no change to `LIVE_E`, and
separate approval for push, merge, release, video publication, and Devpost
submission.

- Verified primary `/feedback` Session ID:
  `019f79f2-6a7e-74f0-b1fa-d65335b29a7c`
- Local session metadata records `gpt-5.6-luna` and `gpt-5.6-sol` during the
  implementation and verification thread.
- Public sanitized record:
  [CODEX_SESSION_EVIDENCE.md](docs/build-week/CODEX_SESSION_EVIDENCE.md)

## Security boundaries and limitations

- Judge Mode is verified on Windows 11; other platforms are not claimed.
- Workflow isolation is not process or operating-system isolation.
- The local grant is repository-visible and bound to
  `JUDGE_MODE_DEMO_ONLY`, the canonical normalized-text SHA-256, and
  `ISOLATED_RUN_WORKSPACE_ONLY`; it is not a cryptographic human signature.
- SHA-256 makes the implemented evidence chain tamper-evident, not invulnerable
  and not externally attested.
- The built-in secret scan is deliberately limited.
- Judge Mode demonstrates a bounded action registry, not arbitrary repair.
- Very deep Windows paths can exceed path-length limits; use a short clone path.
- The Phase-B manifest retains the legacy
  `CANONICAL_SOURCE_STATUS=PROVENANCE_UNRESOLVED`; the provenance dossier uses
  `CLAIM_RECORDED` and `PENDING_EVIDENCE_IMPORT` for pre-public history.
  `FULL_CHECKMATE=false` and `MACRO_PACK_2=NOT_STARTED`.

See [THREAT_MODEL.en.md](THREAT_MODEL.en.md), [SECURITY.md](SECURITY.md), and the
[final adversarial audit](docs/build-week/CHECKMATE_FINAL_AUDIT.md).

## License

THEKEY is distributed under the [MIT License](LICENSE). Direct dependency
licenses were checked for this candidate; this is not a claim of a complete
transitive supply-chain audit.
