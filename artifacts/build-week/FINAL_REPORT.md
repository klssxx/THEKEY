# THEKEY Build Week final report

## Final status

**PARTIAL — FINAL REAL-WPF UI SMOKE PASS; PRODUCT AND REPOSITORY READY;
OWNER-ONLY SUBMISSION ACTIONS PENDING.**

The Windows application, governed backend, clean package, deterministic demo,
tests, DPI captures, security scans and visual comparison pass. The remaining
work is external to the repository: record/upload the video, invoke a new
Codex `/feedback` from the signed-in UI if desired, configure judge access, and
submit Devpost before the deadline.

## Final smoke evidence categories

| Category | Result | Scope and retained evidence |
| --- | --- | --- |
| `AUTOMATED_TESTED` | PASS | Focused portable-entry regression recorded in `artifacts/build-week/final-smoke-2026-07-21/SMOKE_EXECUTION.json`. |
| `PACKAGED_BACKEND_EXECUTED` | PASS | The packaged backend completed inspection, isolated verification, repair preview/apply with backup and re-test, Judge demo, and persisted-evidence validation. |
| `OWNER_VERIFIED_UI` | PASS | The owner manually completed the full smoke in the real THEKEY WPF window. Six content-addressed captures are retained under `artifacts/build-week/final-smoke-2026-07-21/owner-ui-smoke/`. |

The owner-verified sequence covered usable launch, `SAMPLE-PYTHON-APP`
selection, read-only inspection, isolated verification with evidence, repair of
`SAMPLE-REPAIRABLE-PYTHON-APP` through `REPAIRED_AND_VERIFIED` with backup and
re-test, Judge demo, persisted results, clean close, and a second open. This
owner confirmation is distinct from both automated tests and direct packaged
backend execution.

The indexed capture set is `01-home.png`, `02-inspection-pass.png`,
`03-verification-pass.png`, `04-repair-pass.png`, `05-judge-demo-pass.png`, and
`06-results.png`; `EVIDENCE_INDEX.json` binds their SHA-256 values.

## Provenance

- Branch: `implementation/portable-windows-app`
- Baseline commit: `d1c37b9ec2d43289fd9db123e1450dc625e4b305`
- Verified implementation commit: `3038bd82c6cc1916f93c74d96b7c26a88d094274`
- Implementation author/committer: GitHub alias `klssxx`
- Package source state: `CLEAN`, `source_commit_exact=true`
- Evidence report state: committed separately after the clean implementation
  build; use `git log -2 --oneline` to identify both pushed commits.

## Final package

- Path: `dist/THEKEY-Portable-Windows-x64.zip`
- Size: `22,133,899` bytes
- SHA-256: `c1df620d024b3ef05219af014ccdf0fd8b9cea05d8d3dbca266cfcc36086c423`
- Manifest: 120 distributed files, 0 missing files, 0 hash mismatches
- Platform: Windows 10/11 x64; verified on Windows 11
- Exact run: `.\dist\THEKEY-Portable-Windows-x64\THEKEY.exe`

## Gates

| Gate | Result | Evidence |
| --- | --- | --- |
| Startup and native main window | PASS | Final package created the 1448 × 1086 native capture |
| Canonical composition / no invented sections | PASS | Iteration 12 capture and regional diff |
| Native text, controls and vector icons | PASS | WPF visual tree; reference is comparison-only |
| DPI 100/125/150/200% | PASS | 1448×1086, 1810×1358, 2172×1629, 2896×2172 captures |
| Select and analyze | PASS | Native folder dialog, read-only inspection, validation and cancellation |
| Verify | PASS | Isolated copy, consent, real gates, streamed progress and persisted evidence |
| Repair | PASS | Isolated preview, second consent, backup, re-test and rollback protection |
| Judge demo | PASS | Repeated package run, exit 0, 4/4 gates, bound receipts, source unchanged |
| Results | PASS | Structured real JSON fields and truthful empty state |
| Navigation / accessibility | PASS | Seven real views, keyboard focus and accessible names |
| Full regression | PASS | 192 passed, 0 failed |
| Portable build / archive | PASS | Clean exact build and manifest validation |
| Secret review | PASS | Entropy scanner and CI-equivalent regex scan |
| Build Week documentation | PASS | README, English README, function/visual contracts, demo and Devpost files |
| Video and Devpost submission | PARTIAL | Explicit owner action; not fabricated or submitted by this run |

