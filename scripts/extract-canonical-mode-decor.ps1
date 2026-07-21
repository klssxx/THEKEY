[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$reference = Join-Path $repoRoot 'design\reference\THEKEY_BUILD_WEEK_CANONICAL.png'
$outputRoot = Join-Path $repoRoot 'portable\windows\assets'
$canvasWidth = 1448
$canvasHeight = 1086
$modesOrigin = [System.Drawing.Point]::new(312, 702)

# Source rects are exactly the native content areas after WPF card padding.
# Per-output masks remove all labels and badges. The emblems and texture remain
# as non-interactive reference artwork; card shells and text stay WPF.
$assets = @(
    [pscustomobject]@{
        Name = 'THEKEY_mode_king_canonical_decor.png'
        Source = @(28, 31, 453, 90)
        Masks = @(@(110, 8, 150, 33), @(250, 7, 160, 38), @(110, 43, 210, 43))
    },
    [pscustomobject]@{
        Name = 'THEKEY_mode_checkmate_canonical_decor.png'
        Source = @(562, 31, 492, 90)
        Masks = @(@(98, 8, 180, 34), @(260, 7, 165, 38), @(98, 43, 190, 43))
    }
)

if (-not (Test-Path -LiteralPath $reference)) { throw "Canonical reference is missing: $reference" }

Add-Type -AssemblyName System.Drawing
$source = [System.Drawing.Bitmap]::FromFile($reference)
try {
    if ($source.Width -ne $canvasWidth -or $source.Height -ne $canvasHeight) {
        throw "Unexpected canonical dimensions: $($source.Width)x$($source.Height)"
    }
    foreach ($asset in $assets) {
        $width = $asset.Source[2]; $height = $asset.Source[3]
        $bitmap = New-Object System.Drawing.Bitmap($width, $height, [System.Drawing.Imaging.PixelFormat]::Format32bppArgb)
        $graphics = [System.Drawing.Graphics]::FromImage($bitmap)
        try {
            $graphics.CompositingMode = [System.Drawing.Drawing2D.CompositingMode]::SourceCopy
            $graphics.CompositingQuality = [System.Drawing.Drawing2D.CompositingQuality]::HighSpeed
            $graphics.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::NearestNeighbor
            $graphics.PixelOffsetMode = [System.Drawing.Drawing2D.PixelOffsetMode]::Half
            $graphics.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::None
            $destination = [System.Drawing.Rectangle]::new(0, 0, $width, $height)
            $sourceRect = [System.Drawing.Rectangle]::new(
                $modesOrigin.X + $asset.Source[0], $modesOrigin.Y + $asset.Source[1], $width, $height)
            $graphics.DrawImage($source, $destination, $sourceRect, [System.Drawing.GraphicsUnit]::Pixel)
            $transparent = [System.Drawing.SolidBrush]::new([System.Drawing.Color]::Transparent)
            try {
                foreach ($mask in $asset.Masks) {
                    $graphics.FillRectangle($transparent, $mask[0], $mask[1], $mask[2], $mask[3])
                }
            } finally { $transparent.Dispose() }
            $output = Join-Path $outputRoot $asset.Name
            $stream = [IO.File]::Open($output, [IO.FileMode]::Create, [IO.FileAccess]::Write)
            try { $bitmap.Save($stream, [System.Drawing.Imaging.ImageFormat]::Png) } finally { $stream.Dispose() }
        } finally { $graphics.Dispose(); $bitmap.Dispose() }
    }
} finally { $source.Dispose() }

[ordered]@{ status = 'EXTRACTED'; assets = @($assets.Name) } | ConvertTo-Json
