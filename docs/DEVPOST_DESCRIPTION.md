# Devpost submission draft — English

This is a repository-side draft, not evidence of submission. The controlling
requirements are the [OpenAI Build Week Official Rules](https://openai.devpost.com/rules)
and [official FAQ](https://openai.devpost.com/details/faqs).

## Title

THEKEY — The King of Checkmate

## Tagline

Governed coding-agent operations with isolated workspaces, deterministic gates
and auditable evidence.

## Track

Developer Tools

## What THEKEY does

Coding agents accelerate delivery, but teams still need to know which plan was
authorized, what actually ran, what changed, and why a result was allowed.
THEKEY is a native Windows developer tool that turns a local coding-agent
operation into a governed transaction. It combines explicit authorization,
isolated workspaces, deterministic gates and reviewable JSON evidence without
presenting an uncomputed result as safe.

A developer selects a supported local project. THEKEY profiles it read-only,
then requires explicit consent before trusted project tests may run in an
isolated copy. Verification applies deterministic compile, test, secret-scan
and documentation gates and persists the evidence. Repair searches only a
closed, conservative candidate set in the isolated workspace; it can offer an
apply action only after those gates pass. Applying verified bytes requires a
second consent, a fresh source check, an out-of-tree backup and post-apply
re-verification. Stale, unsupported, failed or unauthorized work fails closed.

Judge Mode packages a deterministic sample and exercises the governed boundary
without touching a user project or requiring an API key. The result includes
the decision, invoked-handler count, gates, hashes and receipts so a judge can
inspect the claim rather than trust a success label.

## Why it matters

The primary audience is developer teams adopting coding agents on local
projects. Existing assistants can propose or perform a change; THEKEY focuses
on the control and evidence around that operation. Its differentiator is the
binding between plan identity, scoped consent, policy decision, execution
boundary, deterministic verification and durable evidence.

## OpenAI Build Week work and use of Codex with GPT-5.6

THEKEY is explicitly a pre-existing project. Only the extension documented in
`docs/build-week/BUILD_WEEK_DELTA.md` is presented as new Build Week work. The
baseline already contained the governed lifecycle, workflow workspaces,
evidence store, CLI and canonical demo.

In the primary Build Week thread, Codex with GPT-5.6 was used meaningfully to
inspect the existing callers, design and implement plan-bound receipts and a
fail-closed physical-operation guard, migrate five physical callers, create
adversarial tests, harden the non-reusable Judge Mode grant, run RED-to-GREEN
and full-regression cycles, verify rollback and clean-clone reproduction, and
prepare judge evidence. Product authority, scope and publication decisions
remained with the user. GPT-5.6 is development and validation tooling for this
entry, not a hidden runtime dependency. The organizer-verifiable primary
`/feedback` Session ID and sanitized evidence are documented in
`docs/build-week/CODEX_SESSION_EVIDENCE.md`.

## Technology

Python 3.11+, Pydantic v2, JSON Schema, pytest, SQLite, Git, native WPF/C#,
PowerShell and PyInstaller. The portable Judge Mode requires no OpenAI API key,
paid service, account, network installation or private data.

## How judges can test it

On Windows 10/11 x64, extract the submitted portable ZIP, launch `THEKEY.exe`
and select **Demo para jueces / Judge demo**. The deterministic scenario should
finish within the short judging path and expose its real decision, gates and
receipts. No source rebuild or developer toolchain is required.

For the project flow, select the included repairable Python sample, choose the
repair action, approve execution of that trusted sample’s tests, review the
candidate and separately authorize application. A successful run must end in
`REPAIRED_AND_VERIFIED`; any failed mandatory gate must block that verdict. The
original sample used by Judge Mode remains unchanged.

The final submission must point to the exact audited repository commit and test
build. If the repository is private, it must be shared with
`testing@devpost.com` and `build-week-event@openai.com` as required by the
Official Rules.

## Challenges

The hardest parts were keeping authorization and evidence bound to the same
plan, preventing the deterministic demo grant from becoming reusable in
production, preserving source files during verification and repair preview,
and reproducing a cinematic Windows reference with real DPI-aware controls
instead of a screenshot-shaped interface.

## Accomplishments

- A non-trivial governed execution boundary used by five physical callers.
- Bound policy and execution receipts with fail-closed mismatch handling.
- Isolated verification and conservative repair with explicit two-stage
  consent, backup, re-test and rollback behavior.
- A native Windows product flow, portable judge artifact and deterministic
  evidence path.
- Adversarial, regression, packaging, secret-scan and visual-comparison
  evidence retained in the repository artifacts.

## Limitations and next steps

Workflow isolation is not an operating-system sandbox. The built-in secret scan
is intentionally limited, third-party project toolchains are not bundled, and
automatic repair covers only documented conservative candidates. Unsupported
or unverifiable inputs do not receive a success verdict. Next steps are stronger
process isolation, more adapters and a richer evidence-review experience after
those capabilities are implemented and tested.

## Submission-owner fields still required

- Final repository URL and exact commit SHA.
- Public or explicitly shared judge access and final test-build URL.
- Primary `/feedback` Codex Session ID copied from the verified evidence.
- Final approved screenshots.
- Public YouTube demo URL — **pending the user; video production is intentionally
  outside this preparation task**.
- Devpost submission confirmation before the official deadline.
