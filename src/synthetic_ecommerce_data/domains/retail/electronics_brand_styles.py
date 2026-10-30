"""Marks and house styles of the 17 invented electronics brands (gen#332, #721, #724).

Grape Computer, Halvern, Torvane, Nimbrel, Quorrin, Daskel, Mervane and Pellimar sell the phones, laptops,
desktops, tablets and e-readers of the Electronics department (:mod:`electronics_rows`). Cindrel,
Boltwick, Wexmoor, Dunvale, Ardmoor and Marrick sell its accessories: cases, protectors, chargers,
cables, earbuds, sleeves, mice, keyboards and monitors. Grape Computer, Xell and PackingHarder
(#721) sell computers across departments: PackingHarder also sells monitors and the volt meters
of Home > DIY & Tools. FlyingFoo (#724) sells compatible cases and screen protectors. Each draws its
own name on its product
images: a lockup (the name beside, above or in a badge with the mark) or a mark alone with a text
tag, with a mark no other brand uses.

:mod:`house_styles` imports this module last, so the 17 marks join ``MARKS`` and the 17 styles
join ``HOUSE_STYLES`` whichever module is imported first.
"""

# ruff: noqa: E501 -- the style table reads best whole (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail import house_styles as hs
from synthetic_ecommerce_data.domains.retail.house_styles import H, _dot, _ring, _stroke


def m_vine(c: str) -> list[str]:
    """A sprig: a curled stem over three berries."""
    return [
        _stroke("M0,-.35 Q.05,-.75 .5,-.85", 0.1, c),
        _dot(-0.4, 0.0, 0.3, c),
        _dot(0.4, 0.0, 0.3, c),
        _dot(0.0, 0.6, 0.3, c),
    ]


def m_slab(c: str) -> list[str]:
    """A handset: a tall rounded slab with a speaker slot."""
    return [
        _stroke("M-.45,-.9 L.45,-.9 L.45,.9 L-.45,.9 Z", 0.12, c, "round"),
        _stroke("M-.15,-.65 L.15,-.65", 0.09, c),
    ]


def m_hinge(c: str) -> list[str]:
    """A laptop seen side on: a lid leaning on a base."""
    return [
        _stroke("M-.8,.55 L.8,.55", 0.14, c),
        _stroke("M-.6,.55 L-.35,-.75 L.45,-.75 L.7,.55", 0.1, c, "miter"),
    ]


def m_fins(c: str) -> list[str]:
    """A tower: a tall box with three vent bars."""
    return [
        _stroke("M-.5,-.9 L.5,-.9 L.5,.9 L-.5,.9 Z", 0.11, c, "miter"),
        _stroke("M-.25,-.45 L.25,-.45", 0.09, c),
        _stroke("M-.25,-.1 L.25,-.1", 0.09, c),
        _stroke("M-.25,.25 L.25,.25", 0.09, c),
    ]


def m_pane(c: str) -> list[str]:
    """A tablet: a wide pane with a lens dot on its edge."""
    return [
        _stroke("M-.85,-.6 L.85,-.6 L.85,.6 L-.85,.6 Z", 0.12, c, "round"),
        _dot(-0.62, 0, 0.07, c),
    ]


def m_orbit(c: str) -> list[str]:
    """Two crossing orbits round a core."""
    return [
        _ring(0, 0, 0.75, 0.08, c),
        _stroke("M-.9,.3 Q0,-.9 .9,-.3", 0.08, c),
        _dot(0, 0, 0.16, c),
    ]


def m_pixels(c: str) -> list[str]:
    """A 2 x 2 grid of squares, one of them missing."""
    return [
        f'<rect x="-.8" y="-.8" width=".7" height=".7" fill="{c}"/>',
        f'<rect x=".1" y="-.8" width=".7" height=".7" fill="{c}"/>',
        f'<rect x="-.8" y=".1" width=".7" height=".7" fill="{c}"/>',
    ]


def m_page(c: str) -> list[str]:
    """An e-reader page: a slim slab with two text lines."""
    return [
        _stroke("M-.6,-.9 L.6,-.9 L.6,.9 L-.6,.9 Z", 0.1, c, "miter"),
        _stroke("M-.3,-.4 L.3,-.4", 0.08, c),
        _stroke("M-.3,0 L.15,0", 0.08, c),
        _stroke("M-.3,.4 L.3,.4", 0.08, c),
    ]


