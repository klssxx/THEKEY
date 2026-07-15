"""Project Loader tests (section 48: PROJECT LOADER)."""

import json

import pytest

from thekey.config import REAL_ROOT, RUNS_DIR, WORKSPACES_DIR
from thekey.errors import InvalidArgumentsError
from thekey.project_loader import ProjectLoader, inspect_project

FIX = REAL_ROOT / "tests" / "fixtures"


def test_valid_python_directory():
    insp = inspect_project(FIX / "python_generic_project")
    assert insp.access_mode == "READ_ONLY"
    assert insp.included_file_count > 0
    assert insp.baseline_tree_hash  # deterministic
    assert insp.detected_entrypoints or insp.metadata_files


def test_missing_directory():
    with pytest.raises(InvalidArgumentsError):
        inspect_project(FIX / "does_not_exist_xyz")


def test_file_instead_of_directory():
    with pytest.raises(InvalidArgumentsError):
        inspect_project(FIX / "python_generic_project" / "pyproject.toml")


def test_source_inside_runs_rejected():
    with pytest.raises(InvalidArgumentsError):
        inspect_project(RUNS_DIR)


def test_source_inside_workspaces_rejected():
    with pytest.raises(InvalidArgumentsError):
        inspect_project(WORKSPACES_DIR)


def test_protected_framework_source_rejected():
    # Pointing at the engine's own package (src/thekey) is rejected.
    from thekey.config import REAL_ROOT
    with pytest.raises(InvalidArgumentsError):
        inspect_project(REAL_ROOT / "src" / "thekey")


def test_excluded_directories():
    insp = inspect_project(FIX / "python_generic_project")
    # .git etc. are excluded by default; the fixture has none but the
    # exclusion logic must not crash and must count excluded dirs when present.
    assert isinstance(insp.excluded_dir_count, int)


def test_binary_file_not_loaded():
    # Create a temp binary file inside a temp project to avoid polluting fixtures.
    import tempfile
    from pathlib import Path

    proj = Path(tempfile.mkdtemp())
    (proj / "main.py").write_text("x = 1\n", encoding="utf-8")
    (proj / "blob.bin").write_bytes(b"\x00\x01\x02\x03binary")
    insp = inspect_project(proj)
    assert any(rel.endswith(".bin") for rel in insp.binary_files)
    # binary file must not have a recorded sha256 (not loaded into model).
    assert all("sha256" not in rec for rel, rec in
               ((r["path"], r) for r in insp.file_inventory if r["path"].endswith(".bin")))


def test_deterministic_baseline_tree_hash():
    a = inspect_project(FIX / "python_cli_project").baseline_tree_hash
    b = inspect_project(FIX / "python_cli_project").baseline_tree_hash
    assert a == b


def test_git_status_recorded_when_present():
    # The repo itself is a git project; the engine src is protected, but the
    # fixture python_cli_project is not a git repo -> git_detected False.
    insp = inspect_project(FIX / "python_cli_project")
    assert insp.git_detected is False


def test_unsafe_symlink_rejected(tmp_path):
    # Create a project dir, add a symlink inside, then ensure it is recorded
    # as a symlink finding and not followed.
    proj = tmp_path / "proj"
    proj.mkdir()
    (proj / "good.py").write_text("y = 2\n", encoding="utf-8")
    target = tmp_path / "secret.txt"
    target.write_text("topsecret", encoding="utf-8")
    link = proj / "evil_link"
    try:
        link.symlink_to(target)
    except (OSError, NotImplementedError):
        pytest.skip("symlink creation unsupported on this filesystem")
    insp = inspect_project(proj)
    assert any("evil_link" in rel for rel in insp.symlink_findings)
