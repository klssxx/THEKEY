# OpenAI Build Week submission checkpoints

Last rules audit: **2026-07-21**. The [Official Rules](https://openai.devpost.com/rules)
and the [hackathon website](https://openai.devpost.com/) are the controlling
sources. The [official FAQ](https://openai.devpost.com/details/faqs) and the
[official organizer checklist](https://openai.devpost.com/updates/45362-openai-build-week-halfway-there-where-are-you)
provide submission guidance. If they conflict, the Official Rules prevail.

Status legend: `[x]` verified in the repository; `[ ]` requires the submission
owner or an authenticated external account. This file does not claim that a
Devpost submission, repository publication, or video upload has occurred.

## Checkpoint 0 — deadline and ownership

- [ ] Submit the final Devpost entry before **July 21, 2026 at 5:00 PM Pacific
  Time**. A draft may be saved earlier, but the Official Rules say the entry
  cannot be substantively edited after the submission period ends.
- [ ] The submission owner confirms age, territory and all other eligibility
  requirements in the Official Rules.
- [ ] If submitting as a team or organization, appoint an eligible authorized
  representative and ensure every intended teammate has joined and accepted
  the Devpost invitation before the deadline.
- [ ] The submission owner confirms the project did not receive disqualifying
  financial or preferential support from OpenAI or Devpost and accepts the
  Official Rules.

## Checkpoint 1 — Stage One eligibility gate

- [x] Track selected: **Developer Tools**. THEKEY is a developer-facing tool for
  testing, agentic workflows, governance and security, matching the official
  [track description](https://openai.devpost.com/#requirements).
- [x] The repository documents a working, non-trivial implementation rather
  than a concept-only submission.
- [x] Codex and GPT-5.6 were used meaningfully during development and
  verification, with concrete work and sanitized evidence documented in
  `README.en.md` and `docs/build-week/CODEX_SESSION_EVIDENCE.md`.
- [x] The primary `/feedback` Codex Session ID is recorded in the English
  README and the sanitized session-evidence document.
- [x] THEKEY is declared as a pre-existing project. The evaluable work after the
  session baseline is separated in `docs/build-week/BUILD_WEEK_DELTA.md`, with
  supporting commit/session evidence as required for pre-existing projects.
- [ ] Paste the verified primary `/feedback` Session ID into the Devpost form.

The official FAQ requires both Codex and GPT-5.6 to be used meaningfully and
asks for evidence in the description, README, repository and video. THEKEY
describes them truthfully as **development and validation tooling**, not as a
runtime API dependency.

## Checkpoint 2 — required Devpost fields

- [x] English project title, tagline, track and text description are prepared
  in `docs/DEVPOST_DESCRIPTION.md`.
- [x] The description explains what THEKEY does, how it works, the intended
  audience, the safety boundary, the new Build Week work, and the concrete
  Codex/GPT-5.6 contribution.
- [x] An English README includes setup, sample data, exact test/demo guidance,
  supported Windows platform and limitations.
- [ ] Enter the title, tagline, **Developer Tools** track, description,
  repository URL, testing instructions and primary `/feedback` Session ID in
  Devpost.
- [ ] Review the rendered entry for broken Markdown, clipped screenshots,
  inaccurate claims, private paths, personal data and secrets before submit.
- [ ] Rewrite/review the final description in the submission owner’s own voice;
  the official organizer guidance says not to submit AI-drafted copy as-is.

All submitted materials must be in English or have an English translation.
The prepared English description and `README.en.md` satisfy the repository-side
part of this requirement.

## Checkpoint 3 — repository and judge access

- [x] The repository retains its existing MIT license; no license replacement
  is proposed.
- [x] Installation instructions, supported platform and a deterministic judge
  path that does not require rebuilding from source are documented.
- [x] The portable judge path requires no API key, paid service, login or
  private sample data.
- [x] Sample data needed for the deterministic demo is included in the project.
- [ ] Push the final audited commit to the exact repository URL entered in
  Devpost.
- [ ] Make that repository public with the relevant license **or**, if it stays
  private, grant access to both `testing@devpost.com` and
  `build-week-event@openai.com` before submission.
- [ ] Provide the final Windows test build or functioning demo free of charge
  and without restriction through the end of judging (**August 5, 2026 at
  5:00 PM Pacific Time**).
- [ ] From a clean Windows account or clean VM, download the exact judge
  artifact from its submitted URL, verify its checksum, launch it and complete
  Judge Mode without relying on the development workspace.
- [ ] Confirm that any third-party libraries, fonts, icons, images and sample
  data are used under compatible licenses and that required notices are
  present.
- [ ] The submission owner confirms originality, ownership, permission for all
  submitted material, and absence of third-party rights or privacy violations.

The Official Rules expressly say judges are not required to build or even run
the project. The description, screenshots and demo therefore must be accurate
and independently understandable even though a runnable build is supplied.

## Checkpoint 4 — adversarial product and evidence gate

- [x] Final package launches on the declared Windows version without a
  developer toolchain.
- [x] `OWNER_VERIFIED_UI` final smoke completed manually in the real THEKEY
  WPF window: usable launch, sample selection, read-only inspection, isolated
  verification, repair with backup and re-test, Judge demo, persisted results,
  clean close and second open. The six screenshots under
  `artifacts/build-week/final-smoke-2026-07-21/owner-ui-smoke/` are
  SHA-256-indexed in the adjacent `EVIDENCE_INDEX.json`.
- [x] Main window renders without clipping at 100%, 125%, 150% and 200% DPI.
- [x] Canonical screen is visually compared against the reference; final
  capture, diff and measured similarity are retained as evidence.
- [x] Judge Mode completes deterministically from the candidate artifact and
  leaves the bundled source sample unchanged.
- [x] Selecting a valid project, cancelling selection, an invalid path and an
  unsupported input all produce truthful outcomes.
- [x] Verify emits real bound evidence; Repair uses an isolated copy, explicit
  consent, re-test and rollback/backup protections; Results displays only
  persisted real data.
- [x] Full automated suite, packaging smoke test, secret scan and evidence
  verifier pass on the exact final commit.
- [x] Scan the distributed archive and confirm it contains no disabling device,
  credential, unrelated binary or private development file.
- [x] No UI state claims success, safety or repair without evidence generated
  by that run.
- [ ] Final commit SHA, artifact SHA-256, test count and commands are recorded
  in the final report and match the submitted build.

These are product-quality gates, not additional official form fields. They are
included because the official judging criteria require a working, runnable and
coherent product—not merely a technical proof of concept.

## Checkpoint 5 — four equally weighted judging criteria

### Technological Implementation

- [x] The repository explains the concrete, non-trivial use of Codex and
  GPT-5.6 and links it to inspect/design/implementation/test decisions.
- [x] A judge can reproduce the central claim and inspect the resulting JSON
  evidence in under three minutes.
- [x] The final repository contains no disconnected controls, fabricated
  results, embedded credentials or unexplained failing tests.

### Design

- [x] The final experience is complete and coherent from launch to evidence,
  including empty, loading, error, cancel and success states.
- [x] The canonical visual, secondary views, keyboard focus, accessible names
  and DPI scaling pass final human review.
- [x] Approved screenshots show only the final runnable product and correspond
  to the exact submitted build.

### Potential Impact

- [x] The description names a specific audience: developer teams using coding
  agents on local projects.
- [x] The problem and demonstrated outcome are specific: authorize operations,
  isolate execution, apply deterministic gates and retain auditable evidence.
- [ ] The final Devpost entry makes no unsupported adoption, performance,
  security or market-impact claim.

### Quality of the Idea

- [x] The draft identifies the differentiator: a governed transaction with
  plan-bound authorization, fail-closed gates and evidence—not another generic
  coding assistant.
- [ ] The final text clearly distinguishes THEKEY from ordinary test runners,
  autonomous repair agents and decorative security dashboards using only
  demonstrated behavior.

The criteria above mirror the four equally weighted criteria in the
[Official Rules](https://openai.devpost.com/rules): Technological
Implementation, Design, Potential Impact and Quality of the Idea.

## Checkpoint 6 — screenshots and submission integrity

- [x] Select final screenshots that show the canonical home, a real governed
  decision/evidence view and the deterministic judge result.
- [x] Ensure screenshots contain no personal path, notification, account,
  unrelated window, credential, raw session log or fabricated activity.
- [x] Confirm every visible claim matches the submitted artifact and persisted
  evidence.
- [ ] Confirm all links work in a signed-out browser and all private-repository
  invitations are accepted.
- [ ] Save a local copy of the exact submitted description, links, final commit
  and Devpost confirmation.

Screenshots are an adversarial presentation checkpoint, not stated as a
mandatory field in the Official Rules. They matter because judges may evaluate
the entry solely from its description, images and video.

## Video — deliberately pending for the submission owner

- [ ] **PENDING USER ACTION — not produced or uploaded here.** Record a clear
  working-product demo with audio, **less than three minutes**; explain what
  was built and the concrete use of both Codex and GPT-5.6; avoid unlicensed
  music, trademarks and copyrighted material; upload it as a public YouTube
  video; then add its URL to Devpost.

The video is an official submission requirement, but its production and upload
are explicitly reserved for the submission owner.

## Final release decision

- [ ] All applicable checkpoints above are complete.
- [ ] Final repository/build links, access permissions and checksums have been
  re-tested after the last commit.
- [ ] The owner has reviewed the submission in their own voice and authorized
  publication.
- [ ] Devpost confirms submission before the deadline.

Do not mark the release `READY` from local evidence alone. `READY` requires the
external repository access, exact test build, `/feedback` field and Devpost
confirmation; the video remains the owner’s pending action until supplied.
