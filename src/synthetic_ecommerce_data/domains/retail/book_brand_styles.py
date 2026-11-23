"""Marks and house styles of the eight invented publishers of the Books department (gen#1119).

Wrenhallow Press, Marlowby Books, Thimblecote Press, Ferncastle Editions, Ashcombe & Rook,
Lindenquay Publishing, Moddlewick Books and Gullfeather Press publish the titles of
:mod:`books_rows`. Each draws its own mark and name on its product images, as every other
invented brand does.

:mod:`house_styles` imports this module last, so the eight marks join ``MARKS`` and the eight
styles join ``HOUSE_STYLES`` whichever module is imported first.
"""

# ruff: noqa: E501 -- the style table reads best whole (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail import house_styles as hs
from synthetic_ecommerce_data.domains.retail.house_styles import H, _dot, _stroke


def m_wren(c: str) -> list[str]:
    """A wren: a round body, a cocked tail and a beak."""
    return [
        f'<path d="M-.6,.2 Q-.6,-.45 .05,-.45 Q.55,-.45 .6,.05 Q.45,.6 -.2,.55 Q-.6,.5 -.6,.2 Z" fill="{c}"/>',
        f'<path d="M-.5,-.05 L-.85,-.75 L-.3,-.3 Z" fill="{c}"/>',
        f'<path d="M.55,-.15 L.9,-.25 L.58,.02 Z" fill="{c}"/>',
    ]


def m_marlow_wave(c: str) -> list[str]:
    """A river under a bridge: an arch over two waves."""
    return [
        _stroke("M-.85,.1 Q0,-.9 .85,.1", 0.14, c),
        _stroke("M-.9,.45 Q-.45,.25 0,.45 T.9,.45", 0.1, c),
        _stroke("M-.9,.75 Q-.45,.55 0,.75 T.9,.75", 0.1, c),
    ]


def m_thimble(c: str) -> list[str]:
    """A thimble: a dome with a band of dimples."""
    return [
        f'<path d="M-.5,.7 L-.45,-.3 Q0,-.95 .45,-.3 L.5,.7 Z" fill="{c}"/>',
        _dot(-0.2, 0.0, 0.07, "#ffffff"), _dot(0.0, -0.1, 0.07, "#ffffff"), _dot(0.2, 0.0, 0.07, "#ffffff"),
        _stroke("M-.62,.75 L.62,.75", 0.14, c),
    ]  # fmt: skip


def m_fern_tower(c: str) -> list[str]:
    """A castle turret with a fern beside it."""
    return [
        f'<path d="M-.7,.85 L-.7,-.5 L-.55,-.5 L-.55,-.7 L-.4,-.7 L-.4,-.5 L-.25,-.5 L-.25,-.7 L-.1,-.7 L-.1,.85 Z" fill="{c}"/>',
        _stroke(
            "M.45,.85 Q.4,0 .6,-.75 M.45,.4 L.2,.2 M.45,.4 L.75,.25 M.45,0 L.22,-.2 M.47,0 L.75,-.15",
            0.09,
            c,
        ),
    ]


def m_rook(c: str) -> list[str]:
    """A rook in profile on an ampersand's bar."""
    return [
        f'<path d="M-.55,.2 Q-.4,-.5 .2,-.45 L.75,-.6 L.35,-.25 Q.5,.3 -.1,.45 L-.75,.55 Z" fill="{c}"/>',
        _stroke("M-.85,.8 L.85,.8", 0.12, c),
    ]


def m_linden_leaf(c: str) -> list[str]:
    """A linden leaf: a heart on a stalk, with its veins."""
    return [
        f'<path d="M0,.6 Q-.95,0 -.55,-.6 Q-.2,-.85 0,-.45 Q.2,-.85 .55,-.6 Q.95,0 0,.6 Z" fill="{c}"/>',
        _stroke("M0,.6 L0,.95", 0.1, c),
        _stroke("M0,.5 L0,-.4 M0,.1 L-.35,-.25 M0,.1 L.35,-.25", 0.06, "#ffffff"),
    ]


def m_open_book(c: str) -> list[str]:
    """An open book: two pages on a spine."""
    return [
        f'<path d="M0,-.45 Q-.45,-.7 -.9,-.5 L-.9,.6 Q-.45,.4 0,.65 Z" fill="{c}"/>',
        f'<path d="M0,-.45 Q.45,-.7 .9,-.5 L.9,.6 Q.45,.4 0,.65 Z" fill="{c}"/>',
        _stroke("M0,-.45 L0,.65", 0.06, "#ffffff"),
    ]


def m_gull_feather(c: str) -> list[str]:
    """A gull in flight over a feather's quill."""
    return [
        _stroke("M-.9,-.35 Q-.45,-.75 0,-.3 Q.45,-.75 .9,-.35", 0.13, c),
        f'<path d="M-.5,.85 Q-.2,.05 .6,-.05 Q.25,.55 -.5,.85 Z" fill="{c}"/>',
        _stroke("M-.5,.85 L.45,.05", 0.05, "#ffffff"),
    ]


hs.MARKS.update({
    "wren": m_wren, "marlow_wave": m_marlow_wave, "thimble": m_thimble, "fern_tower": m_fern_tower,
    "rook_bar": m_rook, "linden_leaf": m_linden_leaf, "open_book": m_open_book,
    "gull_feather": m_gull_feather,
})  # fmt: skip

# fmt: off
#: Publisher -> house style: four lockups and four marks alone, as about half the table is.
STYLES = {
    "Wrenhallow Press":      H("thin",    "#5a3d2b", "#2a1a10", 0.95, False, "round", "wren",         "mark_left",  "top_left",      "none",      "serif",    400, "title",     0.5, True),
    "Marlowby Books":        H("double",  "#2a4f6e", "#11222f", 1.05, False, "round", "marlow_wave",  "mark_only",  "top_right",     "underline", "serif",    700, "smallcaps", 1.0),
    "Thimblecote Press":     H("rounded", "#8a4a6a", "#3a1d2c", 1.0,  False, "round", "thimble",      "mark_above", "top_center",    "none",      "humanist", 400, "title",     0.0),
    "Ferncastle Editions":   H("ticks",   "#2e5e3a", "#132818", 1.1,  False, "sharp", "fern_tower",   "mark_only",  "bottom_left",   "rect",      "serif",    700, "caps",      2.0),
    "Ashcombe & Rook":       H("heavy",   "#2a2a33", "#101014", 1.15, False, "sharp", "rook_bar",     "mark_right", "bottom_center", "none",      "sans",     700, "caps",      1.5),
    "Lindenquay Publishing": H("none",    "#5e7a2a", "#263212", 0.9,  False, "round", "linden_leaf",  "mark_only",  "top_left",      "flag",      "humanist", 700, "lower",     0.5),
    "Moddlewick Books":      H("double",  "#a8582a", "#45220f", 1.0,  True,  "round", "open_book",    "pill",       "bottom_right",  "none",      "sans",     400, "title",     1.0),
    "Gullfeather Press":     H("thin",    "#3a6a8a", "#172b38", 0.95, False, "round", "gull_feather", "mark_only",  "top_right",     "plain",     "mono",     400, "lower",     2.5),
}
# fmt: on
hs.HOUSE_STYLES.update(STYLES)