## Functional validation

- `OWNER_VERIFIED_UI`: PASS in the real WPF window for the complete final
  smoke sequence described above; screenshots are indexed separately from the
  automated and backend-executed evidence.
- Valid inspection and isolated verification: PASS.
- Missing path: rejected with `INVALID_ARGUMENTS` and exit 2.
- Unsupported/no-test project: blocked with `NO_VERIFICABLE` and exit 5.
- Repair preview: `REPAIR_READY`, original unchanged.
- Explicit repair apply on a workspace copy: `REPAIRED_AND_VERIFIED`, backup
  created and post-apply gates passed.
- UI automation fallback: window, real Analyze/Results views, selector cancel,
  active-operation cancellation, post-cancel demo and clean close passed.
- Exact extracted final ZIP: manifest 120/120, demo exit 0, source unchanged,
  native capture SHA-256
  `75f1007e1eb9e41efa526fc3247a8ef4ce2914469147353cebc65a1a5741d0b8`.

## Visual validation

- Reference: `design/reference/THEKEY_BUILD_WEEK_CANONICAL.png`
- Final capture: `artifacts/build-week/visual/iteration-12/actual.png`
- Diff: `artifacts/build-week/visual/iteration-12/diff.png`
- Report: `artifacts/build-week/visual/iteration-12/report.json`
- Global similarity: **94.336%**; MAE: `0.056639`
- Equal-weight regional similarity: **93.906%**
- Foreground similarity: **85.571%**
- Edge similarity: **92.222%**
- Changed-pixel ratio: **26.026%** at channel delta > 12
- Region similarity: title 96.252%, navigation 95.219%, hero 93.131%,
  primary action 91.373%, cards 93.346%, modes 93.021%, activity 95.003%.
- Justified residuals: the project-owned king/board art is not the exact
  reference artwork, WPF/system-font antialiasing differs, and activity shows
  real current evidence instead of the reference's illustrative historical
  rows. Mathematical pixel identity is not claimed.

## Commands executed

```powershell
.\.thekey\portable-build-venv\Scripts\python.exe -m pytest -q
.\scripts\build-portable.ps1 -Python .\.thekey\portable-build-venv\Scripts\python.exe
.\scripts\verify-pixel-ui.ps1 -Executable .\dist\THEKEY-Portable-Windows-x64\THEKEY.exe -Dpi 96
python .\scripts\compare-build-week-visual.py --reference .\design\reference\THEKEY_BUILD_WEEK_CANONICAL.png --actual .\artifacts\build-week\visual\iteration-12\actual.png --output-dir .\artifacts\build-week\visual\iteration-12
.\dist\THEKEY-Portable-Windows-x64\core\THEKEY-Core\THEKEY-Core.exe portable-demo
.\.thekey\portable-build-venv\Scripts\python.exe scripts\ci\secret_entropy.py --root .
```

## Principal modified files

- `portable/windows/TheKeyLauncher.cs`
- `scripts/build-portable.ps1`
- `scripts/verify-pixel-ui.ps1`
- `scripts/compare-build-week-visual.py`
- `tests/unit/test_portable_entry.py`
- `README.md`, `README.en.md`, `portable/windows/README-FIRST.txt`
- `docs/BUILD_WEEK_FUNCTION_MAP.md`, `docs/THEKEY_VISUAL_CONTRACT.md`
- `docs/BUILD_WEEK_NEW_WORK.md`, `docs/CODEX_GPT56_USAGE.md`
- `docs/DEMO_SCRIPT_3_MINUTES.md`, `docs/DEVPOST_DESCRIPTION.md`
- `docs/SUBMISSION_CHECKLIST.md` and the updated `docs/build-week` judge files
- Curated baseline, DPI and iteration-12 evidence under `artifacts/build-week`

## Remaining blockers

No remaining technical blocker in the repository or portable package.
The final in-window WPF smoke is complete. Remaining owner-only actions are to
create the video, invoke new `/feedback` in the Codex UI, confirm public/private
judge access and artifact hosting, then submit Devpost.
