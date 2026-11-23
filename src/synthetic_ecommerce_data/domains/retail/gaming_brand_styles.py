"""Marks and house styles of the eight invented video game publishers (gen#1120).

Thornvale Studios, Brassik Softworks, Quillmere Interactive, Calvenby Studios, Larkspire
Softworks, Dunmarrow Interactive, Fennick Studios and Wendlecott Interactive publish the games of
Electronics > Gaming > Video Games (:mod:`type_specs.video_game`): a game's brand is its publisher.
Each draws its own name on its product images with a mark and an arrangement no other brand uses.

:mod:`house_styles` imports this module last, so the eight marks join ``MARKS`` and the eight
styles join ``HOUSE_STYLES`` whichever module is imported first.
"""

# ruff: noqa: E501 -- the style table reads best whole (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail import house_styles as hs
from synthetic_ecommerce_data.domains.retail.house_styles import H, _dot, _ring, _stroke


def m_thorn_crown(c: str) -> list[str]:
    """A three-pointed crown over a band."""
    return [
        f'<path d="M-.75,.35 L-.75,-.45 L-.4,-.05 L0,-.75 L.4,-.05 L.75,-.45 L.75,.35 Z" fill="{c}"/>',
        _stroke("M-.8,.6 L.8,.6", 0.14, c),
    ]


def m_dpad(c: str) -> list[str]:
    """A direction pad: a plus of four arms with a ring at its center."""
    return [
        f'<path d="M-.22,-.8 L.22,-.8 L.22,-.22 L.8,-.22 L.8,.22 L.22,.22 L.22,.8 L-.22,.8 L-.22,.22 L-.8,.22 L-.8,-.22 L-.22,-.22 Z" fill="{c}"/>',
    ]


def m_quill_nib(c: str) -> list[str]:
    """A pen nib: a pointed shield with a slit and a breather hole."""
    return [
        _stroke("M0,.85 L-.5,-.1 Q-.5,-.7 0,-.85 Q.5,-.7 .5,-.1 Z", 0.11, c),
        _stroke("M0,.8 L0,-.2", 0.08, c),
        _dot(0, -0.35, 0.1, c),
    ]


def m_four_buttons(c: str) -> list[str]:
    """Four face buttons set in a diamond."""
    return [_dot(0, -0.5, 0.22, c), _dot(0.5, 0, 0.22, c), _dot(0, 0.5, 0.22, c), _dot(-0.5, 0, 0.22, c)]


def m_lark_wing(c: str) -> list[str]:
    """A swept wing of three feathers."""
    return [
        _stroke("M-.8,.5 Q-.1,.4 .8,-.6", 0.12, c),
        _stroke("M-.6,.65 Q.05,.6 .7,-.2", 0.1, c),
        _stroke("M-.4,.8 Q.2,.78 .6,.2", 0.08, c),
    ]


def m_tower_gate(c: str) -> list[str]:
    """A castle tower with battlements and an arched gate."""
    return [
        _stroke("M-.6,.8 L-.6,-.55 L-.35,-.55 L-.35,-.8 L-.12,-.8 L-.12,-.55 L.12,-.55 L.12,-.8 L.35,-.8 L.35,-.55 L.6,-.55 L.6,.8 Z", 0.1, c),
        _stroke("M-.2,.8 L-.2,.3 Q0,.05 .2,.3 L.2,.8", 0.1, c),
    ]


def m_fox_ears(c: str) -> list[str]:
    """A fox face: two pointed ears over a narrowing muzzle."""
    return [
        f'<path d="M-.75,-.75 L-.3,-.25 L.3,-.25 L.75,-.75 L.7,.05 L0,.8 L-.7,.05 Z" fill="{c}"/>',
    ]


def m_play_ring(c: str) -> list[str]:
    """A play triangle inside a ring."""
    return [
        _ring(0, 0, 0.8, 0.12, c),
        f'<path d="M-.25,-.4 L.45,0 L-.25,.4 Z" fill="{c}"/>',
    ]


hs.MARKS.update(
    {
        "thorn_crown": m_thorn_crown,
        "dpad": m_dpad,
        "quill_nib": m_quill_nib,
        "four_buttons": m_four_buttons,
        "lark_wing": m_lark_wing,
        "tower_gate": m_tower_gate,
        "fox_ears": m_fox_ears,
        "play_ring": m_play_ring,
    }
)

# fmt: off
#: Brand -> house style: four lockups and four marks alone.
STYLES = {
    "Thornvale Studios":      H("heavy",   "#6a2c91", "#2a1139", 1.05, False, "sharp", "thorn_crown",  "mark_left",  "top_right",     "none",      "serif",    700, "smallcaps", 2.7),
    "Brassik Softworks":      H("thin",    "#b5651d", "#43250b", 0.95, True,  "round", "dpad",         "mark_only",  "bottom_right",  "stamp",     "mono",     700, "caps",      0.4),
    "Quillmere Interactive":  H("double",  "#25627d", "#0f2a36", 0.85, False, "round", "quill_nib",    "mark_above", "top_left",      "none",      "humanist", 400, "title",     2.1, True),
    "Calvenby Studios":       H("rounded", "#c23b6e", "#4a1529", 1.25, False, "round", "four_buttons", "mark_only",  "top_right",     "underline", "sans",     400, "lower",     1.7),
    "Larkspire Softworks":    H("none",    "#3c8d5a", "#163a24", 1.15, True,  "sharp", "lark_wing",    "pill",       "bottom_right",  "none",      "sans",     700, "title",     1.3),
    "Dunmarrow Interactive":  H("ticks",   "#5b5f66", "#1f2124", 1.3,  False, "sharp", "tower_gate",   "mark_only",  "bottom_left",   "outline",   "serif",    400, "caps",      2.2),
    "Fennick Studios":        H("heavy",   "#d4602a", "#4d200b", 0.8,  True,  "round", "fox_ears",     "badge",      "bottom_left",   "none",      "mono",     400, "smallcaps", 0.9, True),
    "Wendlecott Interactive": H("rounded", "#2f4fa8", "#101d45", 1.0,  False, "sharp", "play_ring",    "mark_only",  "top_left",      "stamp",     "humanist", 700, "lower",     1.6),
}
# fmt: on
hs.HOUSE_STYLES.update(STYLES)
