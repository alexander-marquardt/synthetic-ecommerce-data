"""Marks and house styles of the six invented colour-word brands (gen#312, decoy class 7).

A brand whose name holds a colour word ("Green Harrow") sells goods of another colour, so a text
search for "green" ranks them first. Each brand draws its own name on its product images: a
dedicated house style (never the generic lockup) whose wordmark is the brand field, spelled the
way the title spells it. The logo may use the brand's colour word (a red "Red Linnet" mark on a
green cushion); the product itself is drawn in its true colour.

:mod:`house_styles` imports this module last, so the six marks join ``MARKS`` and the six
styles join ``HOUSE_STYLES`` whichever module is imported first.
"""

from __future__ import annotations

import house_styles as hs
from house_styles import _dot, _ring, _stroke, H


def m_harrow(c: str) -> list[str]:
    """A comb of five tines hanging from a bar."""
    tines = " ".join(f"M{x},-.5 L{x},.85" for x in ("-.6", "-.3", "0", ".3", ".6"))
    return [_stroke("M-.8,-.55 L.8,-.55", 0.14, c), _stroke(tines, 0.1, c)]


def m_skerry(c: str) -> list[str]:
    """A low rock with two waves breaking over it."""
    return [
        f'<path d="M-.9,.45 L-.45,-.35 L-.1,.1 L.3,-.55 L.9,.45 Z" fill="{c}"/>',
        _stroke("M-.9,.7 Q-.6,.5 -.3,.7 T.3,.7 T.9,.7", 0.1, c),
    ]


def m_larch(c: str) -> list[str]:
    """A tree of angled branch pairs on one trunk."""
    pairs = " ".join(f"M0,{y} L-{w},{y + 0.3} M0,{y} L{w},{y + 0.3}"
                     for y, w in ((-0.7, 0.3), (-0.3, 0.5), (0.1, 0.7)))
    return [_stroke("M0,-.9 L0,.9", 0.12, c), _stroke(pairs, 0.1, c)]


def m_sedge(c: str) -> list[str]:
    """Three blades of sedge leaning apart from one root."""
    return [_stroke("M0,.9 Q-.1,.1 -.6,-.8 M0,.9 Q0,.1 0,-.9 M0,.9 Q.1,.1 .6,-.8", 0.13, c)]


def m_heddle(c: str) -> list[str]:
    """Three upright loom heddles, each an eye on a thread."""
    out = []
    for x in (-0.55, 0.0, 0.55):
        out.append(_stroke(f"M{x},-.9 L{x},.9", 0.07, c))
        out.append(f'<ellipse cx="{x}" cy="0" rx=".17" ry=".34" fill="none" stroke="{c}" stroke-width=".09"/>')
    return out


def m_linnet(c: str) -> list[str]:
    """A small bird: a round body, a beak and a wing arc."""
    return [
        _dot(-0.1, 0.05, 0.6, c),
        f'<path d="M.45,-.1 L.95,.05 L.45,.2 Z" fill="{c}"/>',
        _stroke("M-.55,.2 Q-.1,-.35 .3,.1", 0.08, "#ffffff"),
        _ring(0.15, -0.2, 0.06, 0.04, "#ffffff"),
    ]


NEW_MARKS = {"harrow": m_harrow, "skerry": m_skerry, "larch": m_larch, "sedge": m_sedge,
             "heddle": m_heddle, "linnet": m_linnet}  # fmt: skip
hs.MARKS.update(NEW_MARKS)

# fmt: off
#: Brand -> house style: every lockup (the name is drawn beside or under the mark), none
#: a mark-only tag, so the wordmark is the brand field in title or small-caps case.
STYLES = {
    "Green Harrow":  H("#f1f6ea", "lines",    "thin",    "#3f7a3a", "#23361f", 1.0,  False, "round", "harrow",  "mark_left",  "top_left",      "none", "humanist", 700, "title",     0.5),
    "Yellow Skerry": H("#fffbe9", "none",     "double",  "#d9a521", "#4a3b12", 0.9,  False, "sharp", "skerry",  "badge",      "bottom_right",  "none", "serif",    400, "smallcaps", 1.5, True),
    "Black Larch":   H("#eceded", "grid",     "heavy",   "#232326", "#151517", 1.4,  False, "sharp", "larch",   "band_top",   "top_centre",    "none", "sans",     700, "title",     1.5),
    "Silver Sedge":  H("#f5f6f7", "dots",     "rounded", "#8a929a", "#2c3238", 0.8,  True,  "round", "sedge",   "mark_above", "bottom_left",   "none", "mono",     400, "title",     0.0),
    "Blue Heddon":   H("#eef3fb", "diagonal", "ticks",   "#2f5fa5", "#1b2c4a", 1.2,  False, "round", "heddle",  "pill",       "top_right",     "none", "serif",    700, "smallcaps", 0.5),
    "Red Linnet":    H("#fdf1ee", "hatch",    "none",    "#c8312e", "#3a1f1c", 1.1,  False, "round", "linnet",  "mark_right", "bottom_centre", "none", "sans",     400, "title",     1.0),
}
# fmt: on
hs.HOUSE_STYLES.update(STYLES)
