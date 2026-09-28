"""Render data/contributions.json as an animated 53x7 contribution heatmap.

    python scripts/render_heatmap_svg.py            # animated
    STATIC=1 python scripts/render_heatmap_svg.py   # frozen frame

Cells slide in along the anti-diagonal (week + weekday), once, then freeze.
"""
from __future__ import annotations

import datetime as dt
import json
import os
from pathlib import Path

import config as C
from svgkit import esc, font_face_css

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "data" / "contributions.json"
OUT = ROOT / "contrib-heatmap.svg"

W = 860
PAD = 20
LABEL_W = 30
TOP = 58            # header + month labels
GAP = 3
DIAG_DT = 0.017     # delay per anti-diagonal step (s)
NEON_Q = 0.97       # non-zero days above this quantile get the neon level 5


def fmt_date(iso: str) -> str:
    d = dt.date.fromisoformat(iso)
    return f"{d.strftime('%b')} {d.day}, {d.year}"


def main() -> None:
    static = os.environ.get("STATIC") == "1"
    data = json.loads(SRC.read_text(encoding="utf-8"))
    days, st = data["days"], data["stats"]

    first = dt.date.fromisoformat(days[0]["date"])
    sunday0 = first - dt.timedelta(days=(first.weekday() + 1) % 7)
    n_weeks = (dt.date.fromisoformat(days[-1]["date"]) - sunday0).days // 7 + 1

    step = (W - 2 * PAD - LABEL_W) / n_weeks
    cell = step - GAP
    grid_h = 7 * step - GAP

    nz = sorted(d["count"] for d in days if d["count"] > 0)
    neon = nz[min(int(len(nz) * NEON_Q), len(nz) - 1)] if nz else float("inf")

    total_line = f"{st['total']:,} contributions in the last year"
    kpis = [
        ("current streak", f"{st['current_streak']}d"),
        ("longest streak", f"{st['longest_streak']}d"),
        ("active days", f"{st['active_days']}"),
        ("best day", f"{st['best_day']['count']} · {fmt_date(st['best_day']['date'])}"
         if st["best_day"] else "n/a"),
    ]
    months = "JanFebMarAprMayJunJulAugSepOctNovDec"
    footer_y = TOP + grid_h + 30
    kpi_y = footer_y + 38
    H = int(kpi_y + 30)

    txt = (total_line + months + "MonWedFri LessMore" + "".join(a + b for a, b in kpis)
           + f"{C.PROMPT_USER}@{C.PROMPT_HOST}:~$ ./contributions.sh --user {C.USERNAME}")
    anim = "" if static else (
        "@keyframes drop{from{opacity:0;transform:translateY(-7px)}"
        "to{opacity:1;transform:none}}"
        ".c{opacity:0;animation:drop .38s cubic-bezier(.2,.8,.3,1) forwards}"
        "@keyframes fade{from{opacity:0}to{opacity:1}}"
        ".f{opacity:0;animation:fade .6s ease-out forwards}"
    )
    style = (
        font_face_css(txt, bold_text=total_line + "".join(b for _, b in kpis))
        + f"text{{font-family:{C.FONT_STACK};fill:{C.DIM};font-size:11px}}"
        + f".t{{fill:{C.FG};font-size:14px;font-weight:700}}"
        + f".p{{fill:{C.ACCENT}}}.v{{fill:{C.FG};font-size:13px;font-weight:700}}"
        + f".kl{{font-size:10.5px}}{anim}"
    )

    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
        f'viewBox="0 0 {W} {H}" role="img" aria-label="{esc(total_line)}">',
        f"<style>{style}</style>",
        f'<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="10" fill="{C.PANEL}" '
        f'stroke="{C.BORDER}"/>',
        f'<text x="{PAD}" y="30" class="t">{esc(total_line)}</text>',
        f'<text x="{W - PAD}" y="30" text-anchor="end">'
        f'<tspan class="p">$</tspan> ./contributions.sh --user {esc(C.USERNAME)}</text>',
    ]

    gx0 = PAD + LABEL_W
    # month labels at the first week whose Sunday starts a new month
    last_m = None
    for w in range(n_weeks):
        d = sunday0 + dt.timedelta(days=7 * w)
        if d.month != last_m and w < n_weeks - 2:
            if last_m is not None or d.day <= 7:
                out.append(f'<text x="{gx0 + w * step:.1f}" y="{TOP - 8}">'
                           f'{months[3 * (d.month - 1):3 * d.month]}</text>')
            last_m = d.month
    for r, lab in ((1, "Mon"), (3, "Wed"), (5, "Fri")):
        out.append(f'<text x="{PAD}" y="{TOP + r * step + cell - 2:.1f}">{lab}</text>')

    for d in days:
        date = dt.date.fromisoformat(d["date"])
        col = (date - sunday0).days // 7
        row = (date.weekday() + 1) % 7
        lvl = d["level"]
        if lvl == 4 and d["count"] >= neon:
            lvl = 5
        x, y = gx0 + col * step, TOP + row * step
        delay = "" if static else f' style="animation-delay:{(col + row) * DIAG_DT:.3f}s"'
        cls = "" if static else ' class="c"'
        out.append(
            f'<rect{cls}{delay} x="{x:.1f}" y="{y:.1f}" width="{cell:.1f}" height="{cell:.1f}" '
            f'rx="2.5" fill="{C.HEAT_PALETTE[lvl]}"><title>{d["count"]} on {d["date"]}</title></rect>'
        )

    t_end = (n_weeks + 6) * DIAG_DT + 0.3
    fdelay = "" if static else f' class="f" style="animation-delay:{t_end:.2f}s"'
    foot = [f'<g{fdelay}>']
    # Less -> More legend (right-aligned under the grid)
    lx = W - PAD - 30 - 6 * (cell + 4)
    foot.append(f'<text x="{lx - 8}" y="{footer_y}" text-anchor="end">Less</text>')
    for i, c in enumerate(C.HEAT_PALETTE):
        foot.append(f'<rect x="{lx + i * (cell + 4):.1f}" y="{footer_y - cell + 2:.1f}" '
                    f'width="{cell:.1f}" height="{cell:.1f}" rx="2.5" fill="{c}"/>')
    foot.append(f'<text x="{W - PAD}" y="{footer_y}" text-anchor="end">More</text>')
    upd = data["generated_at"][:10] + (" · demo data" if data.get("demo") else "")
    foot.append(f'<text x="{PAD}" y="{footer_y}">updated {esc(upd)}</text>')
    # KPI strip
    foot.append(f'<line x1="{PAD}" y1="{footer_y + 13}" x2="{W - PAD}" y2="{footer_y + 13}" '
                f'stroke="{C.BORDER}"/>')
    colw = (W - 2 * PAD) / len(kpis)
    for i, (k, v) in enumerate(kpis):
        x = PAD + i * colw
        foot.append(f'<text x="{x:.1f}" y="{kpi_y - 2}" class="kl">{esc(k)}</text>')
        foot.append(f'<text x="{x:.1f}" y="{kpi_y + 15}" class="v">{esc(v)}</text>')
    foot.append("</g>")

    OUT.write_text("\n".join(out + foot + ["</svg>"]), encoding="utf-8")
    print(f"wrote {OUT.name} ({n_weeks} weeks, {OUT.stat().st_size / 1024:.0f} KB)")


if __name__ == "__main__":
    main()
