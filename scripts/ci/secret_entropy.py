"""Entropy-based secret scanner (improvement B).

Complements the regex secret scan in CI. High-Shannon-entropy strings that
look like randomly-generated secrets (long hex / base64 / base62 tokens) are
flagged even when they have no recognizable `api_key=` prefix.

Design constraints (match THEKEY's no-dependency CI scripts):
  - stdlib only.
  - deterministic; returns a clear report and exit code 0 (clean) / 1 (findings).
  - allowlist of known-benign high-entropy literals (test fixtures, hashes).

Usage:
  python scripts/ci/secret_entropy.py [--root .] [--threshold 3.7] [--min-len 20]
"""

from __future__ import annotations

import argparse
import math
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

# File types to scan.
SCAN_GLOBS = ["*.py", "*.ps1", "*.toml", "*.md", "*.json", "*.yaml", "*.yml"]
EXCLUDE_DIRS = {".git", ".thekey", ".venv", "runs", "workspaces", "node_modules",
                "__pycache__", "tests/fixtures", "development-audit",
                "release_evidence"}

# Files whose entire purpose is storing hashes / digests (never secrets).
HASH_FILE_MARKERS = ("hashes.json", "hashes.sha256", "file_hashes", "pytest_count")

# Test modules that deliberately embed high-entropy fixtures for the scanner
# itself. They are not real secrets and are excluded from the scan.
SELF_TEST_MARKERS = ("test_secret_entropy.py", "test_version_parity.py")

# Tokens that are high-entropy by nature but benign in this repo.
ALLOWLIST = {
    # THEKEY's own deterministic review-token infrastructure (evidence, not secret).
    "review_token",
    # Common benign long literals used in docs/tests.
    "0123456789abcdef",
    "abcdef0123456789",
}

# Candidate secret shapes: long runs of hex / base64url / base62.
TOKEN_RE = re.compile(r"[A-Za-z0-9_\-]{20,}")

# A full SHA-256 / hex digest line is a hash, not a secret.
HEX64_RE = re.compile(r"^[0-9a-f]{40,}$")
UUID_RE = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")


def shannon_entropy(s: str) -> float:
    if not s:
        return 0.0
    freq: dict[str, int] = {}
    for ch in s:
        freq[ch] = freq.get(ch, 0) + 1
    n = len(s)
    return -sum((c / n) * math.log2(c / n) for c in freq.values())


def _looks_like_hash(token: str) -> bool:
    return bool(HEX64_RE.match(token)) or bool(UUID_RE.match(token))


def _is_benign(token: str, line: str) -> bool:
    low = line.lower()
    if any(a in low for a in ALLOWLIST):
        return True
    if _looks_like_hash(token):
        return True
    # Hashes / uuids / known identifiers are allowed.
    if re.fullmatch(r"[0-9a-f]{32,}", token) and "hash" in low:
        return True
    if "example" in low or "dummy" in low or "placeholder" in low:
        return True
    return False


def scan_tree(root: Path, threshold: float, min_len: int) -> list[dict]:
    findings: list[dict] = []
    for ext in SCAN_GLOBS:
        for path in root.rglob(ext):
            if any(part in EXCLUDE_DIRS for part in path.parts):
                continue
            if any(m in path.name for m in HASH_FILE_MARKERS):
                continue
            if any(m in path.name for m in SELF_TEST_MARKERS):
                continue
            try:
                text = path.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue
            for lineno, line in enumerate(text.splitlines(), 1):
                for m in TOKEN_RE.finditer(line):
                    token = m.group(0)
                    if len(token) < min_len:
                        continue
                    if _looks_like_hash(token):
                        continue
                    # Require a mix of character classes to avoid flagging
                    # long natural-language words or repeated chars.
                    has_upper = any(c.isupper() for c in token)
                    has_lower = any(c.islower() for c in token)
                    has_digit = any(c.isdigit() for c in token)
                    if sum([has_upper, has_lower, has_digit]) < 2:
                        continue
                    if _is_benign(token, line):
                        continue
                    ent = shannon_entropy(token)
                    if ent >= threshold:
                        findings.append(
                            {
                                "path": str(path.relative_to(root)),
                                "line": lineno,
                                "length": len(token),
                                "entropy": round(ent, 3),
                            }
                        )
    return findings


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=str(ROOT))
    ap.add_argument("--threshold", type=float, default=4.3)
    ap.add_argument("--min-len", type=int, default=20)
    args = ap.parse_args()

    findings = scan_tree(Path(args.root), args.threshold, args.min_len)
    print("=" * 60)
    print("THEKEY ENTROPY SECRET SCAN")
    print("=" * 60)
    if not findings:
        print("RESULT: PASS")
        print("No high-entropy candidate secrets found.")
        return 0
    print("RESULT: FAIL")
    for f in findings:
        print(f"  - {f['path']}:{f['line']} len={f['length']} entropy={f['entropy']}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
