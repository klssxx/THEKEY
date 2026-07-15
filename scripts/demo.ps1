<# .SYNOPSIS
    THEKEY 0.2.0 — definitive demo bootstrap for Windows 11.
.DESCRIPTION
    From a clean clone this script:
      1. Locates the repository root reliably (parent of this script's folder).
      2. Detects a compatible Python (>=3.11) on PATH; fails clearly if missing.
      3. Creates .venv at the repo root if missing, reuses it otherwise.
      4. Installs the project with `pip install -e .` (editable, no dev extras).
      5. Executes `python -m thekey demo`.
      6. Returns the real exit code from the demo.
    It is idempotent, does NOT require administrator privileges, and NEVER
    calls Set-ExecutionPolicy. It works from a clean clone located in a
    Windows path that contains spaces.
.NOTES
    Author: THEKEY Core Contributors
#>
[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'

# 1. Locate repo root (parent of the folder containing this script).
$RepoRoot = Split-Path -Parent $PSScriptRoot
Push-Location $RepoRoot
try {
    # 2. Detect + validate Python.
    $py = Get-Command python -ErrorAction SilentlyContinue
    if (-not $py) {
        Write-Error "Python not found on PATH. Install Python 3.11+ and add it to PATH, then re-run."
        exit 1
    }
    $verStr = & python --version 2>&1
    if ($verStr -notmatch '3\.(\d+)') {
        Write-Error "Unexpected Python version string: $verStr"
        exit 1
    }
    $minor = [int]$Matches[1]
    if ($minor -lt 11) {
        Write-Error "Python 3.11+ required, found: $verStr"
        exit 1
    }
    Write-Host "[ok] Python: $verStr"

    # 3. Create or reuse .venv.
    if (-not (Test-Path .venv)) {
        Write-Host "[*] Creating virtual environment in .venv ..."
        & python -m venv .venv
        if ($LASTEXITCODE -ne 0) {
            Write-Error "Failed to create .venv."
            exit 1
        }
    }
    else {
        Write-Host "[*] Reusing existing .venv"
    }

    # 4. Install the project (editable). No dev extras per contract.
    Write-Host "[*] Installing project with 'pip install -e .' ..."
    & .venv/Scripts/python -m pip install -q -e .
    if ($LASTEXITCODE -ne 0) {
        Write-Error "pip install -e . failed."
        exit 1
    }

    # 4b. Force run-time state to resolve to THIS clone so the demo is
    # isolated and reproducible from a clean checkout (path may contain
    # spaces). THEKEY_REPO_ROOT is honored by src/thekey/config.py.
    $env:THEKEY_REPO_ROOT = $RepoRoot

    # 5. Run the canonical demo and propagate the real exit code.
    Write-Host "[*] Running 'python -m thekey demo' ..."
    & .venv/Scripts/python -m thekey demo
    $demoExit = $LASTEXITCODE
    exit $demoExit
}
finally {
    Pop-Location
}
