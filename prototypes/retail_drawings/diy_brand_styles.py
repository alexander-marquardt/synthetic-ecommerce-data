"""Marks and house styles of the four invented power-tool brands of the drill family (gen#191).

Torvane Tools, Marlowick, Harkwell Power and Stonemarsh sell the drills, drivers, bit sets, tool kits and
step ladders of :mod:`diy_tools`. Each draws its own name on its product images: a lockup (the name
beside, above or under the mark) with a mark and an arrangement no other brand uses.

:mod:`house_styles` imports this module last, so the four marks join ``MARKS`` and the four styles
join ``HOUSE_STYLES`` whichever module is imported first.
"""

# ruff: noqa: E501 -- the style table reads best whole (prototype only).

from __future__ import annotations

import house_styles as hs
from house_styles import H, _dot, _ring, _stroke


def m_bitspiral(c: str) -> list[str]:
    """A drill bit seen end-on: a stem with a spiral flute of zigzag strokes."""
    return [
        _stroke("M0,-.9 L0,.9", 0.12, c),
        _stroke("M-.5,-.5 L.5,-.2 M-.5,-.05 L.5,.25 M-.5,.4 L.5,.7", 0.1, c),
    ]


def m_marlow(c: str) -> list[str]:
    """A square set on its corner with a ring in the middle."""
    return [
        _stroke("M0,-.9 L.9,0 L0,.9 L-.9,0 Z", 0.12, c, "miter"),
        _ring(0, 0, 0.32, 0.1, c),
    ]


def m_hawkwing(c: str) -> list[str]:
    """Two stacked chevrons, a wing seen from below."""
    return [
        _stroke("M-.85,.1 L0,-.6 L.85,.1", 0.14, c),
        _stroke("M-.85,.7 L0,0 L.85,.7", 0.14, c),
    ]


def m_cairn(c: str) -> list[str]:
    """Three stones stacked, the widest at the bottom."""
    return [
        f'<ellipse cx="0" cy=".55" rx=".75" ry=".32" fill="{c}"/>',
        f'<ellipse cx="0" cy="-.05" rx=".5" ry=".27" fill="{c}"/>',
        _dot(0, -0.6, 0.22, c),
    ]


hs.MARKS.update(
    {"bitspiral": m_bitspiral, "marlow": m_marlow, "hawkwing": m_hawkwing, "cairn": m_cairn}
)

# fmt: off
#: Brand -> house style: every one a lockup, so the wordmark is the brand field.
STYLES = {
    "Torvane Tools":  H("#f2f4f0", "diagonal", "heavy",   "#d9541e", "#2b1a12", 1.3,  False, "sharp", "bitspiral", "mark_left",  "top_right",     "none", "sans",     700, "caps",      2.0),
    "Marlowick":      H("#f6f1ea", "dots",     "double",  "#8a5a2b", "#33241a", 0.9,  False, "round", "marlow",    "mark_above", "bottom_right",  "none", "serif",    700, "smallcaps", 1.0, True),
    "Harkwell Power": H("#eef2f7", "grid",     "ticks",   "#1f4e8c", "#14243d", 1.1,  True,  "sharp", "hawkwing",  "band_bottom","bottom_center","none", "humanist", 700, "title",     0.5),
    "Stonemarsh":     H("#eff3ec", "hatch",    "rounded", "#4f6b3a", "#1f2d17", 1.0,  False, "round", "cairn",     "pill",       "top_left", "none", "mono",     400, "lower",     0.5),
}
# fmt: on
hs.HOUSE_STYLES.update(STYLES)
