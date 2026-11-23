"""Marks and house styles of the two invented brands of the sewing and knitting range (gen#1118).

Bobbinmere sells thread and fabric, Purlwick yarn and thread (:mod:`sewing_rows`). Each draws its
own mark and name on its product images, as every other invented brand does.

:mod:`house_styles` imports this module last, so the two marks join ``MARKS`` and the two styles
join ``HOUSE_STYLES`` whichever module is imported first.
"""

# ruff: noqa: E501 -- the style table reads best whole (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail import house_styles as hs
from synthetic_ecommerce_data.domains.retail.house_styles import H, _ring, _stroke


def m_bobbin(c: str) -> list[str]:
    """A bobbin: a barrel between two flanges, wound with thread."""
    return [
        _stroke("M-.6,-.75 L.6,-.75 M-.6,.75 L.6,.75", 0.16, c),
        _stroke("M-.4,-.6 L-.4,.6 M0,-.6 L0,.6 M.4,-.6 L.4,.6", 0.12, c),
    ]


def m_purl(c: str) -> list[str]:
    """A ball of yarn: a ring crossed by two strands."""
    return [
        _ring(0, 0, 0.7, 0.12, c),
        _stroke("M-.55,-.35 Q0,-.05 .55,-.35 M-.6,.1 Q0,.45 .6,.1", 0.09, c),
    ]


hs.MARKS.update({"bobbin_mere": m_bobbin, "purl_ball": m_purl})

# fmt: off
STYLES = {
    "Bobbinmere": H("double",  "#3a6a8a", "#16293a", 1.0,  False, "sharp", "bobbin_mere", "mark_right", "bottom_right", "none", "humanist", 400, "title", 0.5),
    "Purlwick":   H("rounded", "#a83a5a", "#3c1623", 1.05, False, "round", "purl_ball",   "mark_above", "top_center", "none", "serif",    700, "title", 0.0),
}
# fmt: on
hs.HOUSE_STYLES.update(STYLES)
