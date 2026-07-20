# OpenAI Build Week 2026 contribution record
This record separates public history from work attributable to the submission
period and the primary Codex thread. `CLAIM_RECORDED` is an owner statement,
`PENDING_EVIDENCE_IMPORT` is not yet evidence, `VERIFIED_GIT_OBJECT` is an
inspectable Git object, and `VERIFIED_THIS_CODEX_SESSION` means implemented and
tested in this thread on 2026-07-19.
## History and evidence limits
THEKEY is explicitly declared a preexisting project. That pre-public statement
is `CLAIM_RECORDED`. The accessible public Git history begins with commit
`b7b6c32cf3a2621d29ef2c5856db50d116d8dff6`, dated 2026-07-15, after the
cutoff. Any earlier chat exports, backups, or snapshots not actually imported
remain `PENDING_EVIDENCE_IMPORT`.
The governed lifecycle, workflow workspaces, policy/gates, evidence store, CLI,
and calculator demo were already present at the session baseline
`3a8456416ed9ae9183840585b488cec04e9a069d`. The baseline, critical hashes,
pack verification, RED run, tests, caller analysis, rollback, and Phase-B
manifest live under `evidence/phase-b/RBAC-01-v2/`. These prove the recorded
diff, not undocumented history. See the
[provenance declaration](docs/build-week/PRE_PUBLIC_PROVENANCE.md) and
[verifiable delta](docs/build-week/BUILD_WEEK_DELTA.md).
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
- Windows 10/11 x64 portable candidate with a chess-king launcher, user-owned
  five-second cinematic, bilingual clickable controls, and bundled runtime.
- Read-only intake and isolated verification for recognized Python, Node.js,
  Go, Rust, .NET, and Maven projects:
  CHECKMATE, scoped PolicyEngine authorization, explicit trusted-test consent,
  fixed adapter build/test commands, bounded secret scan, documentation, and unchanged-source
  evidence. Generated build trees are excluded and long paths use a short
  per-user runtime root.
- Redacted actionable diagnostics plus bounded single-point repair synthesis.
  A repair is accepted only after every isolated gate passes; exact-byte source
  application requires separate consent, a fresh baseline check, out-of-tree
  backup, post-apply verification, and automatic rollback on failure.
- Bilingual README and judge quickstart, contribution record, Devpost draft,
  evidence verifier, and video package.
Codex performed inspection, adversarial design, implementation, AST analysis,
RED→GREEN testing, regression, rollback preparation, and documentation. The
user retained authority, scope, LIVE_E, push, merge, release, video, and submission
decisions. Exact files, hashes, commands, and diff statistics are in the final
manifest.
## Evidence status and limitations
- Primary `/feedback` Session ID:
  `019f79f2-6a7e-74f0-b1fa-d65335b29a7c`.
- Sanitized GPT-5.6/Codex record:
  [docs/build-week/CODEX_SESSION_EVIDENCE.md](docs/build-week/CODEX_SESSION_EVIDENCE.md).
  No runtime GPT-5.6 integration is claimed.
- Public provenance index:
  [evidence/build-week/provenance/PUBLIC_EVIDENCE_INDEX.json](evidence/build-week/provenance/PUBLIC_EVIDENCE_INDEX.json).
- YouTube URL: `PENDING_PUBLIC_YOUTUBE_URL`.
- Workflow isolation is not an OS sandbox. The local grant is locked to the
  canonical demo path/hash and isolated workspace with production reuse denied;
  it is not a cryptographic human signature. Secret scanning is limited;
  Windows 11 is the verified Judge Mode platform.
- The portable surface targets Windows 10/11 x64 and is exercised on Windows
  11. Selected tests are trusted code; no dependency installation is attempted,
  and unsupported or insufficiently evidenced projects are not called verified.
- Automatic repair never changes tests or installs dependencies. Failures
  outside its closed candidate set remain blocked and diagnosed; arbitrary
  repair is not claimed.
