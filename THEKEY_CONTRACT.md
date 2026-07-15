# THEKEY CONTRACT

THEKEY Core Governed Run is a deterministic control plane that lets an
autonomous actor (MiMo) make real code changes **without** breaking the
source it works on, and **without** anyone having to babysit it.

## The deal (for contributors)

1. **Original source is immutable.** MiMo never writes to the project it is
   fixing. It works in an isolated `workspaces/<run_id>/` copy. If the run
   is BLOCKED, the original is untouched — guaranteed.
2. **Approval is automatic, never a prompt.** The plan is approved by a
   deterministic local identity bound to the plan's SHA-256. No human is
   asked. (A human-in-the-loop transition exists in the state machine for
   future opt-in, but it is *not* the default.)
3. **Evidence is hash-sealed.** Every artifact carries a SHA-256; a tampered
   artifact makes the run BLOCKED, never silent. An append-only SQLite event
   store records every transition, hash-chained, so the audit log is
   tamper-evident.
4. **The verifier does not trust the implementer.** HY3 (or the built-in
   verifier) reproduces the proof (build + tests) in isolation before the
   `RELEASE_ELIGIBLE` decision. `review_token` proves the decision body was
   produced by the deterministic engine.
5. **No arbitrary shell. No external API.** The coordinator runs a closed
   set of safe operations. No model-generated command is ever executed.
6. **Every run is auditable.** `thekey history verify` + `thekey evidence
   verify` reconstruct integrity from on-disk artifacts, not from memory.

## The actors

| Actor | Role | Writes? |
|--------|------|--------|
| MiMo   | Implementer — writes product code in the isolated workspace | workspace only |
| THEKEY | Orchestrator / control plane — deterministic, no LLM calls | state + evidence |
| HY3    | Independent verifier/auditor — reproduces proof | nothing (read-only) |

## Quick start

    pip install -e ".[dev]"
    python -m thekey demo            # canonical governed demo (auto-approved)
    python -m thekey-mimo          # autonomous MiMo launcher (no prompts)
    python -m thekey history verify

## Why it is safe to automate

Because the gates are *mandatory and deterministic*: a failed build or failed
unit-test blocks the release with a stable exit code. The automation cannot
"decide to skip" a gate — the engine has no branch for that.

See `governance/` for the policy-as-code schemas and `src/thekey/` for the
implementation.
