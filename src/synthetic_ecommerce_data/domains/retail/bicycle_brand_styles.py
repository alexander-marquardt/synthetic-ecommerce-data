"""Marks and house styles of the seven invented bicycle-only brands (gen#718).

Gorsecliff, Rindlemoor, Tolvaney, Ostlebury, Wattlebrook, Pipkinford and Hessenby sell bicycles
beside the three house brands (:mod:`bicycle_model_numbers`). Each draws its own mark and name on
its product images, as every other invented brand does.

:mod:`house_styles` imports this module last, so the seven marks join ``MARKS`` and the seven
styles join ``HOUSE_STYLES`` whichever module is imported first.
"""

# ruff: noqa: E501 -- the style table reads best whole (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail import house_styles as hs
from synthetic_ecommerce_data.domains.retail.house_styles import H, _dot, _ring, _stroke


def m_crag(c: str) -> list[str]:
    """A rock face: two peaks over a line of scree."""
    return [
        f'<path d="M-.9,.6 L-.35,-.6 L.05,.1 L.4,-.3 L.9,.6 Z" fill="{c}"/>',
        _stroke("M-.8,.85 L.8,.85", 0.1, c),
    ]


def m_cog(c: str) -> list[str]:
    """A chainring: a ring with a tooth at each quarter and a hub."""
    return [
        _ring(0, 0, 0.62, 0.16, c),
        _stroke("M0,-.9 L0,-.7 M0,.7 L0,.9 M-.9,0 L-.7,0 M.7,0 L.9,0", 0.2, c, "miter"),
        _dot(0, 0, 0.16, c),
    ]


def m_drop_bar(c: str) -> list[str]:
    """A drop bar from the front: a level top curling down at each end."""
    return [_stroke("M-.85,.7 Q-.95,-.45 -.45,-.45 L.45,-.45 Q.95,-.45 .85,.7", 0.17, c)]


def m_milestone(c: str) -> list[str]:
    """A milestone: a round-topped stone with a mile cut into it."""
    return [
        f'<path d="M-.55,.85 L-.55,-.2 Q-.55,-.85 0,-.85 Q.55,-.85 .55,-.2 L.55,.85 Z" fill="{c}"/>',
        _stroke("M-.25,.1 L.25,.1 M-.25,.42 L.25,.42", 0.1, "#ffffff"),
    ]


def m_bolt_ring(c: str) -> list[str]:
    """A charge: a lightning bolt in a ring."""
    return [
        _ring(0, 0, 0.82, 0.12, c),
        f'<path d="M.15,-.6 L-.35,.08 L-.04,.08 L-.15,.6 L.35,-.08 L.04,-.08 Z" fill="{c}"/>',
    ]


def m_pipkin(c: str) -> list[str]:
    """A small wheel: a ring with three spokes and a smaller wheel beside it."""
    return [
        _ring(-0.2, 0, 0.62, 0.14, c),
        _stroke("M-.2,0 L-.2,-.55 M-.2,0 L-.68,.28 M-.2,0 L.28,.28", 0.08, c),
        _ring(0.68, 0.38, 0.22, 0.1, c),
    ]


def m_stag_arch(c: str) -> list[str]:
    """A gateway: an arch on two posts with a keystone."""
    return [
        _stroke("M-.7,.85 L-.7,-.1 Q-.7,-.75 0,-.75 Q.7,-.75 .7,-.1 L.7,.85", 0.18, c),
        f'<path d="M-.16,-.95 L.16,-.95 L.1,-.5 L-.1,-.5 Z" fill="{c}"/>',
    ]


hs.MARKS.update({
    "crag": m_crag, "chainring": m_cog, "drop_bar": m_drop_bar, "milestone": m_milestone,
    "bolt_ring": m_bolt_ring, "pipkin_wheel": m_pipkin, "keystone_arch": m_stag_arch,
})  # fmt: skip

# fmt: off
#: Brand -> house style: four lockups and three marks alone, as about half the table is.
STYLES = {
    "Gorsecliff":  H("#f3f2e8", "hatch",    "heavy",   "#5e6b2e", "#2a3014", 1.15, False, "sharp", "crag",          "mark_left",  "top_right",     "none",      "sans",     700, "caps",      1.5),
    "Rindlemoor":  H("#eff2f5", "none",     "thin",    "#37566e", "#1b2a36", 0.95, False, "round", "chainring",     "mark_only",  "top_left",      "tab",       "humanist", 700, "title",     1.0),
    "Tolvaney":    H("#f7f1ee", "lines",    "none",    "#a0342b", "#42160f", 0.85, False, "round", "drop_bar",      "mark_right", "bottom_left",   "none",      "serif",    700, "caps",      3.0, True),
    "Ostlebury":   H("#f4f3ee", "dots",     "double",  "#6b5a3a", "#2d2616", 1.05, False, "round", "milestone",     "mark_only",  "bottom_right",  "stamp",     "mono",     700, "caps",      1.0),
    "Wattlebrook": H("#eef6f3", "grid",     "rounded", "#16806d", "#0c3a31", 1.0,  False, "round", "bolt_ring",     "pill",       "top_center",    "none",      "humanist", 400, "lower",     1.0),
    "Pipkinford":  H("#fdf5ea", "none",     "ticks",   "#d0702a", "#532a0c", 1.1,  False, "round", "pipkin_wheel",  "mark_above", "bottom_center", "none",      "humanist", 700, "lower",     0.5, True),
    "Hessenby":    H("#f2f0f6", "diagonal", "thin",    "#54418a", "#241a3e", 0.9,  False, "sharp", "keystone_arch", "mark_only",  "top_right",     "outline",   "serif",    400, "smallcaps", 2.0),
}
# fmt: on
hs.HOUSE_STYLES.update(STYLES)
