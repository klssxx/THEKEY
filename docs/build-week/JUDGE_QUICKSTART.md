# THEKEY Build Week Judge quickstart

This is the shortest reproducible path for evaluating THEKEY without an API
key, paid service, Docker, WSL, GPU, private dependency, or test account.

## Two-click portable test build

The primary judge path targets Windows 10 x64 and Windows 11 x64:

1. Extract `THEKEY-Portable-Windows-x64.zip` to a short writable path.
2. Double-click `THEKEY.exe`.
3. Select **Demo para jueces**. That single action runs the governed demo and
   verifies the persisted evidence.

To evaluate the product flow instead, select **SELECCIONAR Y ANALIZAR
APLICACIÓN**, choose a trusted local application, review the read-only
inspection, and then select **Verificar aplicación**. The second action asks
for explicit consent because project tests execute trusted local code in an
isolated copy, not in an operating-system sandbox.

Select **Escanear y reparar** for the complete product path: actionable
diagnosis, bounded repair search, isolated gates, separate source-write
consent, stale-input protection, backup, post-apply verification, and rollback.

The package includes its Python runtime and does not require Python, Git, or
PowerShell 7 on the judge's machine. Its `BUILD_MANIFEST.json` hashes every
distributed file and identifies whether the recorded base commit came from an
exact clean tree or an explicitly marked `DIRTY_BUILD`. See
[Portable Windows test build](PORTABLE_WINDOWS.md) for the full button map and
security boundary.

## Source-install platform

- Windows 11 (verified source-install platform)
- PowerShell 7 (`pwsh`)
- Python 3.11 or newer
- Git

The portable surface additionally targets Windows 10 x64 and Windows 11 x64;
the current candidate is exercised on Windows 11 before publication.

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

## Functional scan-and-repair check

The portable app includes `SAMPLE-PYTHON-APP` for the healthy path. To
demonstrate a real repair, select a trusted Python or Node.js project with its
detected test adapter and a compatible defect, choose **Escanear y reparar**,
and accept the displayed consent. Evidence must end in `NO_CHANGES_NEEDED`,
`REPAIRED_AND_VERIFIED`, or an explicit fail-closed `BLOCKED_*` result.

The source-install equivalent is:

```powershell
.\.venv\Scripts\python.exe -m thekey project repair `
  --source C:\path\to\project `
  --consent execute_trusted_tests `
  --apply-consent apply_verified_repairs
```

THEKEY never changes tests or installs dependencies. It applies only the exact
bytes that passed the adapter build/check, complete detected test suite, bounded
secret scan, and documentation gate; it rechecks hashes first, stores a backup,
and verifies again afterward. A post-apply failure triggers rollback.

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
