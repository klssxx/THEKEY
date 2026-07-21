# Build Week new work

Date: 2026-07-21. Baseline commit: `d1c37b9ec2d43289fd9db123e1450dc625e4b305`.

## Existing before this session

The governed Python lifecycle, policy engine, isolated workspaces, evidence
receipts, CLI, bounded repair flow, Judge Mode and the initial portable launcher
already existed. They are not reclassified as new work here.

## Built in this session

- inspected the launcher/backend contract and documented it in
  `BUILD_WEEK_FUNCTION_MAP.md`;
- reconstructed the canonical desktop home screen as native WPF controls;
- replaced Unicode icon placeholders with WPF vector geometry and central theme tokens;
- connected select, verify, repair-preview, explicit repair-apply, demo and
  results pages to existing CLI entry points;
- added real empty states and evidence discovery instead of fabricated rows;
- added streamed backend progress, bounded cancellation and guarded window close;
- added structured persisted-result cards and real recent-activity rows;
- added PerMonitorV2 capture checks at 100%, 125%, 150% and 200% DPI;
- added native canonical capture and repeatable regional visual comparison;
- prepared the requested Build Week, demo and Devpost handoff documents.

## Main files

- `portable/windows/TheKeyLauncher.cs`
- `scripts/verify-pixel-ui.ps1`
- `scripts/compare-build-week-visual.py`
- `docs/THEKEY_VISUAL_CONTRACT.md`
- `docs/BUILD_WEEK_FUNCTION_MAP.md`

The implementation is committed only after build, regression, functional,
security and visual gates pass. The final report records the verified
implementation commit and the separate evidence-only commit so the package
manifest can remain bound to a clean source state.
