# Issue Backlog

Prioritized issue backlog for THEKEY Core Governed Run. Each issue is ready to
be opened as a GitHub issue (see `.github/ISSUE_TEMPLATE/`). Do **not** publish a
remote repository or open issues without explicit authorization.

## P0 — MVP foundations (status: DONE in 0.1.0)

1. **OSS scaffold and scope contract**
   * Context: Establish repo layout, packaging, license, and a written scope boundary.
   * Problem: No single source of truth for what the MVP is and is not.
   * Scope: README, CONTRIBUTING, GOVERNANCE, pyproject, package shell, license.
   * Out of scope: enterprise features, GUI, AI integration.
   * Acceptance: `pip install -e .` works; README defines not-do list.
   * Tests: package imports; CLI `--help`.
   * Priority: P0. Labels: `scaffold`.

2. **Persistent run model**
   * Context: Each run needs a unique id + artifact directory.
   * Acceptance: `TK-YYYYMMDD-HHMMSS-XXXXXX` ids; `runs/<RUN_ID>/` artifacts.
   * Tests: `tests/unit/test_state_machine.py` (ids unique, atomic writes).
   * Priority: P0. Labels: `run-model`.

3. **Governed state machine**
   * Context: Legal/illegal transitions must be the single source of truth.
   * Acceptance: main flow + BLOCKED/FAILED/ROLLED_BACK; hash chain.
   * Tests: `test_state_machine.py`.
   * Priority: P0. Labels: `state-machine`.

4. **Policy as code**
   * Context: Gates and limits declared as validated YAML.
   * Acceptance: JSON Schema validation; invalid policy stops the run.
   * Tests: `test_policies.py`.
   * Priority: P0. Labels: `policy`.

5. **Stateless HY3 context builder**
   * Context: HY3 must receive only freshly built context, no chat history.
   * Acceptance: minified state, <=3 events, token budgets, kernel preserved.
   * Tests: `test_context_builder.py`.
   * Priority: P0. Labels: `context-builder`.

6. **Restricted output validator**
   * Context: HY3 output must be parsed safely and validated before any write.
   * Acceptance: terminator, exact keys/order, stale-hash rejection.
   * Tests: `test_output_validator.py`.
   * Priority: P0. Labels: `validator`.

7. **Role separation**
   * Context: Planner/Executor/Verifier/Approver have disjoint authority.
   * Acceptance: permission matrix enforced; negative tests.
   * Tests: `test_roles.py`.
   * Priority: P0. Labels: `roles`.

8. **Workspace isolation and path safety**
   * Context: All writes confined to the workspace; no traversal.
   * Acceptance: traversal/sibling/prefix/protected/reparse rejected.
   * Tests: `test_path_security.py`.
   * Priority: P0. Labels: `security`.

9. **Closed action registry**
   * Context: Model requests only fixed action IDs.
   * Acceptance: no arbitrary shell; role-scoped actions.
   * Tests: `test_roles.py` (action matrix).
   * Priority: P0. Labels: `actions`.

10. **Evidence and hash verification**
   * Context: Evidence created from observed results; tampering detected.
   * Acceptance: SHA-256 per artifact; sealed-artifact tamper check.
   * Tests: `test_evidence.py`, `test_e2e.py`.
   * Priority: P0. Labels: `evidence`.

## P1 — Demonstrate the governed change

11. **Canonical deterministic Planner** — done (`roles/planner.py`).
12. **Executor exact-text operation** — done (`actions.py`, `roles/executor.py`).
13. **Verifier gates** — done (`gates.py`, `roles/verifier.py`).
14. **Positive E2E** — done (`tests/e2e/test_e2e.py`).
15. **Blocked E2E** — done (4 blocked scenarios in `main.py`).
16. **PowerShell quickstart** — done (`scripts/bootstrap-and-demo.ps1`).
17. **Recovery protocol** — done (`recovery.py`, `test_recovery.py`).

## P2 — Post-MVP

18. **Windows GitHub Actions** — `.github/workflows/tests.yml` (present, enable on remote).
19. **Stronger secret scanning** — entropy + secret managers.
20. **Optional HY3 adapter** — plug stateless HY3 operator behind context builder.
21. **Evidence signing** — sign evidence records.
22. **Strong identities** — cryptographic approver identity.
23. **Smoke-test profile** — `LAUNCH_SMOKE_TEST` for runtime apps.
24. **Additional project types** — Go/Rust/JS demos.
