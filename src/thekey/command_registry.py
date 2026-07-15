"""Closed action registry.

Maps each model-requestable action ID to metadata (allowed roles, whether it is
a read or write, and the handler). Model-requestable actions never expose shell
strings or arbitrary paths. Orchestrator-internal operations are NOT listed here
(section 20).
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Callable

from .errors import UnauthorizedActionError


class ActionKind(str, Enum):
    READ = "READ"
    WRITE = "WRITE"
    COMMAND = "COMMAND"


@dataclass
class ActionSpec:
    action_id: str
    kind: ActionKind
    allowed_roles: frozenset[str]
    handler: str  # name of function in actions.py


# Declared model-requestable action IDs per role (section 19).
PLANNER_ACTIONS = {
    "LIST_DECLARED_FILES",
    "READ_DECLARED_FILE",
    "COMPUTE_DECLARED_FILE_HASH",
    "CHECK_DECLARED_PYTHON_SYNTAX",
}
EXECUTOR_ACTIONS = {
    "READ_DECLARED_FILE",
    "COMPUTE_DECLARED_FILE_HASH",
    "CHECK_DECLARED_PYTHON_SYNTAX",
    "REPLACE_EXACT_TEXT",
    "CREATE_DECLARED_FILE",
    "RUN_TARGETED_TESTS",
}
VERIFIER_ACTIONS = {
    "READ_DECLARED_FILE",
    "COMPUTE_DECLARED_FILE_HASH",
    "CHECK_DECLARED_PYTHON_SYNTAX",
    "RUN_BUILD",
    "RUN_UNIT_TESTS",
    "RUN_TARGETED_TESTS",
    "SCAN_SECRETS",
    "CHECK_REQUIRED_DOCUMENTATION",
}
APPROVER_ACTIONS: set[str] = set()  # approver does not request commands

ALL_MODEL_ACTIONS = PLANNER_ACTIONS | EXECUTOR_ACTIONS | VERIFIER_ACTIONS

ROLE_ACTIONS = {
    "PLANNER": PLANNER_ACTIONS,
    "EXECUTOR": EXECUTOR_ACTIONS,
    "VERIFIER": VERIFIER_ACTIONS,
    "APPROVER": APPROVER_ACTIONS,
}

# Handler routing (handlers implemented in actions.py).
_REGISTRY: dict[str, ActionSpec] = {}


def _register(action_id: str, kind: ActionKind, allowed_roles: set[str], handler: str) -> None:
    _REGISTRY[action_id] = ActionSpec(
        action_id=action_id,
        kind=kind,
        allowed_roles=frozenset(allowed_roles),
        handler=handler,
    )


# Planner.
_register("LIST_DECLARED_FILES", ActionKind.READ, {"PLANNER"}, "list_declared_files")
_register("READ_DECLARED_FILE", ActionKind.READ, {"PLANNER", "EXECUTOR", "VERIFIER"}, "read_declared_file")
_register("COMPUTE_DECLARED_FILE_HASH", ActionKind.READ, {"PLANNER", "EXECUTOR", "VERIFIER"}, "compute_declared_file_hash")
_register("CHECK_DECLARED_PYTHON_SYNTAX", ActionKind.READ, {"PLANNER", "EXECUTOR", "VERIFIER"}, "check_declared_python_syntax")
# Executor.
_register("REPLACE_EXACT_TEXT", ActionKind.WRITE, {"EXECUTOR"}, "replace_exact_text")
_register("CREATE_DECLARED_FILE", ActionKind.WRITE, {"EXECUTOR"}, "create_declared_file")
_register("RUN_TARGETED_TESTS", ActionKind.COMMAND, {"EXECUTOR", "VERIFIER"}, "run_targeted_tests")
# Verifier.
_register("RUN_BUILD", ActionKind.COMMAND, {"VERIFIER"}, "run_build")
_register("RUN_UNIT_TESTS", ActionKind.COMMAND, {"VERIFIER"}, "run_unit_tests")
_register("SCAN_SECRETS", ActionKind.COMMAND, {"VERIFIER"}, "scan_secrets")
_register("CHECK_REQUIRED_DOCUMENTATION", ActionKind.COMMAND, {"VERIFIER"}, "check_required_documentation")


def get_spec(action_id: str) -> ActionSpec | None:
    return _REGISTRY.get(action_id)


def assert_role_allowed(action_id: str, role: str) -> None:
    spec = get_spec(action_id)
    if spec is None:
        raise UnauthorizedActionError(f"Unknown action id: {action_id!r}")
    if role not in spec.allowed_roles:
        raise UnauthorizedActionError(
            f"Role {role!r} may not request {action_id!r}",
            code="UNAUTHORIZED_ACTION",
        )


def all_action_ids() -> list[str]:
    return sorted(_REGISTRY)
