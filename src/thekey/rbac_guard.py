"""Fail-closed guard evaluated before any physical handler is resolved."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol

from pydantic import ValidationError

from .models import (
    ActionContext,
    ActionReviewVerdict,
    AuthorizationDecision,
    Role,
)


class AuthorizationBackend(Protocol):
    def authorize(
        self, *, context: ActionContext, action_id: str, parameters: Any
    ) -> AuthorizationDecision | dict: ...


class DenyAllAuthorizationBackend:
    def authorize(self, *, context, action_id, parameters) -> AuthorizationDecision:
        return AuthorizationDecision(
            allowed=False,
            reason_code="AUTHORIZATION_BACKEND_NOT_CONFIGURED",
        )


class AuthorizationDeniedError(PermissionError):
    def __init__(self, reason_code: str) -> None:
        self.reason_code = reason_code
        super().__init__(reason_code)


@dataclass(frozen=True)
class AuthorizedAction:
    context: ActionContext
    decision: AuthorizationDecision


_backend: AuthorizationBackend = DenyAllAuthorizationBackend()
_backend_installed = False
_ALLOWED_PHYSICAL_ROLES = frozenset({Role.EXECUTOR})


def _install_production_backend_once(backend: AuthorizationBackend) -> None:
    global _backend, _backend_installed
    if _backend_installed:
        raise RuntimeError("AUTHORIZATION_BACKEND_ALREADY_CONFIGURED")
    if backend.__class__.__module__.split(".")[-1] != "production_backend":
        raise RuntimeError("NON_PRODUCTION_BACKEND_INSTALL_DENIED")
    _backend = backend
    _backend_installed = True


def _validation_reason(exc: ValidationError) -> str:
    fields = {
        str(error.get("loc", ("unknown",))[0])
        for error in exc.errors(include_url=False)
        if error.get("loc")
    }
    if "protocol_version" in fields:
        return "PROTOCOL_VERSION_MISMATCH"
    if "schema_version" in fields:
        return "SCHEMA_VERSION_MISMATCH"
    if "role" in fields:
        return "ROLE_INVALID_OR_MISSING"
    if "review_verdict" in fields:
        return "REVIEW_VERDICT_INVALID_OR_MISSING"
    return "CONTEXT_INVALID_OR_INCOMPLETE"


def enforce_action_context(
    *,
    raw_context: dict[str, Any] | ActionContext | None,
    action_id: str,
    run_id: str | None,
    parameters: Any,
) -> AuthorizedAction:
    try:
        context = (
            raw_context
            if isinstance(raw_context, ActionContext)
            else ActionContext.model_validate(raw_context)
        )
    except ValidationError as exc:
        raise AuthorizationDeniedError(_validation_reason(exc)) from exc

    if run_id is not None and context.run_id != run_id:
        raise AuthorizationDeniedError("RUN_ID_MISMATCH")
    if context.role not in _ALLOWED_PHYSICAL_ROLES:
        raise AuthorizationDeniedError("ROLE_NOT_ALLOWED")
    vetoes = {
        ActionReviewVerdict.FAIL: "CHECKMATE_FAILED",
        ActionReviewVerdict.DEFER: "CHECKMATE_DEFERRED",
        ActionReviewVerdict.PENDING: "CHECKMATE_PENDING",
    }
    if context.review_verdict in vetoes:
        raise AuthorizationDeniedError(vetoes[context.review_verdict])
    if action_id not in context.sovereign_receipt.allowed_action_ids:
        raise AuthorizationDeniedError("ACTION_NOT_SOVEREIGN_AUTHORIZED")

    try:
        raw_decision = _backend.authorize(
            context=context,
            action_id=action_id,
            parameters=parameters,
        )
    except Exception as exc:
        raise AuthorizationDeniedError(f"POLICY_ENGINE_ERROR:{type(exc).__name__}") from exc
    try:
        decision = (
            raw_decision
            if isinstance(raw_decision, AuthorizationDecision)
            else AuthorizationDecision.model_validate(raw_decision)
        )
    except ValidationError as exc:
        raise AuthorizationDeniedError("POLICY_DECISION_INVALID") from exc
    if not decision.allowed:
        raise AuthorizationDeniedError(decision.reason_code)
    if decision.policy_bundle_hash != context.policy_bundle_hash:
        raise AuthorizationDeniedError("POLICY_BUNDLE_HASH_MISMATCH")
    return AuthorizedAction(context=context, decision=decision)
