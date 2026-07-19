[CmdletBinding()]
param(
    [Parameter(Position = 0)]
    [string]$EvidencePath
)

$ErrorActionPreference = 'Stop'
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path

function Assert-True {
    param(
        [bool]$Condition,
        [string]$Message
    )
    if (-not $Condition) {
        throw "Evidence verification failed: $Message"
    }
}

if (-not $EvidencePath) {
    $latest = Get-ChildItem -LiteralPath (Join-Path $repoRoot '.thekey\judge-mode') `
        -Filter 'judge-mode-evidence.json' -Recurse -File -ErrorAction SilentlyContinue |
        Sort-Object LastWriteTimeUtc -Descending |
        Select-Object -First 1
    if (-not $latest) {
        throw 'No Judge Mode evidence found. Run scripts\build-week-demo.ps1 first.'
    }
    $EvidencePath = $latest.FullName
}

$resolvedEvidence = (Resolve-Path -LiteralPath $EvidencePath).Path
$evidence = Get-Content -LiteralPath $resolvedEvidence -Raw | ConvertFrom-Json

Assert-True ($evidence.judge_mode -eq 'THEKEY Build Week Judge Mode') 'unexpected evidence kind'
Assert-True ($evidence.allow.status -eq 'APPLIED') 'ALLOW was not applied'
Assert-True ([int]$evidence.allow.handler_call_count -eq 1) 'ALLOW did not invoke exactly one handler'
Assert-True ($evidence.deny.reason_code -eq 'ROLE_NOT_ALLOWED') 'DENY reason differs'
Assert-True ([int]$evidence.deny.handler_call_count -eq 0) 'DENY invoked a handler'
Assert-True ([bool]$evidence.deny.workspace_hash_unchanged) 'DENY changed the workspace'
Assert-True ([bool]$evidence.source.hash_unchanged) 'Judge Mode changed its source repository'
Assert-True ([bool]$evidence.receipt_binding.run_id_match) 'receipt run IDs differ'
Assert-True ([bool]$evidence.receipt_binding.transaction_id_match) 'receipt transaction IDs differ'
Assert-True ([bool]$evidence.receipt_binding.plan_sha256_match) 'receipt plan hashes differ'
Assert-True ($evidence.production_reuse -eq $false) 'demo authorization permits production reuse'
Assert-True (@($evidence.gates).Count -eq 4) 'expected four gates'
Assert-True (@($evidence.gates | Where-Object { -not $_.passed }).Count -eq 0) 'one or more gates failed'
Assert-True ($evidence.release_decision -eq 'RELEASE_ELIGIBLE') 'release decision differs'

$runPath = (Resolve-Path -LiteralPath $evidence.run_path).Path
$review = Get-Content -LiteralPath (Join-Path $runPath 'checkmate-review-receipt.json') -Raw |
    ConvertFrom-Json
$authorization = Get-Content `
    -LiteralPath (Join-Path $runPath 'sovereign-authorization-receipt.json') -Raw |
    ConvertFrom-Json
$decision = Get-Content -LiteralPath (Join-Path $runPath 'decision.json') -Raw |
    ConvertFrom-Json

Assert-True ($review.run_id -eq $evidence.run_id) 'persisted review run ID differs'
Assert-True ($authorization.run_id -eq $evidence.run_id) 'persisted authorization run ID differs'
Assert-True ($review.transaction_id -eq $evidence.transaction_id) `
    'persisted review transaction ID differs'
Assert-True ($authorization.transaction_id -eq $evidence.transaction_id) `
    'persisted authorization transaction ID differs'
Assert-True ($review.plan_sha256 -eq $evidence.plan_sha256) 'persisted review plan hash differs'
Assert-True ($authorization.plan_sha256 -eq $evidence.plan_sha256) `
    'persisted authorization plan hash differs'
Assert-True ($authorization.production_reuse -eq $false) `
    'persisted authorization permits production reuse'
Assert-True ($decision.decision -eq $evidence.release_decision) 'persisted decision differs'
Assert-True (@($decision.gates | Where-Object { -not $_.passed }).Count -eq 0) `
    'persisted decision contains a failed gate'

[pscustomobject]@{
    status = 'VALID'
    run_id = $evidence.run_id
    transaction_id = $evidence.transaction_id
    allow_handlers = [int]$evidence.allow.handler_call_count
    deny_handlers = [int]$evidence.deny.handler_call_count
    gates = @($evidence.gates).Count
    release_decision = $evidence.release_decision
    source_unchanged = [bool]$evidence.source.hash_unchanged
    production_reuse = [bool]$evidence.production_reuse
} | ConvertTo-Json
