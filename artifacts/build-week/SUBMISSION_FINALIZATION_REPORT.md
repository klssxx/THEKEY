# THEKEY — OpenAI Build Week 2026 submission finalization

**Verdict: READY_WITH_MANUAL_STEPS**

Prepared at: 2026-07-21T22:57:48Z

## Verified repository state

| Field | Value |
| --- | --- |
| Initial checkout commit | 67ffe6862b9f4c03463f2f06afd31ac313b22105 |
| Working branch | implementation/portable-windows-app |
| Remote | https://github.com/klssxx/THEKEY.git |
| Pre-period Git base | none reachable before 2026-07-13T16:00:00Z |
| First reachable commit | b7b6c32cf3a2621d29ef2c5856db50d116d8dff6 at 2026-07-15T06:34:40+02:00 |
| Portable artifact | dist/THEKEY-Portable-Windows-x64.zip |
| Portable SHA-256 | 589cdb85a7c478148b72d0337cfdb8b8454acc4e4c7c782b6e9a05b3969e2f0f |
| Portable manifest source commit | 5cbab680c59ef3c0c1f2709f6540bf2b520c6495 |
| Portable manifest state | CLEAN; source_commit_exact=true |
| Primary /feedback ID | 019f79f2-6a7e-74f0-b1fa-d65335b29a7c |

The frozen Git/tag ref is `openai-build-week-2026-submission` (annotated tag object `3f101f5d87eb7f5fba1a99f61587e8be505293e9`) and resolves to commit `917b546772a3a919d2030bc61bd924f09921e04d`.

Publication completed after the freeze:

- Branches `main` and `implementation/portable-windows-app` were pushed at `917b546772a3a919d2030bc61bd924f09921e04d`.
- Release: https://github.com/klssxx/THEKEY/releases/tag/openai-build-week-2026-submission
- ZIP asset: https://github.com/klssxx/THEKEY/releases/download/openai-build-week-2026-submission/THEKEY-Portable-Windows-x64.zip
- GitHub reports the uploaded ZIP as `22,846,085` bytes with digest `sha256:589cdb85a7c478148b72d0337cfdb8b8454acc4e4c7c782b6e9a05b3969e2f0f`.

## Verification performed

- Portable outer hash, ZIP structure, required paths, and safe archive paths: PASS.
- Manifest: 124 files re-hashed, 0 mismatches: PASS.
- Matching on-disk launcher signature check: NotSigned; SmartScreen limitation documented.
- Limited obvious-token scan of archive text: 0 findings.
- Focused portable regression: python -m pytest -q tests/unit/test_portable_entry.py — **14 passed**.
- Entropy secret scan: python scripts/ci/secret_entropy.py --root . — PASS.
- Relative links in new/changed Build Week documentation and release JSON parsing: PASS.

The previous final report retains the owner-verified Windows WPF smoke, packaged backend execution, and broader regression evidence. This finalization did not rebuild or alter the canonical ZIP.

## Material added or corrected

- English GitHub landing page, Spanish pointer, and five-minute JUDGES.md.
- Portable checksum, static artifact report, release notes, and SmartScreen disclosure.
- Judge testing instructions, Devpost copy, primary/session-register clarification, and a correction that labels the visual handoff as supplementary rather than the primary Devpost session.
- Provenance index that documents the absence of a reachable pre-period commit and a chat-evidence inbox that refuses fabricated transcripts.
- Updated final report wording so it does not request a new /feedback ID where the primary ID is already recorded.

## Manual steps still required

1. Upload/publish the user’s YouTube video (under three minutes, with audio explaining Codex/GPT-5.6 use), paste its URL into Devpost, and submit.
2. Select **Developer Tools**, use the primary `/feedback` ID, paste the repo, release, and video URLs, then confirm Devpost shows **Submitted**, not Draft.
3. If available before submission, add only authentic, sanitized pre-period chat exports to docs/build-week/provenance/chat-evidence/.

## Residual risks and truth limits

- The owner reports a pre-existing THEKEY project, but this checkout has no reachable commit before the Submission Period; that limitation is now clear in the README and provenance dossier.
- No chat export was supplied in this checkout. None was reconstructed.
- The portable executable is unsigned. The checksum and SmartScreen guidance are published; signing is not claimed.
- The GitHub Release is public and the ZIP asset digest matches the canonical SHA-256. Video URL, Devpost category, and final **Submitted** state remain owner-controlled external facts and are not represented as complete here.

## Gate summary

    THEKEY OPENAI BUILD WEEK FINALIZATION
    Repository: PASS
    Portable hash: PASS
    Judge path: PASS
    Pre-existing provenance: READY_WITH_DOCUMENTED_LIMIT
    Build Week delta: PASS
    Codex/GPT-5.6 evidence: PASS
    Primary /feedback ID: PRESENT
    GitHub push: PASS
    GitHub release: PASS
    Devpost manual fields: video URL, category, final Submitted state
    FINAL VERDICT: READY_WITH_MANUAL_STEPS
