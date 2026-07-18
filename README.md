<div align="center">

# THEKEY

### Transacciones Git gobernadas para agentes de programación

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Version](https://img.shields.io/badge/version-0.2.0--preview-blue.svg)](https://github.com/klssxx/THEKEY/releases)
[![Status](https://img.shields.io/badge/status-Public%20Preview-orange.svg)](https://github.com/klssxx/THEKEY)
[![Stars](https://img.shields.io/github/stars/klssxx/THEKEY?style=social)](https://github.com/klssxx/THEKEY/stargazers)

**THEKEY** · *Governed Git transactions for coding agents.*

[English README](https://github.com/klssxx/THEKEY/blob/main/README.en.md) · [Documentación](https://github.com/klssxx/THEKEY/tree/main/docs) · [Roadmap](#roadmap) · [Contribuir](#contribuir)

</div>

---

<div align="center">

<video src="https://github.com/klssxx/THEKEY/raw/main/docs/THEKEY_cinematic_loop_5s.mp4" autoplay loop muted playsinline width="720"></video>

</div>

---

## ¿Qué es THEKEY?

THEKEY resuelve un problema concreto: **los cambios de software impulsados por agentes suelen ser opacos e inauditables.** THEKEY hace que cada cambio sea **gobernado, trazable y verificable**.

Separa planificación, ejecución, verificación y autorización de política en **roles distintos**, aplica puertas definidas por política-como-código, y produce **evidencia verificable** para cada ejecución.

## ¿Para quién es?

| Perfil | Caso de uso |
|---|---|
| 🤖 **Agentes de programación** | Automatizar cambios de código con trazabilidad completa |
| 🔁 **Pipelines de CI/CD** | Añadir gobierno determinista a tus workflows |
| 🏢 **Equipos** | Auditar y controlar cambios automatizados sin tocar la fuente |

## Características principales

- **🔒 Espacios de trabajo aislados** — Los cambios solo se aplican en un workspace controlado; la fuente original nunca se toca.
- **✅ Puertas deterministas** — Build, tests y seguridad son obligatorias. No se pueden omitir ni compensar con métricas globales.
- **📋 Evidencia auditable** — Cada transición de estado se registra en un event store SQLite encadenado por hash SHA-256.
- **🔑 Autorización de política** — La decisión (`RELEASE_ELIGIBLE` / `BLOCKED`) se deriva del hash del plan y la política, sin aprobación interactiva.

## Inicio rápido

```bash
# 1. Clonar el repositorio
git clone https://github.com/klssxx/THEKEY.git
cd THEKEY

# 2. Ejecutar la demo canónica (Windows 11 / PowerShell)
pwsh -NoProfile -File .\scripts\demo.ps1

# 3. O lanzar directamente con Python
python -m thekey demo
```

## Arquitectura

```
SUBMITTED
  └─► BASELINED
        └─► ANALYZED
              └─► PLAN_PROPOSED
                    └─► PLAN_APPROVED
                          └─► IMPLEMENTED
                                └─► TESTED
                                      └─► RELEASE_ELIGIBLE
```

Cada estado es una **transición explícita** registrada en el event store. La política como código determina si la transacción puede avanzar.

## Comandos disponibles

```bash
# Demo automática
python -m thekey demo

# Launcher autónomo
python -m thekey -m mimo

# Flujo manual paso a paso
python -m thekey run create
python -m thekey run plan
python -m thekey run approve-plan
python -m thekey run execute
python -m thekey run verify
python -m thekey run status
python -m thekey evidence verify
```

## Estructura del proyecto

```
THEKEY/
├── src/thekey/          # Core del framework
├── phases/              # Lógica de fases de ejecución
├── governance/          # Políticas y configuración de gobierno
├── prompts/             # Prompts de sistema para agentes
├── scripts/             # Scripts de automatización (demo.ps1)
├── examples/demo_app/   # Proyecto de ejemplo para demos
├── release_evidence/    # Trazas de auditoría
├── docs/                # Documentación y assets
└── .github/             # Workflows de GitHub
```

## Qué NO promete THEKEY

- ❌ No es un sandbox de sistema operativo
- ❌ No garantiza seguridad total
- ❌ No sustituye la revisión humana en proyectos críticos

El modelo de amenazas completo está en [`THREAT_MODEL.md`](https://github.com/klssxx/THEKEY/blob/main/THREAT_MODEL.md) y [`SECURITY.md`](https://github.com/klssxx/THEKEY/blob/main/SECURITY.md).

## Roadmap

Ver el estado actual del proyecto en los [Issues abiertos](https://github.com/klssxx/THEKEY/issues). El proyecto está en **Public Preview v0.2.0** — las APIs pueden cambiar.

## Contribuir

Las contribuciones son bienvenidas. Consulta [`CONTRIBUTING.md`](https://github.com/klssxx/THEKEY/blob/main/CONTRIBUTING.md) antes de abrir un PR.

---

<div align="center">

Distribuido bajo la licencia **MIT**. Ver [`LICENSE`](https://github.com/klssxx/THEKEY/blob/main/LICENSE).

⭐ Si THEKEY te resulta útil, considera dejar una estrella — ayuda al proyecto a crecer.

</div>
