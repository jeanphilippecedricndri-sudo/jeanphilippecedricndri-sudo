"""Prep a portrait photo for ASCII conversion.

    python scripts/prep_photo.py source-photo.jpg

1. remove the background (rembg) so only the subject prints
2. boost local contrast with CLAHE so a flat-lit face gets real shadows
3. composite onto pure white so the background maps to the space glyph

Writes assets/source-prepped.png (grayscale).
"""
from __future__ import annotations

import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "source-prepped.png"


def remove_background(img: Image.Image) -> Image.Image:
    try:
        from rembg import remove
    except ImportError:
        print("rembg not installed: keeping the original background", file=sys.stderr)
        return img.convert("RGBA")
    return remove(img)


def main(src: str, clip_limit: float = 2.5, tile: int = 8) -> None:
    rgba = remove_background(Image.open(src).convert("RGB"))
    arr = np.asarray(rgba).astype(np.float32)
    rgb, alpha = arr[..., :3], arr[..., 3:4] / 255.0

    gray = cv2.cvtColor(rgb.astype(np.uint8), cv2.COLOR_RGB2GRAY)
    clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=(tile, tile))
    gray = clahe.apply(gray).astype(np.float32)

    white = np.full_like(gray, 255.0)
    out = gray * alpha[..., 0] + white * (1.0 - alpha[..., 0])

    # crop to the subject bounding box (+ small margin)
    ys, xs = np.where(alpha[..., 0] > 0.1)
    if len(xs):
        m = int(0.04 * max(out.shape))
        y0, y1 = max(ys.min() - m, 0), min(ys.max() + m, out.shape[0])
        x0, x1 = max(xs.min() - m, 0), min(xs.max() + m, out.shape[1])
        out = out[y0:y1, x0:x1]

    OUT.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(np.clip(out, 0, 255).astype(np.uint8), "L").save(OUT)
    (OUT.parent / ".caption").unlink(missing_ok=True)  # no caption under a portrait
    print(f"wrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("usage: python scripts/prep_photo.py <photo>")
    main(sys.argv[1])
