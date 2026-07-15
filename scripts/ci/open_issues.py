"""Open the 8 THEKEY backlog issues on GitHub from release_evidence/backlog/.

Reads each 01..08_*.md which has YAML-ish front matter:
  ---
  title: "..."
  type: good-first-issue|help-wanted|rfc
  labels: [a, b]
  ---
  <body...>

Requires `gh` authenticated (gh auth login / GH_TOKEN). Does NOT push code.
"""
from __future__ import annotations
import argparse, pathlib, re, subprocess, sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
BACKLOG = ROOT / "release_evidence" / "backlog"

LABELS_BY_TYPE = {
    "good-first-issue": ["good first issue", "documentation", "ci", "windows"],
    "help-wanted": ["help wanted", "enhancement"],
    "rfc": ["rfc", "phase-c"],
}


def parse(path: pathlib.Path):
    text = path.read_text(encoding="utf-8")
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", text, re.DOTALL)
    if not m:
        # fallback: first line as title
        title = text.splitlines()[0].lstrip("# ").strip()
        return title, ["enhancement"], text
    fm, body = m.group(1), m.group(2)
    title = re.search(r"title:\s*\"?(.*?)\"?\s*$", fm, re.MULTILINE)
    title = title.group(1) if title else path.stem
    typ = re.search(r"type:\s*(\S+)", fm)
    typ = typ.group(1) if typ else "enhancement"
    labels = LABELS_BY_TYPE.get(typ, ["enhancement"])
    # ensure type label present
    if typ not in labels and typ not in ("rfc",):
        labels = [typ] + labels
    return title.strip(), labels, body.strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True, help="OWNER/THEKEY")
    ap.add_argument("--dry-run", action="store_true", help="print commands only")
    args = ap.parse_args()

    files = sorted(BACKLOG.glob("*.md"))
    if not files:
        print("No backlog files found in", BACKLOG)
        sys.exit(1)

    for f in files:
        title, labels, body = parse(f)
        cmd = [
            "gh", "issue", "create",
            "--repo", args.repo,
            "--title", title,
            "--body", body,
            "--label", ",".join(labels),
        ]
        if args.dry_run:
            print("WOULD CREATE:", title, "| labels:", labels)
            continue
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode != 0:
            print(f"FAILED {f.name}: {r.stderr.strip()}")
            sys.exit(r.returncode)
        print(f"created: {title} -> {r.stdout.strip()}")


if __name__ == "__main__":
    main()
