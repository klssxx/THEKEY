from __future__ import annotations

import pytest
from test_phase_b_rbac_v2_models import POLICY, valid_context

from thekey.models import ActionReviewVerdict, AuthorizationDecision
from thekey.rbac_guard import AuthorizationDeniedError, enforce_action_context


class Backend:
    def __init__(self, response=None, error=None):
        self.response = response or AuthorizationDecision(
            allowed=True,
            reason_code="AUTHORIZED",
            decision_id="policy-decision-real-1",
            policy_bundle_hash=POLICY,
        )
        self.error = error
        self.calls = 0

    def authorize(self, *, context, action_id, parameters):
        self.calls += 1
        if self.error:
            raise self.error
        return self.response


def _reason(monkeypatch, raw, backend=None, action_id="REPLACE_EXACT_TEXT", run_id=None):
    import thekey.rbac_guard as guard

    backend = backend or Backend()
    monkeypatch.setattr(guard, "_backend", backend)
    run_id = run_id or raw.get("run_id")
    with pytest.raises(AuthorizationDeniedError) as exc:
        enforce_action_context(
            raw_context=raw,
            action_id=action_id,
            run_id=run_id,
            parameters={"target_id": "x"},
        )
    return exc.value.reason_code, backend.calls


@pytest.mark.parametrize(
    "role", [None, "ROOT", "SYSTEM", "AUTHOR", "REVIEWER", "APPROVER", "SOVEREIGN"]
)
def test_non_executor_roles_deny_before_backend(monkeypatch, role):
    raw = valid_context(role=role)
    reason, calls = _reason(monkeypatch, raw)
    assert reason in {"ROLE_INVALID_OR_MISSING", "ROLE_NOT_ALLOWED"}
    assert calls == 0


@pytest.mark.parametrize(
    "verdict,reason_code",
    [
        ("PENDING", "CHECKMATE_PENDING"),
        ("DEFER", "CHECKMATE_DEFERRED"),
        ("FAIL", "CHECKMATE_FAILED"),
    ],
)
def test_checkmate_veto_reaches_zero_backends(monkeypatch, verdict, reason_code):
    raw = valid_context(review_verdict=verdict)
    raw["checkmate_receipt"] = raw["checkmate_receipt"].model_copy(
        update={"verdict": ActionReviewVerdict(verdict)}
    )
    reason, calls = _reason(monkeypatch, raw)
    assert reason == reason_code
    assert calls == 0


def test_pass_with_valid_double_receipt_allows(monkeypatch):
    import thekey.rbac_guard as guard

    backend = Backend()
    monkeypatch.setattr(guard, "_backend", backend)
    authorized = enforce_action_context(
        raw_context=valid_context(),
        action_id="REPLACE_EXACT_TEXT",
        run_id=None,
        parameters={"target_id": "x"},
    )
    assert authorized.decision.allowed is True
    assert authorized.decision.policy_bundle_hash == POLICY
    assert backend.calls == 1


def test_action_outside_sovereign_receipt_denied(monkeypatch):
    raw = valid_context()
    reason, calls = _reason(monkeypatch, raw, action_id="SCAN_SECRETS")
    assert reason == "ACTION_NOT_SOVEREIGN_AUTHORIZED"
    assert calls == 0


def test_run_mismatch_denied_before_backend(monkeypatch):
    raw = valid_context()
    reason, calls = _reason(monkeypatch, raw, run_id="different-run")
    assert reason == "RUN_ID_MISMATCH"
    assert calls == 0


def test_policy_exception_fails_closed(monkeypatch):
    reason, calls = _reason(monkeypatch, valid_context(), Backend(error=RuntimeError("boom")))
    assert reason == "POLICY_ENGINE_ERROR:RuntimeError"
    assert calls == 1


def test_allow_without_decision_id_denied(monkeypatch):
    invalid = {"allowed": True, "reason_code": "AUTHORIZED", "policy_bundle_hash": POLICY}
    reason, calls = _reason(monkeypatch, valid_context(), Backend(response=invalid))
    assert reason == "POLICY_DECISION_INVALID"
    assert calls == 1


def test_policy_bundle_hash_mismatch_denied(monkeypatch):
    response = AuthorizationDecision(
        allowed=True,
        reason_code="AUTHORIZED",
        decision_id="real-decision",
        policy_bundle_hash="c3" * 32,
    )
    reason, calls = _reason(monkeypatch, valid_context(), Backend(response=response))
    assert reason == "POLICY_BUNDLE_HASH_MISMATCH"
    assert calls == 1
