# THEKEY — Block 1 handoff

## Status

**BLOCK 1 COMPLETE / GATES NOT MET.** The requested priority order was
processed without reopening unrelated repository areas: Hero, Sidebar, Modes,
Activity assessment, CTA, then Cards. The result is deliberately **FAIL**:
every named region must satisfy every configured threshold, and none does.
Do not start Devpost or PRIOR_ART work from this checkpoint.

## Canonical project identity

- Visible name: `THEKEY The King of Checkmate`
- Slug: `thekey`
- Feedback Session ID: `019f82e5-5a39-7901-946f-24ddbe1e528f`

## Scope completed in this continuation

- Generated reproducible, transparent canonical-decoration assets. Their
  retained pixels are exact source pixels; text, cards, buttons, CTA, local
  mode, and navigation controls remain native WPF.
- Hero: replaced project art with the canonical king, board, lighting,
  texture, and landscape crop; ran the two remaining permitted iterations
  (14 and 15). It improved, but still fails and must not be changed again.
- Sidebar: added canonical crown/halo/landscape decoration and fixed the
  decoration layer so it cannot change native navigation geometry.
- Modes: aligned card widths/gap and replaced only inner texture/emblem art
  with transparent canonical crops; cards, badges, and text remain WPF.
- CTA: corrected native target-ring diameter and copy offset.
- Cards: corrected native emblem/top-title vertical alignment.
- Activity: intentionally left real persisted activity untouched. The
  canonical reference depicts four historical records while this clean run
  truthfully shows `Sin actividad todavía / No activity yet`; seeding the
  reference rows would fabricate evidence.

## Modified files

- `portable/windows/TheKeyLauncher.cs`
- `portable/windows/assets/THEKEY_hero_canonical_decor.png`
- `portable/windows/assets/THEKEY_sidebar_canonical_decor.png`
- `portable/windows/assets/THEKEY_mode_king_canonical_decor.png`
- `portable/windows/assets/THEKEY_mode_checkmate_canonical_decor.png`
- `portable/windows/assets/README.md`
- `scripts/build-portable.ps1`
- `scripts/extract-canonical-hero-decor.ps1`
- `scripts/extract-canonical-sidebar-decor.ps1`
- `scripts/extract-canonical-mode-decor.ps1`
- `tests/unit/test_portable_entry.py`
- `artifacts/build-week/visual/iteration-20/BLOCK1_CATEGORY_ASSESSMENT.json`
- `CODEX_HANDOFF.md`

## Metrics — iteration 13 baseline → iteration 20 final

Thresholds: p95 edge distance ≤ 4 px; max edge distance ≤ 8 px; SSIM ≥ 0.95;
RGB delta > 12 ≤ 5%. The final comparison and every regional `actual.png`,
`overlay-50.png`, `diff.png`, and `report.json` are below
`artifacts/build-week/visual/iteration-20/`.

| Region | Baseline SSIM | Final SSIM | Baseline RGB >12 | Final RGB >12 | Final p95/max px | Result |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| Sidebar | 0.284417 | 0.428386 | 22.469% | 12.305% | 0 / 9 | FAIL |
| Hero | 0.269738 | 0.447374 | 27.889% | 10.745% | 9 / 9 | FAIL |
| Modes | 0.259888 | 0.432143 | 43.317% | 36.550% | 9 / 9 | FAIL |
| Activity | 0.221295 | 0.134502 | 16.159% | 15.588% | 9 / 9 | FAIL |
| CTA | 0.485883 | 0.492657 | 57.217% | 57.064% | 3 / 9 | FAIL |
| Cards | 0.188153 | 0.253861 | 22.250% | 21.702% | 2 / 9 | FAIL |

No PASS is declared. Full-canvas similarity is 95.326%; it cannot override
the separate regional gates.

## Separate threshold analysis

See `artifacts/build-week/visual/iteration-20/BLOCK1_CATEGORY_ASSESSMENT.json`.

1. **Geometry.** Sidebar p95 now passes at 0 px; CTA and cards p95 pass at 3
   and 2 px. Every remaining max-edge value is 9 px, caused by unmatched
   native glyph/icon edges and data rows; all regions therefore fail the
   strict 8-px maximum.
2. **Decorative art.** The hero retains 220,813 exact source pixels and the
   sidebar retains 202,403; both were pixel-verified with 0 retained-pixel
   mismatches. The modes use masked exact interior texture/emblem crops.
   Decoration is not the reason to rasterize UI controls.
3. **Text.** Reference glyph rasterization differs from WPF's native font
   rendering/metrics. This is material in hero, sidebar, modes, CTA, and
   cards, and cannot be resolved by rasterizing text under the stated rule.
4. **Icons.** Reference icons use different crown/shield/tool/target artwork
   from the native vector `CreateIcon` geometry. Exact decoration crops cover
   non-interactive crown/emblem artwork; action and navigation icons remain
   native WPF, leaving unmatched structural edges.
5. **Activity data.** Four reference historical events cannot be shown in an
   empty, real activity store without fabricating provenance. This is the
   decisive activity mismatch, not WPF antialiasing.

These constraints make an SSIM of 0.98 (and even the configured 0.95) impossible
without violating either native-control requirements or data integrity.

## Relevant verification commands

```powershell
.\scripts\build-portable.ps1 -Python .\.thekey\portable-build-venv\Scripts\python.exe
.\.thekey\portable-build-venv\Scripts\python.exe -m pytest -q tests\unit\test_portable_entry.py
.\scripts\verify-pixel-ui.ps1 -Executable .\dist\THEKEY-Portable-Windows-x64\THEKEY.exe -OutputDirectory .\artifacts\build-week\visual\iteration-20 -Dpi 96
& 'C:\Users\KLSX\AppData\Local\Programs\Python\Python312\python.exe' .\scripts\compare-build-week-visual.py --reference .\artifacts\build-week\visual\iteration-20\reference.png --actual .\artifacts\build-week\visual\iteration-20\actual.png --output-dir .\artifacts\build-week\visual\iteration-20 --allow-failures
```

The final capture is native WPF at 1448 × 1086, DPI 96. The comparator uses
the local Python 3.12 installation because the portable-build venv lacks
NumPy and Pillow.

Relevant test result: **14 passed** (`tests/unit/test_portable_entry.py`, with
an isolated workspace `--basetemp` because the global pytest temp directory is
not readable in this sandbox).
