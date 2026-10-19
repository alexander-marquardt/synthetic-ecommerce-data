"""Marks and house styles of the five invented fruit-word brands (gen#445, decoy class 9).

"Lucky Lemons" and the four other labels of :data:`decoy_plural_nonfood_rows.BRANDS` sell plain
kidswear whose title shows the brand and whose drawing carries no fruit: the word is the label,
not the picture. Each brand draws its own name on its product images in a dedicated house style
(the wordmark is the brand field), with a simple geometric mark that is not a fruit.
"""

# ruff: noqa: E501 -- the style table reads best whole (prototype only).

from __future__ import annotations

import house_styles as hs
from house_styles import H, _dot, _ring, _stroke


def m_clover(c: str) -> list[str]:
    """Three dots round a short stem."""
    return [_dot(-0.4, -0.2, 0.35, c), _dot(0.4, -0.2, 0.35, c), _dot(0.0, 0.4, 0.35, c), _stroke("M0,.3 L0,.95", 0.1, c)]


def m_spiral(c: str) -> list[str]:
    """A ring with a dot at its center."""
    return [_ring(0.0, 0.0, 0.8, 0.12, c), _dot(0.0, 0.0, 0.25, c)]


def m_cushion(c: str) -> list[str]:
    """A rounded square with a cross-stitch."""
    return [f'<rect x="-.8" y="-.8" width="1.6" height="1.6" rx=".3" fill="none" stroke="{c}" stroke-width=".12"/>', _stroke("M-.4,-.4 L.4,.4 M.4,-.4 L-.4,.4", 0.1, c)]


def m_acorn(c: str) -> list[str]:
    """A small seed with a stalk."""
    return [_dot(0.0, 0.2, 0.6, c), _stroke("M0,-.4 L0,-.9", 0.12, c)]


def m_smile(c: str) -> list[str]:
    """Two dots over a smile."""
    return [_dot(-0.35, -0.3, 0.14, c), _dot(0.35, -0.3, 0.14, c), _stroke("M-.6,.2 Q0,.9 .6,.2", 0.12, c)]


hs.MARKS.update({"clover": m_clover, "spiral": m_spiral, "cushion": m_cushion, "acorn": m_acorn, "smile": m_smile})

# fmt: off
STYLES = {
    "Lucky Lemons":   H("#fffdf0", "dots",     "rounded", "#d8b320", "#3f3510", 1.0, False, "round", "clover",  "mark_left",  "top_left",      "none", "sans",     700, "title",     0.5),
    "Going Bananas":  H("#fff9e8", "lines",    "thin",    "#e0a82e", "#4a3a10", 0.9, False, "round", "smile",   "mark_above", "bottom_center", "none", "humanist", 400, "title",     1.0),
    "Couch Potatoes": H("#f6f1ea", "none",     "double",  "#8a6a45", "#3a2c1c", 1.1, False, "sharp", "cushion", "band_top",   "top_center",    "none", "serif",    700, "smallcaps", 1.0),
    "Little Carrots": H("#fff2e8", "hatch",    "ticks",   "#d9732b", "#4a2410", 1.0, True,  "round", "acorn",   "badge",      "bottom_right",  "none", "sans",     400, "title",     0.0),
    "Happy Onions":   H("#f8f1f6", "diagonal", "heavy",   "#a5568a", "#33182c", 1.2, False, "sharp", "spiral",  "pill",       "top_right",     "none", "mono",     700, "title",     0.5),
}
# fmt: on
hs.HOUSE_STYLES.update(STYLES)