def m_loop(c: str) -> list[str]:
    """A cable: a loop with a plug at each end."""
    return [
        _stroke("M-.8,.5 L-.8,-.2 Q-.8,-.8 0,-.8 Q.8,-.8 .8,-.2 L.8,.5", 0.1, c),
        f'<rect x="-.95" y=".45" width=".3" height=".4" fill="{c}"/>',
        f'<rect x=".65" y=".45" width=".3" height=".4" fill="{c}"/>',
    ]


def m_cell(c: str) -> list[str]:
    """A battery cell with a charge bolt."""
    return [
        _stroke("M-.55,-.65 L.55,-.65 L.55,.8 L-.55,.8 Z", 0.1, c, "miter"),
        _stroke("M-.2,-.8 L.2,-.8", 0.14, c),
        f'<path d="M.1,-.4 L-.25,.15 L0,.15 L-.1,.6 L.25,0 L0,0 Z" fill="{c}"/>',
    ]


def m_prong(c: str) -> list[str]:
    """A plug: two prongs on a rounded body."""
    return [
        _stroke("M-.35,-.85 L-.35,-.3", 0.12, c),
        _stroke("M.35,-.85 L.35,-.3", 0.12, c),
        f'<path d="M-.7,-.3 L.7,-.3 L.7,.2 Q.7,.8 0,.8 Q-.7,.8 -.7,.2 Z" fill="{c}"/>',
    ]


def m_fold(c: str) -> list[str]:
    """A sleeve: an open pouch with a folded flap."""
    return [
        _stroke("M-.8,-.3 L.8,-.3 L.8,.8 L-.8,.8 Z", 0.1, c, "miter"),
        f'<path d="M-.8,-.3 L0,.25 L.8,-.3 Z" fill="{c}"/>',
    ]


def m_dial(c: str) -> list[str]:
    """A scroll wheel in a mouse shell."""
    return [
        f'<path d="M0,-.9 Q.65,-.9 .65,-.1 L.65,.45 Q.65,.9 0,.9 Q-.65,.9 -.65,.45 L-.65,-.1 Q-.65,-.9 0,-.9 Z" fill="none" stroke="{c}" stroke-width=".1"/>',
        _stroke("M0,-.7 L0,-.2", 0.14, c),
    ]


def m_arc(c: str) -> list[str]:
    """Sound: an ear arc with two waves."""
    return [
        _stroke("M-.3,.7 Q-.8,.7 -.8,0 Q-.8,-.8 0,-.8 Q.8,-.8 .8,-.1", 0.1, c),
        _stroke("M.25,-.25 Q.6,.05 .25,.4", 0.08, c),
        _dot(-0.3, 0.7, 0.1, c),
    ]


def m_crate(c: str) -> list[str]:
    """A crate: a box with a sloped lid, strapped shut."""
    return [
        _stroke("M-.85,-.35 L.85,-.35 L.85,.85 L-.85,.85 Z", 0.11, c, "miter"),
        _stroke("M-.85,-.35 L-.5,-.85 L.5,-.85 L.85,-.35", 0.11, c, "miter"),
        _stroke("M0,-.35 L0,.85", 0.14, c),
    ]


def m_x_cell(c: str) -> list[str]:
    """A cross in a square with its corners cut."""
    return [
        _stroke("M-.6,-.85 L.6,-.85 L.85,-.6 L.85,.6 L.6,.85 L-.6,.85 L-.85,.6 L-.85,-.6 Z", 0.1, c, "miter"),
        _stroke("M-.4,-.4 L.4,.4", 0.16, c),
        _stroke("M-.4,.4 L.4,-.4", 0.16, c),
    ]


def m_wing(c: str) -> list[str]:
    """A wing: three swept feathers from one root."""
    return [
        _stroke("M-.85,.6 Q-.15,-.65 .85,-.8", 0.13, c),
        _stroke("M-.85,.6 Q-.05,-.2 .7,-.35", 0.11, c),
        _stroke("M-.85,.6 Q.05,.2 .5,.1", 0.09, c),
    ]


hs.MARKS.update(
    {
        "vine": m_vine,
        "slab": m_slab,
        "hinge": m_hinge,
        "fins": m_fins,
        "pane": m_pane,
        "twin_orbit": m_orbit,
        "pixels": m_pixels,
        "page": m_page,
        "loop": m_loop,
        "cell": m_cell,
        "prong": m_prong,
        "flap_sleeve": m_fold,
        "dial": m_dial,
        "arc": m_arc,
        "crate": m_crate,
        "x_cell": m_x_cell,
        "wing": m_wing,
    }
)

