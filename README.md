# THEKEY Core Governed Run

**THEKEY Core Governed Run** is a lightweight engine for governed software
changes. It separates planning, execution, verification, and approval, applies
versioned policies as code, and produces verifiable evidence for every run.

This repository is the **MVP OSS release 0.1.0** — a single, complete governed
change pipeline that works **deterministically without any AI or external API**.

---

## What THEKEY Core is

A control-plane/orchestration engine that takes one declared change request and
runs it through a fixed, auditable lifecycle:

```
SUBMITTED -> BASELINED -> ANALYZED -> PLAN_PROPOSED -> PLAN_APPROVED
          -> IMPLEMENTED -> TESTED -> RELEASE_ELIGIBLE
```

with `BLOCKED`, `FAILED`, and `ROLLED_BACK` as legal terminal/recovery states.

Every step is validated, every state transition is recorded, and every artifact
is hashed so a third party can independently verify the final decision.

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

## Quickstart (10–15 minutes)

From a clean clone, one command runs the whole governed demo:

```powershell
.\scripts\bootstrap-and-demo.ps1
```

It will create a run, plan the fix, approve it, execute it in an isolated
workspace, run the gates, verify the evidence, and print the final decision
(`RELEASE_ELIGIBLE`). The script returns non-zero if any mandatory step fails.

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
