"""Marks and house styles of the invented Health brands (gen#968): first aid, monitors and the own labels.

Quellmoor Care, Halvering and Thrennick sell plasters, first-aid kits, thermometers and
blood-pressure monitors beside Velling Apothecary (:mod:`health_rows`). Each draws its own mark
and name on its product images, as every other invented brand does. No mark is a cross: the
cross on a first-aid kit is the first-aid sign's, drawn by :mod:`kit_health`. Corvane Pharmacy,
Brannock Health and four more of slice 4's own labels sell across every Health type (``department_rates/health.py``).

:mod:`house_styles` imports this module last, so its marks join ``MARKS`` and its
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


def m_mortar(c: str) -> list[str]:
    """A mortar bowl with its pestle leaning in: a chemist's sign (Corvane Pharmacy)."""
    return [
        f'<path d="M-.8,-.05 L.8,-.05 Q.75,.7 0,.75 Q-.75,.7 -.8,-.05 Z" fill="{c}"/>',
        _stroke("M.15,-.1 L.6,-.8", 0.16, c, "round"),
    ]


def m_twin_arc(c: str) -> list[str]:
    """Two nested arcs over a dot, like a rising sun (Brannock Health)."""
    return [
        _stroke("M-.85,.35 A.85,.85 0 0 1 .85,.35", 0.13, c, "round"),
        _stroke("M-.5,.35 A.5,.5 0 0 1 .5,.35", 0.13, c, "round"),
        _dot(0, .35, 0.12, c),
    ]


def m_hex_ring(c: str) -> list[str]:
    """A hexagon outline around a dot (Hallowby Chemist)."""
    return [_stroke("M0,-.85 L.74,-.42 L.74,.42 L0,.85 L-.74,.42 L-.74,-.42 Z", 0.14, c, "miter"), _dot(0, 0, 0.14, c)]


def m_wave(c: str) -> list[str]:
    """Two stacked waves (Lindcombe Health)."""
    return [
        _stroke("M-.9,-.25 Q-.45,-.7 0,-.25 T.9,-.25", 0.14, c, "round"),
        _stroke("M-.9,.35 Q-.45,-.1 0,.35 T.9,.35", 0.14, c, "round"),
    ]


def m_bars(c: str) -> list[str]:
    """Three bars of falling length (Sedgemoor Pharmacy)."""
    return [_stroke(f"M-.8,{y} L{x},{y}", 0.2, c, "butt") for y, x in ((-.5, .8), (0, .45), (.5, .1))]


def m_trio(c: str) -> list[str]:
    """Three dots in a row (Ottermere Care)."""
    return [_dot(x, 0, 0.22, c) for x in (-.6, 0, .6)]


hs.MARKS.update({"pulse_line": m_pulse_line, "still_drop": m_still_drop, "split_disc": m_split_disc,
                 "mortar": m_mortar, "twin_arc": m_twin_arc, "hex_ring": m_hex_ring, "wave": m_wave,
                 "bars": m_bars, "trio": m_trio})

# fmt: off
#: Brand -> house style: one lockup beside the mark, one mark alone, one mark above.
STYLES = {
    "Quellmoor Care": H("rounded", "#2f7f9a", "#123a47", 1.0,  False, "round", "still_drop", "mark_left",  "top_center",   "none",  "humanist", 400, "title",     1.5),
    "Halvering":      H("thin",    "#7a4a8c", "#341f3d", 0.9,  False, "sharp", "split_disc", "mark_only",  "bottom_left",  "plain", "serif",    700, "lower",     2.0),
    "Thrennick":      H("heavy",   "#c0492f", "#4a1a10", 1.2,  True,  "sharp", "pulse_line", "mark_above", "top_left",     "none",  "mono",     700, "smallcaps", 0.5),
    # Slice 4's chemist's own labels, sold across every Health type (department_rates/health.py).
    "Corvane Pharmacy": H("rounded", "#1f6f5c", "#0e352b", 1.0, False, "round", "mortar",     "mark_left",  "bottom_left",  "none",  "sans",     700, "title",     1.0),
    "Brannock Health":  H("thin",    "#3a5aa8", "#18264a", 0.9, False, "sharp", "twin_arc",   "mark_above", "top_center",   "none",  "humanist", 400, "lower",     1.5),
    "Hallowby Chemist":   H("heavy",   "#8a3b52", "#3a1522", 1.1, True,  "sharp", "hex_ring",     "mark_only",  "bottom_left", "plain", "serif",    700, "smallcaps", 1.0),
    "Lindcombe Health":   H("heavy"  , "#2e7d4f", "#123521", 1.0, False, "round", "wave", "mark_left",  "top_left",    "none",  "mono",     400, "title",     0.5),
    "Sedgemoor Pharmacy": H("thin",    "#9a6a1f", "#3d2a0a", 0.9, False, "sharp", "bars",   "mark_above", "top_center",  "none" , "mono",     700, "lower",     2.0),
    "Ottermere Care":     H("rounded", "#2a6f8f", "#0f2f3d", 1.0, False, "round", "trio", "mark_only",  "top_right",  "plain", "humanist", 700, "title",     1.5),
}
# fmt: on
hs.HOUSE_STYLES.update(STYLES)
