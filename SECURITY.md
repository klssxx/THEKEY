# Security

THEKEY Core is a governance engine, not a security sandbox.

## Vulnerability reporting

Open a GitHub issue marked `security` with a minimal reproduction. Do not
include live secrets. For sensitive reports, contact the maintainers via the
repository's security policy.

## Secret scan scope

The `SCAN_SECRETS` gate runs a **limited, honest** regex scan over the isolated
workspace (paths + patterns defined in `governance/policies/local-python-demo.yaml`).
It flags common secret shapes (AWS keys, OpenAI-style keys, long hex, and
assignment patterns like `api_key = ...`).

## Secret scan limitations

* It is a **regex** scan — it will miss obfuscated, encoded, or novel secret
  formats. Absence of a finding is **not** proof of absence of secrets.
* It cannot inspect encrypted stores, external vaults, or environment variables
  outside the scanned workspace.
* It is not a substitute for a dedicated secret-management platform.

## No strong sandbox

The MVP does not provide OS-level isolation (no container, no seccomp, no MAC).
Execution happens in a normal process with filesystem isolation limited to the
workspace root. Do **not** run untrusted code through the executor on a
sensitive host.

## No arbitrary shell

Model action IDs are a **closed set** (`REPLACE_EXACT_TEXT`, `RUN_UNIT_TESTS`,
etc.). There is no free-form shell string, no arbitrary command parameters, and
no path outside the allowed roots. Arbitrary command execution through the model
is impossible by construction.

## Do not use on sensitive repositories without review

Because there is no strong sandbox and the approval identity is simplified
(local, not cryptographic), do not point THEKEY Core at repositories containing
real credentials or production code without human review and additional
isolation.
