"""Workspace creation and path authorization.

All model-visible paths are relative *IDs* resolved against a single allowed
root. We never use startswith()/commonprefix() for security; we use
Path.resolve() + Path.relative_to() and reject reparse points / symlinks /
junctions in write paths. (section 21)
"""

from __future__ import annotations

import os
import stat
from pathlib import Path

from .config import WORKSPACES_DIR
from .errors import UnauthorizedPathError


def _is_reparse_point(path: Path) -> bool:
    """Detect Windows reparse points (symlinks, junctions, symlink dirs)."""
    try:
        st = os.lstat(path)
    except OSError:
        return False
    # FILE_ATTRIBUTE_REPARSE_POINT = 0x400
    return bool(st.st_file_attributes & stat.FILE_ATTRIBUTE_REPARSE_POINT) if hasattr(
        st, "st_file_attributes"
    ) else False


def _is_symlink(path: Path) -> bool:
    try:
        return path.is_symlink()
    except OSError:
        return False


class WorkspaceManager:
    """Creates isolated run workspaces and authorizes path access."""

    def __init__(self, root: Path = WORKSPACES_DIR):
        self.root = Path(root).resolve()
        self.root.mkdir(parents=True, exist_ok=True)

    def create(self, run_id: str) -> Path:
        ws = self.root / run_id
        ws.mkdir(parents=True, exist_ok=True)
        return ws

    def path_for(self, run_id: str, relative_id: str) -> Path:
        """Resolve a relative id inside the run workspace.

        Raises UnauthorizedPathError on traversal, sibling-prefix attack,
        protected path, or unsafe reparse point.
        """
        ws = (self.root / run_id).resolve()
        if not ws.exists():
            ws.mkdir(parents=True, exist_ok=True)
        candidate = (ws / relative_id).resolve()
        # Must be inside the workspace root.
        try:
            candidate.relative_to(ws)
        except ValueError:
            raise UnauthorizedPathError(
                f"Path outside allowed root: {relative_id!r}",
                code="PATH_OUTSIDE_ALLOWED_ROOTS",
            )
        return candidate

    def authorize_write(self, run_id: str, relative_id: str, *, allow_create_parents: bool = True) -> Path:
        """Authorize an absolute write path inside the run workspace.

        Rejects reparse points, symlinks, and junctions anywhere on the
        resolved path (except the final target may be created fresh).
        """
        target = self.path_for(run_id, relative_id)
        # Walk parents up to the workspace root; reject any reparse point.
        cur = target.parent
        ws = (self.root / run_id).resolve()
        while True:
            if cur.exists():
                if _is_reparse_point(cur) or _is_symlink(cur):
                    raise UnauthorizedPathError(
                        f"Unsafe reparse point in path: {cur}", code="UNSAFE_REPARSE_POINT"
                    )
            if cur == ws:
                break
            cur = cur.parent
        if target.exists() and (_is_reparse_point(target) or _is_symlink(target)):
            raise UnauthorizedPathError(
                f"Target is a reparse point: {target}", code="UNSAFE_REPARSE_POINT"
            )
        if allow_create_parents:
            target.parent.mkdir(parents=True, exist_ok=True)
        return target

    def is_inside(self, run_id: str, candidate: Path) -> bool:
        ws = (self.root / run_id).resolve()
        try:
            Path(candidate).resolve().relative_to(ws)
            return True
        except ValueError:
            return False
