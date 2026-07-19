# Build Week video shot list

Target runtime: **2:48**. Acceptable range: **2:40–2:55**. Never exceed three
minutes.

| Shot | Time | Visual | Proof or narration anchor |
| --- | --- | --- | --- |
| 1 | 0:00–0:18 | `THEKEY`<br>`THE KING OF CHECKMATE`<br><br>`Governed Codex Transactions for Coding Agents`, then `README.en.md` | Exact canonical title card, followed by the governance problem: plan, authority, physical execution, and release evidence. |
| 2 | 0:18–0:40 | README authorization flow | THEKEY core → THE KING phase/context orchestration without self-approval → CHECKMATE risk verdict without physical writes → scoped human authority → PolicyEngine → physical guard → one declared handler → gates → evidence. |
| 3 | 0:40–1:32 | PowerShell 7 running `pwsh -NoProfile -File .\scripts\build-week-demo.ps1` | Real demo. Hold on `ALLOW: APPLIED, handlers=1`, `DENY: ROLE_NOT_ALLOWED, handlers=0`, `GATES: 4/4 PASS`, and `DECISION: RELEASE_ELIGIBLE`. |
| 4 | 1:32–2:02 | Safe projection of the generated JSON evidence | Show the shared run, transaction, plan hash, policy bundle hash, ALLOW/DENY counts, unchanged hash, gates, and decision. Hide absolute path fields. |
| 5 | 2:02–2:30 | `git rev-parse HEAD`, `BUILD_WEEK_DELTA.md`, then `CODEX_SESSION_EVIDENCE.md` | Bind the video to the exact final candidate. Distinguish the declared preexisting project from the verified post-baseline delta. Explain how Codex with GPT-5.6 helped; do not imply runtime use. |
| 6 | 2:30–2:48 | README limitations, then the exact opening title card | Workflow isolation is not an OS sandbox; local grant is not a cryptographic signature; scan and action set are bounded. End on the canonical brand and tagline. |

## Screen preparation

- Use a short clean-clone path so the demo is not exposed to the documented
  Windows long-path limitation.
- Confirm `git rev-parse HEAD` equals the final candidate handoff. Pre-open the
  README, Build Week delta, sanitized Codex session record, and generated
  evidence projection in presentation order.
- Use `THEKEY — THE KING OF CHECKMATE` as the one-line public name. The commit
  SHA remains a technical version identifier and must never replace the title.
- In the evidence shot, exclude `run_path` and `workspace_path`; they can reveal
  a local directory or user name.
- Keep the terminal final summary visible long enough to read all four outcome
  lines without pausing the video.
- Show the real run continuously. Cuts may change windows between sections but
  must not make a prerecorded or edited result look live.

## Safe evidence projection

After the demo, this PowerShell snippet prints only the fields needed on screen:

```powershell
$EvidenceFile = Get-ChildItem .thekey\judge-mode -Recurse `
  -Filter judge-mode-evidence.json |
  Sort-Object LastWriteTime -Descending |
  Select-Object -First 1
$Evidence = Get-Content -Raw -LiteralPath $EvidenceFile.FullName |
  ConvertFrom-Json
$Evidence |
  Select-Object run_id, transaction_id, plan_sha256, policy_bundle_hash, `
    allow, deny, source, receipt_binding, production_reuse, gates, `
    release_decision |
  ConvertTo-Json -Depth 5
```
