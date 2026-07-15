name: Pull Request
about: Propose a change to THEKEY
title: "[type] short summary"
labels: [enhancement]
assignees: []
---

## Summary of the change

<!-- What changes and why. Link the issue/RFC if any. -->

## Type of change

- [ ] Bug fix
- [ ] Small improvement (docs, message, policy, profile)
- [ ] New read-only adapter (external, optional)
- [ ] Architectural change (requires RFC)
- [ ] Documentation

## Impact on demo

- [ ] `python -m thekey demo` still reaches RELEASE_ELIGIBLE
- [ ] Not run / N/A

## Impact on documentation

- [ ] Normative docs updated (README / THREAT_MODEL / CONTRIBUTING)
- [ ] ES/EN parity maintained
- [ ] N/A

## Impact on security / threat model

- [ ] No security impact
- [ ] Threat model updated (THREAT_MODEL.md / .en.md)
- [ ] SECURITY.md updated

## Test checklist

- [ ] `python -m pytest -q` passes
- [ ] `scripts/ci/parity_gate.py` passes
- [ ] `scripts/ci/docs_claims.py` passes

## ES/EN parity checklist

- [ ] If I touched README / THREAT_MODEL / CONTRIBUTING, both ES and EN versions were updated.

## Related issue

<!-- Closes #N — link the issue this PR resolves. -->

## Evidence in the event store

<!-- If this touches the transactional core, state:
     - what event type / artifact is recorded on closure,
     - how to confirm the chained-hash store stays intact
       (e.g. `python -m thekey demo` -> evidence_mismatches: []). -->

## Test output

<!-- Paste the relevant output of `pytest -q` so the evidence travels with the PR. -->

## Validated commands checklist

- [ ] Every command I documented is one I actually ran and verified.
