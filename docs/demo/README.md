# Canonical Demo Walkthrough

The canonical demo fixes one intentional defect in
`examples/demo_app/calculator.py`:

```python
def add(a: int, b: int) -> int:
    return a - b   # DEFECT: should be addition
```

while the test expects `add(2, 3) == 5`.

## Step by step

1. **Create run** — `RunCoordinator.create()` generates `TK-...` and transitions
   `SUBMITTED -> BASELINED`.
2. **Baseline** — the original source is hashed; `baseline.json` recorded.
3. **Plan** — the deterministic Planner detects `return a - b` inside `add` and
   proposes exactly one `REPLACE_EXACT_TEXT` operation
   (`return a - b` → `return a + b`). The Planner writes nothing to the source.
4. **Approve** — the Approver accepts the plan via the simplified local identity.
5. **Execute** — the Executor copies the original into the isolated workspace
   `workspaces/<RUN_ID>/` and applies the replacement **only there**.
6. **Diff** — `changes.diff` shows original (untouched) vs repaired workspace.
7. **Verify** — the Verifier runs the four gates (build, unit tests, secret
   scan, documentation). It never modifies the workspace code.
8. **Decide** — the Decision Engine sees all gates pass and all required
   evidence present → `RELEASE_ELIGIBLE`.
9. **Evidence verify** — artifact hashes are checked against
   `artifact-hashes.json`; any tamper would block the run.

## What stays intact

* `examples/demo_app/calculator.py` remains defective (the MVP never "fixes"
  the original — only the workspace copy).
* The historical THEKEY path is never touched.

## Blocked variants

* `--blocked-mode invalid_policy` → policy schema failure, exit 4.
* `--blocked-mode failed_gate` → `UNIT_TESTS_PASSED` fails, exit 5.
* `--blocked-mode tampered_evidence` → changes.diff tamper detected, exit 5.
* `--blocked-mode missing_input` → required source input missing, exit 5.
