<#
.SYNOPSIS
    Bootstrap a clean clone of THEKEY Core Governed Run and run the canonical demo.
.DESCRIPTION
    From a clean checkout this script:
      1. Detects Python (>=3.11).
      2. Validates the version.
      3. Creates .venv if missing.
      4. Installs the package and dev dependencies.
      5. Runs core tests.
      6. Creates a run, captures the run id.
      7. Plans, approves, executes, verifies gates, verifies evidence.
      8. Displays the run path and final decision.
      9. Returns zero only if every mandatory step succeeded.
    Does NOT require admin, does NOT delete previous runs, does NOT touch the
    historical THEKEY path.
#>
[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
$RepoRoot = Split-Path -Parent $PSScriptRoot
Push-Location $RepoRoot

function Fail($msg) {
    Write-Error $msg
    Pop-Location
    exit 1
}

# 1-2. Detect + validate Python.
$py = Get-Command python -ErrorAction SilentlyContinue
if (-not $py) { Fail "Python not found on PATH. Install Python 3.11+." }
$ver = & python --version 2>&1
if ($ver -notmatch '3\.(\d+)') { Fail "Unexpected Python version string: $ver" }
$minor = [int]$Matches[1]
if ($minor -lt 11) { Fail "Python 3.11+ required, found: $ver" }
Write-Host "[ok] Python: $ver"

# 3. Create .venv if missing.
if (-not (Test-Path .venv)) {
    Write-Host "[*] Creating virtual environment..."
    & python -m venv .venv
}

# 4. Install.
Write-Host "[*] Installing package and dev dependencies..."
& .venv/Scripts/python -m pip install -q -e ".[dev]"
if ($LASTEXITCODE -ne 0) { Fail "pip install failed." }

# 5. Core tests.
Write-Host "[*] Running core tests..."
& .venv/Scripts/python -m pytest -q
if ($LASTEXITCODE -ne 0) { Fail "Core tests failed." }

# 6-12. Canonical demo.
Write-Host "[*] Running canonical governed demo..."
$out = & .venv/Scripts/python -m thekey demo 2>&1
if ($LASTEXITCODE -ne 0) { Fail "Demo failed.`n$out" }

# Extract run id + decision from output.
$runId = ($out | Select-String '^run_id: (.+)$' | ForEach-Object { $_.Matches.Groups[1].Value }) | Select-Object -First 1
$decision = ($out | Select-String '^decision: (.+)$' | ForEach-Object { $_.Matches.Groups[1].Value }) | Select-Object -First 1
Write-Host ""
Write-Host "Run ID     : $runId"
Write-Host "Decision   : $decision"
Write-Host "Run path   : $RepoRoot/runs/$runId"
Write-Host "Workspace  : $RepoRoot/workspaces/$runId"

if ($decision -ne 'RELEASE_ELIGIBLE') { Fail "Demo did not reach RELEASE_ELIGIBLE (got $decision)." }

Write-Host "[ok] Canonical demo complete and ELIGIBLE."
Pop-Location
exit 0
