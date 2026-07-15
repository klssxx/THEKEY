# Roadmap

Prioritized post-MVP work. See `docs/github/ISSUE_BACKLOG.md` for the issue
breakdown.

## P0 (already in MVP where applicable)
* OSS scaffold and scope contract — **done in 0.1.0**
* Persistent run model — **done**
* Governed state machine — **done**
* Policy as code — **done**
* Stateless HY3 context builder — **done (deterministic roles in 0.1.0; HY3 plug-in later)**
* Restricted output validator — **done**
* Role separation — **done**
* Workspace isolation and path safety — **done**
* Closed action registry — **done**
* Evidence and hash verification — **done**

## Near term (post-0.1.0)
* **Strong identities** — replace the simplified local approver with signed,
  cryptographic identities.
* **Owners** — assign accountable owners per role.
* **Exceptions** — a governed exception/override path with full audit.
* **Full RFC process** — propose/comment/ratify policy changes.
* **Evidence signing** — sign evidence records so they cannot be silently edited.
* **Concurrency** — multiple in-flight runs with isolated state.

## Later
* **More languages** — Go, Rust, JS demo apps.
* **Optional Hermes/HY3 adapters** — plug the stateless HY3 operator behind the
  same context builder and validator (control plane unchanged).
* **Visual gates** — a dashboard rendering gates/decisions.
* **Plugins** — third-party gates, actions, and policies loaded safely.
* **Remote evidence storage** — immutable off-box evidence ledger.
* **Optional smoke-test profile** — `LAUNCH_SMOKE_TEST` for runtime apps.
* **Additional project types** — beyond single-package Python.
