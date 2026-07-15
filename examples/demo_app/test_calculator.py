"""THEKEY Core - example demo app tests (run in workspace copy only)."""

from src.demo_app.calculator import add


def test_add_uses_addition():
    # The test expects correct addition; the ORIGINAL source fails it.
    assert add(2, 3) == 5
