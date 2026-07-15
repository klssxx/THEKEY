# 04 CI status (local simulation)
Date: 2026-07-15 16:59:25
Objective: mirror the GitHub CI jobs locally.
Jobs:
- windows: compileall rc=0, pytest rc=0
- docs-gates: parity rc=0 (see 02)
- secret-scan: see 05
Result: PASS
Note: GitHub Actions will run the same on windows-latest/ubuntu-latest.
