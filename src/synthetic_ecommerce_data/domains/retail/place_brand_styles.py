"""Marks and house styles of the fifteen place brands (gen#663, decoy class 6).

A class 6 decoy ("Cardigan Bay Running Shoes") puts a garment word in a place-like name. The
place name is the decoy's brand: the brand field holds "Cardigan Bay" and the title keeps the
trap word. Each place brand draws its own name on its product images: a dedicated house style
(never the generic lockup) whose wordmark is the brand field, spelled the way the title spells
it, and a simple geometric mark that does not draw the garment word. A place brand belongs to
its decoys alone (a place name is never a model name under another brand).

:mod:`house_styles` imports this module last, so the fifteen marks join ``MARKS`` and the
fifteen styles join ``HOUSE_STYLES`` whichever module is imported first.
"""

# ruff: noqa: E501 -- the style table reads best whole (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail import house_styles as hs
from synthetic_ecommerce_data.domains.retail.house_styles import H, _dot, _ring, _stroke


def m_lane(c: str) -> list[str]:
    """A road running to the horizon: two edges and a dashed center line."""
    return [_stroke("M-.55,.9 L-.15,-.9 M.55,.9 L.15,-.9", 0.12, c), _stroke("M0,.8 L0,.5 M0,.25 L0,.0 M0,-.25 L0,-.45", 0.09, c)]


def m_hook(c: str) -> list[str]:
    """A wall bar with one curved peg."""
    return [_stroke("M-.8,-.7 L.8,-.7", 0.14, c), _stroke("M0,-.7 L0,.4 Q0,.85 .4,.85 Q.7,.85 .7,.45", 0.13, c)]


def m_row(c: str) -> list[str]:
    """A terrace: three equal doors in a line over a ground bar."""
    doors = "".join(f'<rect x="{x}" y="-.4" width=".42" height=".8" fill="none" stroke="{c}" stroke-width=".09"/>' for x in ("-.75", "-.21", ".33"))
    return [doors, _stroke("M-.9,.65 L.9,.65", 0.1, c)]


def m_circle_seats(c: str) -> list[str]:
    """Tiered seats: two half-rings over a stage bar."""
    return [_stroke("M-.85,.4 A.85,.85 0 0 1 .85,.4", 0.11, c), _stroke("M-.5,.4 A.5,.5 0 0 1 .5,.4", 0.11, c), _stroke("M-.9,.75 L.9,.75", 0.12, c)]


def m_hill(c: str) -> list[str]:
    """A rounded hill under a small flag."""
    return [f'<path d="M-.95,.7 Q-.4,-.4 0,-.3 Q.5,-.3 .95,.7 Z" fill="{c}"/>', _stroke("M0,-.3 L0,-.9", 0.07, c), f'<path d="M0,-.9 L.4,-.75 L0,-.6 Z" fill="{c}"/>']


def m_point(c: str) -> list[str]:
    """A headland: a triangle narrowing to a point, with the sea line under it."""
    return [f'<path d="M-.7,.5 L.1,-.85 L.7,.5 Z" fill="none" stroke="{c}" stroke-width=".12" stroke-linejoin="round"/>', _stroke("M-.9,.8 L.9,.8", 0.09, c)]


def m_quay(c: str) -> list[str]:
    """A landing stage: a deck on three posts over the water."""
    return [_stroke("M-.9,-.35 L.9,-.35", 0.14, c), _stroke("M-.6,-.35 L-.6,.55 M0,-.35 L0,.55 M.6,-.35 L.6,.55", 0.1, c), _stroke("M-.9,.8 Q-.6,.65 -.3,.8 T.3,.8 T.9,.8", 0.07, c)]


def m_hop(c: str) -> list[str]:
    """Two stepping dots joined by a leaping arc."""
    return [_dot(-0.6, 0.55, 0.22, c), _dot(0.6, 0.55, 0.22, c), _stroke("M-.6,.3 Q0,-1.0 .6,.3", 0.1, c)]


def m_stones(c: str) -> list[str]:
    """Three stepping stones set across a path."""
    return [
        f'<ellipse cx="-.55" cy=".55" rx=".3" ry=".18" fill="{c}"/>',
        f'<ellipse cx="0" cy="0" rx=".3" ry=".18" fill="{c}"/>',
        f'<ellipse cx=".55" cy="-.55" rx=".3" ry=".18" fill="{c}"/>',
    ]


def m_bay(c: str) -> list[str]:
    """A curved coast cupping a round of water."""
    return [_stroke("M-.85,-.7 Q-.85,.9 .85,.9", 0.13, c), _ring(0.15, 0.2, 0.28, 0.07, c)]


def m_court(c: str) -> list[str]:
    """A court plan: a box, a halfway line and a center circle."""
    return [f'<rect x="-.85" y="-.55" width="1.7" height="1.1" fill="none" stroke="{c}" stroke-width=".1"/>', _stroke("M0,-.55 L0,.55", 0.08, c), _ring(0.0, 0.0, 0.28, 0.08, c)]


def m_brook(c: str) -> list[str]:
    """Two threads of water over a pebble."""
    return [_stroke("M-.9,-.3 Q-.6,-.55 -.3,-.3 T.3,-.3 T.9,-.3", 0.1, c), _stroke("M-.9,.1 Q-.6,-.15 -.3,.1 T.3,.1 T.9,.1", 0.1, c), _dot(0.0, 0.62, 0.2, c)]


