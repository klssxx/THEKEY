# OpenAI Build Week delivery checkpoints

This checklist is a release record for the final Build Week candidate. It
separates verified facts from actions that require the submission owner's
authenticated account or a public-video URL. It must not be treated as a
substitute for the [Official Rules](https://openai.devpost.com/rules).

## Checkpoint 1 — rules and eligibility

- [x] Developer Tools is the selected track.
- [x] The repository identifies the project as pre-existing and documents the
  post-baseline delta in `BUILD_WEEK_DELTA.md`.
- [x] The README and Devpost draft identify Codex and GPT-5.6 use, the primary
  `/feedback` Session ID, installation instructions, supported platforms, and
  a judge path that does not require rebuilding the app.
- [x] Submission materials are prepared in English.
- [ ] The submission owner confirms individual/team eligibility and accepts the
  official rules in Devpost.

## Checkpoint 2 — product truthfulness and Windows presentation

- [x] The portable launcher declares Per Monitor V2 DPI awareness and uses
  high-quality downscaling for small displays.
- [x] The visible system-status and activity areas are live launcher panels;
  no illustrative health percentage, date, activity, or repair result is shown
  as live data.
- [x] The live status panel reports only locally established facts: backend
  availability, build-manifest presence, no network use, and the selected
  application.
- [x] Visual verification remains exact outside the two explicitly documented
  live-data regions.

## Checkpoint 3 — reproducible package

- [x] Windows x64 portable package built with Python 3.13.13 and PyInstaller
  6.21.0.
- [x] Package contains the WPF launcher, frozen core, judge sample, repair
  sample, guide, build manifest, and ZIP archive.
- [x] Final local ZIP SHA-256 is recorded by `scripts/build-portable.ps1` in
  its build output. Rebuild after the Git commit to bind the manifest to the
  final source commit.

## Checkpoint 4 — functional and safety gates

- [x] Full regression suite: 190 passed, 1 skipped (symlink creation is not
  supported on this filesystem).
- [x] Modified Python files pass Ruff.
- [x] Judge Mode from the final portable package: ALLOW invokes one handler,
  DENY invokes zero, 4/4 gates pass, decision is `RELEASE_ELIGIBLE`, source is
  unchanged, and bound receipts validate.
- [x] The packaged repair sample is inspected, blocked on its initial defect,
  repaired only after explicit test and apply consents, and re-verified as
  `REPAIRED_AND_VERIFIED` in a temporary copy.
- [x] Pixel verification reports `PIXEL_EXACT` for all static pixels.

## Checkpoint 5 — Git and submission readiness

- [ ] Commit the audited candidate and push it to the repository used in the
  Devpost submission.
- [ ] Make the repository public with its license, or grant both
  `testing@devpost.com` and `build-week-event@openai.com` access when private.
- [ ] Replace `PENDING_PUBLIC_YOUTUBE_URL` in `DEVPOST_DRAFT.md` with a public
  YouTube URL for a video under three minutes with English narration explaining
  the working demo, Codex, and GPT-5.6.
- [ ] Enter the public repository URL, YouTube URL, selected track, text
  description, and `/feedback` Session ID in Devpost; save/submit before the
  official deadline.

## Final checkpoint — publication

This checkpoint is PASS only after the final candidate is pushed to the chosen
repository and Devpost confirms the submission. Record the final Git commit,
repository URL, public YouTube URL, and Devpost confirmation URL here. Do not
claim it complete from local build evidence alone.
