"""Marks and house styles of the two invented fishing and golf brands (gen#959).

Pennywhistle Angling sells fishing rods, reels and tackle boxes, and Larchmere Golf golf clubs,
balls and gloves (:mod:`fishing_golf_rows`). Each draws its own name on its product images with a
mark and an arrangement no other brand uses.

:mod:`house_styles` imports this module last, so the two marks join ``MARKS`` and the two styles
join ``HOUSE_STYLES`` whichever module is imported first.
"""

# ruff: noqa: E501 -- the style table reads best whole (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail import house_styles as hs
from synthetic_ecommerce_data.domains.retail.house_styles import H, _dot, _ring, _stroke


def m_fish_hook(c: str) -> list[str]:
    """A fish hook: an eye at the top, a straight shank and a barbed bend."""
    return [
        _ring(0.25, -0.7, 0.13, 0.08, c),
        _stroke("M.25,-.57 L.25,.35 Q.25,.8 -.15,.8 Q-.55,.8 -.55,.35 L-.55,.15", 0.12, c),
        _stroke("M-.55,.15 L-.35,.35", 0.1, c),
    ]


def m_golf_flag(c: str) -> list[str]:
    """A golf pin: a pole with a pennant over a hole, and a ball beside it."""
    return [
        _stroke("M-.2,-.85 L-.2,.6", 0.1, c),
        f'<path d="M-.2,-.85 L.6,-.6 L-.2,-.35 Z" fill="{c}"/>',
        _stroke("M-.75,.7 Q-.2,.5 .35,.7", 0.1, c),
        _dot(0.55, 0.45, 0.14, c),
    ]


hs.MARKS.update({"fish_hook": m_fish_hook, "golf_flag": m_golf_flag})

# fmt: off
#: Brand -> house style: Pennywhistle a lockup with the name beside the hook, Larchmere the flag alone.
STYLES = {
    "Pennywhistle Angling": H("rounded", "#2e6f8e", "#173847", 1.0,  False, "round", "fish_hook", "mark_left", "bottom_right", "none",    "humanist", 700, "title", 1.0, True),
    "Larchmere Golf":       H("double",  "#2f7a3d", "#183d1f", 0.9,  False, "sharp", "golf_flag", "mark_only", "bottom_left",  "outline", "sans",     400, "caps",  2.5),
}
# fmt: on
hs.HOUSE_STYLES.update(STYLES)
