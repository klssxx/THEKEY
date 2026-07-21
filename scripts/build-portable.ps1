[CmdletBinding()]
param(
    [string]$Python,
    [switch]$Bootstrap
)

$ErrorActionPreference = 'Stop'
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$buildRoot = Join-Path $repoRoot 'build\portable'
$packageRoot = Join-Path $repoRoot 'dist\THEKEY-Portable-Windows-x64'
$zipPath = Join-Path $repoRoot 'dist\THEKEY-Portable-Windows-x64.zip'
$sourceVideo = Join-Path $repoRoot 'portable\windows\assets\THEKEY_cinematic_loop_5s.mp4'
$sourceHero = Join-Path $repoRoot 'portable\windows\assets\THEKEY_hero_chess.png'
$sourceIcon = Join-Path $repoRoot 'portable\windows\assets\THEKEY_app_icon.png'
$sourceUiReference = Join-Path $repoRoot 'assets\reference\THEKEY_UI_REFERENCE.png'
$launcherSource = Join-Path $repoRoot 'portable\windows\TheKeyLauncher.cs'
$quickGuide = Join-Path $repoRoot 'portable\windows\README-FIRST.txt'

function Assert-ChildPath {
    param([string]$Path, [string]$Parent)
    $full = [IO.Path]::GetFullPath($Path)
    $root = [IO.Path]::GetFullPath($Parent).TrimEnd([IO.Path]::DirectorySeparatorChar)
    if (-not $full.StartsWith($root + [IO.Path]::DirectorySeparatorChar,
            [StringComparison]::OrdinalIgnoreCase)) {
        throw "Unsafe generated path outside repository: $full"
    }
}

function Remove-GeneratedPath {
    param([string]$Path)
    Assert-ChildPath -Path $Path -Parent $repoRoot
    if (Test-Path -LiteralPath $Path) {
        Remove-Item -LiteralPath $Path -Recurse -Force
    }
}

if (-not $Python) {
    $cached = Join-Path $repoRoot '.thekey\portable-build-venv\Scripts\python.exe'
    if (Test-Path -LiteralPath $cached) {
        $Python = $cached
    } else {
        $command = Get-Command python -ErrorAction SilentlyContinue
        if ($command) {
            $Python = $command.Source
        }
    }
}
if (-not $Python -or -not (Test-Path -LiteralPath $Python)) {
    throw 'Pass -Python with a working 64-bit Python 3.11+ executable.'
}

$version = & $Python -c "import platform,struct,sys; print(platform.python_version()); print(struct.calcsize('P')*8); raise SystemExit(0 if sys.version_info >= (3,11) else 1)"
if ($LASTEXITCODE -ne 0 -or $version[-1] -ne '64') {
    throw "The portable build requires 64-bit Python 3.11+. Observed: $($version -join ', ')"
}

foreach ($required in @($sourceVideo, $sourceHero, $sourceIcon, $sourceUiReference, $launcherSource, $quickGuide)) {
    if (-not (Test-Path -LiteralPath $required)) {
        throw "Required portable source is missing: $required"
    }
}

