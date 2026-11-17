"""Marks and house styles of the three invented paper-goods brands (#962).

Featherlee, Mossdown and Hollinsby sell the toilet paper, paper towels and facial tissues of the
Cleaning department (:mod:`paper_rows`). Each draws its own mark on its product images, a mark and
an arrangement no other brand uses.

:mod:`house_styles` imports this module last, so the three marks join ``MARKS`` and the three
styles join ``HOUSE_STYLES`` whichever module is imported first.
"""

# ruff: noqa: E501 -- the style table reads best whole (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail import house_styles as hs
from synthetic_ecommerce_data.domains.retail.house_styles import H, _dot, _ring, _stroke


def m_feather(c: str) -> list[str]:
    """A feather: a curved quill with a vane on either side of it."""
    return [
        f'<path d="M-.6,.8 Q-.1,.1 .55,-.8 Q.75,-.1 .1,.35 Q-.25,.55 -.6,.8 Z" fill="{c}"/>',
        _stroke("M-.75,.95 Q-.1,.1 .5,-.7", 0.06, "#ffffff"),
    ]


def m_cloud_puffs(c: str) -> list[str]:
    """A soft cloud: three overlapping puffs on a flat base."""
    return [
        _dot(-0.4, 0.15, 0.32, c),
        _dot(0.05, -0.15, 0.42, c),
        _dot(0.45, 0.15, 0.3, c),
        f'<rect x="-.72" y=".15" width="1.47" height=".32" rx=".12" fill="{c}"/>',
    ]


def m_holly_ring(c: str) -> list[str]:
    """A ring round two crossed leaves and a berry."""
    return [
        _ring(0, 0, 0.8, 0.09, c),
        f'<path d="M-.45,.35 Q-.35,-.25 .3,-.45 Q.2,.2 -.45,.35 Z" fill="{c}"/>',
        f'<path d="M.45,.35 Q.35,-.25 -.3,-.45 Q-.2,.2 .45,.35 Z" fill="{c}" opacity=".7"/>',
        _dot(0, 0.42, 0.12, c),
    ]


_MARKS = {"quill_feather": m_feather, "cloud_puffs": m_cloud_puffs, "holly_ring": m_holly_ring}
assert not set(_MARKS) & set(hs.MARKS), (
    "a paper-goods mark would replace a mark another brand draws"
)
hs.MARKS.update(_MARKS)

# fmt: off
#: Brand -> house style: one lockup and two marks alone, which keeps the lockup share near half.
STYLES = {
    "Featherlee": H("thin",    "#7a6fb0", "#2c2846", 0.9,  False, "round", "quill_feather", "mark_left",  "top_right",     "none",  "serif",    400, "title",     1.0, True),
    "Mossdown":   H("rounded", "#5f8a4a", "#24361c", 1.05, True,  "round", "cloud_puffs",   "mark_only",  "top_left",      "rect",  "humanist", 400, "lower",     2.0),
    "Hollinsby":  H("double",  "#a8323e", "#3d1418", 1.15, False, "sharp", "holly_ring",    "mark_only",  "bottom_left",   "stamp", "sans",     700, "smallcaps", 0.5),
}
# fmt: on
hs.HOUSE_STYLES.update(STYLES)
