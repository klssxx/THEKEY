# Portable judge artifact verification

Verified at: `2026-07-21T22:45:58Z` (verification run before the final submission freeze)

| Field | Value |
| --- | --- |
| Artifact | `THEKEY-Portable-Windows-x64.zip` |
| Size | `22,846,085` bytes |
| SHA-256 | `589cdb85a7c478148b72d0337cfdb8b8454acc4e4c7c782b6e9a05b3969e2f0f` |
| ZIP entries | `135` |
| Uncompressed bytes | `40,471,901` |
| Manifest files | `124` |
| Manifest hash/size mismatches | `0` |
| Manifest source commit | `5cbab680c59ef3c0c1f2709f6540bf2b520c6495` |
| Manifest source state | `CLEAN`; `source_commit_exact=true` |
| Unsafe archive paths | none detected |
| Obvious text-secret matches | none detected by limited pattern scan |
| Authenticode | `THEKEY.exe` is `NotSigned` |

The ZIP contains `THEKEY.exe`, `README-FIRST.txt`, `BUILD_MANIFEST.json`, `SAMPLE-PYTHON-APP`, and `SAMPLE-REPAIRABLE-PYTHON-APP`. The manifest does not hash itself; the published ZIP SHA-256 is the complete-package integrity anchor.

Reproduce the outer hash:

```powershell
Get-FileHash .\dist\THEKEY-Portable-Windows-x64.zip -Algorithm SHA256
```

The binaries are not Authenticode-signed. Windows may show **Unknown publisher**; verify the published SHA-256 before running. This report is a static archive and manifest verification, not a substitute for the retained owner-verified WPF smoke evidence in `artifacts/build-week/FINAL_REPORT.md`.
