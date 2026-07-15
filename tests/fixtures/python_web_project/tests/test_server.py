from app.server import app


def test_health():
    assert app is not None
