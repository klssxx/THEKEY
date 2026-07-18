"""NPSC -> THEKEY adapter (READ-ONLY, task 4).

This adapter does NOT execute NeuroPromptSemanticCompiler. It reads an NPSC
output artifact (a JSON file produced by NPSC's compile/export) and maps it
into a THEKEY ``ActorContext`` so a THEKEY actor (e.g. MiMo) can consume a
normalized, governed view.

Robustness: the NPSC export contract has drifted across versions. The audit
(2026-07-15) found NPSC emits ``recommended_output_contract`` while some
consumers expect ``output_contract`` / ``constraints``. This adapter accepts
BOTH shapes and normalizes them. It never writes to the NPSC source and never
evaluates arbitrary code from the artifact.

NPSC output variants handled:
  * {"recommended_output_contract": {...}, "constraints": [...], ...}
  * {"output_contract": {...}, "constraints": [...]}
  * {"output_contract": {"constraints": [...]}}
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


def _extract_constraints(obj: dict) -> list[str]:
    """Pull constraint strings from any of the known NPSC layouts."""
    out: list[str] = []
    top = obj.get("constraints")
    if isinstance(top, list):
        out.extend(str(c) for c in top)
    oc = obj.get("output_contract")
    if isinstance(oc, dict):
        nested = oc.get("constraints")
        if isinstance(nested, list):
            out.extend(str(c) for c in nested)
    rec = obj.get("recommended_output_contract")
    if isinstance(rec, dict):
        nested = rec.get("constraints")
        if isinstance(nested, list):
            out.extend(str(c) for c in nested)
    seen: set[str] = set()
    uniq: list[str] = []
    for c in out:
        if c not in seen:
            seen.add(c)
            uniq.append(c)
    return uniq


def _contract_dict(obj: dict) -> dict:
    rec = obj.get("recommended_output_contract")
    if isinstance(rec, dict):
        return rec
    oc = obj.get("output_contract")
    if isinstance(oc, dict):
        return oc
    return {}


def map_npsc_to_context(
    npsc_artifact: dict | Path | str,
    *,
    actor: str = "MiMo",
    mission_id: str,
    role: str = "executor",
) -> dict:
    """Map an NPSC output artifact into a THEKEY ActorContext.

    ``npsc_artifact`` may be a dict, a JSON file path, or a JSON string.
    Returns a dict conforming to ``actor_context.schema.json``.
    """
    if isinstance(npsc_artifact, (Path, str)):
        p = Path(npsc_artifact)
        if p.exists():
            npsc_artifact = json.loads(p.read_text(encoding="utf-8"))
        else:
            npsc_artifact = json.loads(str(npsc_artifact))
    if not isinstance(npsc_artifact, dict):
        raise TypeError("NPSC artifact must be a JSON object")

    contract = _contract_dict(npsc_artifact)
    constraints = _extract_constraints(npsc_artifact)

    constraints_obj: dict[str, Any] = dict(contract.get("constraints_meta", {}))
    constraints_obj["constraints"] = constraints
    for k, v in contract.items():
        if k in ("constraints",):
            continue
        if isinstance(v, (str, int, float, bool)):
            constraints_obj.setdefault(k, v)

    return {
        "actor": actor,
        "mission_id": mission_id,
        "role": role,
        "allowed_actions": ["READ_NPSC_ARTIFACT", "PRODUCE_CONTEXT"],
        "constraints": constraints_obj,
        "evidence_scope": ["npsc_artifact_hash"],
        "read_only": True,
        "generated_at": "",
    }


def npsc_artifact_hash(artifact: dict | Path | str) -> str:
    """Stable SHA-256 of the NPSC artifact (canonical JSON)."""
    if isinstance(artifact, (Path, str)):
        p = Path(artifact)
        if p.exists():
            data = p.read_bytes()
        else:
            data = str(artifact).encode("utf-8")
    else:
        data = json.dumps(artifact, sort_keys=True, ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def build_hy3_turn(
    context: Any,
    *,
    state_version: int,
    state_hash: str,
    phase_contract_hash: str,
    phase: str,
    allowed_transitions: list[str] | None = None,
    evidence_index: list[str] | None = None,
) -> str:
    """Package a governed BuiltContext into a restricted operator-turn YAML.

    The produced string is exactly what ``output_validator.parse_operator_turn``
    expects: the 10 required keys in the exact required order, terminated by
    ``---END_TURN---``. This closes the loop ContextBuilder -> adapter ->
    OutputValidator without touching the deterministic control plane.

    The HY3 operator receives this as the *template* it must fill; the function
    itself emits a NEXT_PHASE_READY turn with no file writes, so it is safe to
    produce without an actual model call (useful for offline verification).
    """
    from ..output_validator import TERMINATOR

    evidence_refs = evidence_index or []
    turn = {
        "phase": phase,
        "status": "NEXT_PHASE_READY",
        "context_binding": {
            "state_version": int(state_version),
            "state_hash": state_hash,
            "phase_contract_hash": phase_contract_hash,
        },
        "observed": [
            {
                "fact": "Context built from minified authoritative state (no chat history).",
                "source": "state-file",
                "evidence": evidence_refs[0] if evidence_refs else "EVID-BASELINE",
            }
        ],
        "actions": [],
        "files_changed": [],
        "evidence": [{"evidence": r} for r in evidence_refs] or [],
        "state_change_requested": {"from": "", "to": ""},
        "next": "await_operator_input",
        "error_code": "",
    }
    # Ensure exact key order required by the operator-turn contract.
    ordered = {k: turn[k] for k in (
        "phase", "status", "context_binding", "observed", "actions",
        "files_changed", "evidence", "state_change_requested", "next", "error_code",
    )}
    body = json.dumps(ordered, ensure_ascii=False, indent=2)
    return body + "\n" + TERMINATOR + "\n"
