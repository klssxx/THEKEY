# Architecture

THEKEY Core Governed Run splits authority between a **control plane** (the
orchestrator that validates and persists) and an **execution plane** (the roles
that request and perform work).

```
                         ┌─────────────────────────────┐
   thekey CLI ─────────► │     Run Coordinator          │  (control plane)
                         │  - validates every step      │
                         │  - applies state transitions │
                         │  - writes evidence + state   │
                         └──────┬───────────┬───────────┘
                                │           │
              ┌─────────────────┘           └─────────────────┐
              ▼                                               ▼
   ┌──────────────────┐                        ┌──────────────────────┐
   │ State Machine     │                        │ Context Builder       │
   │ (legal transitions│                        │ (minified state,      │
   │  + SHA-256 chain) │                        │  token budgets,       │
   └──────────────────┘                        │  no chat history)     │
                                               └──────────┬───────────┘
                                                          │ builds context
                                                          ▼
                                               ┌──────────────────────┐
                                               │ HY3 Operator (opt.)   │
                                               │  stateless phase agent│
                                               │  returns restricted   │
                                               │  YAML only            │
                                               └──────────┬───────────┘
                                                          │ restricted YAML
                                                          ▼
                                               ┌──────────────────────┐
                                               │ Output Validator       │
                                               │  (terminator, schema,  │
                                               │   binding, role,       │
                                               │   action, transition)  │
                                               └──────────────────────┘

   Execution plane (request work, never persist):
     PLANNER → EXECUTOR → VERIFIER            APPROVER (decision owner)
```

## Authoritative state

* `.thekey/state.json` — atomic, canonical, SHA-256 hashed.
* `.thekey/state-transitions.jsonl` — append-only transition log.
* `.thekey/state-history.jsonl` — recent validated events (max 3 used in context).

## Evidence

* `runs/<RUN_ID>/evidence/*.json` — one record per produced artifact, with hash.
* `runs/<RUN_ID>/artifact-hashes.json` — SHA-256 of principal artifacts.
* Sealed artifacts (changes.diff, baseline.json, approvals.json) are re-checked
  before the release decision; tampering blocks the run.

## Policy as code

* `governance/policies/local-python-demo.yaml` validated against
  `governance/schemas/policy.schema.json`.
* An invalid policy stops execution and never executes the plan.

See [GOVERNANCE.md](../GOVERNANCE.md) for role separation and decision ownership.