# fmt: off
#: Brand -> house style. Nine lockups and eight marks alone with a text tag.
STYLES = {
    # The device brands.
    "Grape Computer":  H("#f4f4f6", "none",  "ticks",   "#6a3d8f", "#2a1638", 0.9,  False, "sharp", "vine",   "mark_right", "bottom_right",  "none",    "humanist", 700, "caps",      1.3),
    "Halvern":  H("#eef2f7", "none",     "thin",    "#2f5fa3", "#14233b", 1.05, False, "round", "slab",   "mark_left",  "top_left",      "none",    "sans",     700, "caps",      1.4),
    "Torvane":  H("#f3f1ea", "lines",    "double",  "#6b5a3c", "#2b2417", 0.95, False, "sharp", "hinge",  "mark_above", "bottom_center", "none",    "serif",    400, "title",     0.6),
    "Nimbrel":  H("#eff6f4", "dots",     "rounded", "#1f7a6c", "#10332d", 1.15, False, "round", "pane",   "badge",      "top_right",     "none",    "humanist", 700, "smallcaps", 1.9),
    "Quorrin":  H("#f6f0f3", "grid",     "heavy",   "#8a2f5a", "#35121f", 1.0,  False, "sharp", "twin_orbit",  "mark_right", "bottom_right",  "none",    "mono",     400, "lower",     2.3),
    "Daskel":   H("#f2f4ee", "diagonal", "ticks",   "#4f7a2a", "#1d3010", 1.1,  True,  "round", "fins",   "pill",       "bottom_left",   "none",    "sans",     400, "title",     0.8),
    "Mervane":  H("#f1f2f8", "hatch",    "none",    "#4a4aa8", "#1a1a45", 0.9,  False, "sharp", "pixels", "mark_only",  "top_left",      "outline", "serif",    700, "caps",      1.2),
    "Pellimar": H("#f8f3ea", "none",     "thin",    "#b0652a", "#40230e", 1.2,  False, "round", "page",   "mark_only",  "bottom_right",  "flag",    "humanist", 400, "smallcaps", 2.6),
    # The accessory brands.
    "Cindrel":  H("#f4f6f0", "lines",    "rounded", "#3d8a4a", "#173a1d", 1.0,  False, "round", "loop",   "band_top",   "top_center",    "none",    "mono",     700, "lower",     1.6),
    "Boltwick": H("#fbf4e6", "grid",     "double",  "#c28a12", "#463208", 1.25, False, "sharp", "cell",   "mark_left",  "top_right",     "none",    "sans",     700, "title",     2.1),
    "Wexmoor":  H("#eff1f4", "dots",     "heavy",   "#58606e", "#1c2028", 0.85, True,  "sharp", "prong",  "mark_only",  "top_right",     "rect",    "mono",     400, "caps",      1.0),
    "Dunvale":  H("#f2eeeb", "diagonal", "none",    "#9a4a3a", "#3a1a14", 1.1,  False, "round", "flap_sleeve", "mark_only",  "bottom_left",   "tab",     "humanist", 700, "lower",     0.4),
    "Ardmoor":  H("#edf4f8", "hatch",    "ticks",   "#2a86a8", "#0f3445", 0.95, False, "round", "dial",   "mark_only",  "top_left",      "underline", "serif",  400, "title",     1.8),
    "Marrick":  H("#f7eef0", "none",     "thin",    "#a83a4a", "#401a20", 1.3,  False, "sharp", "arc",    "mark_only",  "bottom_right",  "stamp",   "sans",     700, "smallcaps", 0.7),
    "FlyingFoo": H("#fdf1ea", "diagonal", "rounded", "#d9541e", "#451a08", 1.1,  False, "round", "wing",   "mark_left",  "bottom_left",   "none",    "sans",     700, "title",     1.5),
    # The computer brands that cross departments (#721).
    "Xell":     H("#edf1f7", "lines",    "none",    "#1d4f91", "#0e2140", 0.9,  False, "sharp", "x_cell", "mark_only",  "bottom_left",   "plain",   "sans",     400, "lower",     2.4),
    "PackingHarder": H("#f0f2ee", "grid", "heavy",  "#3c5a2e", "#18240f", 1.2,  False, "sharp", "crate",  "mark_only",  "top_right",     "stamp",   "mono",     700, "caps",      1.1),
}
# fmt: on
hs.HOUSE_STYLES.update(STYLES)
