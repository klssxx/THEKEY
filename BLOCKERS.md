# Blockers

This file records any open blockers encountered during development.

## None (MVP 0.1.0)

As of the 0.1.0 release, there are **no open blockers**. All acceptance
criteria in the bootstrap hyper mega prompt (section 36) are satisfied:

* Installs from a clean environment.
* CLI help works; one-command demo works.
* Run IDs are unique.
* Policies validate; invalid policy blocks.
* Planner does not write; executor changes only the workspace.
* Original demo remains unchanged; verifier does not modify code.
* Build/tests/secret scan/documentation gates are real.
* Decision matches policy and gates; hashes generated.
* Tampering detected; illegal transitions rejected; stale output rejected.
* Arbitrary shell impossible via action IDs.
* Positive and blocked E2E pass; recovery tests pass.
* README is self-sufficient; historical THEKEY unchanged.

If a new blocker appears, add it below with a date, owner, and planned
resolution, and reference a GitHub issue from `docs/github/ISSUE_BACKLOG.md`.
