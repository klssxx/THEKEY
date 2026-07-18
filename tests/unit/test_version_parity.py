"""Unit tests for the version-parity gate (improvement G)."""

from pathlib import Path

import pytest

from scripts.ci.version_parity import (
    changelog_has_version,
    check,
    package_version,
    pyproject_version,
    status_version,
)


def _write(root: Path, rel: str, text: str) -> None:
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")


def test_package_version_reads_init(tmp_path):
    _write(tmp_path, "src/thekey/__init__.py", '__version__ = "0.2.0"\n')
    assert package_version(tmp_path) == "0.2.0"


def test_pyproject_version_reads_table(tmp_path):
    _write(tmp_path, "pyproject.toml", '[project]\nversion = "0.2.0"\n')
    assert pyproject_version(tmp_path) == "0.2.0"


def test_status_version_parses_table(tmp_path):
    _write(tmp_path, "STATUS.md", "| Release version | 0.2.0 |\n")
    assert status_version(tmp_path) == "0.2.0"


def test_changelog_has_version():
    import tempfile

    d = Path(tempfile.mkdtemp())
    _write(d, "CHANGELOG.md", "## [0.2.0] - 2026-07-15\n\nstuff\n")
    assert changelog_has_version("0.2.0", d) is True
    assert changelog_has_version("0.3.0", d) is False


def test_check_passes_when_aligned(tmp_path):
    _write(tmp_path, "src/thekey/__init__.py", '__version__ = "0.2.0"\n')
    _write(tmp_path, "pyproject.toml", '[project]\nversion = "0.2.0"\n')
    _write(tmp_path, "STATUS.md", "| Release version | 0.2.0 |\n")
    _write(tmp_path, "CHANGELOG.md", "## [0.2.0] - 2026-07-15\n\n- x\n")
    ok, problems = check(tmp_path)
    assert ok, problems
    assert problems == []


def test_check_fails_on_status_mismatch(tmp_path):
    _write(tmp_path, "src/thekey/__init__.py", '__version__ = "0.2.0"\n')
    _write(tmp_path, "pyproject.toml", '[project]\nversion = "0.2.0"\n')
    _write(tmp_path, "STATUS.md", "| Release version | 0.1.0 |\n")
    _write(tmp_path, "CHANGELOG.md", "## [0.2.0] - 2026-07-15\n")
    ok, problems = check(tmp_path)
    assert not ok
    assert any("STATUS.md" in p for p in problems)


def test_check_fails_on_missing_changelog_entry(tmp_path):
    _write(tmp_path, "src/thekey/__init__.py", '__version__ = "0.3.0"\n')
    _write(tmp_path, "pyproject.toml", '[project]\nversion = "0.3.0"\n')
    _write(tmp_path, "STATUS.md", "| Release version | 0.3.0 |\n")
    _write(tmp_path, "CHANGELOG.md", "## [0.2.0] - 2026-07-15\n")
    ok, problems = check(tmp_path)
    assert not ok
    assert any("CHANGELOG" in p for p in problems)
