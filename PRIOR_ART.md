# Prior-art evidence audit

Cutoff: **before 2026-07-13T00:00:00+02:00**. This audit uses internal
timestamps and object metadata where available; Windows modification time was
not used as proof when stronger internal data existed.

## Verified qualifying evidence

No repository-local item met the cutoff. Accordingly, there is no qualifying
prior-art row for which a date, SHA-256, description, and extract could be
reported truthfully.

## Negative audit record and limitations

| Source examined | Strongest internal date/result | SHA-256 / identifier | Description and brief extract | Evidence strength | Limitation |
| --- | --- | --- | --- | --- | --- |
| `.git` local object history | Earliest reachable local commit: `2026-07-15T06:34:40+02:00` | Git object `b7b6c32cf3a2621d29ef2c5856db50d116d8dff6` (Git object ID, not SHA-256) | `THEKEY Core Governed Run MVP 0.1.0` | Strong for the reachable local history | No reachable commit predates the cutoff; it cannot establish that no external or unimported history existed. |
| `.thekey/events.db` | `events.created_at` range: `2026-07-15T08:24:32Z`–`2026-07-21T06:27:36Z` | SQLite event store; current content is post-cutoff | Earliest event is after the cutoff. | Strong for timestamps stored in this event database | Database state may be incomplete or imported after prior work; it is not evidence of pre-cutoff work. |
| `.thekey` nested runtime stores | Earliest inspected event-store timestamp: `2026-07-19T14:26:05Z` | SQLite event stores inspected read-only | All inspected stores started after the cutoff. | Strong for the inspected rows | Only stores present in this workspace were inspected. |
| `artifacts`, `evidence`, `release_evidence`, `runs`, `development-audit` | No internally dated artifact before the cutoff located in the reviewed JSON, JSONL, log, manifest, archive, and exported evidence set | Not applicable: no qualifying artifact | Package archives found were Build Week artifacts dated 2026-07-21; no pre-cutoff export was found. | Moderate: filesystem contents plus embedded data inspected | Absence is bounded to this working copy and does not prove external artifacts never existed. |

The SHA-256 requirement applies to qualifying artifacts. None was found, so
this audit does not fabricate a qualifying hash or date.

## CHATGPT EVIDENCE PENDING OWNER EXPORT

- 2026-07-04 14:42  existencia y ruta Linux de THEKEY.
- 2026-07-04 22:57  THEKEY v3.0 y batch de once aplicaciones.
- 2026-07-04 23:40  tests, fallos y artefactos batch.
- 2026-07-05 01:52  THEKEY read-only y rutas de proyectos.
- 2026-07-11 19:46  migración y ruta Windows de THEKEY.
