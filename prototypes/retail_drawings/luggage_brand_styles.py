"""Marks and house styles of the three invented luggage brands (gen#209).

Tarnwick, Fenmoor & Co and Skerry Travel sell the suitcases, cabin cases, holdalls, weekend bags and
travel organizers (:mod:`luggage_common`). Each draws its own name on its product images: a lockup
(the name beside or under the mark) with a mark and an arrangement no other brand uses.

:mod:`house_styles` imports this module last, so the three marks join ``MARKS`` and the three
styles join ``HOUSE_STYLES`` whichever module is imported first.
"""

# ruff: noqa: E501 -- the style table reads best whole (prototype only).

from __future__ import annotations

import house_styles as hs
from house_styles import H, _dot, _ring, _stroke


def m_trunk(c: str) -> list[str]:
    """A case: a box with a carry handle and two clasps."""
    return [
        _stroke("M-.8,-.2 L.8,-.2 L.8,.8 L-.8,.8 Z", 0.12, c, "miter"),
        _stroke("M-.3,-.2 L-.3,-.7 L.3,-.7 L.3,-.2", 0.1, c),
        _dot(-0.4, 0.2, 0.08, c),
        _dot(0.4, 0.2, 0.08, c),
    ]


def m_tag(c: str) -> list[str]:
    """A luggage label: a shield with a punched hole and a strap loop above it."""
    return [
        f'<path d="M-.55,-.35 L.55,-.35 L.8,.15 L.55,.9 L-.55,.9 L-.8,.15 Z" fill="{c}"/>',
        _ring(0, -0.05, 0.14, 0.07, "#ffffff"),
        _stroke("M-.2,-.35 Q-.2,-.9 0,-.9 Q.2,-.9 .2,-.35", 0.09, c),
    ]


def m_bearing(c: str) -> list[str]:
    """A compass: a ring round a diamond needle."""
    return [
        _ring(0, 0, 0.8, 0.1, c),
        f'<path d="M0,-.6 L.2,0 L0,.6 L-.2,0 Z" fill="{c}"/>',
        _dot(0, 0, 0.07, "#ffffff"),
    ]


hs.MARKS.update({"trunk": m_trunk, "luggage_tag": m_tag, "bearing": m_bearing})

# fmt: off
#: Brand -> house style: every one a lockup, so the wordmark is the brand field.
STYLES = {
    "Tarnwick":      H("#f2f1ec", "lines",    "thin",    "#6b4a2f", "#2d2118", 1.1,  False, "sharp", "trunk",       "mark_left",  "bottom_left",   "none", "sans",     700, "caps",  2.0),
    "Fenmoor & Co":  H("#eef3f1", "none",     "rounded", "#2c6e63", "#17332e", 0.9,  False, "round", "luggage_tag", "mark_above", "top_right",     "none", "serif",    400, "title", 1.0, True),
    "Skerry Travel": H("#f3f5fa", "dots",     "ticks",   "#2f4f8a", "#16233f", 1.0,  False, "round", "bearing",     "badge",      "bottom_center", "none", "humanist", 700, "smallcaps", 1.5),
}
# fmt: on
hs.HOUSE_STYLES.update(STYLES)
