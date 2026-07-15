# Security Policy — THEKEY 0.2.0

THEKEY is a governance engine for coding agents. It provides **workflow
isolation**, not an OS-level sandbox. Read [THREAT_MODEL.md](THREAT_MODEL.md)
for the full analysis.

## How to report a vulnerability

Use GitHub **private security advisories** if available in the repository, or
open a GitHub issue labeled `security` with a minimal reproduction. Do not
include live secrets, credentials, or exploit code in public issues.

There is no separate email or bug-bounty program. The repository's security
advisory / `security` issue is the real, safest available channel.

## What kinds of reports are accepted

- Bypasses of workflow isolation (writes outside the controlled workspace).
- Evidence tampering that escapes `thekey evidence verify`.
- Secret leakage through the demo, the gates, or the adapters.
- Determinism breaks in the policy authorization or gate evaluation.
- Injection through the optional read-only adapters (e.g. NPSC).

## Responsible disclosure

Please give the maintainers a reasonable time to triage and release a fix before
public disclosure. For a public preview with a single maintainer, a window of
**at least 7 days** is appreciated, but this is a request, not a contractual
SLA.

## Response times

No fixed response-time SLA is promised for this public preview. Reports are
reviewed on a best-effort basis.

## Limitations of the security model

- **No OS-level sandbox.** Code runs as a normal process; workspace isolation
  bounds *where* changes are written, not what the process can do on the host.
- **Simplified local authorization identity.** Plan authorization is
  deterministic and hash-bound, not backed by cryptographic human identities.
- **Limited secret scanning.** The `SCAN_SECRETS` gate is a regex scan over the
  workspace. It will miss obfuscated, encoded, or novel secret formats. Absence
  of a finding is not proof of absence of secrets.
- **No strong process isolation**, no container, no seccomp, no MAC by default.
- **External adapters are optional and read-only**; a poorly written adapter can
  still feed untrusted input into the core.

## Secret scanning in this repository

This repo ships a lightweight regex secret scan as a CI step (verifiable
equivalent). For a maintained control, **enable GitHub Secret Scanning and Push
Protection** in the private repository settings before switching to public.
That is the recommended real mechanism; it is not active until enabled by the
repository owner. See the publication audit for the exact enablement checklist.

## Do not run untrusted code on a sensitive host

Because there is no strong sandbox and the authorization identity is simplified,
do not point THEKEY at repositories containing real credentials or production
code without additional isolation (container, VM, restricted account) and human
review.

## References

- [THREAT_MODEL.md](THREAT_MODEL.md) / [THREAT_MODEL.en.md](THREAT_MODEL.en.md)
- [README.md](README.md) / [README.en.md](README.en.md)
