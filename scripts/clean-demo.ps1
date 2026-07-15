<#
.SYNOPSIS
    Remove generated run artifacts (runs/* and workspaces/*) and the local state.
.DESCRIPTION
    Does NOT delete source, tests, docs, or the historical THEKEY path.
    Safe to re-run; previous committed work in runs/ is removed only for the
    local working tree.
#>
[CmdletBinding()] param()
$ErrorActionPreference = 'Stop'
$RepoRoot = Split-Path -Parent $PSScriptRoot
Push-Location $RepoRoot

if (Test-Path runs) { Remove-Item -Recurse -Force runs/* }
if (Test-Path workspaces) { Remove-Item -Recurse -Force workspaces/* }
if (Test-Path .thekey) { Remove-Item -Recurse -Force .thekey }
Write-Host "[ok] Cleared runs/, workspaces/, and .thekey/ local state."
Pop-Location
exit 0
