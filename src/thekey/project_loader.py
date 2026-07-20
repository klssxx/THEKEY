"""Read-only project intake / Mission Loader (section 9/10).

The loader INSPECTS a local Python project directory without modifying it. It:
  * resolves and validates the source path (directory, not inside runs/workspaces/.thekey),
  * rejects unsafe symlinks / junctions / reparse points (does not follow them),
  * records Git status when present (without modifying),
  * excludes generated directories,
  * bounds scan depth / file count / content size,
  * identifies binary files without loading them into HY3,
  * produces a deterministic source baseline (tree hash) and canonical hashes.

It NEVER sends the whole project to HY3 and NEVER writes to the source.
"""

from __future__ import annotations

import hashlib
import os
import stat
from pathlib import Path

from .config import REAL_ROOT, RUNS_DIR, THEKEY_DIR, WORKSPACES_DIR
from .errors import InvalidArgumentsError
from .project_models import ProjectInspection, compute_tree_hash

# Default excluded directories (section 9).
DEFAULT_EXCLUDED_DIRS = {
    ".git",
    ".venv",
    "venv",
    "env",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".tox",
    ".nox",
    "build",
    "dist",
    "bin",
    "obj",
    "publish",
    "artifacts",
    "site-packages",
    "node_modules",
    "runs",
    "workspaces",
    ".thekey",
}

# Protected framework roots that must never be treated as a user source project.
_PROTECTED_PREFIXES = [
    str(REAL_ROOT.resolve()),
]


def default_scan_limits() -> dict:
    return {
        "max_depth": 12,
        "max_files": 10000,
        "max_file_size_bytes_for_content_read": 1_048_576,
        "max_total_content_bytes_for_model_context": 200_000,
        "follow_symlinks": False,
    }


def _is_reparse_point(path: Path) -> bool:
    try:
        st = os.lstat(path)
    except OSError:
        return False
    if hasattr(st, "st_file_attributes"):
        return bool(st.st_file_attributes & stat.FILE_ATTRIBUTE_REPARSE_POINT)
    return False


def _is_symlink(path: Path) -> bool:
    try:
        return path.is_symlink()
    except OSError:
        return False


def _path_is_inside(path: Path, root: Path) -> bool:
    try:
        Path(path).resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


