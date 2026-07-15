"""MiMo actor profile + THEKEY contract (task 7).

MiMo is the IMPLEMENTER actor of THEKEY Core Governed Run. It writes product
code ONLY inside an isolated workspace and only after an automatically-approved
plan. It never mutates the original source, never touches the protected
historical THEKEY framework, never executes arbitrary shell, and never
persists state/evidence on behalf of the verifier (HY3).

This module is the single source of truth for the MiMo contract used by the
launcher, the NPSC adapter context, and the documentation.
"""

from __future__ import annotations

ACTOR_PROFILE = "MiMo"
ROLE = "implementer"

# Hard constraints MiMo is governed by (enforced by the coordinator, not by
# trust). Surfaced in ActorContext.constraints for transparency.
CONTRACT = {
    "writes_only_in_isolated_workspace": True,
    "never_mutates_original_source": True,
    "never_touches_protected_thekey": True,
    "no_arbitrary_shell": True,
    "plan_must_be_auto_approved_before_write": True,
    "mandatory_build_after_import": True,
    "evidence_is_hash_sealed": True,
    "max_work_turns": 3,
    "allowed_cli": [
        "thekey run create",
        "thekey run plan",
        "thekey run approve-plan",
        "thekey run execute",
        "thekey run verify",
        "thekey evidence verify",
        "thekey history verify",
        "thekey-mimo",
    ],
}

# The other principal actor. HY3 is the independent verifier/auditor; it must
# NOT accept MiMo's VERIFIED claims without reproducing proof in an isolated copy.
THEKEY_PRINCIPLES = [
    "Original source is immutable; only isolated workspaces are written.",
    "Approval is automatic and hash-bound, never a prompt.",
    "Evidence is SHA-256 sealed; tamper -> BLOCKED, never silent.",
    "The verifier reproduces proof; it does not trust the implementer.",
    "No arbitrary shell, no external API, no model-generated commands.",
    "Everything is append-only and auditable (event store + state chain).",
]


def as_actor_context(mission_id: str) -> dict:
    """Render MiMo's contract as a THEKEY ActorContext dict."""
    return {
        "actor": ACTOR_PROFILE,
        "mission_id": mission_id,
        "role": ROLE,
        "allowed_actions": [
            "READ_ORIGINAL",
            "WRITE_WORKSPACE",
            "RUN_GATES",
        ],
        "constraints": CONTRACT,
        "evidence_scope": ["workspace.diff", "build.log", "unit_tests.log"],
        "read_only": False,
        "generated_at": "",
    }
