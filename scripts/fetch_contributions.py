"""Scrape the public contribution calendar (no token, no GraphQL).

    python scripts/fetch_contributions.py            # live, for config.USERNAME
    python scripts/fetch_contributions.py --demo     # synthetic data for local previews

GitHub serves the calendar the profile page uses as a public HTML fragment at
https://github.com/users/<username>/contributions. Writes data/contributions.json
with raw days plus derived stats.
"""
from __future__ import annotations

import datetime as dt
import json
import re
import sys
from collections import OrderedDict
from pathlib import Path

import config as C

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "contributions.json"
URL = "https://github.com/users/{user}/contributions"
COUNT_RE = re.compile(r"^\s*(\d[\d,]*|No)\s+contributions?", re.I)


def fetch(user: str) -> list[dict]:
    import requests
    from bs4 import BeautifulSoup

    r = requests.get(URL.format(user=user), timeout=30,
                     headers={"User-Agent": f"{user}-profile-readme"})
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")

    # counts live in <tool-tip for="contribution-day-component-W-D">
    tips = {}
    for tip in soup.select("tool-tip[for]"):
        m = COUNT_RE.match(tip.get_text(" ", strip=True))
        if m:
            tips[tip["for"]] = 0 if m.group(1).lower() == "no" else int(m.group(1).replace(",", ""))

    days = []
    for cell in soup.select("[data-date]"):
        date, level = cell.get("data-date"), cell.get("data-level")
        if not date or level is None:
            continue
        if cell.get("data-count") is not None:            # legacy <rect> markup
            count = int(cell["data-count"])
        else:
            count = tips.get(cell.get("id", ""), 0)
        days.append({"date": date, "count": count, "level": int(level)})

    if not days:
        raise RuntimeError("no contribution cells found: GitHub markup may have changed")
    days.sort(key=lambda d: d["date"])
    return days


def demo_days(seed: int = 7) -> list[dict]:
    import numpy as np

    rng = np.random.default_rng(seed)
    today = dt.date.today()
    start = today - dt.timedelta(days=364 + (today.weekday() + 1) % 7)
    days, n = [], (today - start).days + 1
    trend = 1.5 + 2.5 * np.sin(np.linspace(0, 3 * np.pi, n)) ** 2
    for i in range(n):
        d = start + dt.timedelta(days=i)
        weekday_boost = 0.45 if d.weekday() >= 5 else 1.0
        c = int(rng.poisson(trend[i] * weekday_boost * rng.choice([0, 1, 1, 1, 2, 3])))
        days.append({"date": d.isoformat(), "count": c, "level": 0})
    return relevel(days)


def relevel(days: list[dict]) -> list[dict]:
    """Quartile levels on non-zero days, like GitHub (level 4 is the top bin)."""
    nz = sorted(d["count"] for d in days if d["count"] > 0)
    if not nz:
        return days
    q = [nz[int(len(nz) * p) - 1 if int(len(nz) * p) > 0 else 0] for p in (0.25, 0.5, 0.75)]
    for d in days:
        c = d["count"]
        d["level"] = 0 if c == 0 else 1 if c <= q[0] else 2 if c <= q[1] else 3 if c <= q[2] else 4
    return days


def stats(days: list[dict]) -> dict:
    counts = [d["count"] for d in days]
    total = sum(counts)

    longest = run = 0
    for c in counts:
        run = run + 1 if c > 0 else 0
        longest = max(longest, run)

    # current streak: today may still be empty, so start from yesterday in that case
    i = len(counts) - 1
    if i >= 0 and counts[i] == 0:
        i -= 1
    current = 0
    while i >= 0 and counts[i] > 0:
        current += 1
        i -= 1

    best = max(days, key=lambda d: d["count"]) if days else None
    monthly: OrderedDict[str, int] = OrderedDict()
    for d in days:
        monthly[d["date"][:7]] = monthly.get(d["date"][:7], 0) + d["count"]

    active = sum(1 for c in counts if c > 0)
    return {
        "total": total,
        "current_streak": current,
        "longest_streak": longest,
        "best_day": {"date": best["date"], "count": best["count"]} if best else None,
        "active_days": active,
        "mean_per_active_day": round(total / active, 2) if active else 0.0,
        "monthly": monthly,
    }


def main() -> None:
    demo = "--demo" in sys.argv
    days = demo_days() if demo else fetch(C.USERNAME)
    payload = {
        "username": C.USERNAME,
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "demo": demo,
        "days": days,
        "stats": stats(days),
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=1), encoding="utf-8")
    s = payload["stats"]
    print(f"wrote {OUT.relative_to(ROOT)}: {len(days)} days, {s['total']} contributions, "
          f"streak {s['current_streak']} (max {s['longest_streak']})")


if __name__ == "__main__":
    main()
