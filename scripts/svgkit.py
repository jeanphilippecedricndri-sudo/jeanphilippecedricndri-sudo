"""Shared SVG helpers: font embedding (subset Space Mono as base64) and escaping."""
from __future__ import annotations

import base64
import io
from functools import lru_cache
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parent.parent
FONT_DIR = ROOT / "fonts"


def esc(s: str) -> str:
    return escape(s, {'"': "&quot;"})


@lru_cache(maxsize=None)
def _subset_b64(weight: str, chars: str) -> str | None:
    path = FONT_DIR / f"SpaceMono-{weight}.ttf"
    if not path.exists():
        return None
    try:
        from fontTools import subset
    except ImportError:  # still renders with the fallback monospace stack
        return None
    opts = subset.Options()
    opts.layout_features = []
    opts.name_IDs = []
    opts.notdef_outline = True
    font = subset.load_font(str(path), opts)
    sub = subset.Subsetter(opts)
    sub.populate(text=chars + " ")
    sub.subset(font)
    buf = io.BytesIO()
    subset.save_font(font, buf, opts)
    return base64.b64encode(buf.getvalue()).decode()


def font_face_css(text: str, bold_text: str = "") -> str:
    """@font-face rules with only the glyphs actually used (keeps SVGs small).

    SVGs shown through <img> cannot fetch external fonts, so the font has to
    travel inside the file as a data URI.
    """
    chars = "".join(sorted(set(text)))
    css = []
    b64 = _subset_b64("Regular", chars)
    if b64:
        css.append(
            "@font-face{font-family:'Space Mono';font-weight:400;"
            f"src:url(data:font/ttf;base64,{b64}) format('truetype');}}"
        )
    if bold_text:
        bchars = "".join(sorted(set(bold_text)))
        b64b = _subset_b64("Bold", bchars)
        if b64b:
            css.append(
                "@font-face{font-family:'Space Mono';font-weight:700;"
                f"src:url(data:font/ttf;base64,{b64b}) format('truetype');}}"
            )
    return "".join(css)
