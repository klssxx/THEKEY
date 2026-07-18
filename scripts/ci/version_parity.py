"""Version parity gate for THEKEY.

Ensures the four sources of truth agree on the current version:
  - thekey/__init__.py  -> __version__  (single source of truth)
  - pyproject.toml      -> [project] version
  - STATUS.md           -> "Release version | X.Y.Z"
  - CHANGELOG.md        -> "## [X.Y.Z] - <date>"

Fails the build if any drift is detected. Aligning everything on the package
version prevents the silent 0.1.0/0.2.0 split we had after the public-preview
prep.

Exit code 0 = PASS, 1 = FAIL.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

VERSION_RE = re.compile(r"^\s*0\.\d+\.\d+\s*$", re.MULTILINE)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def package_version(root: Path = ROOT) -> str | None:
    """Read __version__ from src/thekey/__init__.py."""
    init = root / "src" / "thekey" / "__init__.py"
    if not init.exists():
        return None
    m = re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', _read(init))
    if m:
        return m.group(1)
    # Allow `__version__ = VERSION` form (re-exported from config).
    m = re.search(r'__version__\s*=\s*([A-Za-z_][A-Za-z0-9_]*)', _read(init))
    if m:
        name = m.group(1)
        # Resolve the referenced name within the module text.
        mv = re.search(rf'{name}\s*=\s*["\']([^"\']+)["\']', _read(init))
        if mv:
            return mv.group(1)
        # Fall back to config.VERSION if present.
        cfg = root / "src" / "thekey" / "config.py"
        if cfg.exists():
            mc = re.search(r'VERSION\s*=\s*["\']([^"\']+)["\']', _read(cfg))
            if mc:
                return mc.group(1)
    return None


def pyproject_version(root: Path = ROOT) -> str | None:
    p = root / "pyproject.toml"
    if not p.exists():
        return None
    m = re.search(r'^version\s*=\s*["\']([^"\']+)["\']', _read(p), re.MULTILINE)
    return m.group(1) if m else None


def status_version(root: Path = ROOT) -> str | None:
    p = root / "STATUS.md"
    if not p.exists():
        return None
    m = re.search(r"Release version\s*\|\s*([0-9]+\.[0-9]+\.[0-9]+)", _read(p))
    return m.group(1) if m else None


def changelog_has_version(version: str, root: Path = ROOT) -> bool:
    p = root / "CHANGELOG.md"
    if not p.exists():
        return False
    return re.search(rf"##\s*\[{re.escape(version)}\]", _read(p)) is not None


def check(root: Path = ROOT) -> tuple[bool, list[str]]:
    """Return (ok, problems)."""
    problems: list[str] = []
    versions: dict[str, str | None] = {
        "package (__version__)": package_version(root),
        "pyproject.toml": pyproject_version(root),
    }
    # All declared versions must equal the package version (the source of truth).
    pkg = versions["package (__version__)"]
    if pkg is None:
        problems.append("package __version__ could not be read")
    for label, v in versions.items():
        if v is None:
            problems.append(f"{label} version could not be read")
        elif pkg is not None and v != pkg:
            problems.append(f"{label} version '{v}' != package version '{pkg}'")

    sv = status_version(root)
    if sv is None:
        problems.append("STATUS.md version could not be read")
    elif pkg is not None and sv != pkg:
        problems.append(f"STATUS.md version '{sv}' != package version '{pkg}'")

    if pkg is not None and not changelog_has_version(pkg, root):
        problems.append(f"CHANGELOG.md has no entry for version '{pkg}'")

    return (len(problems) == 0, problems)


def main() -> int:
    ok, problems = check(ROOT)
    print("=" * 60)
    print("THEKEY VERSION PARITY GATE")
    print("=" * 60)
    if ok:
        print("RESULT: PASS")
        print(f"All version sources agree on {package_version(ROOT)}.")
        return 0
    print("RESULT: FAIL")
    for p in problems:
        print(f"  - {p}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
