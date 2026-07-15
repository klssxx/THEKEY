# Contributing to THEKEY Core Governed Run

## Environment setup

* Windows 11, PowerShell 7, Python 3.11+.
* No Docker / WSL / GPU / paid service required.

```powershell
.\scripts\bootstrap.ps1
.venv\Scripts\python -m pytest -q
```

## Tests

* Unit, integration, and end-to-end tests live under `tests/`.
* The end-to-end suite runs the real canonical demo and the blocked scenarios.
* New behavior requires a test. Do not weaken tests or remove failing gates to
  obtain a PASS.

## Code style

* `ruff` is configured in `pyproject.toml` (line-length 100).
* Run `ruff check src tests`.
* Type hints and docstrings on every public module/function.

## PR requirements

* Clear description of the governed change.
* All tests green.
* No modification of the protected historical THEKEY path.
* No arbitrary shell exposure; only closed action IDs.
* Evidence/hash verification still passes.

## How to add an action

1. Add the action id to `command_registry.py` with its `ActionKind` and
   `allowed_roles`, plus a handler in `actions.py`.
2. Never expose shell strings or arbitrary paths. Use declared input/output IDs.
3. Add a unit test in `tests/unit/test_roles.py` or `test_path_security.py`.

## How to add a gate

1. Add a `GateResult`-producing runner in `gates.py` and register it in
   `GATE_RUNNERS`.
2. Add the gate code to the allowed set in `governance/schemas/policy.schema.json`.
3. Add a test in `tests/unit/test_verifier.py`.

## How to add a policy

1. Create `governance/policies/<id>.yaml`.
2. It must validate against `governance/schemas/policy.schema.json` (required
   gates, limits, evidence, secret-scan scope, excluded directories).
3. An invalid policy must stop the run and never execute the plan.

## Windows compatibility

* All paths resolved via `pathlib.Path.resolve()`; no POSIX-only assumptions in
  runtime code. PowerShell 7 is the supported shell for scripts.

## Security requirements

* No arbitrary shell from model action IDs.
* Path traversal, sibling-prefix, protected-path, and reparse-point checks are
  mandatory.
* Model output never updates authoritative state or evidence directly.
