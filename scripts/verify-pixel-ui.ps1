[CmdletBinding()]
param(
    [Parameter(Mandatory)]
    [string]$Executable,
    [string]$OutputDirectory = (Join-Path $PSScriptRoot '..\evidence\ui\native-dashboard'),
    [int]$TimeoutSeconds = 30,
    [ValidateSet(96, 120, 144, 192)]
    [int]$Dpi = 96
)

$ErrorActionPreference = 'Stop'
$executablePath = (Resolve-Path -LiteralPath $Executable).Path
$outputPath = [IO.Path]::GetFullPath($OutputDirectory)
$capturePath = Join-Path $outputPath 'final_capture.png'
$reportPath = Join-Path $outputPath 'visual_verification.json'
New-Item -ItemType Directory -Force -Path $outputPath | Out-Null

$startInfo = [Diagnostics.ProcessStartInfo]::new()
$startInfo.FileName = $executablePath
$startInfo.WorkingDirectory = Split-Path $executablePath -Parent
$startInfo.UseShellExecute = $false
$startInfo.EnvironmentVariables['THEKEY_SKIP_SPLASH'] = '1'
$startInfo.EnvironmentVariables['THEKEY_CAPTURE_PATH'] = $capturePath
$startInfo.EnvironmentVariables['THEKEY_CAPTURE_DPI'] = $Dpi.ToString([Globalization.CultureInfo]::InvariantCulture)
$process = [Diagnostics.Process]::new()
$process.StartInfo = $startInfo

try {
    if (-not $process.Start()) { throw 'THEKEY failed to start' }
    if (-not $process.WaitForExit($TimeoutSeconds * 1000)) {
        throw 'Timed out waiting for THEKEY to create its native dashboard capture'
    }
    if ($process.ExitCode -ne 0) { throw "THEKEY capture exited with code $($process.ExitCode)" }
    if (-not (Test-Path -LiteralPath $capturePath -PathType Leaf)) {
        throw 'THEKEY did not create the native dashboard capture'
    }
} finally {
    if (-not $process.HasExited) {
        $null = $process.CloseMainWindow()
        if (-not $process.WaitForExit(3000)) { $process.Kill(); $process.WaitForExit() }
    }
    $process.Dispose()
}

Add-Type -AssemblyName System.Drawing
$bitmap = [Drawing.Bitmap]::FromFile($capturePath)
try {
    $expectedWidth = [int][Math]::Round(1448 * $Dpi / 96)
    $expectedHeight = [int][Math]::Round(1086 * $Dpi / 96)
    if ($bitmap.Width -ne $expectedWidth -or $bitmap.Height -ne $expectedHeight) {
        throw "Native dashboard capture has unexpected dimensions: $($bitmap.Width)x$($bitmap.Height), expected ${expectedWidth}x${expectedHeight} at ${Dpi} DPI"
    }
    $result = [ordered]@{
        status = 'NATIVE_RENDER_CAPTURED'
        capture = $capturePath
        capture_method = 'WPF RenderTargetBitmap of the native canonical dashboard composition'
        capture_sha256 = (Get-FileHash -LiteralPath $capturePath -Algorithm SHA256).Hash.ToLowerInvariant()
        captured_dashboard_dimensions = [ordered]@{ width = $bitmap.Width; height = $bitmap.Height }
        logical_dashboard_dimensions = [ordered]@{ width = 1448; height = 1086 }
        requested_dpi = $Dpi
        scale_percent = [int][Math]::Round($Dpi / 96 * 100)
        dpi_strategy = 'PerMonitorV2 WPF layout; the same native visual tree is rendered at the requested device-pixel density without rasterized controls'
    }
} finally {
    $bitmap.Dispose()
}
$result | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath $reportPath -Encoding utf8
$result | ConvertTo-Json -Depth 4
