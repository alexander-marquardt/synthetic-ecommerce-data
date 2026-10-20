"""Marks and house styles of the six invented large appliance brands (gen#334).

Frostholm, Brimwell, Tavorne, Hollinmere, Cleavewick and Lunden & Voss sell the fridges,
dishwashers and laundry appliances of :mod:`large_appliance_rows`. Each draws its own name on its
product images: three lockups (the name beside, above or in a badge with the mark) and three marks
alone with a text tag, each with a mark no other brand uses.

:mod:`house_styles` imports this module last, so the six marks join ``MARKS`` and the six styles
join ``HOUSE_STYLES`` whichever module is imported first.
"""

# ruff: noqa: E501 -- the style table reads best whole (prototype only).

from __future__ import annotations

import house_styles as hs
from house_styles import H, _dot, _ring, _stroke


def m_frost_star(c: str) -> list[str]:
    """Frost: a six-armed star of three crossing strokes."""
    return [
        _stroke("M0,-.85 L0,.85", 0.1, c),
        _stroke("M-.74,-.43 L.74,.43", 0.1, c),
        _stroke("M-.74,.43 L.74,-.43", 0.1, c),
        _dot(0, 0, 0.12, c),
    ]


def m_brim_bowl(c: str) -> list[str]:
    """A bowl filled to the brim: a half disc under a rim line."""
    return [
        f'<path d="M-.8,-.05 L.8,-.05 Q.8,.8 0,.8 Q-.8,.8 -.8,-.05 Z" fill="{c}"/>',
        _stroke("M-.9,-.3 L.9,-.3", 0.1, c),
    ]


def m_pennant(c: str) -> list[str]:
    """A pennant: a tall pole with a swallow-tail flag."""
    return [
        _stroke("M-.55,-.85 L-.55,.85", 0.12, c),
        f'<path d="M-.5,-.8 L.8,-.8 L.35,-.35 L.8,.1 L-.5,.1 Z" fill="{c}"/>',
    ]


def m_holly(c: str) -> list[str]:
    """Holly: a pointed leaf with two berries."""
    return [
        f'<path d="M-.8,.2 L-.45,-.3 L-.2,0 L.1,-.5 L.3,-.1 L.8,-.2 L.4,.3 L.1,.15 L-.15,.55 L-.4,.3 Z" fill="{c}"/>',
        _dot(-0.2, 0.75, 0.13, c),
        _dot(0.2, 0.75, 0.13, c),
    ]


def m_wick(c: str) -> list[str]:
    """A flame split by a wick: a teardrop with a line down its middle."""
    return [
        f'<path d="M0,-.9 Q.8,-.1 .55,.5 Q.3,.9 0,.9 Q-.3,.9 -.55,.5 Q-.8,-.1 0,-.9 Z" fill="{c}"/>',
        _stroke("M0,-.3 L0,.9", 0.09, "#ffffff"),
    ]


def m_double_slash(c: str) -> list[str]:
    """Two parallel slashes inside a ring."""
    return [
        _ring(0, 0, 0.82, 0.09, c),
        _stroke("M-.25,.5 L.15,-.5", 0.14, c),
        _stroke("M.1,.5 L.5,-.5", 0.14, c),
    ]


hs.MARKS.update(
    {
        "frost_star": m_frost_star,
        "brim_bowl": m_brim_bowl,
        "pennant": m_pennant,
        "holly": m_holly,
        "wick": m_wick,
        "double_slash": m_double_slash,
    }
)

# fmt: off
#: Brand -> house style: three lockups (the wordmark is the brand field), three marks with a tag.
STYLES = {
    "Frostholm":      H("#eef4f8", "none",     "thin",    "#2f6f9a", "#17364d", 1.0,  False, "sharp", "frost_star",   "mark_left",  "top_left",      "none",      "sans",     700, "caps",      3.5),
    "Brimwell":       H("#f6f3ec", "dots",     "rounded", "#a2562f", "#43251a", 1.1,  False, "round", "brim_bowl",    "mark_only",  "bottom_left",   "rect",      "humanist", 400, "title",     0.5),
    "Tavorne":        H("#f1f4ee", "lines",    "double",  "#5b7f3a", "#26331a", 0.95, True,  "sharp", "pennant",      "mark_only",  "top_right",     "flag",      "serif",    700, "smallcaps", 2.5),
    "Hollinmere":     H("#f2f0f5", "grid",     "heavy",   "#6a3f8c", "#2c1a3e", 1.05, False, "round", "holly",        "mark_above", "bottom_right",  "none",      "serif",    400, "title",     0.5),
    "Cleavewick":     H("#faf2e8", "diagonal", "none",    "#c27a1c", "#4b2d0b", 0.9,  False, "sharp", "wick",         "mark_only",  "bottom_right",  "underline", "mono",     400, "lower",     3.5),
    "Lunden & Voss":  H("#f0f1f3", "hatch",    "ticks",   "#3b4a5a", "#161c24", 1.2,  False, "round", "double_slash", "badge",      "top_center",    "none",      "sans",     400, "smallcaps", 4.0, True),
}
# fmt: on
hs.HOUSE_STYLES.update(STYLES)
