# THEKEY

## Governed Git transactions for coding agents.

> **THEKEY** · *Transacciones Git gobernadas para agentes de programación.*
> Versión completa en español: [README.md](README.md)

**THEKEY 0.2.0 — Public Preview.** A small, serious core for governed Git
transactions aimed at coding agents, with **workflow isolation**,
**deterministic gates**, and **auditable evidence**.

THEKEY is a small, serious core for governed Git transactions aimed at coding
agents. It provides workflow isolation, deterministic gates, and auditable
evidence. It does not provide OS-level sandboxing.

[![CI](https://img.shields.io/badge/CI-passing-2ea043)](.github/workflows/tests.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue)](LICENSE)
![v0.2.0 Public Preview](https://img.shields.io/badge/v0.2.0-Public%20Preview-orange)
![Python](https://img.shields.io/badge/python-3.11%2B-3776ab)
![Windows 11](https://img.shields.io/badge/Windows-11-0078d4)

> Español: *Transacciones Git gobernadas para agentes de programación ·
> aislamiento de flujo de trabajo, puertas deterministas, evidencia auditable.*
> Versión completa: [README.md](README.md)

It runs agents in isolated workspaces, verifies every change through
deterministic gates, and promotes only results with auditable evidence.
**102 tests, 0 skipped**, demo reproducible on Windows 11 without Docker, WSL,
or GPU.

![THEKEY demo: full cycle PASS + evidence](docs/assets/thekey-demo.gif)

---

## What it is

THEKEY solves a concrete problem: agent-driven software changes are usually a
blurry mix of "someone edited something, tests ran, we shipped." THEKEY makes
the change **governed**.

- **Who it is for:** coding agents, CI pipelines, and teams that want to
  automate code changes with traceability and without touching the original
  source.
- **What it actually does:** it separates planning, execution, verification,
  and policy authorization into distinct roles; it applies the gates defined
  by a policy-as-code; and it produces verifiable evidence for every run.
- **What it does NOT promise:** it is not an OS-level sandbox, it does not
  guarantee total security, it does not replace human review in critical
  projects, and it does not integrate NPSC into the core.

Plan authorization is performed through **deterministic policy authorization**:
the policy defines the mandatory gates and the decision (`RELEASE_ELIGIBLE` /
`BLOCKED`) is derived deterministically from gates and evidence, never from a
global score or a "VERIFIED" stamp. There is no interactive "human approval"
step by default; authorization is a consequence of the policy and the plan
hash.

## Project status

- **THEKEY 0.2.0 — Public Preview.**
- This is a *public preview*, not a work in progress (WIP).
- The core is kept intentionally small.
- **Phase C does not begin before the public launch.**

## Quick start (Windows 11)

```powershell
git clone <URL_DEL_REPOSITORIO>
cd THEKEY
pwsh -NoProfile -File .\scripts\demo.ps1
```

## Minimal prerequisites

Only what is necessary to run the demo:

- **Windows 11**
- **PowerShell 7** (`pwsh`) — already present on Windows 11; the script does
  not modify the execution policy.
- **Python 3.11+** on `PATH`.
- No Docker, no WSL, no GPU, no paid service, no external API after installing
  dependencies.

The script `scripts/demo.ps1` creates or reuses `.venv`, installs the project
with `pip install -e .`, and runs `python -m thekey demo`. It is idempotent,
does not require administrator privileges, and returns the real exit code from
the demo.

## What the demo does

The canonical demo creates a governed run over a sample project
(`examples/demo_app`), plans it, authorizes it by policy, executes it in an
isolated workspace, verifies the gates, and emits the decision. It ends with
`decision: RELEASE_ELIGIBLE` and `gates_passed: 4` when everything is correct.
Real output from a verified run:

```text
run_id: TK-20260715-...-XXXXXX
state: RELEASE_ELIGIBLE
decision: RELEASE_ELIGIBLE
gates_passed: 4
gates_total: 4
evidence_mismatches: []
workspace: ...\workspaces\TK-20260715-...-XXXXXX
run_path: ...\runs\TK-20260715-...-XXXXXX
```

The demo requires no user input and needs no network or models.

## Architecture in 5 minutes

- **Governed transaction:** a unit of software change that traverses explicit
  states (SUBMITTED → BASELINED → ANALYZED → PLAN_PROPOSED → PLAN_APPROVED →
  IMPLEMENTED → TESTED → RELEASE_ELIGIBLE) with recovery states (`BLOCKED`,
  `FAILED`, `ROLLED_BACK`).
- **Workflow-isolated workspace:** changes are only applied in a controlled
  workspace; the original source is never touched.
- **Deterministic gates:** a policy declares mandatory gates (build, tests,
  secret scan, documentation). A failed mandatory gate cannot be offset by any
  other metric.
- **Deterministic policy authorization:** the plan is authorized from the
  policy and the plan hash; there is no interactive approval and no global
  score.
- **Auditable evidence:** every state transition is recorded in an
  append-only, hash-chained SQLite event store; every artifact is hashed
  (SHA-256) so a third party can verify the decision and detect tampering.
- **Optional read-only adapters:** NPSC is an example of an external
  read-only adapter. The core does not conceptually depend on NPSC in order to
  exist.

## Guarantees and limits

THEKEY provides **workflow isolation**, not OS-level sandboxing. The repository
**does not promise total security**. Guarantees depend on configuration, the
host environment, and the implemented gates. NPSC is optional and not part of
the core.

Current (honest) limitations: simplified local authorization identity, limited
secret scanning, no strong process sandbox, no cryptographic human identities,
no multi-developer concurrency, no mandatory external AI, and no enterprise
guarantee. See [THREAT_MODEL.en.md](THREAT_MODEL.en.md) and
[SECURITY.md](SECURITY.md).

## Commands

All commands below are validated in this release.

```powershell
# Canonical demo (deterministic policy authorization, no input)
python -m thekey demo

# MiMo autonomous launcher (same pipeline, actor-profile aware)
python -m thekey-mimo

# Manual flow
python -m thekey run create --title "Fix calculator.add"
python -m thekey run plan --run-id <RUN_ID>
python -m thekey run approve-plan --run-id <RUN_ID>
python -m thekey run execute --run-id <RUN_ID>
python -m thekey run verify --run-id <RUN_ID>
python -m thekey run status --run-id <RUN_ID>
python -m thekey evidence verify --run-id <RUN_ID>

# Core tests
python -m pytest -q
```

Both `python -m thekey demo` and `python -m thekey-mimo` exit 0 on
`RELEASE_ELIGIBLE` and non-zero on `BLOCKED`.

## Development

Read [CONTRIBUTING.en.md](CONTRIBUTING.en.md) to set up the environment, run
the tests, and propose changes. For the security model, see
[SECURITY.md](SECURITY.md).

## Threat model

The realistic security analysis is in [THREAT_MODEL.en.md](THREAT_MODEL.en.md).
It covers objectives, protected assets, trust boundaries, attack surface,
present and missing mitigations, and explicit limitations.

## Roadmap / initial backlog

The initial backlog is organized into three categories (without starting Phase
C in code):

- **Onboarding / good first issue:** approachable tasks for new contributors
  (for example, the ES/EN README parity gate, improved error messages in
  `scripts/demo.ps1`, and the forbidden-language check in normative docs).
- **Practical extensions / help wanted:** additional read-only adapters,
  improved exportable evidence format, and Windows 11 / path-with-spaces
  hardening for auxiliary tooling.
- **RFC / future architecture:** a formal contract for read-only adapters for
  external providers, and a preliminary design for Phase C/D.

## License

Distributed under the MIT license. See [LICENSE](LICENSE).
