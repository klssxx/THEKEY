# THEKEY — Checklist de flip público (v0.2.0 Public Preview)

Ejecutar en orden el día que decidas hacer el repo público. NO ejecutar antes.
Requiere `gh` autenticado (`gh auth login --web`) o un token con permisos de
repo. Nada de esto se ejecuta automáticamente.

## Pre-requisitos (verificar antes del flip)

- [ ] `gh auth status` responde autenticado.
- [ ] Demo verificada en clone limpio: `pwsh -NoProfile -File .\scripts\demo.ps1` → exit 0.
- [ ] GIF en `docs/assets/thekey-demo.gif` existe (obligatorio, no anunciar sin él).
- [ ] CI verde en la rama que será `main` (jobs windows + docs-gates + secret-scan).

## Pasos

**Paso 1 — Verificar CI verde en rama main**
```bash
gh run list --branch main --limit 5
# Confirma el último run de tests.yml en green.
```

**Paso 2 — Confirmar demo.ps1 en clone limpio**
```powershell
git clone <URL> "C:\Temp\THEKEY Check"
cd "C:\Temp\THEKEY Check"
pwsh -NoProfile -File .\scripts\demo.ps1
# Debe terminar exit 0 / RELEASE_ELIGIBLE / gates_passed: 4
```

**Paso 3 — About (repo Settings → About)**
Pegar EXACTAMENTE (97 chars, no trunca):
```
Governed Git transactions for coding agents  isolated workspaces, deterministic gates, auditable evidence.
```

**Paso 4 — Topics (repo Settings → About → Topics), en este orden**
```
coding-agents, agent-governance, ai-safety, git-transactions, workflow-isolation, audit-trail, deterministic-gates, supply-chain-security, code-review-automation, python, windows, sqlite, llm-tools, developer-tools
```
(15 topics. No incluir NPSC en ninguno.)

**Paso 5 — README primera pantalla**
Confirmar que `README.md` muestra, sin scroll: header `# THEKEY` + subtítulo
ES/EN + badges (CI/licencia/versión/Python/Windows) + GIF + línea de
conversión ("102 tests, 0 skipped"). Ya implementado localmente.

**Paso 6 — Abrir los 8 issues del backlog (release_evidence/backlog/)**
Abrirlos el MISMO día del flip (no antes) para señal de actividad reciente.
Usar los archivos `01..08_*.md` como cuerpo. Aplicar labels de cada archivo.
```bash
# Ejemplo por issue (adaptar título/labels del archivo):
gh issue create --title "[good first issue] Automated ES/EN README parity gate" \
  --label "good first issue,documentation,ci,windows" \
  --body-file release_evidence/backlog/01_gfi_readme_parity.md
```

**Paso 7 — Habilitar GitHub Discussions (opcional)**
Settings → Options → Features → Discussions. Aumenta engagement.

**Paso 8 — Switch privado → público**
Settings → Danger Zone → "Change repository visibility" → Make public.
Confirmar con el nombre del repo.

**Paso 9 — Compartir (orden de prioridad para audiencia técnica)**
1. Hacker News → Show HN (ver ENTREGABLE B).
2. Reddit r/programming.
3. X/Twitter (280 chars).
4. LinkedIn.

**Paso 10 — Monitorizar 48h**
- Issues: responder en ≤ 24h.
- Stars/forks: anotar día 1 y día 2.
- Si aparece un bug crítico, abrir issue y parchear en privado antes de merge.

## Notas
- Nombre del repo: `THEKEY` (no thekey-core / thekey-oss / thekey-framework).
- Nunca usar "auto-approval"; usar "deterministic policy authorization".
- Nunca usar "sandbox" sin "workflow isolation, not OS-level sandboxing".
- Nunca prometer prevención total de riesgos de agentes autónomos.
- Nunca mencionar NPSC en About, topics ni anuncio público.
- Versión siempre "v0.2.0 Public Preview".
