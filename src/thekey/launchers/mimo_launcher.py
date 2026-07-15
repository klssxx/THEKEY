"""THEKEY MiMo autonomous launcher (task 6/7).

Runs the full governed pipeline end-to-end with 100% automated approval and
the MiMo actor profile. No prompts, no human input. Exits 0 on
RELEASE_ELIGIBLE, non-zero on BLOCKED or error (stable exit codes).

Usage:
    python -m thekey.launchers.mimo_launcher            # canonical demo
    python -m thekey.launchers.mimo_launcher --title "..." --description "..."
    thekey-mimo                                            # if installed

Guardas (task 6): the launcher refuses to run outside an allowed root and
refuses if the protected historical THEKEY path would be touched. It also
captures evidence (the event store + artifact hashes are written by the
coordinator itself).
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from ..config import (
    REAL_ROOT,
    THEKEY_DIR,
)
from ..main import RunCoordinator
from .. import mimo_profile as mimo


# Paths THEKEY must NEVER mutate (read-only historical framework).
PROTECTED_ROOTS = [
    Path(r"E:\KLSX PROYECTS\KlsxMaker\TheKey\Thekey"),
    Path(r"E:\KLSX PROYECTS\KlsxMaker\TheKeyCore_Governed_OSS"),
]


def _guard_allowed_root() -> None:
    """Defensive guard: refuse to run if the runtime root sits inside a
    protected historical path. THEKEY only ever writes under its own repo."""
    rt = REAL_ROOT.resolve()
    for prot in PROTECTED_ROOTS:
        try:
            prot_res = prot.resolve()
        except Exception:
            continue
        if rt == prot_res or str(rt).startswith(str(prot_res) + os.sep):
            sys.stderr.write(
                f"[GUARD] refusing to run: runtime root {rt} is inside a "
                f"protected path {prot_res}. THEKEY never mutates the historical framework.\n"
            )
            raise SystemExit(8)  # UNAUTHORIZED_PATH


def run(title: str, description: str) -> int:
    _guard_allowed_root()
    coord = RunCoordinator()
    coord.create(title or "MiMo autonomous governed run", description=description)
    coord.baseline()
    coord.plan()
    coord.approve_plan()  # 100% automated
    coord.execute()
    results = coord.verify()
    decision = coord.decide()
    coord.close()

    out = {
        "run_id": coord.run.run_id,
        "actor_profile": mimo.ACTOR_PROFILE,
        "state": coord.sm.load().run_state,
        "decision": decision.decision,
        "gates_passed": sum(r.passed for r in results),
        "gates_total": len(results),
        "review_token": decision.review_token,
        "run_path": str(coord.run.dir),
        "evidence_store": str(THEKEY_DIR / "events.db"),
    }
    print(json.dumps(out, indent=2, ensure_ascii=False))

    if decision.decision != "RELEASE_ELIGIBLE":
        return 5  # GATE_FAILURE exit code
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="thekey-mimo", description="THEKEY MiMo autonomous launcher")
    p.add_argument("--title", default="MiMo autonomous governed run")
    p.add_argument("--description", default="Autonomous fix of calculator.add")
    args = p.parse_args(argv)
    try:
        return run(args.title, args.description)
    except SystemExit:
        raise
    except Exception as err:  # pragma: no cover - last resort
        sys.stderr.write(f"error: {type(err).__name__}: {err}\n")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
