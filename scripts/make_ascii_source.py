"""Procedural ASCII sources (used when no photo is supplied).

    python scripts/make_ascii_source.py --kind paths     # default
    python scripts/make_ascii_source.py --kind candles
    python scripts/make_ascii_source.py --kind vol

Each kind renders a dark-on-white image to assets/source-prepped.png
(dark = dense glyphs) and writes its caption to assets/.caption.

paths    : Monte Carlo GBM, dS_t = mu S_t dt + sigma S_t dW_t, with 5/50/95% quantile bands
candles  : OHLC candlesticks with 20/50-day moving averages
vol      : sigma(k, T) = atm(T) + skew(T) k + conv(T) k^2 implied-vol surface
"""
from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "source-prepped.png"
CAPTION = ROOT / "assets" / ".caption"
RNG = np.random.default_rng(42)
FIGSIZE = (5.0, 6.2)   # portrait: the ASCII panel sits next to a tall card


def _fig():
    fig, ax = plt.subplots(figsize=FIGSIZE, dpi=160)
    ax.set_axis_off()
    fig.patch.set_facecolor("white")
    plt.subplots_adjust(0.02, 0.02, 0.98, 0.98)
    return fig, ax


def paths():
    n, steps, T, mu, sig = 14, 252, 1.0, 0.08, 0.24
    dt = T / steps
    z = RNG.standard_normal((n, steps))
    logS = np.cumsum((mu - 0.5 * sig**2) * dt + sig * np.sqrt(dt) * z, axis=1)
    S = 100 * np.exp(np.hstack([np.zeros((n, 1)), logS]))
    t = np.linspace(0, T, steps + 1)
    fig, ax = _fig()
    big = 100 * np.exp(np.cumsum((mu - 0.5 * sig**2) * dt
                                 + sig * np.sqrt(dt) * RNG.standard_normal((4000, steps)), axis=1))
    q05, q50, q95 = np.percentile(np.hstack([np.full((4000, 1), 100.0), big]), [5, 50, 95], axis=0)
    ax.fill_between(t, q05, q95, color="0.80", lw=0)
    for p in S:
        ax.plot(t, p, color="0.25", lw=1.8)
    ax.plot(t, q50, color="black", lw=5)
    ax.plot(t, q05, color="black", lw=3.2)
    ax.plot(t, q95, color="black", lw=3.2)
    return fig, "dS = μS dt + σS dW · GBM paths, 5/50/95%"


def candles():
    n = 36
    ret = RNG.standard_t(4, n) * 0.012 + 0.0015
    close = 100 * np.exp(np.cumsum(ret))
    open_ = np.r_[100, close[:-1]] * (1 + RNG.normal(0, 0.003, n))
    hi = np.maximum(open_, close) * (1 + np.abs(RNG.normal(0, 0.007, n)))
    lo = np.minimum(open_, close) * (1 - np.abs(RNG.normal(0, 0.007, n)))
    fig, ax = _fig()
    for i in range(n):
        up = close[i] >= open_[i]
        ax.vlines(i, lo[i], hi[i], color="black", lw=2.6)
        y0, h = min(open_[i], close[i]), abs(close[i] - open_[i]) or 0.05
        ax.add_patch(plt.Rectangle((i - 0.36, y0), 0.72, h,
                                   facecolor="0.72" if up else "black", edgecolor="black", lw=2.4))
    for w_, lw in ((10, 4.5), (25, 3.0)):
        ma = np.convolve(close, np.ones(w_) / w_, mode="valid")
        ax.plot(np.arange(w_ - 1, n), ma, color="black", lw=lw, ls="-" if w_ == 10 else (0, (4, 2)))
    ax.set_xlim(-1, n)
    return fig, "OHLC · MA(10) · MA(25)"


def vol():
    from matplotlib.colors import LightSource
    k = np.linspace(-0.5, 0.5, 120)
    T = np.linspace(0.15, 2.5, 90)
    K, TT = np.meshgrid(k, T)
    IV = (0.16 + 0.04 * (1 - np.exp(-TT))) - 0.18 / np.sqrt(TT + 0.25) * K + 0.35 / (TT + 0.4) * K**2
    fig = plt.figure(figsize=FIGSIZE, dpi=160)
    ax = fig.add_subplot(111, projection="3d")
    rgb = LightSource(azdeg=225, altdeg=35).shade(IV, cmap=plt.cm.gray_r, vert_exag=6,
                                                  blend_mode="soft", vmin=IV.min() - 0.45,
                                                  vmax=IV.max() + 0.02)
    ax.plot_surface(K, TT, IV, facecolors=rgb, rstride=1, cstride=1, linewidth=0, shade=False)
    ax.plot_wireframe(K, TT, IV, rstride=9, cstride=10, color="black", linewidth=0.9)
    ax.view_init(elev=26, azim=-52)
    ax.set_box_aspect((1.0, 1.1, 0.9))
    ax.set_axis_off()
    fig.patch.set_facecolor("white")
    plt.subplots_adjust(0, 0, 1, 1)
    return fig, "σ(k, T) · implied-vol surface"


KINDS = {"paths": paths, "candles": candles, "vol": vol}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--kind", choices=KINDS, default="paths")
    ap.add_argument("--out", type=Path, default=OUT)
    args = ap.parse_args()

    fig, caption = KINDS[args.kind]()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    tmp = args.out.with_suffix(".rgb.png")
    fig.savefig(tmp, facecolor="white")
    plt.close(fig)

    img = ImageOps.grayscale(Image.open(tmp))
    bbox = ImageOps.invert(img).point(lambda p: 255 if p > 12 else 0).getbbox()
    if bbox:
        pad = 10
        img = img.crop((max(bbox[0] - pad, 0), max(bbox[1] - pad, 0),
                        min(bbox[2] + pad, img.width), min(bbox[3] + pad, img.height)))
    if args.kind != "vol":
        from PIL import ImageFilter
        img = img.filter(ImageFilter.MinFilter(5))
    img.save(args.out)
    tmp.unlink()
    if args.out == OUT:
        CAPTION.write_text(caption, encoding="utf-8")
    print(f"wrote {args.out.name} ({args.kind})")


if __name__ == "__main__":
    main()
