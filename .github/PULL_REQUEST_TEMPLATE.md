name: Pull Request

description: Contribute a change to THEKEY Core Governed Run
title: "[PR] "
labels: []

body: |
  ## Summary
  <!-- What governed change does this PR implement? -->

  ## Run lifecycle impact
  <!-- Which states, transitions, gates, or roles are affected? -->

  ## Evidence & tests
  - [ ] `pytest` passes locally.
  - [ ] `.\scripts\bootstrap-and-demo.ps1` reaches RELEASE_ELIGIBLE.
  - [ ] Evidence/hash verification still passes.
  - [ ] No modification of the protected historical THEKEY path.

  ## Guardrails (non-negotiable)
  - [ ] The model still cannot write authoritative state or evidence directly.
  - [ ] No arbitrary shell exposed via action IDs.
  - [ ] JSON Schemas and tests updated for any contract change.

  ## Related issues
  <!-- e.g. Closes #12 -->
