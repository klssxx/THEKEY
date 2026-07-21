[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$reference = Join-Path $repoRoot 'design\reference\THEKEY_BUILD_WEEK_CANONICAL.png'
$output = Join-Path $repoRoot 'portable\windows\assets\THEKEY_hero_canonical_decor.png'
$canvasWidth = 1448
$canvasHeight = 1086
$heroOrigin = [System.Drawing.Point]::new(270, 48)
$heroSize = [System.Drawing.Size]::new(1178, 254)

# The complete hero crop is retained as a source for decorative artwork. The
# native UI rectangles below are then cleared to transparent before packaging.
$decorationRect = @(0, 0, 1178, 254)
$nativeUiRects = @(
    @(45, 25, 215, 23),   # greeting
    @(45, 57, 325, 63),   # THEKEY wordmark
    @(45, 123, 365, 31),  # tagline
    @(45, 174, 543, 23),  # Spanish description
    @(45, 202, 525, 23),  # English description
    @(923, 22, 240, 54),  # local-mode control
    @(45, 248, 690, 6)    # visible top edge of CTA
)

if (-not (Test-Path -LiteralPath $reference)) { throw "Canonical reference is missing: $reference" }

Add-Type -AssemblyName System.Drawing
$source = [System.Drawing.Bitmap]::FromFile($reference)
$outputBitmap = New-Object System.Drawing.Bitmap($heroSize.Width, $heroSize.Height, [System.Drawing.Imaging.PixelFormat]::Format32bppArgb)
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

    $destination = [System.Drawing.Rectangle]::new(
        $decorationRect[0], $decorationRect[1], $decorationRect[2], $decorationRect[3])
    $sourceRect = [System.Drawing.Rectangle]::new(
        $heroOrigin.X + $decorationRect[0], $heroOrigin.Y + $decorationRect[1],
        $decorationRect[2], $decorationRect[3])
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
    try {
        $outputBitmap.Save($stream, [System.Drawing.Imaging.ImageFormat]::Png)
    } finally {
        $stream.Dispose()
    }
} finally {
    $graphics.Dispose()
    $outputBitmap.Dispose()
    $source.Dispose()
}

[ordered]@{
    status = 'EXTRACTED'
    output = $output
    dimensions = "$($heroSize.Width)x$($heroSize.Height)"
    decoration_rectangles = 1
    native_ui_masks = $nativeUiRects.Count
} | ConvertTo-Json
