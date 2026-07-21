# THEKEY portable app for Windows

The portable build provides a graphical path for verifying a trusted local
application and a separate reproducible Build Week demonstration. It targets
**Windows 10 x64 and Windows 11 x64** and does not require a local Python
installation, Git, PowerShell 7, an API key, Docker, WSL, a GPU, paid services,
or a test account.

## Scan, verify, and repair an application

1. Download and extract `THEKEY-Portable-Windows-x64.zip` to a short writable
   path.
2. Double-click `THEKEY.exe` without moving it out of the extracted directory.
3. Select **Seleccionar y analizar / Select & Analyze** and choose a supported project.
   The included `SAMPLE-PYTHON-APP` is the safe healthy first run, while
   `SAMPLE-REPAIRABLE-PYTHON-APP` transparently demonstrates a real repair.
4. Review the read-only profile, CHECKMATE verdict, PolicyEngine decision, and
   detected tests.
5. Select **Verificar / Verify** for diagnosis without changing the source,
   or **Reparar / Repair** to search for a bounded repair and explicitly
   authorize applying it only after every isolated gate passes.
6. Review `NO_CHANGES_NEEDED`, `REPAIRED_AND_VERIFIED`, or the fail-closed
   `BLOCKED_*` result, then open the JSON evidence with **Ver resultados /
   View**.

The inspection phase executes no project code. After consent, THEKEY copies
only inspected source and metadata files to a short workspace below the user's
local application-data directory. It excludes generated directories such as
`bin`, `obj`, `publish`, `build`, `dist`, virtual environments, and caches. It
then runs the adapter's fixed local checks, existing tests, a bounded regex
secret scan, and a documentation check before confirming the original tree hash
did not change. It performs no dependency or network installation. Python,
Node.js, Go, Rust, .NET, and Maven manifests are profiled explicitly; a missing
toolchain or dependency produces a fail-closed diagnostic rather than success.

Repair is a second, separately authorized phase. THEKEY searches a closed set
of conservative single-point Python and JavaScript changes and never edits tests
or installs packages. A candidate must compile and pass the complete existing
adapter test suite,
the bounded secret scan, and the documentation gate. Immediately before a
source write, THEKEY checks the source and test hashes again, saves an
out-of-tree backup, applies the exact verified bytes atomically, and runs a
fresh verification. A failure triggers rollback. Defects outside the bounded
candidate set remain blocked with diagnostics and evidence.

Selected tests are trusted local code. Workflow isolation protects the source
tree, but it is **not** process or operating-system sandboxing. Do not consent
to running tests from an untrusted project.

## Reproducible judge path

Select **Demo para jueces** to run the bundled positive transaction,
adversarial zero-handler denial, four mandatory gates, and independent
persisted-evidence verification. The graphical cards invoke the frozen form of
the same `thekey` CLI and governance engine; they do not substitute prerecorded
results or bypass CHECKMATE, scoped authority, the `PolicyEngine`, physical-
dispatch authorization, or mandatory gates.

## Available cards

- **Seleccionar y analizar / Select & Analyze:** read-only project intake and policy
  decision; it executes no selected-project code.
- **Verificar / Verify:** after explicit consent, verifies an isolated copy
  and confirms whether the source stayed unchanged.
- **Reparar / Repair:** diagnoses failures, proves one bounded repair in the
  isolated copy, and applies it only with explicit consent, backup, stale-input
  protection, post-apply verification, and rollback.
- **Demo para jueces / Judge demo:** runs and independently verifies the canonical Build
  Week scenario.
- **Ver resultados / View results:** renders structured fields from persisted
  local evidence and provides a real demo restart action.
- The sidebar opens real Analyze, Tools, Results, Modes, Logs, and Settings
  views; unavailable future modes remain honestly marked **Soon**.

## Build from source

Building the distributable requires Windows, 64-bit Python 3.11 or newer, and
the .NET Framework 4 compiler supplied by Windows. PyInstaller is pinned by the
build script. Generated artifacts remain ignored under `build/` and `dist/`.

```powershell
pwsh -NoProfile -File .\scripts\build-portable.ps1 `
  -Python C:\Path\To\python.exe `
  -Bootstrap
```

The output contains:

```text
dist/THEKEY-Portable-Windows-x64/
  THEKEY.exe
  THEKEY_hero_chess.png
  THEKEY_app_icon.png
  README-FIRST.txt
  BUILD_MANIFEST.json
  SAMPLE-PYTHON-APP/...
  SAMPLE-REPAIRABLE-PYTHON-APP/...
  core/THEKEY-Core/...
```

`BUILD_MANIFEST.json` records the base Git commit plus clean/dirty source-tree
state and the SHA-256 and size of every distributed file. Only a clean build
sets `source_commit_exact=true`; a changed local build is explicitly marked
`DIRTY_BUILD`. The executable is a convenience surface, not a new
authorization path. The bundled Judge Mode grant remains non-reusable in
production.
