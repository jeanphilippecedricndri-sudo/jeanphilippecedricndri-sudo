"""Convert assets/source-prepped.png into a self-typing monochrome ASCII SVG.

    python scripts/make_ascii_svg.py            # animated
    STATIC=1 python scripts/make_ascii_svg.py   # frozen frame (for previews)

Each row is revealed by a left-to-right clip wipe with a block cursor riding
the edge, staggered top to bottom. SMIL runs inside <img>, so GitHub plays it.
"""
from __future__ import annotations

import os
import re
from pathlib import Path

import numpy as np
from PIL import Image, ImageOps

import config as C
from svgkit import esc, font_face_css

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "assets" / "source-prepped.png"
OUT = ROOT / "ascii.svg"

RAMP = " .`:-=+*cs#%@"   # bright (sparse) -> dark (dense); leading space clears bg
COLS = 84
FONT_SIZE = 11.0
CW = FONT_SIZE * 0.6     # Space Mono advance width = 0.6 em
LH = 12.0                # line height
PAD = 18
ROW_DT = 0.055           # stagger between rows (s)
ROW_DUR = 0.22           # wipe duration per row (s)
GAMMA = 1.45             # >1 pushes mid-tones toward sparse glyphs
DISPLAY_ASCII_W, DISPLAY_CARD_W = 370, 490  # column widths used in README.md


def to_grid(img: Image.Image) -> list[str]:
    img = ImageOps.autocontrast(img.convert("L"), cutoff=1)
    rows = max(1, round(COLS * img.height / img.width * CW / LH))
    small = np.asarray(img.resize((COLS, rows), Image.LANCZOS), dtype=np.float32) / 255.0
    darkness = (1.0 - small) ** GAMMA
    idx = np.clip((darkness * (len(RAMP) - 1)).round().astype(int), 0, len(RAMP) - 1)
    lines = ["".join(RAMP[i] for i in row).rstrip() for row in idx]
    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()
    # drop common left margin
    indent = min(len(l) - len(l.lstrip()) for l in lines if l.strip())
    return [l[indent:] for l in lines]


def card_matched_height(W: int) -> int:
    """Height that makes this SVG as tall as info-card.svg once both sit in the
    README table (370 px and 490 px columns)."""
    card = ROOT / "info-card.svg"
    if not card.exists():
        return 0
    m = re.search(r'viewBox="0 0 (\d+(?:\.\d+)?) (\d+(?:\.\d+)?)"', card.read_text("utf-8"))
    if not m:
        return 0
    card_w, card_h = float(m.group(1)), float(m.group(2))
    return round(W * (card_h * DISPLAY_CARD_W / card_w) / DISPLAY_ASCII_W)


def build_svg(lines: list[str], caption: str | None, static: bool) -> str:
    ncols = max(len(l) for l in lines)
    text_w = ncols * CW
    cap_h = 26 if caption else 0
    W = round(text_w + 2 * PAD)
    H = max(round(len(lines) * LH + 2 * PAD + cap_h), card_matched_height(W))
    y_off = (H - cap_h - 2 * PAD - len(lines) * LH) / 2  # vertically centre the art
    css = font_face_css("".join(lines) + (caption or ""))

    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
        f'viewBox="0 0 {W} {H}" role="img" aria-label="ASCII art">',
        f"<style>{css}"
        f"text{{font-family:{C.FONT_STACK};font-size:{FONT_SIZE}px;fill:{C.ASCII_FG};"
        "white-space:pre}"
        f".cap{{fill:{C.DIM};font-size:10.5px}}</style>",
        f'<rect width="{W}" height="{H}" rx="10" fill="{C.PANEL}" stroke="{C.BORDER}"/>',
    ]
    defs, body = [], []
    for i, line in enumerate(lines):
        if not line.strip():
            continue
        y = PAD + y_off + (i + 1) * LH - 3
        lw = len(line) * CW
        text = (f'<text x="{PAD}" y="{y:.1f}" xml:space="preserve">{esc(line)}</text>')
        if static:
            body.append(text)
            continue
        t0 = i * ROW_DT
        top = y - LH + 3
        defs.append(
            f'<clipPath id="r{i}"><rect x="{PAD}" y="{top:.1f}" width="0" height="{LH}">'
            f'<animate attributeName="width" from="0" to="{lw + 2:.1f}" begin="{t0:.3f}s" '
            f'dur="{ROW_DUR}s" fill="freeze"/></rect></clipPath>'
        )
        body.append(f'<g clip-path="url(#r{i})">{text}</g>')
        # block cursor riding the wipe edge, vanishes when the row is done
        body.append(
            f'<rect x="{PAD}" y="{top + 1:.1f}" width="{CW:.1f}" height="{LH - 2}" '
            f'fill="{C.ACCENT}" opacity="0">'
            f'<set attributeName="opacity" to="0.9" begin="{t0:.3f}s"/>'
            f'<animate attributeName="x" from="{PAD}" to="{PAD + lw:.1f}" '
            f'begin="{t0:.3f}s" dur="{ROW_DUR}s" fill="freeze"/>'
            f'<set attributeName="opacity" to="0" begin="{t0 + ROW_DUR:.3f}s"/></rect>'
        )
    if defs:
        out.append("<defs>" + "".join(defs) + "</defs>")
    out += body
    if caption:
        cy = H - PAD + 4
        if static:
            out.append(f'<text class="cap" x="{PAD}" y="{cy}">{esc(caption)}</text>')
        else:
            t_end = len(lines) * ROW_DT + ROW_DUR
            out.append(
                f'<text class="cap" x="{PAD}" y="{cy}" opacity="0">{esc(caption)}'
                f'<animate attributeName="opacity" from="0" to="1" begin="{t_end:.2f}s" '
                'dur="0.6s" fill="freeze"/></text>'
            )
    out.append("</svg>")
    return "\n".join(out)


def main() -> None:
    static = os.environ.get("STATIC") == "1"
    caption = os.environ.get("ASCII_CAPTION")
    cap_file = ROOT / "assets" / ".caption"
    if caption is None and cap_file.exists():
        caption = cap_file.read_text(encoding="utf-8").strip()
    lines = to_grid(Image.open(SRC))
    OUT.write_text(build_svg(lines, caption or None, static), encoding="utf-8")
    print(f"wrote {OUT.name} ({len(lines)} rows, {OUT.stat().st_size / 1024:.0f} KB)")


if __name__ == "__main__":
    main()
