"""Path security tests (section 31: PATH SECURITY)."""

import pytest

from thekey.errors import UnauthorizedPathError
from thekey.workspaces import WorkspaceManager


@pytest.fixture
def wm(tmp_path):
    return WorkspaceManager(tmp_path / "workspaces")


def test_normal_workspace_path(wm):
    p = wm.path_for("R1", "src/demo_app/calculator.py")
    assert "R1" in str(p)
    assert p.is_relative_to(wm.root / "R1")


def test_path_traversal(wm):
    with pytest.raises(UnauthorizedPathError):
        wm.path_for("R1", "../../../etc/passwd")


def test_sibling_prefix_attack(wm):
    # 'R1evil' must not be confused with 'R1' (prefix confusion).
    with pytest.raises(UnauthorizedPathError):
        wm.path_for("R1", "../R1evil/secret.txt")


def test_protected_path_outside_root(wm):
    with pytest.raises(UnauthorizedPathError):
        wm.path_for("R1", "/Windows/System32/foo.txt")


def test_authorize_write_creates_parents(wm):
    target = wm.authorize_write("R1", "src/demo_app/calculator.py")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("x", encoding="utf-8")
    assert target.exists()


def test_unsafe_reparse_point(tmp_path, monkeypatch):
    # Simulate a reparse point by monkeypatching _is_reparse_point.
    from thekey import workspaces as ws_mod

    monkeypatch.setattr(ws_mod, "_is_reparse_point", lambda p: True)
    wm = WorkspaceManager(tmp_path / "ws")
    with pytest.raises(UnauthorizedPathError):
        wm.authorize_write("R1", "src/x.py")
