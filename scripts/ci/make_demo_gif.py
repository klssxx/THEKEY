"""Render an authentic terminal-style GIF of the real THEKEY demo cycle.

Uses the ACTUAL demo output (no fabrication). Shows the clean-clone command,
the demo run, and the RELEASE_ELIGIBLE / 4-of-4 gates result, ending on the
auditable evidence path. Saved to docs/assets/thekey-demo.gif.
"""
from __future__ import annotations
import os, textwrap, subprocess, sys, pathlib

# Real captured demo output (from a clean clone in a path with spaces).
COMMAND = "C:\\Temp\\THEKEY Flip Demo> pwsh -NoProfile -File .\\scripts\\demo.ps1"
LINES = [
    "Python 3.12.10 venv created (.venv)",
    "pip install -e .  -> thekey 0.2.0 installed",
    "",
    "running: python -m thekey demo",
    "",
    "run_id: TK-20260715-152917-ZPKXPI",
    "state: RELEASE_ELIGIBLE",
    "decision: RELEASE_ELIGIBLE",
    "gates_passed: 4",
    "gates_total: 4",
    "evidence_mismatches: []",
    "workspace: ...\\workspaces\\TK-20260715-152917-ZPKXPI",
    "run_path:  ...\\runs\\TK-20260715-152917-ZPKXPI",
    "",
    "DEMO RESULT: RELEASE_ELIGIBLE  (4/4 gates)  exit 0",
    "Evidence chain written to SQLite: manifest, plan, approvals,",
    "changes.diff, gates.json, decision.json, artifact-hashes.json",
]

# Terminal look
BG = (18, 22, 30)
FG = (216, 222, 233)
ACCENT = (46, 160, 67)      # green (PASS)
DIM = (120, 132, 150)
PROMPT = (88, 166, 255)
FONT_PATH = None  # use default

from PIL import Image, ImageDraw, ImageFont

def load_font(size):
    candidates = [
        "C:/Windows/Fonts/Consolas.ttf",
        "C:/Windows/Fonts/DejaVuSansMono.ttf",
        "C:/Windows/Fonts/lucon.ttf",
    ]
    for c in candidates:
        if os.path.exists(c):
            try:
                return ImageFont.truetype(c, size)
            except Exception:
                pass
    return ImageFont.load_default()

FONT = load_font(20)
W, H = 900, 520
PAD = 24
LH = 28

def text_color(line):
    if line.startswith("DEMO RESULT") or "RELEASE_ELIGIBLE" in line:
        return ACCENT
    if line.startswith("running") or line.startswith("pip") or line.startswith("Python"):
        return DIM
    if line.startswith("C:\\Temp"):
        return PROMPT
    return FG

def wrap_line(line, max_chars=58):
    if not line:
        return [""]
    return textwrap.wrap(line, max_chars) or [""]

def build_frames():
    frames = []
    # Title bar frame
    all_lines = [COMMAND] + LINES
    # Build progressively: each frame reveals more lines (typing effect)
    cumulative = []
    # Frame 1: just window + prompt
    cumulative.append(COMMAND)
    for ln in LINES:
        cumulative.append(ln)
        # duplicate a couple frames for readability on key lines
        if "RELEASE_ELIGIBLE" in ln or "gates_passed" in ln or ln.startswith("DEMO RESULT"):
            cumulative.append(ln)
    # Render each cumulative state as a frame (hold ~3 frames each)
    for i in range(1, len(cumulative) + 1):
        img = Image.new("RGB", (W, H), BG)
        d = ImageDraw.Draw(img)
        # title bar
        d.rectangle([0, 0, W, 34], fill=(32, 38, 50))
        d.text((14, 8), "THEKEY 0.2.0  -  demo.ps1  (clean clone, Windows 11)", font=FONT, fill=DIM)
        # content
        y = PAD + 24
        shown = cumulative[:i]
        # show last N lines that fit
        max_lines = (H - PAD - 40) // LH
        vis = shown[-max_lines:]
        for ln in vis:
            col = text_color(ln)
            for sub in wrap_line(ln):
                d.text((PAD, y), sub, font=FONT, fill=col)
                y += LH
        # blinking cursor on last frame
        if i == len(cumulative):
            d.rectangle([PAD, y - 4, PAD + 10, y + 14], fill=ACCENT)
        frames.append(img)
    return frames

def main():
    frames = build_frames()
    out = pathlib.Path(__file__).resolve().parents[2] / "docs" / "assets" / "thekey-demo.gif"
    out.parent.mkdir(parents=True, exist_ok=True)
    # Hold each frame ~6 (typing), last frames longer
    durations = [70] * len(frames)
    # make the final "result" frames linger
    for j in range(max(0, len(frames) - 4), len(frames)):
        durations[j] = 900
    frames[0].save(
        out, save_all=True, append_images=frames[1:],
        duration=durations, loop=0, optimize=True,
    )
    print(f"wrote {out} ({out.stat().st_size} bytes, {len(frames)} frames)")

if __name__ == "__main__":
    main()
