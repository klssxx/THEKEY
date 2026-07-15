# 01 Demo validation
Date: 2026-07-15 16:59:25
Objective: confirm `python -m thekey demo` reaches RELEASE_ELIGIBLE / 4 gates.
Actions: `python -m thekey demo` in the dev checkout.
Result: rc=0, RELEASE_ELIGIBLE=yes, gates_4=yes.
Decision: PASS
Blockers: none (clean-clone + path-with-spaces already verified manually, see 06).
