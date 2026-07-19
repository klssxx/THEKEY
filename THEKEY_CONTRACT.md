# THEKEY CONTRACT

**THEKEY — THE KING OF CHECKMATE**

**Governed Codex Transactions for Coding Agents**

`THEKEY Core Governed Run` is a legacy technical label for the deterministic
control-plane flow; it is not the current public brand. That flow lets an
autonomous actor (MiMo) make real code changes **without** breaking the
source it works on, and **without** anyone having to babysit it.

THEKEY is the product and governed-transaction core. THE KING orchestrates
phases and context, but cannot approve itself or bypass the PolicyEngine.
CHECKMATE performs adversarial pre-execution review: it analyzes risk and emits
a verdict, but performs no physical writes. Codex with GPT-5.6 is the agent used
to analyze, build, test, and improve the project.

## The deal (for contributors)

1. **Original source is immutable.** MiMo never writes to the project it is
   fixing. It works in an isolated `workspaces/<run_id>/` copy. If the run
   is BLOCKED, the original is untouched — guaranteed.
2. **Plan progression may be automated; authority is never implicit.** The
   legacy deterministic flow can bind a local approver identity to the plan's
   SHA-256 without an interactive prompt. This is not THE KING self-approval.
   Physical execution requires a CHECKMATE verdict, scoped authority, and
   PolicyEngine authorization before handler resolution.
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
| THEKEY | Product and governed-transaction core | state + evidence |
| THE KING | Orchestrates phases and context; cannot self-approve or bypass the PolicyEngine | orchestration records only |
| CHECKMATE | Adversarial pre-execution review; analyzes risk and emits a verdict | no physical writes |
| HY3    | Independent verifier/auditor — reproduces proof | nothing (read-only) |
| Codex with GPT-5.6 | Development agent used to analyze, build, test, and improve the project | development workspace only |

## Quick start

    pip install -e ".[dev]"
    python -m thekey demo          # deterministic plan progression; governed dispatch
    python -m thekey-mimo          # autonomous MiMo launcher (no prompts)
    python -m thekey history verify

## Why it is safe to automate

Because the gates are *mandatory and deterministic*: a failed build or failed
unit-test blocks the release with a stable exit code. The automation cannot
"decide to skip" a gate — the engine has no branch for that.

See `governance/` for the policy-as-code schemas and `src/thekey/` for the
implementation.
