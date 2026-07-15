<#
.SYNOPSIS
    Prepare the development environment (venv + install) without running the demo.
#>
[CmdletBinding()] param()
$ErrorActionPreference = 'Stop'
$RepoRoot = Split-Path -Parent $PSScriptRoot
Push-Location $RepoRoot

$py = Get-Command python -ErrorAction SilentlyContinue
if (-not $py) { Write-Error "Python not found."; Pop-Location; exit 1 }
$ver = & python --version 2>&1
if ($ver -notmatch '3\.(\d+)' -or [int]$Matches[1] -lt 11) {
    Write-Error "Python 3.11+ required (found $ver)."; Pop-Location; exit 1
}
if (-not (Test-Path .venv)) { & python -m venv .venv }
& .venv/Scripts/python -m pip install -q -e ".[dev]"
if ($LASTEXITCODE -ne 0) { Write-Error "pip install failed."; Pop-Location; exit 1 }
Write-Host "[ok] Environment ready. Run .\scripts\run-demo.ps1 or bootstrap-and-demo.ps1"
Pop-Location
exit 0
