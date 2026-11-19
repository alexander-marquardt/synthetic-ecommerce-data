"""Marks and house styles of the three invented fluids and electrics brands of Automotive (gen#970).

Corvane sells motor oil and coolant; Ampwick and Holtvane sell jump starters, tire inflators,
phone mounts and car chargers (:mod:`automotive_fluids_rows`). Kestrova and Drayfield, slice 1's
brands (:mod:`automotive_brand_styles`), sell in this slice too. Each new brand draws its own name
on its product images with a mark no other brand uses.

:mod:`automotive_fluids_rows` imports this module, so the three marks join ``MARKS`` and the three
styles join ``HOUSE_STYLES`` before any of its records is drawn.
"""

# ruff: noqa: E501 -- the style table reads best whole (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail import house_styles as hs
from synthetic_ecommerce_data.domains.retail.house_styles import H, _dot, _stroke


def m_oil_can(c: str) -> list[str]:
    """An oil can on its side with a long spout and one drop."""
    return [
        _stroke("M-.85,.55 L-.85,-.05 L.15,-.05 L.15,.55 Z", 0.11, c, "round"),
        _stroke("M.15,.1 L.8,-.45", 0.1, c),
        _stroke("M-.6,-.05 L-.6,-.3 L-.25,-.3 L-.25,-.05", 0.09, c),
        _dot(0.8, 0.0, 0.13, c),
    ]


def m_spark_bolt(c: str) -> list[str]:
    """A lightning bolt in a ring."""
    return [
        _stroke("M.1,-.75 L-.35,.08 L.05,.08 L-.1,.75 L.38,-.12 L-.02,-.12 Z", 0.1, c, "round"),
        _stroke("M-.85,0 A.85,.85 0 1,1 .85,0 A.85,.85 0 1,1 -.85,0", 0.08, c),
    ]


def m_clamp_arc(c: str) -> list[str]:
    """Two jaws of a clamp closing on a post."""
    return [
        _stroke("M-.8,-.6 Q-.1,-.6 0,0 Q-.1,.6 -.8,.6", 0.11, c),
        _stroke("M.8,-.6 Q.1,-.6 0,0 Q.1,.6 .8,.6", 0.11, c),
        _dot(0.0, 0.0, 0.16, c),
    ]


hs.MARKS.update(
    {
        "oil_can": m_oil_can,
        "spark_bolt": m_spark_bolt,
        "clamp_arc": m_clamp_arc,
    }
)

# fmt: off
#: Brand -> house style.
STYLES = {
    "Corvane":  H("rounded", "#7a1f2b", "#2b0b10", 1.0,  False, "round", "oil_can",    "mark_above", "bottom_left", "none",      "sans",     700, "caps",  1.6),
    "Ampwick":  H("ticks",   "#b88a00", "#2a2100", 1.1,  False, "sharp", "spark_bolt", "mark_left",  "top_left",    "none",      "mono",     700, "caps",  1.9),
    "Holtvane": H("thin",    "#2d5d7b", "#0f2230", 1.2,  True,  "round", "clamp_arc",  "mark_only",  "bottom_left", "plain",     "humanist", 400, "title", 2.3),
}
# fmt: on
hs.HOUSE_STYLES.update(STYLES)
