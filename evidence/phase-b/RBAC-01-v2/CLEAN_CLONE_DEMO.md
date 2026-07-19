# Clean-clone demo — Windows paths with spaces

Generated at `2026-07-19T14:36:16.059Z`.

## Verified clone

- Path: `.thekey/CC Space`
- Fresh clone at parent commit: CLEAN.
- Candidate reconstructed from tracked binary diff plus 19 explicit new files.
- Protected `scripts/make_thelkey_guide_pdf.py`: absent.
- Full regression: `148 passed, 1 skipped in 30.95s`.
- Judge Mode: exit `0`, 2.68 seconds.
- ALLOW: `APPLIED`, one handler.
- Adversarial DENY: `ROLE_NOT_ALLOWED`, zero handlers, workspace hash unchanged.
- Gates: 4/4 PASS.
- Release decision: `RELEASE_ELIGIBLE`.

## Long-path observation

A deeper clean-clone path with spaces passed all 149 tests, but Judge Mode hit a
Windows path-length failure while creating an atomic policy-snapshot temporary
file. This is recorded as a Windows long-path limitation, not hidden as a pass.
The required path-with-spaces reproduction passes at the shorter clean path.
