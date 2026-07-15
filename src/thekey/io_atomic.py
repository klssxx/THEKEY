"""Windows-safe atomic file writes.

On Windows, antivirus can briefly lock a `*.tmp` file between its creation and
the atomic rename, causing ``PermissionError`` on ``Path.replace``. We retry the
rename a few times with a tiny backoff. The write remains atomic from the
reader's perspective (either the old file or the new file is visible; the temp
file is unique per call so a lingering lock from a previous call cannot block
this one).
"""

from __future__ import annotations

import os
import tempfile
import time
from pathlib import Path


def atomic_write_text(path: Path, text: str, *, encoding: str = "utf-8", max_retries: int = 8) -> Path:
    """Write ``text`` to ``path`` atomically, retrying the rename on Windows
    ``PermissionError`` (antivirus lock on the temp file)."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    # Unique temp file in the same directory so the rename is atomic on the
    # same volume and a stale lock on an old temp name cannot block us.
    fd, tmp_name = tempfile.mkstemp(dir=str(path.parent), prefix=path.name + ".", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding=encoding) as fh:
            fh.write(text)
            fh.flush()
            os.fsync(fh.fileno())
        tmp = Path(tmp_name)
        last_err: Exception | None = None
        for attempt in range(max_retries):
            try:
                tmp.replace(path)
                return path
            except PermissionError as exc:  # pragma: no cover - timing dependent
                last_err = exc
                time.sleep(0.05 * (attempt + 1))
                continue
        raise last_err if last_err else RuntimeError("atomic write failed")
    finally:
        # Ensure the temp file is gone even if the rename raised.
        try:
            if Path(tmp_name).exists():
                os.unlink(tmp_name)
        except OSError:
            pass


def atomic_write_json(path: Path, payload: dict, *, encoding: str = "utf-8") -> Path:
    import json

    text = json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True)
    return atomic_write_text(path, text, encoding=encoding)
