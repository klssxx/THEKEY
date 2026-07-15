name: Governance change
description: Propose a change to the governed run lifecycle, policy schema, or role matrix
title: "[GOV] "
labels: ["governance"]
body:
  - type: textarea
    id: change
    attributes:
      label: Change
      description: What control-plane or policy change is proposed?
    validations:
      required: true
  - type: textarea
    id: impact
    attributes:
      label: Impact
      description: Which states, transitions, gates, or roles are affected? Does it grant the model any new authority?
    validations:
      required: true
  - type: checkboxes
    id: guardrails
    attributes:
      label: Guardrails
      options:
        - label: The model still cannot write authoritative state or evidence directly.
        - label: A JSON Schema and tests are updated.
        - label: A CHANGELOG entry will be added.
