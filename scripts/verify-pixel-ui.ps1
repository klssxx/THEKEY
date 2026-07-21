[CmdletBinding()]
param(
    [Parameter(Mandatory)]
    [string]$Executable,
    [string]$Reference = (Join-Path $PSScriptRoot '..\assets\reference\THEKEY_UI_REFERENCE.png'),
    [string]$OutputDirectory = (Join-Path $PSScriptRoot '..\evidence\ui\pixel-perfect'),
    [int]$TimeoutSeconds = 30
)

$ErrorActionPreference = 'Stop'
$executablePath = (Resolve-Path -LiteralPath $Executable).Path
$referencePath = (Resolve-Path -LiteralPath $Reference).Path
$outputPath = [IO.Path]::GetFullPath($OutputDirectory)
$capturePath = Join-Path $outputPath 'final_capture.png'
$diffPath = Join-Path $outputPath 'final_diff.png'
$reportPath = Join-Path $outputPath 'visual_verification.json'
New-Item -ItemType Directory -Force -Path $outputPath | Out-Null

Add-Type -AssemblyName System.Drawing
$drawingReferences = @(
    [System.Drawing.Bitmap].Assembly.Location,
    [System.Drawing.Size].Assembly.Location,
    (Join-Path $PSHOME 'System.Private.Windows.GdiPlus.dll'),
    (Join-Path $PSHOME 'System.Private.Windows.Core.dll')
)
Add-Type -ReferencedAssemblies $drawingReferences -TypeDefinition @'
using System;
using System.Drawing;
using System.Drawing.Imaging;
using System.Runtime.InteropServices;

public static class TheKeyPixelVerifier
{
    [StructLayout(LayoutKind.Sequential)]
    private struct RECT { public int Left, Top, Right, Bottom; }

    [DllImport("user32.dll")]
    private static extern bool GetWindowRect(IntPtr hwnd, out RECT rect);

    [DllImport("user32.dll")]
    private static extern bool PrintWindow(IntPtr hwnd, IntPtr hdc, uint flags);

    public static Size Capture(IntPtr hwnd, string output)
    {
        RECT rect;
        if (!GetWindowRect(hwnd, out rect)) throw new InvalidOperationException("GetWindowRect failed");
        int width = rect.Right - rect.Left;
        int height = rect.Bottom - rect.Top;
        using (Bitmap bitmap = new Bitmap(width, height, PixelFormat.Format24bppRgb))
        using (Graphics graphics = Graphics.FromImage(bitmap))
        {
            IntPtr hdc = graphics.GetHdc();
            bool captured;
            try { captured = PrintWindow(hwnd, hdc, 2); }
            finally { graphics.ReleaseHdc(hdc); }
            if (!captured) throw new InvalidOperationException("PrintWindow failed");
            bitmap.Save(output, ImageFormat.Png);
        }
        return new Size(width, height);
    }

    public static double[] Compare(string referencePath, string capturePath, string diffPath)
    {
        using (Bitmap reference = new Bitmap(referencePath))
        using (Bitmap capture = new Bitmap(capturePath))
        {
            if (reference.Width != capture.Width || reference.Height != capture.Height)
                throw new InvalidOperationException(String.Format(
                    "Dimension mismatch: reference {0}x{1}, capture {2}x{3}",
                    reference.Width, reference.Height, capture.Width, capture.Height));

            long pixelCount = (long)reference.Width * reference.Height;
            long differingPixels = 0;
            int maximumDifference = 0;
            double absoluteSum = 0;
            double squaredSum = 0;
            double[] sumX = new double[3], sumY = new double[3];
            double[] sumXX = new double[3], sumYY = new double[3], sumXY = new double[3];

            using (Bitmap diff = new Bitmap(reference.Width, reference.Height, PixelFormat.Format24bppRgb))
            {
                for (int y = 0; y < reference.Height; y++)
                {
                    for (int x = 0; x < reference.Width; x++)
                    {
                        Color a = reference.GetPixel(x, y);
                        Color b = capture.GetPixel(x, y);
                        int dr = Math.Abs(a.R - b.R);
                        int dg = Math.Abs(a.G - b.G);
                        int db = Math.Abs(a.B - b.B);
                        if (dr != 0 || dg != 0 || db != 0) differingPixels++;
                        maximumDifference = Math.Max(maximumDifference, Math.Max(dr, Math.Max(dg, db)));
                        absoluteSum += dr + dg + db;
                        squaredSum += dr * dr + dg * dg + db * db;
                        double[] av = { a.R, a.G, a.B };
                        double[] bv = { b.R, b.G, b.B };
                        for (int c = 0; c < 3; c++)
                        {
                            sumX[c] += av[c]; sumY[c] += bv[c];
                            sumXX[c] += av[c] * av[c]; sumYY[c] += bv[c] * bv[c];
                            sumXY[c] += av[c] * bv[c];
                        }
                        diff.SetPixel(x, y, Color.FromArgb(dr, dg, db));
                    }
                }
                diff.Save(diffPath, ImageFormat.Png);
            }

            const double c1 = 6.5025;
            const double c2 = 58.5225;
            double ssim = 0;
            for (int c = 0; c < 3; c++)
            {
                double meanX = sumX[c] / pixelCount;
                double meanY = sumY[c] / pixelCount;
                double varianceX = sumXX[c] / pixelCount - meanX * meanX;
                double varianceY = sumYY[c] / pixelCount - meanY * meanY;
                double covariance = sumXY[c] / pixelCount - meanX * meanY;
                ssim += ((2 * meanX * meanY + c1) * (2 * covariance + c2)) /
                    ((meanX * meanX + meanY * meanY + c1) * (varianceX + varianceY + c2));
            }
            ssim /= 3.0;
            double channels = pixelCount * 3.0;
            return new[] {
                (double)differingPixels,
                (double)maximumDifference,
                absoluteSum / channels,
                Math.Sqrt(squaredSum / channels),
                ssim
            };
        }
    }
}
'@