if ($Bootstrap) {
    & $Python -m pip install --disable-pip-version-check --quiet `
        -e "$repoRoot[dev]" 'pyinstaller==6.21.0'
    if ($LASTEXITCODE -ne 0) {
        throw 'Portable build dependency installation failed.'
    }
}

& $Python -c "import PyInstaller,pytest,thekey; print('PyInstaller='+PyInstaller.__version__); print('THEKEY='+thekey.__version__)"
if ($LASTEXITCODE -ne 0) {
    throw 'PyInstaller, pytest, or THEKEY is unavailable. Rerun with -Bootstrap.'
}

Remove-GeneratedPath -Path $buildRoot
Remove-GeneratedPath -Path $packageRoot
Remove-GeneratedPath -Path $zipPath
New-Item -ItemType Directory -Force -Path $buildRoot, $packageRoot | Out-Null

$backendDist = Join-Path $buildRoot 'backend-dist'
$backendWork = Join-Path $buildRoot 'backend-work'
$backendSpec = Join-Path $buildRoot 'backend-spec'
& $Python -m PyInstaller `
    --noconfirm `
    --clean `
    --onedir `
    --console `
    --noupx `
    --name 'THEKEY-Core' `
    --paths (Join-Path $repoRoot 'src') `
    --collect-all pytest `
    --collect-submodules _pytest `
    --hidden-import py `
    --distpath $backendDist `
    --workpath $backendWork `
    --specpath $backendSpec `
    (Join-Path $repoRoot 'scripts\portable_entry.py')
if ($LASTEXITCODE -ne 0) {
    throw 'PyInstaller failed.'
}

$backendSource = Join-Path $backendDist 'THEKEY-Core'
$backendTargetParent = Join-Path $packageRoot 'core'
New-Item -ItemType Directory -Force -Path $backendTargetParent | Out-Null
Copy-Item -LiteralPath $backendSource -Destination $backendTargetParent -Recurse
$backendTarget = Join-Path $backendTargetParent 'THEKEY-Core'

foreach ($directory in @('governance', 'prompts', 'phases')) {
    Copy-Item -LiteralPath (Join-Path $repoRoot $directory) `
        -Destination (Join-Path $backendTarget $directory) -Recurse
}
$demoTarget = Join-Path $backendTarget 'examples\demo_app'
New-Item -ItemType Directory -Force -Path $demoTarget | Out-Null
Copy-Item -LiteralPath (Join-Path $repoRoot 'examples\demo_app\calculator.py') -Destination $demoTarget
Copy-Item -LiteralPath (Join-Path $repoRoot 'examples\demo_app\test_calculator.py') -Destination $demoTarget
Copy-Item -LiteralPath (Join-Path $repoRoot 'README.en.md') -Destination $backendTarget
Copy-Item -LiteralPath (Join-Path $repoRoot 'LICENSE') -Destination $backendTarget

# Include a tiny, transparent Python CLI project so judges can exercise the
# application-verification flow without preparing a separate repository.
$sampleTarget = Join-Path $packageRoot 'SAMPLE-PYTHON-APP'
Copy-Item -LiteralPath (Join-Path $repoRoot 'tests\fixtures\python_cli_project') `
    -Destination $sampleTarget -Recurse
$repairSampleTarget = Join-Path $packageRoot 'SAMPLE-REPAIRABLE-PYTHON-APP'
Copy-Item -LiteralPath (Join-Path $repoRoot 'portable\windows\sample-repairable-app') `
    -Destination $repairSampleTarget -Recurse

# Convert the project-owned premium chess icon into the executable icon.
$iconPath = Join-Path $buildRoot 'thekey-king.ico'
Add-Type -AssemblyName System.Drawing
$sourceIconBitmap = [System.Drawing.Image]::FromFile($sourceIcon)
$bitmap = New-Object System.Drawing.Bitmap $sourceIconBitmap, 256, 256
$handle = $bitmap.GetHicon()
$icon = [System.Drawing.Icon]::FromHandle($handle)
$stream = [IO.File]::Open($iconPath, [IO.FileMode]::Create)
try { $icon.Save($stream) } finally { $stream.Dispose() }
$icon.Dispose(); $bitmap.Dispose(); $sourceIconBitmap.Dispose()

