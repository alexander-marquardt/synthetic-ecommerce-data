"""The four invented brands of the misspelled products (gen#944): owners, marks and house styles.

:mod:`feature_decoys.misspelled_words_944` sells ordinary chocolate, bananas, leggings and
cardigans whose brand, title or description spells the product word the way shoppers mistype it.
Four of them carry the misspelling in an invented brand; each is third party and draws its own
name on its product images in a dedicated house style (the wordmark or the mark-only tag is the
brand field, spelled as the title spells it), with a mark of its own: no other brand draws it.

Two of the four are full lockups and two show the mark alone with a tag, so the brands keep
about half of the house styles on a full lockup (``test_house_styles.py``).
"""

# ruff: noqa: E501 -- the style table reads best whole (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail import house_styles as hs
from synthetic_ecommerce_data.domains.retail.breadth_rows import OWNERS
from synthetic_ecommerce_data.domains.retail.class_model import BRAND_OWNER
from synthetic_ecommerce_data.domains.retail.house_styles import H, _dot, _ring, _stroke

#: The invented brands, each holding one misspelled product word.
BRANDS = ("Choocolate Factory", "Bannana Bros", "Leggins Lab", "Cardigen & Co")
OWNERS.update(dict.fromkeys(BRANDS, "third_party"))
BRAND_OWNER.update(dict.fromkeys(BRANDS, "third_party"))


def m_bar_grid(c: str) -> list[str]:
    """A bar of six squares, two across and three down."""
    return [
        f'<rect x="{x}" y="{y}" width=".7" height=".5" rx=".08" fill="{c}"/>'
        for y in ("-.85", "-.25", ".35")
        for x in ("-.75", ".05")
    ]


def m_peel_arc(c: str) -> list[str]:
    """Two nested arcs opening upward, joined by a dot at each tip."""
    return [
        _stroke("M-.85,-.3 Q0,1.1 .85,-.3", 0.14, c),
        _stroke("M-.5,-.3 Q0,.5 .5,-.3", 0.12, c),
        _dot(-0.85, -0.3, 0.13, c),
        _dot(0.85, -0.3, 0.13, c),
    ]


def m_stride_bars(c: str) -> list[str]:
    """Three slanted bars of rising height."""
    return [_stroke("M-.7,.8 L-.45,.2 M-.15,.8 L.15,-.25 M.4,.8 L.75,-.75", 0.18, c)]


def m_button_pair(c: str) -> list[str]:
    """Two rings stacked on a line, each with two holes."""
    return [
        _stroke("M0,-.95 L0,.95", 0.08, c),
        _ring(0.0, -0.45, 0.36, 0.12, c),
        _ring(0.0, 0.45, 0.36, 0.12, c),
        _dot(-0.12, -0.45, 0.07, c),
        _dot(0.12, -0.45, 0.07, c),
        _dot(-0.12, 0.45, 0.07, c),
        _dot(0.12, 0.45, 0.07, c),
    ]


hs.MARKS.update({"bar_grid": m_bar_grid, "peel_arc": m_peel_arc, "stride_bars": m_stride_bars, "button_pair": m_button_pair})

# fmt: off
STYLES = {
    "Choocolate Factory": H("heavy",   "#6b3a1f", "#2e1a0e", 1.1, False, "sharp", "bar_grid",    "mark_left",  "top_left",     "none",      "serif",    700, "caps",      1.0),
    "Bannana Bros":       H("rounded", "#e0b82e", "#4a3a10", 1.0, False, "round", "peel_arc",    "mark_only",  "top_right",    "flag",      "sans",     700, "title",     0.5),
    "Leggins Lab":        H("thin",    "#3a3a6e", "#1c1c38", 0.9, False, "round", "stride_bars", "mark_only",  "bottom_left",  "underline", "humanist", 400, "smallcaps", 2.0),
    "Cardigen & Co":      H("ticks",   "#8a5a6a", "#3a1e28", 1.0, True,  "round", "button_pair", "mark_left",  "bottom_right", "none",      "serif",    400, "title",     1.5, True),
}
# fmt: on
hs.HOUSE_STYLES.update(STYLES)
