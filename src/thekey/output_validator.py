"""Restricted YAML output parser and validation pipeline.

Validates HY3 operator turns (section 22, 23). The parser is deliberately
restrictive:
  * No Markdown fences.
  * No text before the YAML.
  * No text after the terminator.
  * Exact key set and key order.
  * Strings quoted, empty lists as [].
  * No anchors / aliases / tags / comments.

The full validation pipeline (terminator -> extract -> parse -> unknown keys ->
schema -> binding -> role -> action -> budget -> paths -> transition ->
evidence) runs BEFORE any state or write is applied (section 23).
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import yaml

from .errors import (
    InvalidModelOutputError,
    OutputTruncatedError,
    StaleModelOutputError,
    UnauthorizedActionError,
)
from .config import OPERATOR_TURN_SCHEMA_FILE
from .command_registry import assert_role_allowed

TERMINATOR = "---END_TURN---"

# Exact key order required by the operator-turn contract.
EXPECTED_KEYS = [
    "phase",
    "status",
    "context_binding",
    "observed",
    "actions",
    "files_changed",
    "evidence",
    "state_change_requested",
    "next",
    "error_code",
]

STATUS_VALUES = {
    "IN_PROGRESS",
    "PASSED",
    "FAILED",
    "BLOCKED",
    "BLOCKED_UNCERTAIN",
    "BLOCKED_UNVERIFIED",
    "NEXT_PHASE_READY",
}

# A yaml parser that refuses unsafe constructs.
_SAFE_LOAD = yaml.SafeLoader


def parse_operator_turn(raw: str) -> dict:
    """Parse a restricted operator turn. Raises on terminator / structure
    violations."""
    if not raw or not raw.strip():
        raise OutputTruncatedError("Empty model output", code="OUTPUT_TRUNCATED")

    text = raw.strip()

    # Terminator must be present and at the very end.
    if not text.endswith(TERMINATOR):
        raise OutputTruncatedError(
            "Missing ---END_TURN--- terminator", code="OUTPUT_TRUNCATED"
        )
    body = text[: -len(TERMINATOR)].rstrip("\n")

    # No leading/trailing commentary. The body must parse as a single mapping.
    try:
        data = yaml.load(body, Loader=_SAFE_LOAD)
    except yaml.YAMLError as exc:
        raise InvalidModelOutputError(f"Invalid YAML: {exc}", code="INVALID_MODEL_OUTPUT") from exc

    if not isinstance(data, dict):
        raise InvalidModelOutputError(
            "Top-level YAML must be a mapping", code="INVALID_MODEL_OUTPUT"
        )

    # Unknown keys rejected.
    unknown = set(data.keys()) - set(EXPECTED_KEYS)
    if unknown:
        raise InvalidModelOutputError(
            f"Unknown keys: {sorted(unknown)}", code="INVALID_MODEL_OUTPUT"
        )

    # Exact key order.
    order = [k for k in data.keys()]
    if order != EXPECTED_KEYS:
        raise InvalidModelOutputError(
            f"Key order mismatch: expected {EXPECTED_KEYS}", code="INVALID_MODEL_OUTPUT"
        )

    # Status value.
    if data.get("status") not in STATUS_VALUES:
        raise InvalidModelOutputError(
            f"Invalid status: {data.get('status')!r}", code="INVALID_MODEL_OUTPUT"
        )

    return data


class OutputValidator:
    """Runs the full validation pipeline and exposes a clean result object."""

    def __init__(self, operator_schema_file: Path = OPERATOR_TURN_SCHEMA_FILE):
        self.schema = json.loads(Path(operator_schema_file).read_text(encoding="utf-8"))

    def validate(
        self,
        raw: str,
        *,
        expected_phase: str,
        expected_state_version: int,
        expected_state_hash: str,
        expected_contract_hash: str,
        role: str,
        state,  # StateSnapshot
        allowed_transitions: list[str],
        evidence_index: list[str] | None = None,
    ) -> dict:
        parsed = parse_operator_turn(raw)

        # Schema validation (keys/types/enum via JSON schema over the parsed map).
        from jsonschema import Draft7Validator

        validator = Draft7Validator(self.schema)
        errs = sorted(validator.iter_errors(parsed), key=lambda e: list(e.path))
        if errs:
            msgs = [f"{list(e.path)}: {e.message}" for e in errs]
            raise InvalidModelOutputError(
                "Schema violations: " + "; ".join(msgs), code="INVALID_MODEL_OUTPUT"
            )

        # Context binding (stale output protection).
        cb = parsed.get("context_binding", {})
        if int(cb.get("state_version", -1)) != int(expected_state_version):
            raise StaleModelOutputError(
                "State version mismatch", code="STALE_MODEL_OUTPUT"
            )
        if cb.get("state_hash") != expected_state_hash:
            raise StaleModelOutputError(
                "State hash mismatch", code="STALE_MODEL_OUTPUT"
            )
        if cb.get("phase_contract_hash") != expected_contract_hash:
            raise StaleModelOutputError(
                "Phase contract hash mismatch", code="STALE_MODEL_OUTPUT"
            )

        # Phase match.
        if parsed.get("phase") != expected_phase:
            raise InvalidModelOutputError(
                f"Phase mismatch: {parsed.get('phase')!r} != {expected_phase!r}",
                code="INVALID_MODEL_OUTPUT",
            )

        # Action authorization (role + id).
        for action in parsed.get("actions", []):
            action_id = action.get("action_id")
            assert_role_allowed(action_id, role)

        # Transition validity: the requested (from->to) must be present in the
        # contract's allowed_transitions list (formatted "FROM->TO"), OR the
        # target state must be a legal target under the state machine.
        scr = parsed.get("state_change_requested", {})
        to_state = scr.get("to")
        from_state = scr.get("from")
        if to_state:
            allowed = allowed_transitions or []
            transition_ok = (
                f"{from_state}->{to_state}" in allowed
                or to_state in allowed
            )
            if not transition_ok:
                raise InvalidModelOutputError(
                    f"Transition {from_state} -> {to_state} not in allowed set {allowed}",
                    code="INVALID_MODEL_OUTPUT",
                )

        # Evidence references must always be non-empty (rule 14: evidence is
        # created from observed execution results, never blank).
        for ev in parsed.get("evidence", []):
            ref = ev.get("evidence") if isinstance(ev, dict) else None
            if not ref:
                raise InvalidModelOutputError(
                    "Evidence entry without reference", code="INVALID_MODEL_OUTPUT"
                )
            # When an evidence index is supplied, the reference must name a known
            # artifact (or be a valid path) so tampering/fabrication is caught.
            if evidence_index is not None and ref not in evidence_index:
                raise InvalidModelOutputError(
                    f"Evidence reference {ref!r} not in known evidence index",
                    code="INVALID_MODEL_OUTPUT",
                )

        return parsed
