# Discovery

Phase 0 discovery notes for THEKEY Core Governed Run OSS MVP.

## Environment
* OS: Windows 11
* Shell: PowerShell 7.6.3
* Python: 3.12.10 (>= 3.11 required)
* CPU/RAM: Intel Core i5 / 16 GB
* No Docker / WSL / Kubernetes / GPU required.

## Paths
* New repository: `E:\KLSX PROYECTS\KlsxMaker\TheKeyCore_Governed_OSS` (created).
* Protected historical THEKEY: `E:\KLSX PROYECTS\KlsxMaker\TheKey\Thekey`
  (READ_ONLY — never written by this project).

## Scope decision
The MVP implements ONE complete governed change (the canonical calculator demo)
end to end with deterministic roles. It deliberately does NOT:
* Migrate every old THEKEY agent.
* Build an enterprise platform or GUI.
* Require external AI APIs.

## Reuse decisions
* The historical THEKEY framework is treated as a frozen reference only. No code
  is copied from it into this repository.
* The canonical defect (`calculator.add` returns `a - b`) is intentionally left
  in `examples/demo_app/calculator.py` so the demo can always be reproduced.

## Risks
* Single active run at a time (repo-level state). Acceptable for MVP.
* Simplified local approver identity (not cryptographic). Documented in
  SECURITY.md and ROADMAP.md.
