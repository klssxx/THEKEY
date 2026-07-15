name: Bug report
description: Report a defect in THEKEY Core Governed Run
title: "[BUG] "
labels: ["bug"]
body:
  - type: textarea
    id: problem
    attributes:
      label: Problem
      description: What went wrong? Include the run id and the observed vs expected behavior.
    validations:
      required: true
  - type: textarea
    id: repro
    attributes:
      label: Reproduction
      description: Steps to reproduce, including the exact command(s) run.
    validations:
      required: true
  - type: textarea
    id: evidence
    attributes:
      label: Evidence
      description: Paste relevant gate output, decision.json excerpt, or artifact hashes.
    validations:
      required: false
  - type: checkboxes
    id: checks
    attributes:
      label: Confirmations
      options:
        - label: I did not modify the protected historical THEKEY path.
        - label: I ran the latest bootstrap-and-demo.ps1.