$framework = Join-Path $env:WINDIR 'Microsoft.NET\Framework64\v4.0.30319'
$csc = Join-Path $framework 'csc.exe'
$wpf = Join-Path $framework 'WPF'
if (-not (Test-Path -LiteralPath $csc)) {
    throw 'The Windows .NET Framework 4 compiler was not found.'
}
$launcher = Join-Path $packageRoot 'THEKEY.exe'
$compilerArguments = @(
    '/nologo'
    '/target:winexe'
    '/platform:anycpu'
    '/optimize+'
    '/utf8output'
    "/win32icon:$iconPath"
    "/out:$launcher"
    "/reference:$(Join-Path $framework 'System.dll')"
    "/reference:$(Join-Path $framework 'System.Core.dll')"
    "/reference:$(Join-Path $framework 'System.Windows.Forms.dll')"
    "/reference:$(Join-Path $framework 'Microsoft.CSharp.dll')"
    "/reference:$(Join-Path $framework 'System.Xaml.dll')"
    "/reference:$(Join-Path $wpf 'WindowsBase.dll')"
    "/reference:$(Join-Path $wpf 'PresentationCore.dll')"
    "/reference:$(Join-Path $wpf 'PresentationFramework.dll')"
    $launcherSource
)
& $csc $compilerArguments
if ($LASTEXITCODE -ne 0) {
    throw 'Windows launcher compilation failed.'
}

Copy-Item -LiteralPath $sourceVideo -Destination $packageRoot
Copy-Item -LiteralPath $sourceHero -Destination $packageRoot
Copy-Item -LiteralPath $sourceIcon -Destination $packageRoot
Copy-Item -LiteralPath $sourceUiReference -Destination $packageRoot
Copy-Item -LiteralPath $quickGuide -Destination $packageRoot

$manifestPath = Join-Path $packageRoot 'BUILD_MANIFEST.json'
$sourceCommit = git -C $repoRoot rev-parse HEAD
$sourceStatus = @(git -C $repoRoot status --porcelain=v1 --untracked-files=all | Sort-Object)
$sourceTreeState = if ($sourceStatus.Count -eq 0) { 'CLEAN' } else { 'DIRTY_BUILD' }
$statusText = $sourceStatus -join "`n"
$statusBytes = [Text.Encoding]::UTF8.GetBytes($statusText)
$statusHasher = [Security.Cryptography.SHA256]::Create()
try {
    $sourceStatusSha256 = ([BitConverter]::ToString(
        $statusHasher.ComputeHash($statusBytes))).Replace('-', '').ToLowerInvariant()
} finally {
    $statusHasher.Dispose()
}
$files = Get-ChildItem -LiteralPath $packageRoot -File -Recurse |
    Where-Object FullName -ne $manifestPath |
    Sort-Object FullName |
    ForEach-Object {
        [ordered]@{
            path = [IO.Path]::GetRelativePath($packageRoot, $_.FullName).Replace('\', '/')
            size = $_.Length
            sha256 = (Get-FileHash -Algorithm SHA256 -LiteralPath $_.FullName).Hash.ToLowerInvariant()
        }
    }
[ordered]@{
    schema_version = 'v1'
    product = 'THEKEY — THE KING OF CHECKMATE'
    tagline = 'Governed Codex Transactions for Coding Agents'
    supported_platforms = @('Windows 10 x64', 'Windows 11 x64')
    source_commit = $sourceCommit
    source_commit_exact = $sourceStatus.Count -eq 0
    source_tree_state = $sourceTreeState
    source_status_sha256 = $sourceStatusSha256
    source_changed_path_count = $sourceStatus.Count
    cinematic_sha256 = (Get-FileHash -Algorithm SHA256 -LiteralPath $sourceVideo).Hash.ToLowerInvariant()
    files = @($files)
} | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $manifestPath -Encoding utf8

Compress-Archive -LiteralPath $packageRoot -DestinationPath $zipPath -CompressionLevel Optimal

[ordered]@{
    status = 'BUILT'
    package = $packageRoot
    zip = $zipPath
    zip_size = (Get-Item -LiteralPath $zipPath).Length
    zip_sha256 = (Get-FileHash -Algorithm SHA256 -LiteralPath $zipPath).Hash.ToLowerInvariant()
    source_commit = $sourceCommit
    source_tree_state = $sourceTreeState
    source_commit_exact = $sourceStatus.Count -eq 0
    python = $version[0]
    architecture = "$($version[1])-bit"
} | ConvertTo-Json
