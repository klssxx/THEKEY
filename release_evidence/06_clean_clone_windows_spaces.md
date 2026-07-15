# 06 Clean clone / Windows / path-with-spaces
Date: 2026-07-15 16:59:25
Objective: demo from a clean clone in a path containing spaces via the exact
mandated command.
Status: VERIFIED MANUALLY on this machine (pwsh -NoProfile -File .\scripts\demo.ps1
in 'C:\Users\KLSX\AppData\Local\Temp\THEKEY Test 0.2' -> exit 0, RELEASE_ELIGIBLE, 4/4).
Exact command for any other machine:
    git clone <URL> "C:\Some Path With Spaces\THEKEY"
    cd "C:\Some Path With Spaces\THEKEY"
    pwsh -NoProfile -File .\scripts\demo.ps1
Decision: PASS (reproducible on this host; require re-run on target host only
if the environment differs).
