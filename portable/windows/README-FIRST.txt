THEKEY — THE KING OF CHECKMATE
Governed Codex Transactions for Coding Agents

WINDOWS 10 / 11 PORTABLE QUICK START

SCAN, VERIFY, AND REPAIR A TRUSTED LOCAL APPLICATION

1. Extract the complete ZIP to a short writable path.
2. Double-click THEKEY.exe.
3. Watch the five-second opening or select SKIP.
4. Select "SELECCIONAR Y ANALIZAR APLICACIÓN" and choose the project folder.
   Choose SAMPLE-PYTHON-APP for a healthy run or
   SAMPLE-REPAIRABLE-PYTHON-APP for a transparent real repair.
5. Read the profile, CHECKMATE verdict, PolicyEngine decision and test list.
6. Select "Verificar aplicación" for read-only-source diagnosis, or "Escanear
   y reparar" to search for a bounded repair. Explicitly consent to trusted
   test execution and, separately, to applying only a fully verified repair.
7. Review NO_CHANGES_NEEDED, REPAIRED_AND_VERIFIED, or the fail-closed
   BLOCKED_* result and open the JSON evidence.

The first phase is read-only and executes no selected-project code. The second
phase copies inspected source files to a short local workspace, excludes build
artifacts (including bin, obj and publish), runs the adapter's fixed local
checks and tests, a bounded secret scan and a documentation gate, then confirms
the source tree hash did not change. No dependency or network installation is
performed. Python, Node.js, Go, Rust, .NET and Maven projects are identified;
missing toolchains or dependencies produce explicit fail-closed diagnostics.

Automatic repair uses a closed set of conservative single-point Python and
JavaScript mutations. THEKEY never changes tests or installs dependencies. Before an
authorized source write, it rechecks source and test hashes, stores a backup
outside the project, applies the exact bytes that passed every isolated gate,
and performs a fresh verification. Any post-apply failure triggers rollback.
Unsupported defects remain blocked with readable diagnostics.

SECURITY BOUNDARY

Project tests are trusted local code. THEKEY protects the original through a
read-only intake and isolated working copy, but this is not an operating-system
sandbox. Do not consent to tests from an untrusted project.

JUDGE DEMO

Select "Demo para jueces" for the deterministic Build Week scenario. A
successful run reports:

   ALLOW: APPLIED, handlers=1
   DENY: ROLE_NOT_ALLOWED, handlers=0
   GATES: 4/4 PASS
   DECISION: RELEASE_ELIGIBLE
   SOURCE: unchanged=True
   RECEIPTS: bound=True
   PRODUCTION REUSE: False

The portable app does not require Python, Git, PowerShell 7, an API key,
Docker, WSL, a GPU, paid services, or a test account. Do not move THEKEY.exe
out of its extracted folder. "Acceso / Shortcut" creates a desktop shortcut.
BUILD_MANIFEST.json records the base source commit, clean/dirty build state,
and SHA-256 of every distributed file. Only a clean build marks the commit as
exact.

---

INICIO RÁPIDO EN ESPAÑOL

1. Extrae el ZIP completo en una ruta corta con permiso de escritura.
2. Haz doble clic en THEKEY.exe.
3. Reproduce la apertura de cinco segundos o pulsa SKIP.
4. Pulsa "SELECCIONAR Y ANALIZAR APLICACIÓN" y elige un proyecto compatible. Para
   el recorrido saludable usa SAMPLE-PYTHON-APP; para una reparación real y
   transparente usa SAMPLE-REPAIRABLE-PYTHON-APP.
5. Revisa el perfil, el veredicto CHECKMATE, la decisión del PolicyEngine y los
   tests detectados. Esta fase no ejecuta código del proyecto.
6. Pulsa "Verificar aplicación" para diagnosticar sin modificar el origen, o
   "Escanear y reparar" para buscar una reparación acotada. Confirma únicamente
   si confías en sus tests y autoriza por separado aplicar solo un cambio que
   haya superado todos los gates.
7. Revisa NO_CHANGES_NEEDED, REPAIRED_AND_VERIFIED o el resultado BLOCKED_* y
   abre la evidencia JSON.

La copia excluye artefactos generados como bin, obj, publish, build y dist. El
original permanece en modo solo lectura y se comprueba otra vez por hash. Para
el recorrido reproducible del concurso, pulsa "Demo para jueces".

La reparación automática prueba un conjunto cerrado de mutaciones Python y
JavaScript de un solo punto; no cambia tests ni instala dependencias. Antes de escribir vuelve a
comprobar hashes, guarda un backup fuera del proyecto, aplica exactamente los
bytes verificados y ejecuta una verificación nueva. Si falla, hace rollback.
