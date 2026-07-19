# TDD RED — FASE-B-v2
Command: `pytest -q tests/test_phase_b_rbac_v2_models.py tests/test_phase_b_rbac_v2_guard.py tests/test_phase_b_rbac_v2_integration.py`
Result: **RED as expected**. Collection stopped with three errors because
`thekey.models` did not yet exist. This proves the security tests preceded the
production implementation.
