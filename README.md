# THEKEY

Transacciones de software gobernadas para agentes de programación.

> **Valor en una frase:** THEKEY permite que un agente modifique un workspace
> aislado solo cuando plan, revisión, autoridad humana, decisión de política y
> evidencia coinciden sobre la misma transacción.

[English README](README.en.md) · [Contribución Build Week](BUILD_WEEK_CONTRIBUTION.es.md) · [Seguridad](SECURITY.md) · [Licencia MIT](LICENSE)

THEKEY resuelve un problema concreto de herramientas de desarrollo: los
cambios agénticos son rápidos, pero suele ser difícil demostrar qué plan fue
autorizado, qué cruzó la frontera física de ejecución y por qué el resultado
fue elegible para release. Está dirigido a creadores de agentes, responsables
de CI/CD y equipos que necesitan una capa de gobierno pequeña e inspeccionable.

THEKEY proporciona aislamiento de flujo de trabajo, gates deterministas y
evidencia tamper-evident dentro de límites documentados. No es un sandbox de
sistema operativo.

## Judge Mode — OpenAI Build Week

La ruta más rápida para evaluarlo en Windows 11 es:

```powershell
git clone https://github.com/klssxx/THEKEY.git
cd THEKEY
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e .
pwsh -NoProfile -File .\scripts\build-week-demo.ps1
```

Judge Mode crea un repositorio Git temporal pequeño, inicia una transacción
gobernada real, copia el objetivo a un runtime aislado por workflow, aplica una
reparación controlada, ejecuta cuatro gates, demuestra un ALLOW autorizado y un
DENY adversarial, y escribe evidencia JSON. No requiere secretos, servicios de
pago, Docker, WSL ni GPU.

Forma de salida verificada:

```text
THEKEY BUILD WEEK JUDGE MODE
ALLOW: APPLIED, handlers=1
DENY: ROLE_NOT_ALLOWED, handlers=0
GATES: 4/4 PASS
DECISION: RELEASE_ELIGIBLE
EVIDENCE: ...\judge-mode-evidence.json
Isolation: workflow workspace only; this is not an OS sandbox.
```

La ejecución local verificada terminó en menos de diez segundos e incluyó
rutas con espacios. El tiempo varía según hardware y estado de dependencias.

## Cómo funciona la autorización

```text
Plan de misión
  → recibo CHECKMATE previo a la acción
  → recibo de autorización explícita y acotada de moli
  → decisión determinista del PolicyEngine
  → guard físico de THEKEY
  → exactamente un handler declarado
  → build, tests, escaneo de secretos y gate de documentación
  → decisión de release y evidencia
```

Antes de resolver un handler físico, THEKEY valida un `ActionContext` Pydantic
estricto. Los dos recibos persistidos deben coincidir en run ID, transaction ID
y SHA-256 del plan. También deben coincidir authorization ID, versión de
política, hash del policy bundle, rol, verdict y scope de acción. Solo
`Role.EXECUTOR` cruza la frontera. Campos ausentes o adicionales, mismatches,
`SYSTEM`, `PENDING`, `DEFER`, `FAIL`, excepciones de política, respuestas
inválidas o ALLOW sin decision ID fallan de forma cerrada.

`ActionReviewVerdict` es una revisión CHECKMATE anterior a ejecutar.
`ReleaseDecision` nace después de los gates y nunca se reutiliza
retroactivamente como autorización.

## Arquitectura

- **Coordinador:** persiste artefactos y rehidrata la transacción entre procesos
  CLI.
- **Revisor CHECKMATE:** emite el recibo previo para el plan acotado.
- **Binder soberano:** liga el grant explícito y visible de moli a un run y una
  transacción reales.
- **PolicyEngine:** devuelve `allowed`, reason code, decision ID y hash de policy
  bundle conservado.
- **Guard físico:** autoriza antes de buscar el handler; no expone shell ni
  rutas arbitrarias.
- **Workspace manager:** limita cambios declarados al workspace de workflow.
- **Verifier:** ejecuta build, tests, escaneo limitado de secretos y
  documentación.
- **Evidencia/estado:** hashea artefactos, registra transiciones y verifica el
  estado persistido al cargarlo.

## Requisitos y plataforma soportada

- Windows 11 — verificado
- PowerShell 7 (`pwsh`) — verificado
- Python 3.11 o superior
- Git

El core es Python. Judge Mode solo está verificado actualmente en Windows 11.

## Comandos

```powershell
# Ruta para jueces
pwsh -NoProfile -File .\scripts\build-week-demo.ps1

# Demo canónica
python -m thekey demo

# Tests focalizados y regresión
python -m pytest -q tests\test_phase_b_rbac_v2_models.py `
  tests\test_phase_b_rbac_v2_guard.py `
  tests\test_phase_b_rbac_v2_integration.py
python -m pytest -q

# Ciclo reanudable entre procesos
python -m thekey run create --title "Fix calculator.add"
python -m thekey run plan --run-id <RUN_ID>
python -m thekey run approve-plan --run-id <RUN_ID>
python -m thekey run execute --run-id <RUN_ID>
python -m thekey run verify --run-id <RUN_ID>
python -m thekey evidence verify --run-id <RUN_ID>
```

## Procedencia Build Week y uso de Codex

El repositorio público empieza después del corte, aunque el propietario afirma
que el proyecto existía antes. [BUILD_WEEK_CONTRIBUTION.es.md](BUILD_WEEK_CONTRIBUTION.es.md)
separa el trabajo verificado de este hilo de Codex de la procedencia histórica
no resuelta, sin presentar automáticamente el primer commit como trabajo nuevo.

Codex se usó para inspección del código, análisis arquitectónico y adversarial,
implementación, verificación AST, TDD RED→GREEN, regresión, preparación de
rollback y documentación. moli conservó las decisiones de autoridad, scope,
LIVE_E, push, merge, release, publicación del vídeo y envío final.

- Evidencia de uso de GPT-5.6: `PENDING_SESSION_METADATA_VERIFICATION`
- Session ID principal de `/feedback`: `PENDING_REAL_FEEDBACK_SESSION_ID`
- Vídeo público de YouTube: `PENDING_PUBLIC_YOUTUBE_URL`

Estos placeholders deben sustituirse por evidencia real. THEKEY no afirma una
integración runtime con GPT-5.6.

## Límites de seguridad

- El aislamiento de workflow no es aislamiento de procesos ni de SO.
- El grant soberano incluido no es una autorización productiva: el binder exige
  `JUDGE_MODE_DEMO_ONLY`, la ruta y SHA-256 de texto normalizado exactas del demo canónico, salida
  únicamente al workspace aislado y `production_reuse=false`. Sigue sin ser una
  firma humana criptográfica.
- La evidencia SHA-256 es tamper-evident dentro de la cadena implementada; no
  es invulnerable ni reemplaza una atestación externa.
- El escaneo de secretos es deliberadamente limitado.
- El registro de acciones y Judge Mode cubren una demostración acotada, no la
  reparación arbitraria de repositorios.
- `CANONICAL_SOURCE_STATUS` sigue `UNRESOLVED`; `FULL_CHECKMATE` es `FALSE`.

Consulta [THREAT_MODEL.md](THREAT_MODEL.md) y [SECURITY.md](SECURITY.md).

## Licencia

THEKEY se distribuye bajo la [Licencia MIT](LICENSE).
