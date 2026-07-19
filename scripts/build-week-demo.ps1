[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path

$pythonExe = $null
$pythonPrefix = @()
if ($env:THEKEY_PYTHON) {
    $pythonExe = $env:THEKEY_PYTHON
} elseif (Get-Command python -ErrorAction SilentlyContinue) {
    $pythonExe = (Get-Command python).Source
} elseif (Get-Command py -ErrorAction SilentlyContinue) {
    $pythonExe = (Get-Command py).Source
    $pythonPrefix = @('-3')
} elseif (Test-Path (Join-Path $repoRoot '.venv\Scripts\python.exe')) {
    $pythonExe = Join-Path $repoRoot '.venv\Scripts\python.exe'
} else {
    throw 'Python 3.11+ was not found. Install the project first with: python -m pip install -e .'
}

$sessionId = [guid]::NewGuid().ToString('N')
$sessionRoot = Join-Path $repoRoot ".thekey\judge-mode\Judge Mode $sessionId"
$sampleRepo = Join-Path $sessionRoot 'Temporary Sample Repository'
$runtimeRoot = Join-Path $sessionRoot 'Isolated Runtime'
$evidenceFile = Join-Path $sessionRoot 'judge-mode-evidence.json'
New-Item -ItemType Directory -Force $sampleRepo | Out-Null
New-Item -ItemType Directory -Force $runtimeRoot | Out-Null

Copy-Item -LiteralPath (Join-Path $repoRoot 'examples\demo_app\calculator.py') -Destination $sampleRepo
Copy-Item -LiteralPath (Join-Path $repoRoot 'examples\demo_app\test_calculator.py') -Destination $sampleRepo

& git init --quiet $sampleRepo
if ($LASTEXITCODE -ne 0) {
    throw 'git init failed for the temporary sample repository.'
}

$previousRuntime = $env:THEKEY_REPO_ROOT
$env:THEKEY_REPO_ROOT = $runtimeRoot
$env:PYTHONDONTWRITEBYTECODE = '1'
try {
    & $pythonExe @pythonPrefix -m thekey judge-mode `
        --source (Join-Path $sampleRepo 'calculator.py') `
        --output $evidenceFile `
        --json
    $demoExit = $LASTEXITCODE
} finally {
    $env:THEKEY_REPO_ROOT = $previousRuntime
}

if (-not (Test-Path -LiteralPath $evidenceFile)) {
    throw 'Judge Mode did not produce its evidence file.'
}
$evidence = Get-Content -LiteralPath $evidenceFile -Raw | ConvertFrom-Json

Write-Host ''
Write-Host 'THEKEY BUILD WEEK JUDGE MODE'
Write-Host "ALLOW: $($evidence.allow.status), handlers=$($evidence.allow.handler_call_count)"
Write-Host "DENY: $($evidence.deny.reason_code), handlers=$($evidence.deny.handler_call_count)"
Write-Host "GATES: $(@($evidence.gates | Where-Object passed).Count)/$(@($evidence.gates).Count) PASS"
Write-Host "DECISION: $($evidence.release_decision)"
Write-Host "EVIDENCE: $evidenceFile"
Write-Host 'Isolation: workflow workspace only; this is not an OS sandbox.'

exit $demoExit
