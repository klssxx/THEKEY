<#
.SYNOPSIS
    Run the canonical governed demo end to end (assumes environment is set up).
#>
[CmdletBinding()] param()
$ErrorActionPreference = 'Stop'
$RepoRoot = Split-Path -Parent $PSScriptRoot
Push-Location $RepoRoot
if (-not (Test-Path .venv)) {
    Write-Error "Environment not set up. Run .\scripts\bootstrap.ps1 first."; Pop-Location; exit 1
}
& .venv/Scripts/python -m thekey demo
$code = $LASTEXITCODE
Pop-Location
exit $code
