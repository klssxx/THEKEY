# Build Week video recording checklist

## Before recording

- [ ] Use 1920×1080, 16:9, at 30 fps or better.
- [ ] Set the terminal and editor font to at least 22 px and verify readability
  at normal playback size.
- [ ] Record from a short clean clone on Windows 11 with PowerShell 7, Python
  3.11+, and the editable package installed.
- [ ] Run `git rev-parse HEAD` and confirm it exactly equals the
  `FINAL_CANDIDATE` SHA in the post-commit handoff. Record that value on screen.
- [ ] Run Judge Mode once before recording and confirm ALLOW has one handler,
  DENY has zero, all four gates pass, and the decision is
  `RELEASE_ELIGIBLE`.
- [ ] Pre-open the README, contribution record, and a safe projection of the
  evidence JSON, plus the sanitized Codex session record.
- [ ] Do not display `run_path`, `workspace_path`, a personal user name, private
  directory names, notifications, browser sessions, session logs, or unrelated
  files.
- [ ] Close password managers and messaging apps; enable Do Not Disturb.
- [ ] Confirm that no API key, token, cookie, email, credential, or secret is
  visible in the terminal, editor, history, tabs, or clipboard.
- [ ] Clear terminal scrollback and command history visible in the recording.
- [ ] Test the microphone, remove echo and background noise, and record a short
  sample to check volume and intelligibility.
- [ ] Rehearse against `VIDEO_SCRIPT.md`; target 2:40–2:55 and set a hard stop
  before 3:00.
- [ ] Use no copyrighted music. Silence or properly licensed audio is safer.

## Claims to verify while speaking

- [ ] Say that THEKEY is a declared preexisting project, that its accessible
  public Git history begins after the cutoff, and that only the verified
  post-baseline delta is submitted.
- [ ] Do not describe `CLAIM_RECORDED` or `PENDING_EVIDENCE_IMPORT` as verified
  pre-cutoff proof.
- [ ] Describe Codex with GPT-5.6 as development and validation tooling only,
  never as a runtime dependency.
- [ ] Do not claim an exact split of work between GPT-5.6 variants or sessions.
- [ ] Say “workflow isolation,” not OS sandboxing.
- [ ] Say the local grant is not a cryptographic human signature.
- [ ] Describe SHA-256 evidence as tamper-evident within the implemented chain,
  not external attestation or invulnerability.
- [ ] Describe the secret scan and the Judge Mode action set as bounded.
- [ ] Do not claim `FULL_CHECKMATE` or resolved pre-baseline provenance.
- [ ] Explain the concrete Codex/GPT-5.6 work: five-caller analysis, adversarial
  cases, governed-boundary implementation, and regression/clean-clone checks.

## During recording

- [ ] Show the live command from invocation through completion without replacing
  its result.
- [ ] Hold the summary long enough to read ALLOW, DENY, 4/4 gates, and the
  release decision.
- [ ] Show the evidence identities and state checks, not only printed marketing
  text.
- [ ] Keep the pointer still while each proof field is being explained.
- [ ] Watch the timer; preserve provenance and limitations if narration needs
  trimming.

## Before publication

- [ ] Export at 1080p using H.264 video and clear AAC audio.
- [ ] Verify the final duration is under 3:00, ideally 2:40–2:55.
- [ ] Watch the exported file from beginning to end with headphones.
- [ ] Check every visible frame for secrets, private paths, names,
  notifications, and unrelated tabs.
- [ ] Add accurate English captions; add an English translation if any spoken
  segment is not in English.
- [ ] Use the prepared `VIDEO_DESCRIPTION.txt` and verify its repository link.
- [ ] Confirm the SHA shown in the video, the checked-out repository HEAD, and
  the Devpost candidate SHA are identical.
- [ ] Upload to YouTube as a **public** video (not unlisted) and ensure it is
  accessible without signing in.
- [ ] Open the YouTube link in an incognito/logged-out window and play the full
  video.
- [ ] Confirm captions, audio, resolution, duration, title, and description on
  the published page before using the link in Devpost.
