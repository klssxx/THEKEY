# OpenAI Build Week 2026 contribution record
This record separates public history from work attributable to the submission
period and the primary Codex thread. Labels: `VERIFIED_PREEXISTING` means dated
pre-cutoff evidence exists; `VERIFIED_BUILD_WEEK` means dated post-cutoff
evidence exists; `VERIFIED_THIS_CODEX_SESSION` means implemented and tested in
this thread on 2026-07-19; `PROVENANCE_UNRESOLVED` means evidence is insufficient.
## History and evidence limits
The owner says THEKEY existed before Build Week, but the public repository was
created on 2026-07-15 and its first visible commit is
`b7b6c32cf3a2621d29ef2c5856db50d116d8dff6`. No visible commit predates the
cutoff. Earlier history is therefore `PROVENANCE_UNRESOLVED` pending dated
backups, Codex exports, or equivalent evidence.
The governed lifecycle, workflow workspaces, policy/gates, evidence store, CLI,
and calculator demo were already present at the session baseline
`3a8456416ed9ae9183840585b488cec04e9a069d`; their original date remains
`PROVENANCE_UNRESOLVED`. The baseline, critical hashes, pack verification, RED
run, tests, caller analysis, rollback, and final manifest live under
`evidence/phase-b/RBAC-01-v2/`. These prove this diff, not undocumented history.
## `VERIFIED_THIS_CODEX_SESSION`
- Strict Pydantic contracts for ActionContext, CHECKMATE and sovereign
  receipts, policy decisions, and governed transactions.
- Persisted double receipts bound to one run, transaction, plan,
  authorization, policy version, and policy bundle hash.
- Fail-closed physical guard restricted to `Role.EXECUTOR`, plus deterministic
  `PolicyEngine.authorize_action()` and production adapter.
- Five of five live dispatch callers rebased with persisted context.
- Verified state load, authorization provenance, security tests and schemas.
- Judge Mode: temporary Git repository, workflow isolation, one-handler ALLOW,
  zero-handler adversarial DENY, four gates, JSON evidence, and a Windows path
  containing spaces.
- Bilingual README, contribution record, Devpost draft, and video script.
Codex performed inspection, adversarial design, implementation, AST analysis,
RED→GREEN testing, regression, rollback preparation, and documentation. moli
retained authority, scope, LIVE_E, push, merge, release, video, and submission
decisions. Exact files, hashes, commands, and diff statistics are in the final
manifest.
## Pending evidence and limitations
- Primary `/feedback` Session ID: `PENDING_REAL_FEEDBACK_SESSION_ID`.
- GPT-5.6 evidence: `PENDING_SESSION_METADATA_VERIFICATION`; no runtime
  integration is claimed.
- YouTube URL: `PENDING_PUBLIC_YOUTUBE_URL`.
- Workflow isolation is not an OS sandbox. The local grant is locked to the
  canonical demo path/hash and isolated workspace with production reuse denied;
  it is not a cryptographic human signature. Secret scanning is limited;
  Windows 11 is the verified Judge Mode platform.
