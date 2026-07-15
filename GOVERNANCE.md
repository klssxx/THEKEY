# Governance

THEKEY Core separates **control plane** from **execution plane**. The control
plane validates, executes privileged operations, records evidence, and changes
authoritative state. The execution plane may request work but never persists
that work happened.

## Control plane

* Run Coordinator
* State Machine
* Policy Engine
* Context Builder
* Output Validator
* Approval Handler
* Evidence Manager
* Release Decision Engine
* Recovery Controller

## Execution plane

* Planner
* Executor
* Verifier
* Workspace Manager
* Closed action handlers
* Safe command handlers

## Role separation

| Role | Reads original | Writes workspace | Approves | Decides |
|------|---------------|-----------------|----------|---------|
| PLANNER | yes | no | no | no |
| EXECUTOR | yes | yes (workspace only) | no | no |
| VERIFIER | no | no | no | no |
| APPROVER | no | no | yes | yes |

The **Executor never modifies the policy, framework, original source, or
approvals**. The **Verifier never modifies product code, weakens tests, or
repairs the implementation**. The **Approver never implements changes**.

## Decision ownership

The Release Decision Engine — not any individual role, and not the HY3 operator —
owns the final RELEASE_ELIGIBLE / BLOCKED decision. It is a deterministic
function of (mandatory gates, required evidence, policy).

## Why implementation and verification are separate

If the same actor implements and verifies, a defect can be hidden by a
self-approved gate. Separating Executor from Verifier makes the gate result
trustworthy: the verifier reads the workspace and the diff, runs the gates, and
reports what it observes — it cannot silently "fix" a failing test.

## Minimal framework-change process

Changing the state machine, validator, or contract schema requires:

1. A GitHub issue describing the change and its governance impact.
2. Updated JSON Schema + tests.
3. A CHANGELOG entry.
4. Review by a maintainer.

Framework changes MUST NOT grant the model the ability to write authoritative
state or evidence directly.
