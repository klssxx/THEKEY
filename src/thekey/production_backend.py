"""Production adapter joining the physical guard to PolicyEngine."""

from __future__ import annotations

import hashlib
import json
from typing import Any, Mapping, Protocol

from pydantic import ValidationError

from . import rbac_guard
from .models import ActionContext, AuthorizationDecision


class PolicyEngineProtocol(Protocol):
    def authorize_action(self, request: Mapping[str, Any]) -> Mapping[str, Any]: ...


def canonical_hash(value: Any) -> str:
    try:
        body = json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        ).encode("utf-8")
    except (TypeError, ValueError) as exc:
        raise ValueError("PARAMETERS_NOT_CANONICAL_JSON") from exc
    return hashlib.sha256(body).hexdigest()


class ProductionAuthorizationBackend:
    def __init__(self, policy_engine: PolicyEngineProtocol) -> None:
        if not callable(getattr(policy_engine, "authorize_action", None)):
            raise TypeError("POLICY_ENGINE_AUTHORIZE_ACTION_REQUIRED")
        self._policy_engine = policy_engine

    def authorize(
        self, *, context: ActionContext, action_id: str, parameters: Any
    ) -> AuthorizationDecision:
        request = context.model_dump(mode="json")
        request["action_id"] = action_id
        request["parameters_sha256"] = canonical_hash(parameters)
        try:
            raw = self._policy_engine.authorize_action(request)
            return AuthorizationDecision.model_validate(raw)
        except ValidationError:
            return AuthorizationDecision(
                allowed=False,
                reason_code="POLICY_ENGINE_INVALID_RESPONSE",
                policy_bundle_hash=context.policy_bundle_hash,
            )
        except Exception as exc:
            return AuthorizationDecision(
                allowed=False,
                reason_code=f"POLICY_ENGINE_ERROR:{type(exc).__name__}",
                policy_bundle_hash=context.policy_bundle_hash,
            )


def install_production_authorization_backend(
    policy_engine: PolicyEngineProtocol,
) -> ProductionAuthorizationBackend:
    backend = ProductionAuthorizationBackend(policy_engine)
    rbac_guard._install_production_backend_once(backend)
    return backend


def ensure_production_authorization_backend(policy_engine: PolicyEngineProtocol) -> None:
    if not rbac_guard._backend_installed:
        install_production_authorization_backend(policy_engine)
