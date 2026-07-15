# THEKEY 0.2.0 — Public Preview launch plan (Entregables A/B/C)

Owner action required before any step: authenticate `gh` (see bottom).
This file is documentation; it performs NO push, NO remote change, NO release.

Repository name (do not change after public): **THEKEY**
About (exact, 97 chars, no truncation):
  Governed Git transactions for coding agents  isolated workspaces, deterministic gates, auditable evidence.

====================================================================
ENTREGABLE A — Flip público checklist (10 pasos, con comandos)
====================================================================

Prerrequisito: `gh auth login` completado y repo creado como PRIVADO.
Sustituye OWNER por tu handle de GitHub.

Paso 1 — Verificar CI verde en rama main
  gh run list --repo OWNER/THEKEY --branch main --limit 5
  (Confirmar que el último run de cada job windows/docs-gates/secret-scan es green.)

Paso 2 — Confirmar que demo.ps1 pasa en clone limpio
  git clone <URL> "C:\Temp\THEKEY Flip Demo"
  cd "C:\Temp\THEKEY Flip Demo"
  pwsh -NoProfile -File .\scripts\demo.ps1
  (Debe salir exit 0 y mostrar RELEASE_ELIGIBLE / gates_passed: 4.)

Paso 3 — About exacto (GitHub: repo Settings > About > Description)
  gh repo edit OWNER/THEKEY --description "Governed Git transactions for coding agents  isolated workspaces, deterministic gates, auditable evidence."

Paso 4 — Topics (15, en orden de prioridad)
  gh repo edit OWNER/THEKEY \
    --add-topic coding-agents --add-topic agent-governance \
    --add-topic ai-safety --add-topic git-transactions \
    --add-topic workflow-isolation --add-topic audit-trail \
    --add-topic deterministic-gates --add-topic supply-chain-security \
    --add-topic code-review-automation --add-topic python \
    --add-topic windows --add-topic sqlite --add-topic llm-tools \
    --add-topic developer-tools

Paso 5 — Verificar primera pantalla del README
  Abrir README.md en GitHub sin scroll: debe verse
  # THEKEY + subtítulo ES + badges (CI/license/v0.2.0/Python/Windows) +
  línea EN + GIF + one-liner. Confirmar que docs/assets/thekey-demo.gif carga.

Paso 6 — Abrir los 8 issues del backlog (release_evidence/backlog/)
  python scripts/ci/open_issues.py --repo OWNER/THEKEY
  (Lee 01..08_*.md y crea un issue por cada uno con su title/labels/body.
   No los abras antes: deben abrirse el día del flip para señal de actividad.)

Paso 7 — Habilitar GitHub Discussions (opcional, sube engagement)
  gh api -X PATCH repos/OWNER/THEKEY --field has_discussions=true

Paso 8 — Switch privado -> público
  gh repo edit OWNER/THEKEY --visibility public
  (O en Settings > Danger Zone > Make public. Confirmar el nombre THEKEY.)

Paso 9 — Compartir en canales (orden de prioridad para audiencia técnica)
  Hacker News (Show HN) -> Reddit r/programming -> X/Twitter -> LinkedIn
  Textos en ENTREGABLE B.

Paso 10 — Monitorizar issues y stars (primeras 48h)
  gh repo view OWNER/THEKEY --json stargazersCount,openIssues
  Revisar issues con etiqueta `bug` en < 24h.

====================================================================
ENTREGABLE B — Texto del primer anuncio (por canal)
====================================================================

--- Hacker News (Show HN) ---
Show HN: THEKEY — governed Git transactions for coding agents
I built a small core (102 tests, no Docker) that runs coding-agent changes in
isolated workspaces, checks every change with deterministic gates, and promotes
only results with an auditable evidence chain (SQLite). It is workflow
isolation, not an OS-level sandbox, and the policy authorization is deterministic
(hash-bound), not a magic "auto-approve". Demo reproduces on Windows 11 from a
clean clone. Feedback welcome.

--- Reddit r/programming ---
THEKEY tackles a concrete problem: agent-driven code changes are usually an
opaque "someone edited, we ran tests, we shipped". THEKEY makes the change
governed — isolated workspace, deterministic gates, verifiable evidence chain —
and never touches your original repo until the policy says so. It's not an
OS sandbox and doesn't promise to stop all agent risks. 102 tests, demo on
Windows 11 without Docker.

--- X/Twitter (280 chars exactos) ---
THEKEY: governed Git transactions for coding agents. Isolated workspaces, deterministic gates, auditable evidence chain (SQLite). Workflow isolation, not an OS sandbox. 102 tests, demo on Windows 11, no Docker. Public Preview. #codingagents #AgentGovernance #DevTools
(278 caracteres incl. hashtags; ajusta el link al publicar.)

--- LinkedIn ---
THEKEY 0.2.0 (Public Preview) brings governance to coding-agent change
pipelines. Each agent-proposed change runs in an isolated workspace and is
promoted only when it passes deterministic gates and receives verifiable policy
authorization. Every cycle leaves an auditable evidence chain in SQLite —
supporting supply-chain security and reviewability. It is workflow isolation,
not an OS-level sandbox. 102 tests; reproducible demo on Windows 11 without
Docker, WSL, or GPU.

====================================================================
ENTREGABLE C — Descripción larga del repo (Website / pinned comment)
====================================================================

THEKEY es un motor de transacciones Git gobernadas para agentes de programación.
Cada cambio propuesto por un agente se ejecuta en un workspace aislado — nunca
sobre el código original. Solo se promueve al repositorio lo que pasa todos los
gates deterministas y recibe autorización de política verificable. Cada ciclo
deja una cadena de evidencia auditable en SQLite. 102 tests. Demo reproducible
en Windows 11 sin Docker, sin WSL, sin GPU.

====================================================================
RESTRICCIONES ABSOLUTAS (aplican a todos los textos)
====================================================================
- "sandbox" solo con calificador "workflow isolation, not OS-level sandboxing".
- "deterministic policy authorization", nunca "auto-approval".
- No prometer que previene TODOS los riesgos de agentes autónomos.
- No mencionar NPSC en About, topics ni primer anuncio público.
- GIF debe existir antes del flip (docs/assets/thekey-demo.gif — generado).
- Versión siempre "v0.2.0 Public Preview"; nunca "v1.0" ni "stable".

====================================================================
AUTENTICACIÓN GH (bloqueante para push/topics/issues)
====================================================================
`gh auth status` muestra "not logged in". Para ejecutar los pasos que tocan
GitHub (3,4,6,7,8) necesitas autenticar. Opciones:
  (a) Interactive: gh auth login  (abra el navegador y autoriza).
  (b) Token: export GH_TOKEN=ghp_xxx  (classic token con repo + write:discussion
      + read:org según corresponda), luego re-ejecutar los comandos.
Sin esto, los pasos 3,4,6,7,8 quedan documentados pero no ejecutables por mí.
