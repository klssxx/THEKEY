# THEKEY Build Week Judge quickstart

This is the shortest reproducible path for evaluating THEKEY without an API
key, paid service, Docker, WSL, GPU, private dependency, or test account.

## Verified platform

- Windows 11
- PowerShell 7 (`pwsh`)
- Python 3.11 or newer
- Git

Judge Mode is currently claimed only on that platform.

## Install from a clean clone

```powershell
git clone https://github.com/klssxx/THEKEY.git
cd THEKEY
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -e .
```

## Run and independently verify the evidence

```powershell
pwsh -NoProfile -File .\scripts\build-week-demo.ps1
pwsh -NoProfile -File .\scripts\verify-build-week-evidence.ps1
```

The demo summary must report:

```text
ALLOW: APPLIED, handlers=1
DENY: ROLE_NOT_ALLOWED, handlers=0
GATES: 4/4 PASS
DECISION: RELEASE_ELIGIBLE
SOURCE: unchanged=True
RECEIPTS: bound=True
PRODUCTION REUSE: False
```

The second command parses the generated JSON and persisted run artifacts. A
valid run returns JSON with `status: VALID`, one ALLOW handler, zero DENY
handlers, four gates, `RELEASE_ELIGIBLE`, unchanged source, and production
reuse disabled. It does not trust the printed demo summary.

## What Judge Mode does

1. Creates a temporary Git repository under ignored `.thekey/judge-mode` state.
2. Creates a separate workflow runtime and governed transaction.
3. Binds the CHECKMATE review and scoped sovereign grant to the same run,
   transaction, and plan SHA-256.
4. Applies one declared calculator repair through the real physical guard.
5. Runs build, unit-test, limited secret-scan, and documentation gates.
6. Attempts the same physical action with `Role.SYSTEM`; it must be denied
   before handler execution and leave the workspace unchanged.
7. Persists receipts, the release decision, and `judge-mode-evidence.json`.

The temporary source and the THEKEY checkout remain unchanged. All mutable demo
state stays below ignored runtime directories.

## Python selection and troubleshooting

The demo uses `THEKEY_PYTHON` when explicitly set. Otherwise it tries a working
repository `.venv`, then `python`, then `py -3`. A stale `.venv` is skipped
instead of being selected merely because its launcher exists.

To select a specific installed Python:

```powershell
$env:THEKEY_PYTHON = 'C:\Path\To\Python311\python.exe'
pwsh -NoProfile -File .\scripts\build-week-demo.ps1
```

- If `pwsh` is missing, install PowerShell 7 and open a new terminal.
- If `git init failed` appears, ensure Git is installed and on `PATH`.
- If import resolution fails, rerun the editable-install command with the same
  Python selected for the demo.
- Use a short clone path on Windows; deeply nested paths can exceed platform
  path-length limits.

## Security boundary

This is workflow isolation, not process or operating-system sandboxing. The
local demo grant is transparent repository data, not a cryptographic human
signature. Its subject and output are bounded and `production_reuse` is false.
SHA-256 is tamper-evident inside the implemented chain, not external
attestation. The action registry and secret scan are deliberately limited.

[Versión en español](JUDGE_QUICKSTART.es.md)
