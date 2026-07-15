"""THEKEY Core - canonical error taxonomy.

All errors raised by the control plane carry a stable ``code`` (string) and a
deterministic ``exit_code`` so that the CLI can map them to the documented
exit-code contract (see the hyper mega prompt, section 29).
"""

from __future__ import annotations


class TheKeyError(Exception):
    """Base class for all THEKEY Core errors.

    Attributes:
        code: short stable identifier, uppercase, underscore-separated.
        exit_code: process exit code per the documented contract.
        detail: human-readable explanation (no secrets).
    """

    code = "GENERAL_ERROR"
    exit_code = 1

    def __init__(self, message: str, *, code: str | None = None, exit_code: int | None = None):
        super().__init__(message)
        self.detail = message
        if code is not None:
            self.code = code
        if exit_code is not None:
            self.exit_code = exit_code

    def __str__(self) -> str:  # pragma: no cover - trivial
        return f"[{self.code}] {self.detail}"


class InvalidArgumentsError(TheKeyError):
    code = "INVALID_ARGUMENTS"
    exit_code = 2


class IncompatibleRunStateError(TheKeyError):
    code = "INCOMPATIBLE_RUN_STATE"
    exit_code = 3


class InvalidPolicyError(TheKeyError):
    code = "INVALID_POLICY"
    exit_code = 4


class GateFailureError(TheKeyError):
    code = "GATE_FAILURE"
    exit_code = 5


class InvalidEvidenceError(TheKeyError):
    code = "INVALID_EVIDENCE"
    exit_code = 6


class BudgetExceededError(TheKeyError):
    code = "BUDGET_EXCEEDED"
    exit_code = 7


class UnauthorizedPathError(TheKeyError):
    code = "UNAUTHORIZED_PATH"
    exit_code = 8


class StaleModelOutputError(TheKeyError):
    code = "STALE_MODEL_OUTPUT"
    exit_code = 9


class RecoveryBlockedError(TheKeyError):
    code = "RECOVERY_BLOCKED"
    exit_code = 10


class OutputTruncatedError(TheKeyError):
    code = "OUTPUT_TRUNCATED"
    exit_code = 9


class InvalidModelOutputError(TheKeyError):
    code = "INVALID_MODEL_OUTPUT"
    exit_code = 9


class UnauthorizedActionError(TheKeyError):
    code = "UNAUTHORIZED_ACTION"
    exit_code = 8


class InvalidTransitionError(TheKeyError):
    code = "INVALID_TRANSITION"
    exit_code = 1


class BlockedUncertainError(TheKeyError):
    code = "BLOCKED_UNCERTAIN"
    exit_code = 1


class BlockedUnverifiedError(TheKeyError):
    code = "BLOCKED_UNVERIFIED"
    exit_code = 1


# Model-facing status / error codes (used in restricted YAML outputs and
# validation results). These are *strings returned to/by* the operator layer.
MODEL_CODES = {
    "OUTPUT_TRUNCATED",
    "INVALID_MODEL_OUTPUT",
    "STALE_MODEL_OUTPUT",
    "UNAUTHORIZED_ACTION",
    "UNAUTHORIZED_PATH",
    "PATH_OUTSIDE_ALLOWED_ROOTS",
    "PROTECTED_PATH",
    "UNSAFE_REPARSE_POINT",
    "BLOCKED_UNCERTAIN",
    "BLOCKED_UNVERIFIED",
    "NO_VERIFICABLE",
}
