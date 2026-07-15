# Guía de contribución — THEKEY 0.2.0

> Versión en inglés: [CONTRIBUTING.en.md](CONTRIBUTING.en.md)

Gracias por tu interés en THEKEY. Esta guía es corta y seria.

THEKEY aplica aislamiento de flujo de trabajo y autorización de política
determinista; no proporciona sandboxing a nivel de sistema operativo.

## Preparar el entorno de desarrollo

```powershell
git clone <URL_DEL_REPOSITORIO>
cd THEKEY
pwsh -NoProfile -File .\scripts\demo.ps1
```

El script crea `.venv`, instala con `pip install -e .` y ejecuta la demo. Para
trabajo de desarrollo adicional puedes instalar las dependencias de desarrollo:

```powershell
.venv\Scripts\python -m pip install -e ".[dev]"
```

## Ejecutar los tests

```powershell
.venv\Scripts\python -m pytest -q
```

## Ejecutar la demo

```powershell
.venv\Scripts\python -m thekey demo
```

## Cambios pequeños vs. cambios de arquitectura

- **Cambio pequeño:** corrección de bug, mejora de mensaje, nueva política,
  nuevo perfil de verificador, adaptador de solo lectura externo.
- **Cambio de arquitectura:** modificación del núcleo de transacciones, del
  estado de la máquina, del event store o de las puertas obligatorias. Requiere
  RFC.

## Proponer RFCs

Los RFC describen diseños futuros (p. ej. Fase C/D, contrato de adaptadores).
Se documentan como issues etiquetados `rfc`. Un RFC puede existir como diseño
sin obligar a su implementación en esta versión.

## Reportar bugs

Usa la plantilla de bug en GitHub. Incluye pasos de reproducción, entorno
(Windows 11, Python, pwsh) y salida relevante. Para vulnerabilidades, sigue
[SECURITY.md](SECURITY.md), no abras un issue público.

## Elegir issues por etiqueta

- `good first issue`: aptos para quienes se inician.
- `help wanted`: extensiones prácticas.
- `enhancement` / `documentation` / `bug` / `security`: mejoras dirigidas.
- `rfc` / `phase-c` / `phase-d`: diseño futuro.
- `adapter`: adaptadores externos de solo lectura.
- `windows` / `ci`: específicos de plataforma o automatización.

## Etiquetas esperadas

`good first issue`, `help wanted`, `enhancement`, `documentation`, `bug`,
`security`, `rfc`, `phase-c`, `phase-d`, `adapter`, `windows`, `ci`.

## Criterios de aceptación para PRs

- Los tests pasan (`pytest -q`).
- La demo alcanza `RELEASE_ELIGIBLE` (o el cambio no la rompe).
- No se agregan afirmaciones de seguridad o marketing no verificadas.
- Se mantiene la paridad ES/EN al tocar documentación normativa.
- El núcleo no crece innecesariamente en este release.

## Paridad ES/EN

Al modificar documentación normativa (README, THREAT_MODEL, CONTRIBUTING) debes
actualizar la versión en inglés correspondiente. El gate de paridad lo verifica
en CI.

## Prohibiciones

- No añadas afirmaciones de seguridad o marketing no verificadas.
- No expandas el núcleo innecesariamente en este release.
- No integres NPSC en el núcleo; NPSC es un adaptador de solo lectura opcional.
- No uses el término «auto-approval»; usa «autorización de política
  determinista».

## Cuándo un aporte toca el núcleo y cuándo debe ser un adaptador externo

Si el aporte cambia el flujo de transacción gobernada, la máquina de estados, el
event store o las puertas obligatorias, toca el núcleo y requiere RFC. Si aporta
un proveedor externo (p. ej. otro compilador como NPSC), debe vivir como
adaptador de solo lectura externo, sin acoplarse al núcleo.
