"""Neofetch-style info card.

    python scripts/make_info_card.py            # animated
    STATIC=1 python scripts/make_info_card.py   # frozen frame

Content lives in config.CARD_ROWS. Each line fades and slides in on a short
stagger (CSS keyframes, played once, then frozen).
"""
from __future__ import annotations

import os
from pathlib import Path

import config as C
from svgkit import esc, font_face_css

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "info-card.svg"

W = 490
FS = 12.5
LH = 21
PAD_X = 22
TITLE_H = 34
KEY_W = 60
DT = 0.09           # stagger between lines (s)
T0 = 0.35           # first line delay (s)


def main() -> None:
    static = os.environ.get("STATIC") == "1"
    rows = C.CARD_ROWS
    swatch_y0 = TITLE_H + 24 + (len(rows) + 2) * LH
    H = swatch_y0 + 40

    prompt = f"{C.PROMPT_USER}@{C.PROMPT_HOST} ~ $ neofetch"
    header = C.CARD_TITLE
    all_text = prompt + header + "-" * len(header) + "".join(k + v for k, v in rows) + ":"
    css_font = font_face_css(all_text, bold_text=header + "".join(k for k, _ in rows) + ":")

    anim = "" if static else (
        "@keyframes in{from{opacity:0;transform:translateX(-8px)}to{opacity:1;transform:none}}"
        ".l{opacity:0;animation:in .45s ease-out forwards}"
        "@keyframes blink{50%{opacity:0}}.cur{animation:blink 1s step-end infinite}"
    )
    style = (
        f"{css_font}"
        f"text{{font-family:{C.FONT_STACK};font-size:{FS}px;fill:{C.FG};white-space:pre}}"
        f".k{{fill:{C.ACCENT};font-weight:700}}.h{{fill:{C.ACCENT2};font-weight:700}}"
        f".d{{fill:{C.DIM}}}{anim}"
    )

    def line(y: float, i: int, inner: str) -> str:
        delay = "" if static else f' style="animation-delay:{T0 + i * DT:.2f}s"'
        return f'<g class="l"{delay}><text y="{y:.1f}">{inner}</text></g>'

    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
        f'viewBox="0 0 {W} {H}" role="img" aria-label="{esc(header)} profile card">',
        f"<style>{style}</style>",
        f'<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="10" fill="{C.PANEL}" '
        f'stroke="{C.BORDER}"/>',
        # title bar
        f'<path d="M.5 10.5a10 10 0 0 1 10-10h{W - 21}a10 10 0 0 1 10 10V{TITLE_H}H.5z" '
        f'fill="#161b22"/>',
        f'<line x1="0" y1="{TITLE_H}" x2="{W}" y2="{TITLE_H}" stroke="{C.BORDER}"/>',
    ]
    for j, col in enumerate(("#ff5f57", "#febc2e", "#28c840")):
        out.append(f'<circle cx="{18 + j * 18}" cy="{TITLE_H / 2}" r="5.5" fill="{col}"/>')
    out.append(f'<text x="{W / 2}" y="{TITLE_H / 2 + 4}" text-anchor="middle" class="d" '
               f'style="font-size:11px">{esc(C.PROMPT_USER)}@{esc(C.PROMPT_HOST)}: ~</text>')

    y = TITLE_H + 26
    body = [f'<g transform="translate({PAD_X},0)">']
    body.append(line(y, 0, f'<tspan class="k">$</tspan> {esc(prompt.split("$ ")[1])}'))
    y += LH + 4
    body.append(line(y, 1, f'<tspan class="h">{esc(header)}</tspan>'))
    y += LH - 4
    body.append(line(y, 2, f'<tspan class="d">{"-" * len(header)}</tspan>'))
    y += LH
    for i, (k, v) in enumerate(rows, start=3):
        if not k and not v:
            y += LH * 0.45
            continue
        key = f'<tspan class="k">{esc(k)}{":" if k else ""}</tspan>'
        body.append(line(y, i, f'{key}<tspan x="{KEY_W}">{esc(v)}</tspan>'))
        y += LH

    # neofetch colour swatches + blinking cursor
    y += 8
    n = len(rows) + 3
    sw = "".join(
        f'<rect x="{i * 26}" y="{y}" width="22" height="12" rx="2" fill="{c}"/>'
        for i, c in enumerate(["#484f58", "#ff7b72", "#7ee787", "#d29922",
                               "#79c0ff", "#d2a8ff", "#56d4dd", "#e6edf3"])
    )
    delay = "" if static else f' style="animation-delay:{T0 + n * DT:.2f}s"'
    body.append(f'<g class="l"{delay}>{sw}</g>')
    cur_delay = "" if static else f' style="animation-delay:{T0 + (n + 1) * DT:.2f}s"'
    body.append(
        f'<g class="l"{cur_delay}><rect class="cur" x="{8 * 26 + 6}" y="{y}" width="8" '
        f'height="12" fill="{C.FG}"/></g>'
    )
    body.append("</g>")

    # shrink-wrap height to content
    H2 = int(y + 12 + 22)
    svg = "\n".join(out + body + ["</svg>"])
    svg = svg.replace(f'height="{H}"', f'height="{H2}"', 1).replace(
        f'viewBox="0 0 {W} {H}"', f'viewBox="0 0 {W} {H2}"').replace(
        f'height="{H - 1}"', f'height="{H2 - 1}"')
    OUT.write_text(svg, encoding="utf-8")
    print(f"wrote {OUT.name} ({OUT.stat().st_size / 1024:.0f} KB)")


if __name__ == "__main__":
    main()
