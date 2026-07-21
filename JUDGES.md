# THEKEY — Judge start here

**OpenAI Build Week 2026 — Developer Tools submission**

THEKEY is a governed workflow for coding-agent changes: it keeps a declared plan, pre-execution review, explicit authorization, deterministic gates, and persisted evidence together. It is a **pre-existing project reported by its owner**; only the meaningful Build Week extensions documented in this repository are presented for judging.

## Judge it in five minutes

1. On Windows 10/11 x64, download the [portable judge build](https://github.com/klssxx/THEKEY/releases/download/openai-build-week-2026-submission/THEKEY-Portable-Windows-x64.zip). If the Release asset is temporarily unavailable, use the identical [tag-pinned fallback](https://github.com/klssxx/THEKEY/raw/openai-build-week-2026-submission/releases/openai-build-week-2026/THEKEY-Portable-Windows-x64.zip).
2. Verify its SHA-256 before opening it:

   ```powershell
   Get-FileHash .\THEKEY-Portable-Windows-x64.zip -Algorithm SHA256
   # 589cdb85a7c478148b72d0337cfdb8b8454acc4e4c7c782b6e9a05b3969e2f0f
   ```

3. Extract the whole ZIP to a short, writable folder and run `THEKEY.exe`.
4. Select **Demo para jueces / Judge demo** for the shortest reproducible governed transaction and persisted-evidence check.
5. For the application path, use `SAMPLE-PYTHON-APP` first, then `SAMPLE-REPAIRABLE-PYTHON-APP` to observe a bounded repair and re-test.
6. Open **Ver resultados / View results** to inspect the persisted outcome.

No Python, Git, PowerShell, Docker, WSL, API key, GPU, payment, or test account is required for the bundled demo and samples. Tests from a project selected by the judge are still trusted local code: THEKEY uses a workflow copy, **not** an operating-system sandbox.

The portable binaries are not Authenticode-signed. Windows may show an **Unknown publisher** warning; verify the SHA-256 above before running. The artifact is free and intended to remain available through judging.

## What to review

- [Detailed testing instructions](docs/build-week/TESTING_INSTRUCTIONS.md)
- [Portable Windows behavior and limits](docs/build-week/PORTABLE_WINDOWS.md)
- [Build Week delta](docs/build-week/BUILD_WEEK_DELTA.md)
- [Codex and GPT-5.6 usage](docs/build-week/CODEX_AND_GPT56_USAGE.md)
- [Provenance index and evidence limits](docs/build-week/provenance/PROVENANCE_INDEX.md)
- [Smoke-test evidence](artifacts/build-week/FINAL_REPORT.md)

For source-based reproduction, follow [Judge Quickstart](docs/build-week/JUDGE_QUICKSTART.md).

THEKEY is built for OpenAI Build Week 2026. It is not an official OpenAI product and is not endorsed by OpenAI.
