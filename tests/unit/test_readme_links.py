from __future__ import annotations

import re
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[2]
LOCAL_LINK = re.compile(r"(?<!!)\[[^]]+\]\(([^)]+)\)")


def test_candidate_document_relative_links_resolve():
    missing: list[str] = []
    documents = [
        ROOT / "README.md",
        ROOT / "README.en.md",
        ROOT / "BUILD_WEEK_CONTRIBUTION.md",
        ROOT / "BUILD_WEEK_CONTRIBUTION.es.md",
        *(ROOT / "docs/build-week").glob("*.md"),
    ]
    for document in documents:
        text = document.read_text(encoding="utf-8")
        for raw_target in LOCAL_LINK.findall(text):
            target = raw_target.strip().strip("<>")
            if target.startswith(("http://", "https://", "mailto:", "#")):
                continue
            relative = unquote(target.split("#", 1)[0])
            if relative and not (document.parent / relative).exists():
                missing.append(f"{document.relative_to(ROOT)}: {target}")

    assert missing == []
