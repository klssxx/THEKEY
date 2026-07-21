# Devpost copy — owner review required

Read and edit this in your own voice before publishing. Replace the video URL and confirm the repository and release are public. Do not submit it unchanged if it no longer matches the final video.

## Project name

THEKEY — The King of Checkmate

## Tagline

Governed Codex transactions for safer coding-agent changes.

## Category

Developer Tools

## Built with

Codex, GPT-5.6, Python, Pydantic, pytest, PowerShell, .NET/WPF, Git

## Description

Coding agents can edit quickly, but teams still need to know what plan was approved, what was allowed to run, which checks passed, and how to review the result later. THEKEY makes those controls part of one governed transaction. It binds a plan identity, CHECKMATE pre-action review, explicit scoped human authorization, deterministic policy, physical dispatch, verification gates, and persisted receipts.

For Build Week I used Codex with GPT-5.6 to inspect and harden the physical execution boundary, implement strict receipt/context contracts and adversarial denials, test and review the governed flows, prepare Judge Mode and evidence, and complete the portable Windows judge experience. I retained the product and authority decisions, including bounded scope, no production reuse of the demo grant, and separate approval for release and submission.

THEKEY was reported by its owner as a pre-existing project. This submission presents only the meaningful, documented Build Week extension; the repository clearly records the limits of the available pre-period Git evidence and does not invent earlier history.

Judges can download the Windows portable build, run the included Judge demo, inspect the healthy sample, and follow a bounded repair of the repairable sample without rebuilding or providing credentials. Workflow isolation is not an operating-system sandbox, selected tests are trusted local code, repairs are deliberately limited, and no guarantee of arbitrary or fully secure code repair is claimed.

## Testing instructions

Windows 10/11 x64: download the release ZIP, verify SHA-256 `589cdb85a7c478148b72d0337cfdb8b8454acc4e4c7c782b6e9a05b3969e2f0f`, extract, and run `THEKEY.exe`. Start with **Demo para jueces / Judge demo**, then use `SAMPLE-PYTHON-APP` and `SAMPLE-REPAIRABLE-PYTHON-APP`. No Python, Git, API key, or account is required. The binaries are unsigned, so Windows may show Unknown publisher; verify the published checksum first. Full steps: [JUDGES.md](../../JUDGES.md).

## Required fields to complete manually

- Video URL: `PENDING_PUBLIC_YOUTUBE_URL`
- Primary `/feedback` Session ID: `019f79f2-6a7e-74f0-b1fa-d65335b29a7c`
- Repository: `https://github.com/klssxx/THEKEY`
- Judge build release: `https://github.com/klssxx/THEKEY/releases/tag/openai-build-week-2026-submission` (preferred); tag-pinned repository fallback is available at `releases/openai-build-week-2026/THEKEY-Portable-Windows-x64.zip`
- Final submit status: confirm **Submitted**, not Draft.
