# THEKEY Build Week function map

Baseline inspected: `d1c37b9ec2d43289fd9db123e1450dc625e4b305` on 2026-07-21.

| Surface | Entry point | Inputs | Persisted output / errors | Status |
| --- | --- | --- | --- | --- |
| Read-only project intake | `thekey project inspect --source <directory>` | Existing project directory | `inspection.json`; unsupported profiles and unsafe links are reported | FUNCTIONAL |
| Isolated verification | `thekey project verify --source <directory> --consent execute_trusted_tests` | Supported project plus explicit consent | Isolated workspace, gate evidence and `verification.json`; toolchain, test, policy and timeout errors are persisted | FUNCTIONAL |
| Bounded repair preview | `thekey project repair --source <directory> --consent execute_trusted_tests` | Supported project plus explicit consent | Repair evidence and a `REPAIR_READY` preview; no source write | FUNCTIONAL |
| Apply verified repair | `thekey project repair ... --apply-consent apply_verified_repairs` | A fresh explicit apply consent | Out-of-tree backup, post-apply verification and rollback evidence; refused on stale input or failed gates | FUNCTIONAL |
| Judge demo | `portable-demo` in the Windows bundle; `thekey judge-mode` in source | Bundled calculator sample | Bound receipts, four gates and evidence; non-zero exit on a failed gate | FUNCTIONAL |
| Evidence validation | `portable-verify [evidence-path]` | Persisted Judge Mode evidence | Validates receipts, bindings and decision | FUNCTIONAL |
| History | `thekey history` | Existing run history | Real run records or empty result | FUNCTIONAL |
| Windows selector | Native folder picker in `TheKeyLauncher.cs` | Existing directory only | Starts asynchronous read-only intake; cancellation and bad paths remain local, without execution | FUNCTIONAL |
| Windows results view | `TheKeyLauncher.cs` evidence discovery | Local `%LOCALAPPDATA%\\THEKEY\\.thekey` evidence | Structured date, project, gates, findings, decision, artifact path and error fields from real JSON, or an explicit empty state | FUNCTIONAL |
| Windows operation cancellation | Confirmation plus bounded process-tree termination | One active local backend process | Cancels the exact locally launched process tree; clean close is guarded while work is active | FUNCTIONAL |
| Sidebar navigation | Native WPF navigation entries | Keyboard or pointer activation | Real Home, Analyze, Tools, Results, Modes, Logs and Settings views with truthful empty/unavailable states | FUNCTIONAL |
| THE KING mode | Launcher navigation | None | Honest unavailable view | MISSING |
| CHECKMATE mode | Launcher navigation | None | Honest unavailable view | MISSING |
| Arbitrary executable inspection | None | Executable file | Not supported by the safe project profiler | NOT_APPLICABLE |
| Arbitrary project test execution without consent | None | Project directory | Deliberately refused | UNSAFE |

The Windows UI is an adapter only: it starts the existing bounded CLI commands
and never manufactures gate, repair, or evidence results.
