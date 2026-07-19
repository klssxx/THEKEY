[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path

function Test-PythonRuntime {
    param(
        [Parameter(Mandatory)]
        [string]$Executable,
        [string[]]$Prefix = @()
    )

    try {
        & $Executable @Prefix -c `
            'import sys; raise SystemExit(0 if sys.version_info >= (3, 11) else 1)' `
            *> $null
        return $LASTEXITCODE -eq 0
    } catch {
        return $false
    }
}

$pythonExe = $null
$pythonPrefix = @()
if ($env:THEKEY_PYTHON) {
    if (-not (Test-PythonRuntime -Executable $env:THEKEY_PYTHON)) {
        throw 'THEKEY_PYTHON must point to a working Python 3.11+ executable.'
    }
    $pythonExe = $env:THEKEY_PYTHON
} else {
    $venvPython = Join-Path $repoRoot '.venv\Scripts\python.exe'
    $pythonCommand = Get-Command python -ErrorAction SilentlyContinue
    $pyCommand = Get-Command py -ErrorAction SilentlyContinue

    if ((Test-Path -LiteralPath $venvPython) -and
        (Test-PythonRuntime -Executable $venvPython)) {
        $pythonExe = $venvPython
    } elseif ($pythonCommand -and
        (Test-PythonRuntime -Executable $pythonCommand.Source)) {
        $pythonExe = $pythonCommand.Source
    } elseif ($pyCommand -and
        (Test-PythonRuntime -Executable $pyCommand.Source -Prefix @('-3'))) {
        $pythonExe = $pyCommand.Source
        $pythonPrefix = @('-3')
    }
}

if (-not $pythonExe) {
    throw ('A working Python 3.11+ runtime was not found. Install the project ' +
        'or set THEKEY_PYTHON to its Python executable.')
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
    $null = & $pythonExe @pythonPrefix -m thekey judge-mode `
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
$evidenceDisplay = [IO.Path]::GetRelativePath($repoRoot, $evidenceFile)

Write-Host ''
Write-Host 'THEKEY BUILD WEEK JUDGE MODE'
Write-Host "ALLOW: $($evidence.allow.status), handlers=$($evidence.allow.handler_call_count)"
Write-Host "DENY: $($evidence.deny.reason_code), handlers=$($evidence.deny.handler_call_count)"
Write-Host "GATES: $(@($evidence.gates | Where-Object passed).Count)/$(@($evidence.gates).Count) PASS"
Write-Host "DECISION: $($evidence.release_decision)"
Write-Host "SOURCE: unchanged=$($evidence.source.hash_unchanged)"
Write-Host "RECEIPTS: bound=$(@($evidence.receipt_binding.PSObject.Properties.Value | Where-Object { -not $_ }).Count -eq 0)"
Write-Host "PRODUCTION REUSE: $($evidence.production_reuse)"
Write-Host "EVIDENCE: $evidenceDisplay"
Write-Host 'Isolation: workflow workspace only; this is not an OS sandbox.'

exit $demoExit
