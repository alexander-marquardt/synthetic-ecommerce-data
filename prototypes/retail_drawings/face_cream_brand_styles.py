"""Marks and house styles of the five invented face cream brands (gen#542).

Cleary Dew, Pellam Labs, Wyncombe Skin, Lorimer & Vale and Sorrene Atelier sell the day, night and
SPF face creams of :mod:`type_specs.face_cream`. Each draws its own name on its product images: a
lockup (the name beside, above or inside a band with the mark) with a mark and an arrangement no
other brand uses. The names are invented; none is a brand the author knows to exist (the PR for
gen#542 says whether a web check was possible).

:mod:`house_styles` imports this module last, so the five marks join ``MARKS`` and the five styles
join ``HOUSE_STYLES`` whichever module is imported first.
"""

# ruff: noqa: E501 -- the style table reads best whole (prototype only).

from __future__ import annotations

import house_styles as hs
from house_styles import H, _dot, _ring, _stroke


def m_pot_lid(c: str) -> list[str]:
    """A cream pot: a wide lid over a rounded body, with a small label bar."""
    return [
        f'<rect x="-.8" y="-.7" width="1.6" height=".3" rx=".1" fill="{c}"/>',
        f'<rect x="-.65" y="-.3" width="1.3" height="1" rx=".3" fill="{c}"/>',
        _stroke("M-.25,.2 L.25,.2", 0.1, "#ffffff"),
    ]


def m_ring_square(c: str) -> list[str]:
    """A ring round a small square: a clinical seal."""
    return [
        _ring(0, 0, 0.8, 0.1, c),
        f'<rect x="-.28" y="-.28" width=".56" height=".56" fill="{c}"/>',
    ]


def m_fern(c: str) -> list[str]:
    """A fern frond: a curved stem with three pairs of leaflets."""
    return [
        _stroke("M0,.85 Q.1,0 0,-.8", 0.1, c),
        _stroke("M0,.45 L-.5,.15 M0,.45 L.5,.15", 0.1, c),
        _stroke("M0,0 L-.42,-.28 M0,0 L.42,-.28", 0.1, c),
        _stroke("M0,-.4 L-.3,-.6 M0,-.4 L.3,-.6", 0.1, c),
    ]


def m_swirl(c: str) -> list[str]:
    """A dollop of cream: a spiral that winds in to a dot."""
    return [
        _stroke("M-.7,.4 Q-.7,-.7 .1,-.7 Q.7,-.7 .7,-.05 Q.7,.5 .1,.5 Q-.35,.5 -.35,.05", 0.12, c),
        _dot(0.05, 0.02, 0.1, c),
    ]


def m_half_sun(c: str) -> list[str]:
    """A sun on the horizon: a half disc with three rays."""
    return [
        f'<path d="M-.6,.45 A.6,.6 0 0 1 .6,.45 Z" fill="{c}"/>',
        _stroke("M0,-.35 L0,-.85 M-.55,-.15 L-.85,-.45 M.55,-.15 L.85,-.45", 0.1, c),
        _stroke("M-.85,.75 L.85,.75", 0.1, c),
    ]


hs.MARKS.update(
    {
        "pot_lid": m_pot_lid,
        "ring_square": m_ring_square,
        "fern": m_fern,
        "swirl": m_swirl,
        "half_sun": m_half_sun,
    }
)

# fmt: off
#: Brand -> house style: every one a lockup, so the wordmark is the brand field.
STYLES = {
    "Cleary Dew":     H("#eef5fb", "dots",  "thin",    "#1f7ab8", "#0f3550", 0.85, False, "round", "pot_lid",     "mark_left",  "top_left",      "none", "sans",     700, "title",     0.3),
    "Pellam Labs":    H("#f6f9f8", "grid",  "ticks",   "#2a8f86", "#10332f", 1.15, False, "sharp", "ring_square", "badge",      "top_center",    "none", "mono",     400, "caps",      1.8),
    "Wyncombe Skin":  H("#f6f4ec", "lines", "rounded", "#6d8a3c", "#2c3a18", 0.95, False, "round", "fern",        "mark_above", "bottom_left",   "none", "serif",    400, "smallcaps", 1.3, True),
    "Lorimer & Vale": H("#fbf3ee", "none",  "double",  "#b4573b", "#43231a", 1.05, False, "sharp", "swirl",       "pill",       "bottom_right",  "none", "humanist", 700, "lower",     0.7),
    "Sorrene Atelier": H("#efeaf3", "none", "thin",    "#3d2a5e", "#1e1433", 0.8,  False, "sharp", "half_sun",    "band_top",   "top_center",    "none", "serif",    400, "caps",      2.2),
}
# fmt: on
hs.HOUSE_STYLES.update(STYLES)
