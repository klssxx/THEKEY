[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$reference = Join-Path $repoRoot 'design\reference\THEKEY_BUILD_WEEK_CANONICAL.png'
$output = Join-Path $repoRoot 'portable\windows\assets\THEKEY_sidebar_canonical_decor.png'
$canvasWidth = 1448
$canvasHeight = 1086
$sidebarOrigin = [System.Drawing.Point]::new(0, 48)
$sidebarSize = [System.Drawing.Size]::new(270, 1038)

# Hero-style canonical crop, with only native title and navigation content
# cleared. The decorative crown, halo, texture, frame, and landscape remain
# exact reference pixels.
$nativeUiRects = @(
    @(40, 127, 200, 43),  # THEKEY title
    @(50, 169, 185, 18),  # sidebar tagline
    @(4, 206, 254, 68),   # active home button
    @(30, 291, 220, 37),  # analyze icon and label
    @(30, 359, 220, 37),  # tools icon and label
    @(30, 427, 220, 37),  # results icon and label
    @(30, 495, 220, 37),  # modes icon and label
    @(30, 563, 220, 37),  # logs icon and label
    @(30, 631, 220, 37)   # settings icon and label
)

if (-not (Test-Path -LiteralPath $reference)) { throw "Canonical reference is missing: $reference" }

Add-Type -AssemblyName System.Drawing
$source = [System.Drawing.Bitmap]::FromFile($reference)
$outputBitmap = New-Object System.Drawing.Bitmap($sidebarSize.Width, $sidebarSize.Height, [System.Drawing.Imaging.PixelFormat]::Format32bppArgb)
$graphics = [System.Drawing.Graphics]::FromImage($outputBitmap)
try {
    if ($source.Width -ne $canvasWidth -or $source.Height -ne $canvasHeight) {
        throw "Unexpected canonical dimensions: $($source.Width)x$($source.Height)"
    }
    $graphics.CompositingMode = [System.Drawing.Drawing2D.CompositingMode]::SourceCopy
    $graphics.CompositingQuality = [System.Drawing.Drawing2D.CompositingQuality]::HighSpeed
    $graphics.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::NearestNeighbor
    $graphics.PixelOffsetMode = [System.Drawing.Drawing2D.PixelOffsetMode]::Half
    $graphics.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::None
    $graphics.Clear([System.Drawing.Color]::Transparent)
    $destination = [System.Drawing.Rectangle]::new(0, 0, $sidebarSize.Width, $sidebarSize.Height)
    $sourceRect = [System.Drawing.Rectangle]::new($sidebarOrigin.X, $sidebarOrigin.Y, $sidebarSize.Width, $sidebarSize.Height)
    $graphics.DrawImage($source, $destination, $sourceRect, [System.Drawing.GraphicsUnit]::Pixel)

    $transparent = [System.Drawing.SolidBrush]::new([System.Drawing.Color]::Transparent)
    try {
        foreach ($rect in $nativeUiRects) {
            $graphics.FillRectangle($transparent, $rect[0], $rect[1], $rect[2], $rect[3])
        }
    } finally {
        $transparent.Dispose()
    }

    $stream = [IO.File]::Open($output, [IO.FileMode]::Create, [IO.FileAccess]::Write)
    try { $outputBitmap.Save($stream, [System.Drawing.Imaging.ImageFormat]::Png) } finally { $stream.Dispose() }
} finally {
    $graphics.Dispose(); $outputBitmap.Dispose(); $source.Dispose()
}

[ordered]@{
    status = 'EXTRACTED'
    output = $output
    dimensions = "$($sidebarSize.Width)x$($sidebarSize.Height)"
    native_ui_masks = $nativeUiRects.Count
} | ConvertTo-Json
