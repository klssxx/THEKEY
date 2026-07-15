# Threat model — THEKEY 0.2.0

> Versión en español: [THREAT_MODEL.md](THREAT_MODEL.md)

This document is honest and technical; it makes no absolute claims about
THEKEY's security. THEKEY is a small core for governed Git transactions.

## Realistic security objectives

- Make an automated code change **reproducible and auditable**.
- Never modify the original source (workflow isolation).
- Make a failed mandatory gate stop the release deterministically.
- Let the evidence detect later tampering.

## Protected assets

- The original source of the project under change (read-only for THEKEY).
- The per-run evidence artifacts (`runs/<RUN_ID>/`).
- The hash-chained event store (`.thekey/`).
- The gate policy (`governance/policies/`).

## Trust boundaries

- **Inside:** the THEKEY process, the isolated workspace, the local policy.
- **Outside:** the host system, other processes, the network, the user running
  the demo, external providers (e.g. NPSC as an adapter).

THEKEY trusts that the host system is not compromised. That boundary is out of
its scope.

## Relevant attack surface

- Tampering with the policy or run parameters.
- Writing outside the isolated workspace (path escape).
- Altering evidence artifacts after the run.
- Injection through the read-only adapter (untrusted input).
- Environment misconfiguration (Python, permissions, `PATH`).

## Plausible threats

- **T1 — Write outside the workspace:** a path defect could write outside the
  isolated space. Current mitigation: the workspace manager authorizes paths
  relative to the workspace; the original source is never touched by design.
- **T2 — Evidence forgery:** an actor with disk access could rewrite
  artifacts. Current mitigation: SHA-256 hashes and a hash-chained event
  store; verification (`thekey evidence verify`) detects mismatches. It is not
  proof against an attacker with full disk control.
- **T3 — Weak policy:** a misconfigured policy could relax gates. Current
  mitigation: gates are declared explicitly and a mandatory gate is not
  offset. It still depends on the loaded policy.
- **T4 — Untrusted input via adapter:** a read-only adapter could receive
  manipulated data. Current mitigation: the adapter is read-only and does not
  execute the provider; input validation is the consumer's responsibility.

## Present mitigations

- Workflow isolation (controlled workspace).
- Deterministic policy authorization (plan hash, no interactive approval).
- Append-only, hash-chained event store.
- SHA-256 hashes of principal artifacts.
- Limited, honest secret scan over the workspace.
- Reproducible verification of build + tests in isolation.

## Mitigations not yet present

- Cryptographic human identities.
- Process isolation via container or VM (not yet implemented).
- Multi-developer concurrency with locking.
- Exhaustive secret scanning (not a replacement for dedicated tools).
- Evidence signing with an external key.

## Explicit limitations

THEKEY **does not provide OS-level sandboxing**. The isolation is **workflow
isolation**: the code runs on the same host as the user. It must not be
presented as an OS security boundary.

## Relationship between workflow isolation and absence of OS sandbox

Workflow isolation protects the **original source** and bounds **where changes
are written**. It does not isolate the process from the operating system: a
compromised workspace shares the privileges of the user running THEKEY. Anyone
needing OS isolation should run THEKEY inside their own sandbox (container, VM,
restricted account).

## Evidence integrity and its assumptions

Integrity relies on:
- the event store and artifacts not being altered after the run;
- the hashes being computed over the real content;
- the applied policy being the expected one.

If an attacker controls the disk or the policy, the evidence can be
regenerated coherently and detection fails. Therefore the evidence is
**auditable**, not **tamper-proof**.

## Threats from the optional read-only adapter

NPSC and other external adapters are read-only and optional. They are not part
of the core. One threat is a poorly written adapter injecting data into the
core's input. Mitigation: the adapter does not execute the provider and the
core validates what it consumes. NPSC is not integrated into the core.

## Misconfiguration risks

- Running THEKEY with unnecessary administrator privileges.
- Using a policy that omits mandatory gates.
- Skipping the secret scan before releasing.
- Mixing run state (`.thekey/`, `runs/`) into the project's version control.

## Residual risks

- Dependence on host-system integrity.
- Simplified local authorization identity.
- Limited secret-scan coverage.
- No guarantee against an attacker with full environment control.

## Out of scope

- Process isolation at the OS level via container or VM.
- Enterprise authorization.
- Remote agent execution.
- Integration of NPSC into the core.

## References

- [SECURITY.md](SECURITY.md)
- [README.en.md](README.en.md)
