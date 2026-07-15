# Contributing guide — THEKEY 0.2.0

> Versión en español: [CONTRIBUTING.md](CONTRIBUTING.md)

Thank you for your interest in THEKEY. This guide is short and serious.

THEKEY applies workflow isolation and deterministic policy authorization; it
does not provide OS-level sandboxing.

## Set up the development environment

```powershell
git clone <URL_DEL_REPOSITORIO>
cd THEKEY
pwsh -NoProfile -File .\scripts\demo.ps1
```

The script creates `.venv`, installs with `pip install -e .`, and runs the demo.
For additional development work you may install the dev dependencies:

```powershell
.venv\Scripts\python -m pip install -e ".[dev]"
```

## Run the tests

```powershell
.venv\Scripts\python -m pytest -q
```

## Run the demo

```powershell
.venv\Scripts\python -m thekey demo
```

## Small changes vs. architectural changes

- **Small change:** bug fix, message improvement, new policy, new verifier
  profile, external read-only adapter.
- **Architectural change:** modification of the transaction core, the state
  machine, the event store, or the mandatory gates. Requires an RFC.

## Propose RFCs

RFCs describe future designs (e.g. Phase C/D, adapter contract). They are filed
as issues labeled `rfc`. An RFC may exist as design without forcing its
implementation in this release.

## Report bugs

Use the bug template on GitHub. Include reproduction steps, environment
(Windows 11, Python, pwsh), and relevant output. For vulnerabilities, follow
[SECURITY.md](SECURITY.md); do not open a public issue.

## Choose issues by label

- `good first issue`: suitable for newcomers.
- `help wanted`: practical extensions.
- `enhancement` / `documentation` / `bug` / `security`: targeted improvements.
- `rfc` / `phase-c` / `phase-d`: future design.
- `adapter`: external read-only adapters.
- `windows` / `ci`: platform- or automation-specific.

## Expected labels

`good first issue`, `help wanted`, `enhancement`, `documentation`, `bug`,
`security`, `rfc`, `phase-c`, `phase-d`, `adapter`, `windows`, `ci`.

## Acceptance criteria for PRs

- Tests pass (`pytest -q`).
- The demo reaches `RELEASE_ELIGIBLE` (or the change does not break it).
- No unverified security or marketing claims are added.
- ES/EN parity is maintained when touching normative documentation.
- The core is not grown unnecessarily in this release.

## ES/EN parity

When modifying normative documentation (README, THREAT_MODEL, CONTRIBUTING) you
must update the corresponding English version. The parity gate verifies this in
CI.

## Prohibitions

- Do not add unverified security or marketing claims.
- Do not expand the core unnecessarily in this release.
- Do not integrate NPSC into the core; NPSC is an optional read-only adapter.
- Do not use the term "auto-approval"; use "deterministic policy authorization".

## When a contribution touches the core and when it should be an external adapter

If the contribution changes the governed transaction flow, the state machine,
the event store, or the mandatory gates, it touches the core and requires an
RFC. If it provides an external provider (e.g. another compiler such as NPSC),
it must live as an external read-only adapter, without coupling to the core.
