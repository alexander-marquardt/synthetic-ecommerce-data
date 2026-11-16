"""Marks and house styles of the four invented car care brands of the Automotive department (gen#970).

Glossmere sells detailing products, Kestrova wiper blades and fluids, Drayfield the everyday
range, and Ostrel air fresheners and wash accessories (:mod:`automotive_rows`). Each draws its own
name on its product images: two lockups (the name beside or above the mark) and two marks alone
with a text tag, each with a mark no other brand uses.

:mod:`automotive_rows` imports this module, so the four marks join ``MARKS`` and the four styles
join ``HOUSE_STYLES`` before any automotive record is drawn.
"""

# ruff: noqa: E501 -- the style table reads best whole (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail import house_styles as hs
from synthetic_ecommerce_data.domains.retail.house_styles import H, _dot, _stroke


def m_droplet(c: str) -> list[str]:
    """A water drop with a shine line."""
    return [
        _stroke("M0,-.9 Q.75,.05 .55,.45 Q.3,.9 0,.9 Q-.3,.9 -.55,.45 Q-.75,.05 0,-.9 Z", 0.11, c, "round"),
        _stroke("M-.25,.15 Q-.25,.5 .05,.6", 0.09, c),
    ]


def m_sweep(c: str) -> list[str]:
    """A wiper's sweep: an arc over its pivot."""
    return [
        _stroke("M-.85,.5 Q0,-1.05 .85,.5", 0.12, c),
        _stroke("M0,.6 L.55,-.35", 0.11, c),
        _dot(0.0, 0.6, 0.16, c),
    ]


def m_lane(c: str) -> list[str]:
    """A road in perspective: two edges and a dashed center line."""
    return [
        _stroke("M-.8,.85 L-.2,-.85", 0.11, c),
        _stroke("M.8,.85 L.2,-.85", 0.11, c),
        _stroke("M0,.75 L0,.4 M0,.1 L0,-.15 M0,-.4 L0,-.55", 0.09, c),
    ]


def m_leaf_tag(c: str) -> list[str]:
    """A hanging tag on its string: a rounded card with a leaf vein."""
    return [
        _stroke("M0,-.9 L0,-.55", 0.08, c),
        _stroke("M-.45,-.55 L.45,-.55 L.55,.75 Q0,1.0 -.55,.75 Z", 0.11, c, "round"),
        _stroke("M0,.6 L0,-.25 M0,.25 L.25,0 M0,.25 L-.25,0", 0.08, c),
    ]


hs.MARKS.update(
    {
        "droplet": m_droplet,
        "wiper_sweep": m_sweep,
        "road_lane": m_lane,
        "leaf_tag": m_leaf_tag,
    }
)

# fmt: off
#: Brand -> house style. Two lockups and two marks alone with a text tag.
STYLES = {
    "Glossmere": H("rounded", "#1d5c8c", "#0c2538", 1.05, False, "round", "droplet",     "mark_left",  "top_center",    "none",      "serif",    700, "title",     1.35, True),
    "Kestrova":  H("ticks",   "#3b4a59", "#151c23", 1.15, False, "sharp", "wiper_sweep", "mark_only",  "bottom_left",   "underline", "sans",     700, "caps",      2.15),
    "Drayfield": H("double",  "#a8461c", "#3d1808", 0.9,  True,  "sharp", "road_lane",   "mark_above", "top_left",      "none",      "mono",     700, "smallcaps", 0.55),
    "Ostrel":    H("thin",    "#4d7f2f", "#1c2f11", 1.25, False, "round", "leaf_tag",    "mark_only",  "top_right",      "plain",     "humanist", 400, "lower",     2.45),
}
# fmt: on
hs.HOUSE_STYLES.update(STYLES)
