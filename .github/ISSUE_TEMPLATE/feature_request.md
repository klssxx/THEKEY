name: Feature request
description: Propose an enhancement to THEKEY Core Governed Run
title: "[FEATURE] "
labels: ["enhancement"]
body:
  - type: textarea
    id: context
    attributes:
      label: Context
      description: Why is this needed? Link to the relevant roadmap item if any.
    validations:
      required: true
  - type: textarea
    id: proposal
    attributes:
      label: Proposal
      description: Describe the change and its governance impact (roles, state, policy).
    validations:
      required: true
  - type: textarea
    id: scope
    attributes:
      label: Out of scope
      description: What this change explicitly will NOT do.
    validations:
      required: false
