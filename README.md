# THEKEY — THE KING OF CHECKMATE

**Governed Codex transactions for safer coding-agent changes.**

**OpenAI Build Week 2026 — Developer Tools submission.** THEKEY is a
pre-existing project reported by its owner and meaningfully extended during the
Submission Period. This repository distinguishes the documented Build Week
extension from prior-work claims and does not invent missing historical proof.

[Español](README.es.md) · [Judge path](JUDGES.md) · [Build Week delta](docs/build-week/BUILD_WEEK_DELTA.md) · [Codex/GPT-5.6 usage](docs/build-week/CODEX_AND_GPT56_USAGE.md) · [Provenance](docs/build-week/provenance/PROVENANCE_INDEX.md) · [MIT License](LICENSE)

## Download the Windows portable judge build

[**Download THEKEY-Portable-Windows-x64.zip**](https://github.com/klssxx/THEKEY/releases/download/openai-build-week-2026-submission/THEKEY-Portable-Windows-x64.zip)

The GitHub Release asset is preferred. The identical, tag-pinned emergency
fallback is [versioned in the repository](https://github.com/klssxx/THEKEY/raw/openai-build-week-2026-submission/releases/openai-build-week-2026/THEKEY-Portable-Windows-x64.zip).

Windows 10/11 x64 · no build · no Python · no Git · no API key · no account

SHA-256:

```text
589cdb85a7c478148b72d0337cfdb8b8454acc4e4c7c782b6e9a05b3969e2f0f
```

```powershell
Get-FileHash .\THEKEY-Portable-Windows-x64.zip -Algorithm SHA256
```

The portable binaries are not Authenticode-signed. Windows may show **Unknown
publisher**; verify the published SHA-256 before running.

## Judge in 60 seconds

1. Download, verify, and fully extract the ZIP to a short writable folder.
2. Run `THEKEY.exe`.
3. Click **Demo para jueces / Judge demo**.
4. Inspect the persisted result in **Ver resultados / View results**.
5. For the product flow, choose `SAMPLE-PYTHON-APP`, then
   `SAMPLE-REPAIRABLE-PYTHON-APP` for a bounded repair and re-test.

The bundle contains the runtime, samples, a manifest, and first-run guidance.
It does not require Python, Git, PowerShell, Docker, WSL, API keys, a GPU,
payment, or a test account. Read [JUDGES.md](JUDGES.md) for the five-minute
path and [testing instructions](docs/build-week/TESTING_INSTRUCTIONS.md) for
the full procedure.

## What problem it solves

Coding agents can edit code quickly, but teams still need to know which plan was
approved, what was permitted to run, which checks passed, and how to review a
result later. THEKEY treats those controls as one transaction rather than an
after-the-fact narrative.

## What THEKEY does — and does not do

THEKEY binds a plan, CHECKMATE pre-action review, explicit scoped human
authorization, deterministic policy, physical dispatch, verification gates, and
persisted evidence to one run and transaction.

- **THEKEY** is the governed-transaction product.
- **THE KING** orchestrates phases and context; it cannot self-approve.
- **CHECKMATE** reviews risk before execution and does not perform physical
  writes.
- **Codex with GPT-5.6** was used to develop and review the project; it is not
  a runtime dependency.

THEKEY uses an isolated workflow copy for verification and repair. That is **not
an operating-system sandbox**: selected project tests remain trusted local code.
Repair is deliberately bounded, never changes tests or installs dependencies,
and only applies bytes that passed the configured gates with separate consent.

## Demonstrated Build Week contribution

The documented extension includes strict receipt/context contracts, a
fail-closed physical authorization boundary, adversarial denial coverage, Judge
Mode with evidence, portable Windows delivery, WPF integration, included
samples, and retained smoke/verification material. Review the factual
[Build Week delta](docs/build-week/BUILD_WEEK_DELTA.md), [contribution
record](BUILD_WEEK_CONTRIBUTION.md), and
[final smoke report](artifacts/build-week/FINAL_REPORT.md).

## Codex, GPT-5.6, and human responsibility

Codex with GPT-5.6 accelerated codebase inspection, authorization and receipt
design, adversarial tests, regression/rollback checks, Judge Mode evidence, the
portable path, and judge documentation. The verified primary `/feedback`
Session ID is `019f79f2-6a7e-74f0-b1fa-d65335b29a7c`.

The owner retained product and authority decisions, including bounded scope, no
production reuse of the Judge Mode grant, and separate approval for release,
video publication, and Devpost submission. Details and limitations are in
[Codex/GPT-5.6 usage](docs/build-week/CODEX_AND_GPT56_USAGE.md).

## Testing and evidence

The package manifest records its source state and hashes every distributed file;
the outer ZIP hash above anchors the whole package. The final evidence retains
a Windows 11 owner-verified WPF smoke, packaged backend execution, and
automated test results. The smoke record is explicitly separate from automated
testing. See [artifact verification](artifacts/build-week/release/PORTABLE_ARTIFACT_REPORT.md)
and [FINAL_REPORT.md](artifacts/build-week/FINAL_REPORT.md).

## Build from source

Source reproduction is documented in
[Judge Quickstart](docs/build-week/JUDGE_QUICKSTART.md). It requires Windows
11, PowerShell 7, Python 3.11+, and Git; judges do not need this path to
evaluate the portable build.

## Provenance

The owner reports that THEKEY existed before Build Week. The reachable Git
history in this checkout begins after the Submission Period, so it cannot
independently prove the earlier project history. The repository does not claim
otherwise and does not fabricate chats. See the [provenance index](docs/build-week/provenance/PROVENANCE_INDEX.md)
and the [owner-evidence request](docs/build-week/provenance/chat-evidence/NEEDED_FROM_USER.md).

## License and disclosure

THEKEY is distributed under the [MIT License](LICENSE). It was prepared for
OpenAI Build Week 2026; it is not an official OpenAI product and is not endorsed
by OpenAI.
