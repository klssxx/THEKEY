# THEKEY testing instructions for judges

## Platform and download

- Supported portable platform: Windows 10 x64 and Windows 11 x64.
- Download: [THEKEY-Portable-Windows-x64.zip](https://github.com/klssxx/THEKEY/releases/download/openai-build-week-2026-submission/THEKEY-Portable-Windows-x64.zip)
- Emergency fallback: [tag-pinned copy](https://github.com/klssxx/THEKEY/raw/openai-build-week-2026-submission/releases/openai-build-week-2026/THEKEY-Portable-Windows-x64.zip)
- SHA-256: `589cdb85a7c478148b72d0337cfdb8b8454acc4e4c7c782b6e9a05b3969e2f0f`

```powershell
Get-FileHash .\THEKEY-Portable-Windows-x64.zip -Algorithm SHA256
```

Extract the archive completely to a short writable path. Do not move `THEKEY.exe` outside the extracted folder. The archive contains the runtime, healthy and repairable samples, `README-FIRST.txt`, and `BUILD_MANIFEST.json`.

The binaries are not Authenticode-signed. Windows SmartScreen may show **Unknown publisher**. Verify the checksum above before deciding whether to run the artifact.

## No-build evaluation

1. Run `THEKEY.exe`.
2. Click **Demo para jueces / Judge demo**. Confirm the result reports the positive governed transaction, adversarial denial, four passing gates, and persisted evidence.
3. Click **Ver resultados / View results** and inspect the recorded result.
4. Select **Seleccionar y analizar / Select & Analyze** and open `SAMPLE-PYTHON-APP`. The first phase is read-only.
5. Select **Verificar / Verify** only after reviewing consent: it runs trusted local tests in an isolated workflow copy and confirms the original source remained unchanged.
6. Repeat with `SAMPLE-REPAIRABLE-PYTHON-APP`; choose **Reparar / Repair** to see a bounded repair candidate, re-test, separate source-write consent, backup, and post-apply verification.

No Python, Git, PowerShell, Docker, WSL, API key, GPU, payment, or test account is required for the included path. Do not choose an untrusted project: workflow isolation is not an operating-system sandbox.

## Existing test and smoke evidence

The repository retains a Windows 11 owner-verified WPF smoke, packaged backend execution, and focused automated tests in [FINAL_REPORT.md](../../artifacts/build-week/FINAL_REPORT.md). The final owner sequence includes launch, healthy inspection/verification, repair, Judge demo, persisted results, clean close, and a second open. It is explicitly distinct from automated tests.

For source reproduction rather than the portable path, see [JUDGE_QUICKSTART.md](JUDGE_QUICKSTART.md). It needs Windows 11, PowerShell 7, Python 3.11+, and Git.
