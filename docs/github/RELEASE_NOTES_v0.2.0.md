# THEKEY Core — Release Notes v0.2.0 (DRAFT — local only)

Status: **DRAFT, not published.** No tag, no push, no release created.
Scope: THEKEY Core Governed Run **0.2.0 only**. NPSC is NOT part of this
release evidence (see §5).

## 1. Version state

- Version: `0.2.0`
- Verified commit: `ebb0770`
- Current state: `RELEASE_ELIGIBLE` (deterministic, from the governed
  pipeline). **Pending human approval + publication.**

## 2. Real changes (in THEKEY Core 0.2.0)

Capabilities added:
- **100% autonomous run.** The plan is approved automatically by a
  deterministic, hash-bound local identity. No human prompt in the default
  flow. (`approve_plan` auto-approves; the `WAITING_FOR_HUMAN_APPROVAL`
  state is retained in the machine as an opt-in transition, not the default.)
- **Append-only, hash-chained SQLite event store** (`event_store.py`)
  records every state transition; `verify_chain()` detects tampering.
- **review_token** (`decisions.py`): a deterministic, unforgeable-without-
  inputs token embedded in `decision.json`; `verify_review_token` rejects
  a forged/tampered decision body.
- **NPSC read-only adapter** (`adapters/npsc_adapter.py`): maps NPSC
  output (`recommended_output_contract` / `output_contract` / `constraints`)
  into a THEKEY `ActorContext`. Never executes or mutates NPSC.
- **MiMo actor profile + contract** (`mimo_profile.py`, `THEKEY_CONTRACT.md`):
  the implementer contract — writes only in isolated workspace, never the
  original source, no arbitrary shell.
- **Autonomous launcher** (`launchers/mimo_launcher.py`, `thekey-mimo`):
  runs the full pipeline with no prompts; refuses to run if the runtime root
  sits inside a protected historical THEKEY path (guard, exit 8).
- **JSON schemas** (`governance/schemas/`): Mission, ActorContext,
  ExecutionEvidence, ReviewDecision.

Gates / lifecycle:
- Mandatory gates unchanged and enforced: BUILD_PASSED, UNIT_TESTS_PASSED,
  SECURITY_GATE_PASSED, DOCUMENTATION_GATE_PASSED. A failed mandatory
  gate cannot be offset by any other score → BLOCKED with stable exit code.

Fixes derived from adversarial tests:
- An **empty plan** no longer raises dangling; it flows to the verifier gates
  which BLOCK it (complete auditable trail, no silent release).
- (Adversarial coverage added — see §3.)

## 3. Verification evidence

- `python -m compileall src` → **OK**
- `python -m pytest -q` → **102 passed**
  - 89 baseline (preserved from 0.1.0)
  - 9 automation-surface (schemas, NPSC adapter, review_token, MiMo launcher)
  - 4 adversarial:
    - tampered sealed artifact → BLOCKED (never silent)
    - forged review_token fails `verify_review_token`
    - launcher guard refuses a protected historical root
    - empty plan never reaches RELEASE_ELIGIBLE
- `python -m thekey demo` → exit **0**, decision `RELEASE_ELIGIBLE`, **4/4 gates**,
  evidence_mismatches `[]`
- `python -m thekey-mimo` → exit **0** (autonomous)
- `python -m thekey history verify` → `integrity_status: VALID`
- `python -m thekey evidence verify` → `evidence_ok: true`
- Tree is clean: no runtime state (`.thekey/`, `runs/`, `workspaces/` gitignored),
  no tokens / secrets / private paths in the tracked tree (129 files).

## 4. Guarantees and limits

- This system is **NOT** infallible, fully secure, or production-ready
  without supervision. It is a deterministic governance control plane.
- **No model can self-approve.** Approval is a deterministic local identity
  bound to the plan hash; it is not a cognitive sign-off. The gates — not
  any actor — decide release eligibility.
- Risk-bearing operations stay subject to the mandatory gates and to human
  approval where the operator opts into `WAITING_FOR_HUMAN_APPROVAL`.
- THEKEY Core and NPSC are distinct. THEKEY Core is the governed runtime;
  NPSC is an external compiler consumed only through the read-only adapter.

## 5. NPSC hardening — PENDING

Work on NeuroPromptSemanticCompiler is performed **exclusively on an
isolated copy** (`NPSC_REVIEW_EXPORT_20260715-100257/.../current/`). The
protected original has **not** been modified. Nothing from NPSC will be
integrated until the following are validated: the diff, the patched package,
contract alignment, the `--strict` blocking behaviour, the redaction logic,
and regression tests. **This task is NOT part of the THEKEY Core 0.2.0
evidence.** Status: PENDING (background task, not yet completed with
verifiable output).

## 6. Reproducibility (non-destructive commands used)

```powershell
# verify commit
git rev-parse HEAD            # -> ebb0770

# compile
.venv\Scripts\python -m compileall src

# run the 102 tests
.venv\Scripts\python -m pytest -q

# run the autonomous demo
.venv\Scripts\python -m thekey demo

# confirm clean tree (no runtime state / secrets tracked)
git ls-tree -r --name-only HEAD | findstr /i ".thekey/ events.db token secret" || echo clean
```

## 7. Publication artifacts (PENDING placeholders)

- Final package SHA-256: **PENDING**
- Repository URL: **PENDING** (proposed: `THEKEY-Core-Governed-Run`)
- Tag: **PENDING** (proposed: `v0.2.0`)
- Publication date: **PENDING**
- License confirmed: **MIT** (present in tree)

## 8. Honesty rule

Every unproven item above is marked **PENDING** and is not asserted as done.
NPSC hardening is explicitly excluded from THEKEY Core 0.2.0 evidence.