class ProjectLoader:
    """Read-only inspector for a local Python project."""

    def __init__(
        self,
        scan_limits: dict | None = None,
        excluded_dirs: set[str] | None = None,
    ):
        self.scan_limits = scan_limits or default_scan_limits()
        self.excluded_dirs = set(excluded_dirs or DEFAULT_EXCLUDED_DIRS)

    # -- validation -----------------------------------------------------
    def resolve_source(self, source: str | Path) -> Path:
        """Resolve, validate, and authorize the source path (read-only)."""
        src = Path(source).expanduser()
        if not src.exists():
            raise InvalidArgumentsError(f"Source path does not exist: {source}")
        if not src.is_dir():
            raise InvalidArgumentsError(f"Source is not a directory: {source}")
        src = src.resolve()

        # Reject source inside the engine's own runtime dirs.
        for bad in (RUNS_DIR.resolve(), WORKSPACES_DIR.resolve(), THEKEY_DIR.resolve()):
            if _path_is_inside(src, bad) or src == bad:
                raise InvalidArgumentsError(
                    f"Source must not be inside runtime dir: {source}"
                )
        # Reject source equal to or inside the protected repo root itself being
        # used as a mission target (the engine dir is not a user project).
        if _path_is_inside(src, REAL_ROOT.resolve()):
            rel = src.relative_to(REAL_ROOT.resolve())
            top = str(rel).split(os.sep)[0]
            # Engine's own protected source/governance trees are never a user
            # project. Sample projects under tests/fixtures/ ARE allowed.
            if top in ("src", "governance", "scripts", "prompts", "phases", ".thekey"):
                if top == "src" and not str(rel).startswith(
                    "src" + os.sep + "thekey"
                ):
                    # A non-engine src subdir (e.g. a sample project) is allowed.
                    pass
                else:
                    raise InvalidArgumentsError(
                        "Source points at THEKEY's own protected tree; refusing."
                    )

        # Reject unsafe links on the resolved root.
        if _is_symlink(src) or _is_reparse_point(src):
            raise InvalidArgumentsError(
                f"Source root is an unsafe link/reparse point: {source}"
            )
        return src

    # -- scan -----------------------------------------------------------
    def inspect(self, source: str | Path) -> ProjectInspection:
        root = self.resolve_source(source)
        insp = ProjectInspection(
            source_root=str(root),
            access_mode="READ_ONLY",
            scan_limits=self.scan_limits,
        )
        max_depth = int(self.scan_limits["max_depth"])
        max_files = int(self.scan_limits["max_files"])
        max_content = int(self.scan_limits["max_file_size_bytes_for_content_read"])

        excluded_dirs = {d.lower() for d in self.excluded_dirs}
        root_depth = len(root.parts)

        file_count = 0
        excluded_dir_count = 0
        rel_hashes: dict[str, str] = {}
        inventory: list[dict] = []

        # Git status (read-only).
        self._record_git(root, insp)

        for dirpath, dirnames, filenames in os.walk(root):
            cur = Path(dirpath)
            # Exclude generated dirs in-place (prune descent).
            pruned = []
            for d in list(dirnames):
                low = d.lower()
                if low in excluded_dirs:
                    excluded_dir_count += 1
                    continue
                child = cur / d
                if _is_symlink(child) or _is_reparse_point(child):
                    insp.symlink_findings.append(str(child.relative_to(root)))
                    # Do not descend into unsafe links.
                    continue
                pruned.append(d)
            dirnames[:] = pruned

            depth = len(cur.parts) - root_depth
            if depth > max_depth:
                insp.warnings.append(f"depth limit exceeded at {cur}")
                dirnames[:] = []
                continue

            for fname in filenames:
                file_count += 1
                if file_count > max_files:
                    insp.warnings.append("file count limit exceeded; partial scan")
                    break
                fpath = cur / fname
                rel = str(fpath.relative_to(root))
                # Skip unsafe links / reparse points.
                if _is_symlink(fpath) or _is_reparse_point(fpath):
                    insp.symlink_findings.append(rel)
                    continue
                try:
                    size = fpath.stat().st_size
                except OSError:
                    continue
                rec = {"path": rel, "size": size, "ext": fpath.suffix}
                # Binary detection by NUL byte in head (does NOT load full file).
                if self._looks_binary(fpath):
                    insp.binary_files.append(rel)
                    rec["binary"] = True
                else:
                    if size <= max_content:
                        try:
                            h = hashlib.sha256(
                                fpath.read_bytes()
                            ).hexdigest()
                            rel_hashes[rel] = h
                            rec["sha256"] = h
                        except OSError:
                            pass
                inventory.append(rec)
            if file_count > max_files:
                break

        insp.included_file_count = len(rel_hashes)
        insp.excluded_dir_count = excluded_dir_count
        insp.canonical_hashes = rel_hashes
        insp.baseline_tree_hash = compute_tree_hash(rel_hashes)
        insp.file_inventory = inventory
        insp.metadata_files = sorted(
            set(rel for rel in rel_hashes if Path(rel).name in (
                "pyproject.toml", "setup.py", "setup.cfg", "requirements.txt",
                "Pipfile", "tox.ini",
            ))
        )
        insp.detected_entrypoints = sorted(
            rel for rel in rel_hashes
            if Path(rel).name in ("__main__.py", "main.py", "cli.py", "app.py", "wsgi.py")
        )
        insp.test_roots = sorted(
            set(
                str(Path(rel).parts[0])
                for rel in rel_hashes
                if Path(rel).name.startswith("test_")
            )
        )
        if file_count > max_files:
            insp.warnings.append("scan truncated at max_files")
        return insp

    # -- helpers --------------------------------------------------------
    def _looks_binary(self, path: Path) -> bool:
        try:
            with path.open("rb") as fh:
                chunk = fh.read(1024)
        except OSError:
            return False
        return b"\x00" in chunk

    def _record_git(self, root: Path, insp: ProjectInspection) -> None:
        git_dir = root / ".git"
        if not git_dir.exists():
            insp.git_detected = False
            return
        insp.git_detected = True
        import subprocess

        try:
            head = subprocess.run(
                ["git", "-C", str(root), "rev-parse", "HEAD"],
                capture_output=True, text=True, timeout=30,
            )
            insp.git_head = head.stdout.strip() or None
            status = subprocess.run(
                ["git", "-C", str(root), "status", "--porcelain"],
                capture_output=True, text=True, timeout=30,
            )
            insp.git_status_text = status.stdout
            insp.git_dirty = bool(status.stdout.strip())
        except Exception:
            insp.warnings.append("git status could not be read")
            insp.git_detected = True


def inspect_project(source: str | Path, scan_limits: dict | None = None) -> ProjectInspection:
    return ProjectLoader(scan_limits).inspect(source)
