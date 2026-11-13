"""Marks and house styles of the nine invented brands of the Pets department (gen#967).

Hound & Heath, Barkwell and Furrow & Field sell dog food, Whiskerby, Purrsey Lane and Furrow &
Field cat food, and Pinehollow, Clumpton and Whiskerby cat litter (:mod:`pets_rows`). Alley Cat
Larder and Kitten Mill are the brands of two text-match decoys. Each draws its own mark and name
on its product images, as every other invented brand does.

:mod:`house_styles` imports this module last, so the nine marks join ``MARKS`` and the nine
styles join ``HOUSE_STYLES`` whichever module is imported first.
"""

# ruff: noqa: E501 -- the style table reads best whole (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail import house_styles as hs
from synthetic_ecommerce_data.domains.retail.house_styles import H, _dot, _ring, _stroke


def m_paw(c: str) -> list[str]:
    """A paw print: a pad and four toes."""
    return [
        '<ellipse cx="0" cy=".35" rx=".42" ry=".34" fill="' + c + '"/>',
        _dot(-0.58, -0.2, 0.15, c), _dot(-0.2, -0.55, 0.16, c),
        _dot(0.2, -0.55, 0.16, c), _dot(0.58, -0.2, 0.15, c),
    ]  # fmt: skip


def m_bone(c: str) -> list[str]:
    """A dog's bone, level, with a knuckle at each end."""
    return [
        _stroke("M-.55,0 L.55,0", 0.26, c),
        _dot(-0.62, -0.16, 0.2, c), _dot(-0.62, 0.16, 0.2, c),
        _dot(0.62, -0.16, 0.2, c), _dot(0.62, 0.16, 0.2, c),
    ]  # fmt: skip


def m_furrow(c: str) -> list[str]:
    """A ploughed field: three furrows under a rising sun."""
    return [
        _ring(0, -0.25, 0.38, 0.12, c),
        _stroke("M-.85,.25 Q0,.05 .85,.25 M-.85,.5 Q0,.3 .85,.5 M-.85,.75 Q0,.55 .85,.75", 0.1, c),
    ]


def m_whisker(c: str) -> list[str]:
    """A cat's face: two ears, and three whiskers each side."""
    return [
        f'<path d="M-.6,.6 L-.6,-.35 L-.35,-.75 L-.1,-.4 L.1,-.4 L.35,-.75 L.6,-.35 L.6,.6 Z" fill="{c}"/>',
        _stroke("M-.95,.05 L-.45,.15 M-.95,.3 L-.45,.3 M-.95,.55 L-.45,.45 "
                "M.95,.05 L.45,.15 M.95,.3 L.45,.3 M.95,.55 L.45,.45", 0.07, c),
    ]  # fmt: skip


def m_lane_gate(c: str) -> list[str]:
    """A garden gate: a ring over two posts."""
    return [_ring(0, -0.35, 0.4, 0.1, c), _stroke("M-.55,.9 L-.55,0 M.55,.9 L.55,0 M-.55,.45 L.55,.45", 0.14, c)]


def m_pine(c: str) -> list[str]:
    """A pine in a hollow: a three-tier tree over a dip."""
    return [
        f'<path d="M0,-.9 L.5,-.2 L.25,-.2 L.65,.35 L-.65,.35 L-.25,-.2 L-.5,-.2 Z" fill="{c}"/>',
        _stroke("M-.85,.55 Q0,.95 .85,.55", 0.12, c),
    ]


def m_clump(c: str) -> list[str]:
    """A clump: three granules gathered in a scoop."""
    return [
        _dot(-0.3, -0.1, 0.24, c), _dot(0.3, -0.1, 0.24, c), _dot(0, -0.45, 0.24, c),
        _stroke("M-.8,.25 Q0,.85 .8,.25", 0.14, c),
    ]  # fmt: skip


def m_larder(c: str) -> list[str]:
    """A larder shelf: a crescent moon over a shelf of two jars."""
    return [
        f'<path d="M-.2,-.9 A.45,.45 0 1 0 .3,-.25 A.35,.35 0 1 1 -.2,-.9 Z" fill="{c}"/>',
        f'<rect x="-.7" y=".05" width=".5" height=".55" rx=".08" fill="{c}"/>',
        f'<rect x=".2" y="-.05" width=".5" height=".65" rx=".08" fill="{c}"/>',
        _stroke("M-.9,.75 L.9,.75", 0.12, c),
    ]


def m_mill_wheel(c: str) -> list[str]:
    """A water mill's wheel: a ring with six paddles."""
    return [
        _ring(0, 0, 0.55, 0.12, c),
        _stroke("M0,-.95 L0,.95 M-.82,-.47 L.82,.47 M-.82,.47 L.82,-.47", 0.1, c),
        _dot(0, 0, 0.14, c),
    ]


hs.MARKS.update({
    "heath_paw": m_paw, "dog_bone": m_bone, "furrowed_field": m_furrow, "cat_face": m_whisker,
    "lane_gate": m_lane_gate, "hollow_pine": m_pine, "litter_clump": m_clump,
    "larder_moon": m_larder, "mill_wheel": m_mill_wheel,
})  # fmt: skip

# fmt: off
#: Brand -> house style: five lockups and four marks alone, as about half the table is.
STYLES = {
    "Hound & Heath":    H("double",  "#7a4a26", "#33200f", 1.05, False, "round", "heath_paw",      "mark_left",  "top_left",      "none",      "serif",    700, "title",     0.5),
    "Barkwell":         H("heavy",   "#b13a2a", "#4a170f", 1.15, False, "round", "dog_bone",       "mark_only",  "top_right",     "flag",      "sans",     700, "caps",      2.0),
    "Furrow & Field":   H("thin",    "#4f7a2a", "#223512", 0.95, False, "round", "furrowed_field", "mark_above", "top_center",    "none",      "humanist", 400, "title",     0.0),
    "Whiskerby":        H("rounded", "#6a3f8a", "#2c1a3a", 1.0,  False, "round", "cat_face",       "pill",       "top_left",      "none",      "humanist", 700, "lower",     0.5),
    "Purrsey Lane":     H("none",    "#c0577a", "#4e2131", 0.9,  False, "round", "lane_gate",      "mark_only",  "bottom_left",   "underline", "serif",    400, "smallcaps", 1.5, True),
    "Pinehollow":       H("ticks",   "#2e5e4a", "#13281f", 1.1,  False, "sharp", "hollow_pine",    "mark_right", "top_right",     "none",      "sans",     400, "caps",      2.5),
    "Clumpton":         H("double",  "#4a6a8a", "#1d2a37", 1.0,  True,  "round", "litter_clump",   "mark_only",  "top_left",      "rect",      "mono",     700, "lower",     0.0),
    "Alley Cat Larder": H("heavy",   "#3a3a5e", "#181828", 1.2,  False, "sharp", "larder_moon",    "mark_left",  "bottom_center", "none",      "serif",    700, "caps",      1.0, True),
    "Kitten Mill":      H("thin",    "#a8742a", "#45300f", 0.9,  False, "round", "mill_wheel",     "mark_only",  "bottom_right",  "plain",     "humanist", 400, "title",     1.0),
}
# fmt: on
hs.HOUSE_STYLES.update(STYLES)
