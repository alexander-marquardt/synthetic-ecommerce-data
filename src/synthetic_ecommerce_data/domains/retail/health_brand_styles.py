"""Marks and house styles of the three invented Health brands of first aid and monitors (gen#968).

Quellmoor Care, Halvering and Thrennick sell plasters, first-aid kits, thermometers and
blood-pressure monitors beside Velling Apothecary (:mod:`health_rows`). Each draws its own mark
and name on its product images, as every other invented brand does. No mark is a cross: the
cross on a first-aid kit is the first-aid sign's, drawn by :mod:`kit_health`.

:mod:`house_styles` imports this module last, so the three marks join ``MARKS`` and the three
styles join ``HOUSE_STYLES`` whichever module is imported first.
"""

# ruff: noqa: E501 -- the style table reads best whole (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail import house_styles as hs
from synthetic_ecommerce_data.domains.retail.house_styles import H, _dot, _ring, _stroke


def m_pulse_line(c: str) -> list[str]:
    """A pulse trace: a level line with one sharp beat."""
    return [_stroke("M-.95,.1 L-.4,.1 L-.2,-.6 L.05,.75 L.25,-.2 L.4,.1 L.95,.1", 0.14, c, "miter")]


def m_still_drop(c: str) -> list[str]:
    """A drop of water inside a ring."""
    return [
        _ring(0, 0, 0.82, 0.12, c),
        f'<path d="M0,-.5 Q.38,.05 .3,.25 Q.2,.55 0,.55 Q-.2,.55 -.3,.25 Q-.38,.05 0,-.5 Z" fill="{c}"/>',
    ]


def m_split_disc(c: str) -> list[str]:
    """Two half discs facing apart across a dot."""
    return [
        f'<path d="M-.15,-.75 A.75,.75 0 0 0 -.15,.75 Z" fill="{c}"/>',
        f'<path d="M.15,-.75 A.75,.75 0 0 1 .15,.75 Z" fill="{c}"/>',
        _dot(0, 0, 0.08, c),
    ]


hs.MARKS.update({"pulse_line": m_pulse_line, "still_drop": m_still_drop, "split_disc": m_split_disc})

# fmt: off
#: Brand -> house style: one lockup beside the mark, one mark alone, one mark above.
STYLES = {
    "Quellmoor Care": H("rounded", "#2f7f9a", "#123a47", 1.0,  False, "round", "still_drop", "mark_left",  "top_center",   "none",  "humanist", 400, "title",     1.5),
    "Halvering":      H("thin",    "#7a4a8c", "#341f3d", 0.9,  False, "sharp", "split_disc", "mark_only",  "bottom_left",  "plain", "serif",    700, "lower",     2.0),
    "Thrennick":      H("heavy",   "#c0492f", "#4a1a10", 1.2,  True,  "sharp", "pulse_line", "mark_above", "top_left",     "none",  "mono",     700, "smallcaps", 0.5),
}
# fmt: on
hs.HOUSE_STYLES.update(STYLES)
