# Build Week work boundary and attribution

Audit date: 2026-07-21. Prior-art cutoff: `2026-07-13T00:00:00+02:00`.
Functional baseline inspected: `d1c37b9ec2d43289fd9db123e1450dc625e4b305`.
“Inherited” below means inherited by the final desktop session from that
baseline; it does **not** mean it has been verified as pre-period work.

## A. Work evidenced before the period

No repository-local commit, event-store row, manifest, archive, export, or
other internally dated artifact was found before the cutoff. `PRIOR_ART.md`
records the negative audit and its limits. Therefore this repository does not
credit any implementation as verified pre-period work. Owner-supplied dated
ChatGPT exports may add evidence later, but are pending and are not verified.

## B. Work implemented during Build Week

The reachable local Git history starts on 2026-07-15, so its recorded product
and governance work is Build Week work. The final desktop implementation added
the native WPF presentation, real project-flow bindings, results discovery,
cancellation, packaged samples, build automation, DPI checks, visual
measurement, Build Week documentation, and package/evidence verification.

## C. Functionality created with Codex and GPT-5.6

The requested attribution is development collaboration with Codex and GPT-5.6;
the repository has no independently auditable runtime model identifier and does
not claim model-driven governance decisions. The attributable implementation
outputs are:

- the WPF launcher adapter in `portable/windows/TheKeyLauncher.cs`, wired to
  read-only inspection, isolated verification, bounded repair, Judge Mode and
  persisted results;
- asynchronous progress, cancellation and clean-close guards around the
  existing governed CLI;
- real evidence discovery and truthful empty/unavailable states;
- `scripts/build-portable.ps1`, DPI/capture validation and repeatable visual
  comparison tooling; and
- Build Week function mapping, demo, Devpost and verification documentation.

See `docs/CODEX_GPT56_USAGE.md` for the bounded attribution statement and
`docs/CODEX_SESSIONS.md` for the session record.

## D. Functionality that remains inherited

The following functional core was already present in baseline
`d1c37b9ec2d43289fd9db123e1450dc625e4b305` and was reused rather than
reclassified as new desktop functionality:

- governed Python lifecycle, policy engine and CLI;
- isolated workspaces, evidence receipts and event persistence;
- consent-gated verification and repair semantics;
- Judge Mode's core gates; and
- the initial portable-launcher foundation.

These are inherited from the Build Week baseline only. Their existence before
2026-07-13 is not established by this working copy.

## E. Corresponding commits and Codex sessions

| Commit / session | Recorded scope |
| --- | --- |
| `3038bd82c6cc1916f93c74d96b7c26a88d094274` | Final desktop experience and functional WPF integration. |
| `f27a70a8d7e37f2b938bdb09f044dde0d18fb6fb` | Final verification report and evidence documentation. |
| `f96bae18878595ec19082c5c92f7d891dca8dd53` | Complementary visual-alignment checkpoint. |
| `5cbab680c59ef3c0c1f2709f6540bf2b520c6495` | Interactive dashboard work-area functional adaptation. |
| `019f82e5-5a39-7901-946f-24ddbe1e528f` | Principal Devpost session: majority functional development. |
| Secondary visual session | Not registered and not required; no `/feedback` ID is invented. Later visual iterations are complementary. |