def m_rings(c: str) -> list[str]:
    """The cut end of a log: growth rings round a heart."""
    return [_ring(0.0, 0.0, 0.85, 0.09, c), _ring(0.0, 0.0, 0.55, 0.09, c), _dot(0.0, 0.0, 0.18, c)]


def m_spout(c: str) -> list[str]:
    """A village pump: a post, a handle and a drop beneath the spout."""
    return [_stroke("M-.2,.85 L-.2,-.4 L.4,-.4 L.4,-.1", 0.13, c), _stroke("M-.2,-.4 L-.75,-.85", 0.1, c), f'<path d="M.4,.15 Q.2,.5 .4,.65 Q.6,.5 .4,.15 Z" fill="{c}"/>']


def m_fork(c: str) -> list[str]:
    """A road that splits: one stem into two branches."""
    return [_stroke("M0,.9 L0,.1 L-.6,-.8 M0,.1 L.6,-.8", 0.13, c), _dot(0.0, 0.9, 0.1, c)]


NEW_MARKS = {
    "pl_lane": m_lane, "pl_hook": m_hook, "pl_row": m_row, "pl_seats": m_circle_seats,
    "pl_hill": m_hill, "pl_point": m_point, "pl_quay": m_quay, "pl_hop": m_hop,
    "pl_stones": m_stones, "pl_bay": m_bay, "pl_court": m_court, "pl_brook": m_brook,
    "pl_rings": m_rings, "pl_spout": m_spout, "pl_fork": m_fork,
}  # fmt: skip
hs.MARKS.update(NEW_MARKS)

# fmt: off
#: Brand -> house style: every lockup (the name is drawn beside or under the mark), none
#: a mark-only tag, so the wordmark is the brand field in title or small-caps case. No two
#: share a mark, nor an arrangement and wordmark (:func:`house_styles.lockup_key`).
STYLES = {
    "Jumper Lane":   H("#f4f1ea", "none",     "thin",    "#8a5a2b", "#3a2a18", 1.0,  False, "round", "pl_lane",   "mark_left",  "top_left",      "none", "humanist", 700, "title",     0.15),
    "Coat Hook":     H("#eef2f5", "lines",    "double",  "#3b5b78", "#1f2f3f", 1.1,  False, "sharp", "pl_hook",   "mark_above", "top_center",    "none", "serif",    700, "title",     0.25),
    "Shirt Mews":    H("#fbf3e6", "dots",     "none",    "#b5651d", "#4a2b10", 0.9,  False, "round", "pl_row",    "mark_right", "bottom_left",   "none", "sans",     400, "title",     0.35),
    "Dress Circle":  H("#f6eef3", "none",     "rounded", "#8e3b6e", "#3d1a30", 0.8,  False, "round", "pl_seats",  "badge",      "bottom_center", "none", "serif",    400, "smallcaps", 0.45),
    "Boot Hill":     H("#eef3ea", "hatch",    "heavy",   "#4c7a34", "#22361a", 1.3,  False, "sharp", "pl_hill",   "band_bottom","bottom_center", "none", "mono",     700, "title",     0.55),
    "Skirt Point":   H("#fdf0ee", "diagonal", "thin",    "#c04a3a", "#4a1d17", 1.0,  True,  "sharp", "pl_point",  "pill",       "top_right",     "none", "sans",     700, "smallcaps", 0.65),
    "Jacket Quay":   H("#eaf3f4", "grid",     "ticks",   "#1f7a84", "#12363b", 1.2,  False, "sharp", "pl_quay",   "band_top",   "top_center",    "none", "humanist", 400, "title",     0.75),
    "Sock Hop":      H("#fff4d9", "none",     "double",  "#d98a1c", "#4d3208", 1.1,  False, "round", "pl_hop",    "mark_left",  "bottom_right",  "none", "humanist", 700, "title",     0.85, True),
    "Shoe Lane":     H("#f1efe9", "dots",     "none",    "#6b5d4a", "#2b241a", 0.9,  False, "round", "pl_stones", "mark_above", "bottom_left",   "none", "mono",     400, "smallcaps", 0.95),
    "Cardigan Bay":  H("#e9f1f8", "lines",    "rounded", "#2c6ea6", "#162f48", 0.85, False, "round", "pl_bay",    "mark_right", "top_left",      "none", "serif",    700, "smallcaps", 1.05, True),
    "Blazer Court":  H("#efefef", "none",     "heavy",   "#2f3b4a", "#161c24", 1.4,  False, "sharp", "pl_court",  "badge",      "top_right",     "none", "sans",     700, "title",     1.15),
    "Slipper Brook": H("#eef6f0", "diagonal", "thin",    "#3a8f6e", "#17382b", 0.8,  True,  "round", "pl_brook",  "pill",       "bottom_right",  "none", "serif",    400, "title",     1.25),
    "Sandal Wood":   H("#f7efe3", "hatch",    "ticks",   "#a0693a", "#40250f", 1.0,  False, "sharp", "pl_rings",  "band_bottom","bottom_center", "none", "humanist", 700, "smallcaps", 1.35),
    "Pump Lane":     H("#f0f3f9", "grid",     "none",    "#4a5fb0", "#1d2650", 1.2,  False, "sharp", "pl_spout",  "mark_left",  "bottom_center", "none", "mono",     700, "title",     1.45),
    "Slip Road":     H("#f5f0f6", "none",     "thin",    "#7a4a9a", "#2e1a3d", 0.9,  False, "round", "pl_fork",   "mark_above", "bottom_right",  "none", "sans",     400, "smallcaps", 1.55),
}
# fmt: on
hs.HOUSE_STYLES.update(STYLES)
