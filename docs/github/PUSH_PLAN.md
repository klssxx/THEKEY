# THEKEY Core — Push / Release Plan (PREPARED LOCALLY, NOT EXECUTED)

Status: **PREPARED ONLY**. No remote created, no push, no release.
All push/release commands below are listed for the operator to run after explicit
approval. `gh` is installed at `C:\Program Files\GitHub CLI\gh.exe`
(version 2.96.0) but is **NOT authenticated** — `gh auth login` has not
been run.

## 1. Proposed remote + repository

- Host: github.com
- Proposed repo name: `THEKEY-Core-Governed-Run`
- Proposed description:
  "Autonomous, deterministic governed-run engine for software changes. Plans,
  executes in isolated workspaces, verifies with mandatory gates, and produces
  tamper-evident evidence — no human in the loop by default, no external API."
- Visibility: **public** (target: stars, issues, PRs)
- Local working copy: `E:\PROYECTS\GovernedOSS`
- Current branch to publish: `feature/universal-python-missions-0.2`
  (this is the active branch; it will be the `main` of the new repo, or
  renamed to `main` at publish time — see commands).

## 2. Publication branch

- Source branch: `feature/universal-python-missions-0.2`
- Target default branch on GitHub: `main`
- Planned tag: `v0.2.0` (annotated) — see §6.
- No other branches will be published.

## 3. .gitignore / README / license / metadata

- `.gitignore`: updated — `.thekey/`, `runs/`, `workspaces/`,
  `development-audit/` are ignored. Runtime state is NEVER pushed.
- `LICENSE`: MIT (present).
- `README.md`: updated for the autonomous, contributor-ready story
  (Quick start, For contributors, THEKEY_CONTRACT reference).
- `THEKEY_CONTRACT.md`: the implementer/verifier contract (new in 0.2.0).
- `pyproject.toml`: version `0.2.0`, `[dev]` extras, `thekey` and
  `thekey-mimo` console scripts.
- `.github/ISSUE_TEMPLATE/*`, `.github/PULL_REQUEST_TEMPLATE.md`,
  `.github/workflows/tests.yml`: present (CI runs `pytest` on push/PR).

## 4. Pre-release gate checklist (MUST all be true before any push)

1. [ ] GPT_HARDENING finished with verifiable output (background task done).
2. [ ] NPSC diff + patched package validated via the read-only adapter.
3. [ ] `--strict` blocks for real; `redacted_review` leaks nothing;
      contract aligned (`recommended_output_contract` <-> `output_contract`).
4. [ ] Tests + demo + regression run on the EXACT tree to be pushed.
5. [ ] No keys / tokens / private paths / temp exports / stray artifacts.
6. [ ] Manifest generated (commit, hashes, test results, planned content).
7. [ ] **Operator explicit approval to run the push.** (PENDING)

Current state of gates: **1–7 OPEN** (GPT background task still running;
gates 2–7 cannot close until gate 1 has verifiable evidence).

## 5. Exact commands (DO NOT RUN without approval)

```powershell
# Locate gh (already installed; not on PATH by default)
$gh = "C:\Program Files\GitHub CLI\gh.exe"

# Authenticate (OPERATOR must complete browser login personally)
# & $gh auth login --hostname github.com --git-protocol https --web

# Create the repo (public) — needs auth
# & $gh repo create THEKEY-Core-Governed-Run --public `
#     --description "Autonomous deterministic governed-run engine for software changes." `
#     --source . --remote origin --push --branch main

# If repo already exists / remote added manually:
# git remote add origin https://github.com/<YOU>/THEKEY-Core-Governed-Run.git
# git push -u origin main

# Tag + release (after push, with approval)
# git tag -a v0.2.0 -m "THEKEY Core Governed Run 0.2.0 — autonomous, contributor-ready"
# git push origin v0.2.0
# & $gh release create v0.2.0 --title "v0.2.0" --notes-file docs\github\RELEASE_NOTES_v0.2.0.md
```

## 6. What would be published (inventory)

- 3 commits:
  - `b7b6c32` THEKEY Core Governed Run MVP 0.1.0
  - `3cc3950` 0.2.0: autonomous governed run + contributor-ready surface
  - `cc31b7b` chore: stop tracking runtime state (.thekey/) — push hygiene
- 129 tracked files (source + governance + tests + docs + fixtures).
- Excluded from push (gitignored): `.thekey/`, `runs/`, `workspaces/`,
  `development-audit/`, `.venv/`.
- Test result on the publish tree: **102 passed** (baseline 89 preserved +
  9 automation-surface + 4 adversarial). `python -m compileall src` OK.
  `thekey demo` → RELEASE_ELIGIBLE, exit 0. `thekey-mimo` → exit 0.
  `thekey history verify` → VALID.

## 7. Secret / sensitive review

- No `api_key` / `token` / `secret` / `password` / `.env` named files in
  the tracked tree.
- `.thekey/events.db` (SQLite audit log, contains only run metadata +
  hashes) is gitignored and NOT pushed.
- No private absolute paths outside the repo root in committed files.
- NPSC original (protected) is untouched; only the isolated export copy is
  referenced, and only by GPT_HARDENING on a separate task.

## 8. Blocker

Until gate 1 (GPT_HARDENING verifiable output) closes, this plan is
**frozen**. No `gh repo create`, no `git push`, no `gh release create`
will be executed. The original NPSC is not modified or integrated.