$startInfo = [Diagnostics.ProcessStartInfo]::new()
$startInfo.FileName = $executablePath
$startInfo.WorkingDirectory = Split-Path $executablePath -Parent
$startInfo.UseShellExecute = $false
$startInfo.EnvironmentVariables['THEKEY_SKIP_SPLASH'] = '1'
$startInfo.EnvironmentVariables['THEKEY_NATIVE_UI'] = '1'
$startInfo.EnvironmentVariables['THEKEY_CAPTURE_PATH'] = $capturePath
$process = [Diagnostics.Process]::new()
$process.StartInfo = $startInfo

try {
    if (-not $process.Start()) { throw 'THEKEY failed to start' }
    if (-not $process.WaitForExit($TimeoutSeconds * 1000)) {
        throw 'Timed out waiting for THEKEY to create the native capture'
    }
    if ($process.ExitCode -ne 0) { throw "THEKEY capture exited with code $($process.ExitCode)" }
    if (-not (Test-Path -LiteralPath $capturePath -PathType Leaf)) {
        throw 'THEKEY did not create the native capture'
    }
} finally {
    if (-not $process.HasExited) {
        $null = $process.CloseMainWindow()
        if (-not $process.WaitForExit(3000)) { $process.Kill(); $process.WaitForExit() }
    }
    $process.Dispose()
}

$metrics = [TheKeyPixelVerifier]::Compare($referencePath, $capturePath, $diffPath)
$referenceBitmap = [Drawing.Bitmap]::FromFile($referencePath)
$captureBitmap = [Drawing.Bitmap]::FromFile($capturePath)
try {
    $referenceWidth = $referenceBitmap.Width
    $referenceHeight = $referenceBitmap.Height
    $captureWidth = $captureBitmap.Width
    $captureHeight = $captureBitmap.Height
} finally {
    $referenceBitmap.Dispose()
    $captureBitmap.Dispose()
}
$result = [ordered]@{
    status = if ($metrics[0] -eq 0) { 'PIXEL_EXACT' } else { 'DIFFERENT' }
    reference = $referencePath
    capture = $capturePath
    difference = $diffPath
    reference_sha256 = (Get-FileHash -LiteralPath $referencePath -Algorithm SHA256).Hash.ToLowerInvariant()
    capture_sha256 = (Get-FileHash -LiteralPath $capturePath -Algorithm SHA256).Hash.ToLowerInvariant()
    reference_dimensions = @{ width = $referenceWidth; height = $referenceHeight }
    captured_window_dimensions = @{ width = $captureWidth; height = $captureHeight }
    differing_pixels = [long]$metrics[0]
    maximum_channel_difference = [int]$metrics[1]
    mean_absolute_error = $metrics[2]
    root_mean_square_error = $metrics[3]
    ssim = $metrics[4]
}
$result | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath $reportPath -Encoding utf8
$result | ConvertTo-Json -Depth 4
if ($metrics[0] -ne 0) { exit 1 }
