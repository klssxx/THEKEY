# Guía rápida de THEKEY Build Week Judge Mode

Esta es la ruta reproducible más corta para evaluar THEKEY sin API key,
servicios de pago, Docker, WSL, GPU, dependencias privadas ni cuenta de prueba.

## Plataforma verificada

- Windows 11
- PowerShell 7 (`pwsh`)
- Python 3.11 o superior
- Git

Judge Mode solo se afirma actualmente sobre esa plataforma.

## Instalación desde un clon limpio

```powershell
git clone https://github.com/klssxx/THEKEY.git
cd THEKEY
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -e .
```

## Ejecución y verificación independiente

```powershell
pwsh -NoProfile -File .\scripts\build-week-demo.ps1
pwsh -NoProfile -File .\scripts\verify-build-week-evidence.ps1
```

El resumen debe mostrar:

```text
ALLOW: APPLIED, handlers=1
DENY: ROLE_NOT_ALLOWED, handlers=0
GATES: 4/4 PASS
DECISION: RELEASE_ELIGIBLE
SOURCE: unchanged=True
RECEIPTS: bound=True
PRODUCTION REUSE: False
```

El segundo comando analiza el JSON y los artefactos persistidos. Un run válido
devuelve `status: VALID`, un handler ALLOW, cero DENY, cuatro gates,
`RELEASE_ELIGIBLE`, fuente sin cambios y reutilización productiva desactivada.
No confía en el resumen impreso.

## Prueba funcional de escaneo y reparación

La aplicación portable incluye `SAMPLE-PYTHON-APP` para verificar el recorrido
saludable. Para demostrar una reparación real, usa un proyecto Python o Node.js
de confianza con el adaptador de tests detectado y un fallo compatible, pulsa **Escanear y reparar**
y acepta el consentimiento mostrado. La evidencia debe terminar en
`NO_CHANGES_NEEDED`, `REPAIRED_AND_VERIFIED` o un `BLOCKED_*` explícito.

Desde una instalación fuente, el mismo motor se ejecuta así:

```powershell
.\.venv\Scripts\python.exe -m thekey project repair `
  --source C:\ruta\al\proyecto `
  --consent execute_trusted_tests `
  --apply-consent apply_verified_repairs
```

THEKEY no cambia tests ni instala dependencias. Solo aplica el byte exacto que
pasó el build/check del adaptador, la suite de tests detectada, el secret scan limitado y el gate
documental; antes revalida hashes, crea un backup y después vuelve a verificar.
Un fallo posterior provoca rollback.

## Qué hace Judge Mode

1. Crea un Git temporal bajo el estado ignorado `.thekey/judge-mode`.
2. Crea un runtime de workflow separado y una transacción gobernada.
3. Liga la revisión CHECKMATE y el grant soberano al mismo run, transacción y
   SHA-256 del plan.
4. Aplica una reparación declarada del calculador a través del guard físico.
5. Ejecuta gates de build, tests, secret scan limitado y documentación.
6. Intenta la misma acción con `Role.SYSTEM`; debe denegarse antes del handler y
   mantener el workspace intacto.
7. Persiste recibos, decisión y `judge-mode-evidence.json`.

La fuente temporal y el checkout de THEKEY no cambian. Todo el estado mutable
queda dentro de directorios runtime ignorados.

## Selección de Python y diagnóstico

El script usa `THEKEY_PYTHON` si se define. En otro caso prueba un `.venv`
funcional del repositorio, después `python` y por último `py -3`. Omite un
`.venv` obsoleto en lugar de seleccionarlo solo porque exista el launcher.

Para elegir un Python concreto:

```powershell
$env:THEKEY_PYTHON = 'C:\Ruta\A\Python311\python.exe'
pwsh -NoProfile -File .\scripts\build-week-demo.ps1
```

- Si falta `pwsh`, instala PowerShell 7 y abre una terminal nueva.
- Si aparece `git init failed`, confirma que Git está instalado y en `PATH`.
- Si falla un import, repite la instalación editable con el mismo Python que
  usará la demo.
- Usa una ruta de clon corta; rutas Windows profundas pueden exceder el límite.

## Límite de seguridad

Es aislamiento de flujo de trabajo, no sandbox de proceso o sistema operativo.
El grant local es dato visible del repositorio, no firma humana criptográfica.
Fuente y salida están acotadas y `production_reuse` es falso. SHA-256 aporta
evidencia tamper-evident dentro de la cadena implementada, no atestación
externa. El registro de acciones y el secret scan son deliberadamente
limitados.

[English version](JUDGE_QUICKSTART.md)
