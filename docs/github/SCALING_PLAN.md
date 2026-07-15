# THEKEY — Plan de Escalado y Protocolo de Prompts

Fuente de verdad para el coordinador (Hermes) y el Equipo senior. Autocontenido:
cualquier subagente relanzado con este texto reanuda sin contexto previo.

## 0. Principios (no negociables)

1. **Evidencia > afirmación.** Nada se da por hecho sin salida real de ejecución
   en disco. Cada fase cierra solo si su gate de verificación pasa.
2. **Original protegido intocable.** `E:\KLSX PROYECTS\KlsxMaker\TheKey\Thekey`,
   `Aplicaciones`, y el THEKEY Core ya commiteado NO se modifican por el equipo
   salvo THEKEY Core en su propio repo (E:\PROYECTS\GovernedOSS) bajo control de
   git y tests verdes.
3. **100% automático por defecto.** THEKEY Core nunca introduce prompts
   interactivos humanos en el flujo gobernado.
4. **Sin push / release / remoto sin aprobación.** El coordinador no ejecuta
   `git push`, `gh repo create`, `gh release create` sin luz explícita del owner.
5. **Regenerable.** Cada fase deja un `PROGRESS.md` con comando + salida real;
   si un subagente se satura, se relanza con el prompt canónico de su fase y
   retoma del último sub-punto completado.

## 1. Fases de escalado (orden y gates)

### Fase A — Cierre de NPSC hardening (obligatoria, bloquea todo lo demás)
- Entrada: copia aislada `...\NPSC_REVIEW_EXPORT_20260715-100257\10_FILES_TO_REVIEW\current\`
- Salida esperada en `...\GPT_HARDENING\`: `02_NPSC_HARDENING_DIFF.patch`,
  `NPSC_HARDENED\`, `01_HARDENING_REPORT.md`, `00_PROGRESS.md`.
- Gates: B1 (output_contract alineado) ✅ ya aplicado, confirmar; B2 (--strict
  bloquea, 0 archivos) ✅ ya aplicado, confirmar; B3 (NO leak de secreto en
  `hybrid_markdown`) — DEBE CERRARSE (hoy filtra). Tests core NPSC ≥60 passed.
- Parada: solo cuando B1/B2/B3 verificados por script Y los 3 archivos existan.

### Fase B — Integración opcional NPSC en THEKEY (solo si A pasa)
- Validar el paquete `NPSC_HARDENED` vía el adaptador read-only de THEKEY Core.
- NO integrar el compilador; solo consumir su salida. Tests de THEKEY no bajan
  de 102.
- Gate: adaptador parsea `NPSC_HARDENED` sin error; demo sigue verde.

### Fase C — Siguiente incremento de THEKEY Core (roadmap Near term)
- Candidatos (el equipo elige 1 por fase, con veto security/product/OSS):
  C1 Strong identities firmadas; C2 Evidence signing; C3 Concurrency de runs;
  C4 Exceptions/override gobernado; C5 RFC de políticas.
- Gate por candidato: diseño + impl + tests nuevos + demo verde + doc.

### Fase D — Atractivo OSS (issue backlog, CONTRIBUTING, good-first-issues)
- Generar issues desde el estado real; no inventar.
- Gate: ISSUE_BACKLOG.md actualizado; al menos 3 good-first-issues verificables.

### Fase E — Push / release (SOLO con aprobación del owner)
- Ejecuta `PUSH_PLAN.md` tras cerrar los 7 gates del push.
- Gate: owner aprueba explícitamente.

## 2. Jerarquía de prompts

```
OWNER (tú)
  └─ COORDINADOR (Hermes / yo)
       ├─ P1  Equipo senior (1 subagente multi-rol)  → Fase A
       ├─ P2  Equipo senior (reutilizable)            → Fase B/C/D por turno
       └─ P-REGEN  mismo prompt de la fase            → si se satura
