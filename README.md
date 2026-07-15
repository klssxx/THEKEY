# THEKEY Core Governed Run

**THEKEY Core Governed Run** is a lightweight engine for governed software
changes. It separates planning, execution, verification, and approval, applies
versioned policies as code, and produces verifiable evidence for every run.

This repository is the **OSS release 0.2.0** — a single, complete governed
change pipeline that runs **100% autonomously** (no prompts, no human in
the loop by default) and **deterministically without any AI or external API**.

## Autonomous by default

The pipeline approves its own plan with a deterministic, hash-bound local
identity and runs every gate to completion. No one is asked to click "approve".
If a mandatory gate fails, the run is `BLOCKED` with a stable exit code —
the automation cannot choose to skip a gate, because there is no such branch.

```text
SUBMITTED -> BASELINED -> ANALYZED -> PLAN_PROPOSED -> PLAN_APPROVED
          -> IMPLEMENTED -> TESTED -> RELEASE_ELIGIBLE
```

with `BLOCKED`, `FAILED`, and `ROLLED_BACK` as legal terminal/recovery states.

Every step is validated, every state transition is recorded in an
**append-only, hash-chained SQLite event store**, and every artifact is hashed
so a third party can independently verify the final decision (and detect any
tampering).

## What problem it solves

Software changes are usually a blur of "someone edited something, tests ran, we
shipped." THEKEY Core makes the change **governed**:

* Planning, execution, verification, and approval are separate roles.
* Changes happen only in an **isolated workspace** — the original is never touched.
* A **policy** defines the mandatory gates (build, tests, secret scan, docs).
* The **decision** (RELEASE_ELIGIBLE / BLOCKED) is derived deterministically from
  gates + evidence, never from a global score or a "VERIFIED" stamp.

## What it does NOT do

THEKEY Core is **not**:

* A generic application generator.
* Only a collection of prompts.
* An enterprise authorization platform.
* A complete security sandbox.
* A guarantee that software is fully secure.
* A replacement for human review in critical projects.
* A system that approves through a global score.
* A system that uses `VERIFIED` as a universal status.

---

## Installation

Requires **Windows 11**, **PowerShell 7**, and **Python 3.11+**. No Docker, no
WSL, no GPU, no paid service, no external API after dependencies install.

```powershell
cd TheKeyCore_Governed_OSS
.\scripts\bootstrap.ps1        # creates .venv and installs the package + dev deps
```

Or manually:

```powershell
python -m venv .venv
.venv\Scripts\python -m pip install -e ".[dev]"
```

## Quick start (autonomous)

Run the canonical governed demo — it approves itself and finishes with no input:

```powershell
.venv\Scripts\python -m thekey demo
```

Or use the MiMo autonomous launcher (same pipeline, actor-profile aware):

```powershell
.venv\Scripts\python -m thekey-mimo
```

Both exit 0 on `RELEASE_ELIGIBLE` and non-zero on `BLOCKED`.

## One-command demo

```powershell
.\scripts\bootstrap-and-demo.ps1
```

## Manual workflow

```powershell
# 1. Create a run
.venv\Scripts\python -m thekey run create --title "Fix calculator.add"
# Capture the run id from the output, e.g. TK-20260715-...-ABC123

# 2. Baseline + plan
.venv\Scripts\python -m thekey run plan --run-id <RUN_ID>

# 3. Approve
.venv\Scripts\python -m thekey run approve-plan --run-id <RUN_ID>

# 4. Execute in the isolated workspace
.venv\Scripts\python -m thekey run execute --run-id <RUN_ID>

# 5. Verify gates
.venv\Scripts\python -m thekey run verify --run-id <RUN_ID>

# 6. Status + evidence
.venv\Scripts\python -m thekey run status --run-id <RUN_ID>
.venv\Scripts\python -m thekey evidence verify --run-id <RUN_ID>
```

## Run lifecycle

| State | Meaning |
|-------|---------|
| SUBMITTED | Run created, no work yet. |
| BASELINED | Original source hashed and captured. |
| ANALYZED | Defect detected, analysis recorded. |
| PLAN_PROPOSED | Planner proposed exactly one operation. |
| PLAN_APPROVED | Approver accepted the plan (local identity). |
| IMPLEMENTED | Operation applied in the isolated workspace. |
| TESTED | All gates executed. |
| RELEASE_ELIGIBLE | Policy + evidence satisfied. |
| BLOCKED | A gate failed, evidence missing, or policy invalid. |
| FAILED | Execution error not recoverable inline. |
| ROLLED_BACK | Changes reverted. |

## Artifacts (per run, under `runs/<RUN_ID>/`)

* `manifest.json`, `request.json`
* `plan.json`, `approvals.json`
* `changes.diff`
* `gates.json`, `decision.json`
* `artifact-hashes.json` (SHA-256 of principal artifacts)
* `evidence/` (per-evidence records with hashes)
* `.thekey/state-transitions.jsonl` (repo-level, append-only)

## Gates (from `governance/policies/local-python-demo.yaml`)

* `BUILD_PASSED` — `compileall` over the workspace sources.
* `UNIT_TESTS_PASSED` — full `pytest` over the workspace tests.
* `SECURITY_GATE_PASSED` — limited, honest secret scan (see SECURITY.md).
* `DOCUMENTATION_GATE_PASSED` — workspace ships README + a test module.

A failed **mandatory** gate cannot be offset by any other score.

## Decision

The Release Decision Engine evaluates the mandatory gates against the policy.
If all gates pass and all required evidence is present → `RELEASE_ELIGIBLE`;
otherwise → `BLOCKED` (with the concrete reason: failed gate, missing evidence,
or tampered evidence).

## Limitations

See [SECURITY.md](SECURITY.md) and [GOVERNANCE.md](GOVERNANCE.md). In short:
simplified local approval identity, basic secret scanning, no strong process
sandbox, no cryptographic human identities, no multi-developer concurrency, no
mandatory external AI, and no enterprise guarantee.

## Tests

```powershell
.venv\Scripts\python -m pytest -q
```

## Contribution

See [CONTRIBUTING.md](CONTRIBUTING.md).

## For contributors — why it is safe to automate

THEKEY Core is built so that **automation cannot cheat**:

* Original source is immutable; only isolated workspaces are written.
* Approval is automatic and hash-bound, never a prompt.
* Evidence is SHA-256 sealed; a tampered artifact makes the run `BLOCKED`, never silent.
* The verifier reproduces proof (build + tests) in isolation; it does not trust the implementer.
* No arbitrary shell, no external API, no model-generated commands.
* Every run is auditable: `thekey history verify` + `thekey evidence verify`
  reconstruct integrity from on-disk artifacts, not from memory.

Good first issues: add a policy, add a verifier profile, extend the NPSC
adapter, or strengthen the secret-scan gate. See `THEKEY_CONTRACT.md`.
