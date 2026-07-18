# Changelog

All notable changes to THEKEY Core Governed Run are documented here. The format
is based on [Keep a Changelog](https://keepachangelog.com/).

## [0.2.0] - 2026-07-18

Public Preview. Governance, workspace isolation, deterministic gates, and
verifiable evidence are unchanged from the 0.1.0 core; this release adds the
public-preview surface (docs, badges, demo assets, issue/PR templates) and the
CI documentation gates.

### Added
* ES/EN parity gate and forbidden-claims gate in CI (`scripts/ci/`).
* Public-preview documentation, badges, demo GIF/video.
* Issue/PR templates and launch/backlog evidence artifacts.

### Changed
* Version aligned across `src/thekey/__init__.py`, `pyproject.toml`,
  `STATUS.md`, and `CHANGELOG.md` (added this entry).

## [0.1.0] - 2026-07-15

First public MVP OSS release.

### Added
* Governed run lifecycle: SUBMITTED -> BASELINED -> ANALYZED -> PLAN_PROPOSED ->
  PLAN_APPROVED -> IMPLEMENTED -> TESTED -> RELEASE_ELIGIBLE, with BLOCKED /
  FAILED / ROLLED_BACK states.
* Four logical roles (PLANNER, EXECUTOR, VERIFIER, APPROVER) with strict
  permission matrix.
* Authoritative, atomically-updated state (`.thekey/state.json`) with an
  append-only transition log and SHA-256 chain.
* Policy-as-code engine validated by JSON Schema
  (`governance/policies/local-python-demo.yaml`).
* Closed action registry — no arbitrary shell.
* Workspace isolation with path-traversal / sibling-prefix / protected-path /
  reparse-point defenses.
* Restricted YAML operator-output parser + full validation pipeline.
* Context builder with token budgets and a minified state view (no chat
  history injected).
* Deterministic gates: build, unit tests, secret scan, documentation.
* Release Decision Engine (RELEASE_ELIGIBLE / BLOCKED) derived from policy.
* Evidence manager with SHA-256 hashing and tamper detection.
* Recovery controller (orchestrator mode, not a run state).
* CLI: `thekey run ...`, `thekey evidence verify`, `thekey demo`.
* Canonical deterministic demo (defective `calculator.add`) and four blocked
  scenarios (invalid policy, failed gate, tampered evidence, missing input).
* One-command PowerShell bootstrap (`scripts/bootstrap-and-demo.ps1`).
* Test suite: unit, integration, end-to-end (63 tests).
