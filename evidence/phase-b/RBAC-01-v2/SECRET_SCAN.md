# Secret scan — FASE-B-v2 candidate

Generated at `2026-07-19T14:36:16.059Z`.

## Working candidate

- Files scanned from `git ls-files -co --exclude-standard`: 204.
- OpenAI key patterns: 0.
- GitHub token patterns: 0.
- AWS access-key patterns: 0.
- Private-key headers: 0.
- Slack token patterns: 0.
- Generic quoted secret assignments: 1, the intentional synthetic fixture in
  `tests/unit/test_secret_entropy.py:19`.
- Entropy scan over candidate files excluding ignored `.thekey` runtime: PASS,
  zero findings.

## Git history

- OpenAI, GitHub, AWS, private-key and Slack patterns: 0 commits / 0 paths.
- Generic quoted assignment value: one commit, only
  `tests/unit/test_secret_entropy.py` (intentional scanner fixture).

An unscoped entropy invocation over the entire developer directory also scanned
ignored `.thekey` dependencies and generated test fixtures, producing 21
non-candidate findings. Those ignored runtime files are excluded from the
candidate result above; no finding was silently discarded from a commit-bound
file.