```

El "Equipo senior" es UN subagente leaf que adopta 5 roles en su razonamiento:
(a) ingeniería de dev-tools, (b) sistemas de agentes IA, (c) seguridad
verificable, (d) producto, (e) ecosistemas OSS. No se delega a más de 1 nivel
(max_spawn_depth=1 en esta cuenta). Si una fase necesita paralelismo real,
el coordinador lanza 2-3 subagentes leaf con briefs separados.

## 3. Prompts exactos a mandar (canónicos)

### P1 — Fase A (YA ENVIADO, deleg_95fdbec5)
Brief autocontenido con: estado verificado, Tarea 1 (1.1-1.5), Tarea 2 (solo
tras A), reglas de no-detención/regeneración, prohibidos. Ver
`deleg_95fdbec5` en el historial.

### P2 — Fase B (se manda SOLO si P1 cerró A con evidencia)
```
"Equipo senior: Fase B de THEKEY. El paquete NPSC_HARDENED está en
.../GPT_HARDENING/NPSC_HARDENED/. Valida su salida con el adaptador read-only
de THEKEY Core (E:\PROYECTS\GovernedOSS\src\thekey\adapters\npsc_adapter.py)
usando un JSON de ejemplo. NO integres el compilador; solo consume salida.
Añade un test en tests/unit/ que confirme que el adaptador parsea el contrato
alineado (output_contract + constraints). Corre 'python -m pytest' y asegura
>=102 passed. Deja INFORME en .../GPT_HARDENING/02_THEKEY_ADVANCE.md.
Prohibido: push, modificar original NPSC, inventar."
```

### P3 — Fase C (se manda SOLO si B pasó)
```
"Equipo senior: Fase C de THEKEY Core. Revisa ROADMAP.md (Near term). Elige 1
incremento (Strong identities / Evidence signing / Concurrency / Exceptions /
RFC) justificando con los 5 roles. Impleméntalo en E:\PROYECTS\GovernedOSS con
tests nuevos, manteniendo 100% automático y >=102 passed. Deja INFORME en
docs/github/ con diseño + evidencia. Prohibido: romper núcleo, push, inventar."
```

### P4 — Fase D (se manda SOLO si C pasó)
```
"Equipo senior: Fase D de THEKEY. Genera el issue backlog REAL desde el estado
verificado (STATUS.md, ROADMAP.md, tests). Al menos 3 good-first-issues con
pasos de reproducción. Actualiza docs/github/ISSUE_BACKLOG.md. No inventes
issues sin evidencia de código. Prohibido: push."
```

### P-REGEN — regeneración (si cualquier Pn se satura sin cerrar su fase)
```
"Reanuda la Fase X. Lee el estado en disco:
.../GPT_HARDENING/00_PROGRESS.md (o el INFORME de la fase) y el commit ebb0770.
Retoma del último sub-punto completado. Escribe PROGRESS.md con cada paso.
NO necesitas contexto previo del coordinador. Cierra la fase con los archivos
de entrega y evidencia real. Prohibido: push, red, tocar original protegido."
```
(X se reemplaza por A/B/C/D según corresponda.)

## 4. Criterios de parada por fase
- A: B1/B2/B3 verificados por script + 3 archivos de entrega presentes.
- B: adaptador parsea NPSC_HARDENED + pytest >=102.
- C: incremento implantado + tests + demo verde + doc.
- D: ISSUE_BACKLOG.md real + >=3 good-first-issues.
- E: solo tras aprobación explicita del owner.

## 5. Señales de saturación y recuperación
- Si un subagente devuelve "tool-call limit" sin archivos de entrega → se
  considera INCOMPLETO, no exitoso. El coordinador relanza con P-REGEN.
- Si los archivos de entrega existen pero los gates fallan al re-verificar →
  el coordinador lo marca como FALLIDO y no simula éxito; relanza o pide
  decisión al owner.
- Nunca se asume éxito por "el subagente dijo que terminó"; el coordinador
  re-lee los archivos en disco y ejecuta la verificación mínima.

## 6. Estado actual
- THEKEY Core 0.2.0: commit ebb0770, 102 passed, demo autónoma OK.
- Release notes: borrador `docs/github/RELEASE_NOTES_v0.2.0.md` (untracked).
- Push: `PUSH_PLAN.md` + `PUSH_MANIFEST.md` listos; gh instalado sin auth.
- NPSC: Fase A en curso (deleg_95fdbec5), aún sin progreso en disco.
- Gates de push (1-7): ABIERTOS hasta que A cierre con evidencia.
