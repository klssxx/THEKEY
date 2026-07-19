[CmdletBinding()]
param(
    [Parameter(Position = 0)]
    [string[]]$SourcePath = @()
)

$ErrorActionPreference = 'Stop'
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$privateRoot = Join-Path $repoRoot 'evidence-private\build-week\chat-exports'
$privateManifest = Join-Path $repoRoot `
    'evidence-private\build-week\PRIVATE_IMPORT_MANIFEST.json'

if ($SourcePath.Count -eq 0) {
    [pscustomobject]@{
        status = 'PENDING_EVIDENCE_IMPORT'
        imported = 0
        destination = 'evidence-private/build-week/chat-exports/'
        next_step = 'Pass one or more explicit evidence file paths.'
    } | ConvertTo-Json
    exit 0
}

New-Item -ItemType Directory -Force -Path $privateRoot | Out-Null

$records = @()
if (Test-Path -LiteralPath $privateManifest) {
    $existing = Get-Content -Raw -LiteralPath $privateManifest | ConvertFrom-Json
    $records = @($existing.entries)
}

$imported = @()
foreach ($source in $SourcePath) {
    $resolvedSource = (Resolve-Path -LiteralPath $source).Path
    $item = Get-Item -LiteralPath $resolvedSource
    if ($item.PSIsContainer) {
        throw "Evidence imports must be explicit files, not directories: $($item.Name)"
    }

    $hash = (Get-FileHash -Algorithm SHA256 -LiteralPath $resolvedSource).Hash.ToLowerInvariant()
    $base = [IO.Path]::GetFileNameWithoutExtension($item.Name)
    $safeBase = ($base -replace '[^A-Za-z0-9._-]', '_').Trim('_')
    if (-not $safeBase) {
        $safeBase = 'evidence'
    }
    $extension = [IO.Path]::GetExtension($item.Name).ToLowerInvariant()
    $storedName = '{0}-{1}{2}' -f $safeBase, $hash.Substring(0, 12), $extension
    $destination = Join-Path $privateRoot $storedName

    if (Test-Path -LiteralPath $destination) {
        $storedHash = (Get-FileHash -Algorithm SHA256 -LiteralPath $destination).Hash.ToLowerInvariant()
        if ($storedHash -ne $hash) {
            throw "Existing private evidence has an unexpected hash: $storedName"
        }
    } else {
        Copy-Item -LiteralPath $resolvedSource -Destination $destination
    }

    $record = [ordered]@{
        evidence_id = 'private-import-' + $hash.Substring(0, 16)
        status = 'IMPORTED_PRIVATE_PENDING_REVIEW'
        original_file_name = $item.Name
        stored_relative_path = 'chat-exports/' + $storedName
        sha256 = $hash
        size_bytes = [int64]$item.Length
        imported_at_utc = [DateTime]::UtcNow.ToString('o')
        public = $false
    }
    $records = @($records | Where-Object { $_.sha256 -ne $hash }) + @($record)
    $imported += $record
}

$manifest = [ordered]@{
    schema_version = 'v1'
    generated_at_utc = [DateTime]::UtcNow.ToString('o')
    status = 'PRIVATE_EVIDENCE_REQUIRES_REVIEW'
    entries = @($records)
}
$manifest | ConvertTo-Json -Depth 6 | Set-Content `
    -LiteralPath $privateManifest -Encoding utf8

[pscustomobject]@{
    status = 'IMPORTED_PRIVATE_PENDING_REVIEW'
    imported = @($imported).Count
    total_private_records = @($records).Count
    public_files_written = 0
} | ConvertTo-Json
