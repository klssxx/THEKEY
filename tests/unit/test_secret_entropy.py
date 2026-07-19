"""Unit tests for the entropy secret scanner (improvement B)."""

from scripts.ci.secret_entropy import scan_tree, shannon_entropy


def test_entropy_distinguishes_random_from_text():
    random_token = "k9F2mPqLx7RtVbN3wZc8YsA1uD4eH6gJ"
    natural = "this is a normal sentence with words"
    assert shannon_entropy(random_token) > shannon_entropy(natural)
    assert shannon_entropy(random_token) >= 3.7


def test_scan_finds_high_entropy_secret(tmp_path):
    f = tmp_path / "config.py"
    # A realistically-shaped leaked token (no api_key= prefix).
    f.write_text(
        'TOKEN = "k9F2mPqLx7RtVbN3wZc8YsA1uD4eH6gJ0aB2cD4eF6"\n',
        encoding="utf-8",
    )
    findings = scan_tree(tmp_path, threshold=3.7, min_len=20)
    assert any("config.py" in fr["path"] for fr in findings)
    assert findings[0]["entropy"] >= 3.7


def test_scan_ignores_benign_text(tmp_path):
    f = tmp_path / "notes.md"
    f.write_text(
        "The quick brown fox jumps over the lazy dog repeatedly in the demo.\n"
        "review_token = abcdef0123456789abcdef0123456789\n",
        encoding="utf-8",
    )
    findings = scan_tree(tmp_path, threshold=3.7, min_len=20)
    assert findings == []


def test_scan_ignores_short_tokens(tmp_path):
    f = tmp_path / "x.py"
    f.write_text('short = "abc123"\n', encoding="utf-8")
    assert scan_tree(tmp_path, threshold=3.7, min_len=20) == []


def test_scan_ignores_thekey_runtime_state(tmp_path):
    runtime = tmp_path / ".thekey"
    runtime.mkdir()
    (runtime / "generated.json").write_text(
        '{"generated": "k9F2mPqLx7RtVbN3wZc8YsA1uD4eH6gJz"}',
        encoding="utf-8",
    )

    assert scan_tree(tmp_path, threshold=3.7, min_len=20) == []
