"""A brand's type treatment: font, weight, case, spacing, set to a measured width (#412).

The retail prototype names its brands in four type families, in four cases, with
letter-spacing and an italic. This module sets any of those on the shared core's
width model (:func:`brand_mark.text_width`, the Helvetica-Bold advance table) rather
than on a second table of its own:

* a family only scales the core's width (and Courier is fixed-pitch, so its width
  is the pitch), so there is one table of glyph advances in the repo;
* :func:`set_lines` fits a name to a room the way :func:`brand_mark.lockup` does:
  one line if the name reaches the least legible size on it, else two lines broken
  at the balancing space (:func:`brand_mark.split_name`), else it raises;
* :func:`text` writes the line with ``textLength`` pinned to the model's width, so
  a viewer with another face squeezes the glyphs instead of overflowing the box.

The least legible size is the core's rule (:data:`sheet.MIN_NAME_PX`: the capitals
stand at least 10 px tall at the Studio tile) stated for the family's cap height.
Small capitals are drawn at :data:`SMALL_CAP` of a capital, so a small-caps name
is held to that smaller glyph.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from html import escape
from typing import Protocol

from synthetic_ecommerce_data.core.drawing import brand_mark, sheet


class Treatment(Protocol):
    """What a brand's wordmark needs of its style: the retail house style has all of it."""

    font: str
    weight: int
    case: str
    spacing: float
    italic: bool


@dataclass(frozen=True)
class Family:
    """One of the four wordmark families."""

    stack: str  # the CSS font stack
    cap_height: float  # a capital's height, as a share of the font size
    regular: float  # width at weight 400, as a share of Helvetica-Bold's
    bold: float  # width at weight 700, likewise
    pitch: float | None = None  # a fixed-pitch face's advance per font size


FAMILIES: dict[str, Family] = {
    "sans": Family("Helvetica, Arial, sans-serif", 0.716, 0.935, 1.0),
    "serif": Family("Georgia, 'Times New Roman', serif", 0.692, 0.92, 0.98),
    "mono": Family("'Courier New', Courier, monospace", 0.571, 1.0, 1.0, pitch=0.6),
    "humanist": Family("'Trebuchet MS', Verdana, sans-serif", 0.715, 0.90, 0.96),
}
#: A small capital's height and width, as a share of a full capital's.
SMALL_CAP = 0.8
#: The share of a line's font size between two baselines (the core's).
LINE_GAP = brand_mark.LINE_GAP
#: A descender's depth, as a share of the font size (the core's).
DESCENDER = brand_mark.DESCENDER

CASES = ("title", "caps", "lower", "smallcaps")


def cased(style: Treatment, text: str) -> str:
    """``text`` in ``style``'s case: the string the viewer is given."""
    return {"caps": text.upper(), "lower": text.lower()}.get(style.case, text)


def cap_height(style: Treatment) -> float:
    """The height of the smallest capital the wordmark draws, per unit of font size."""
    cap = FAMILIES[style.font].cap_height
    return cap * SMALL_CAP if style.case == "smallcaps" else cap


def _unit(style: Treatment, shown: str) -> float:
    """``shown``'s advance at font size 1, before letter-spacing."""
    fam = FAMILIES[style.font]
    if fam.pitch is not None:
        return len(shown) * fam.pitch
    if style.case == "smallcaps":
        # a lowercase letter is drawn as a small capital of its own capital's width
        wide = sum(
            brand_mark.text_width(c.upper(), 1.0) * (SMALL_CAP if c.islower() else 1.0)
            for c in shown
        )
    else:
        wide = brand_mark.text_width(shown.upper() if style.case == "caps" else shown, 1.0)
    return wide * (fam.bold if style.weight >= 600 else fam.regular)


def width(style: Treatment, text: str, size: float) -> float:
    """``text``'s set width at ``size`` in ``style``, letter-spacing included."""
    shown = cased(style, text)
    return _unit(style, shown) * size + len(shown) * style.spacing


def min_size(style: Treatment, px_per_unit: float) -> float:
    """The least font size, to one decimal, that stands :data:`sheet.MIN_NAME_PX` tall
    at the tile (``px_per_unit`` tile pixels to a sheet unit)."""
    return math.ceil(sheet.MIN_NAME_PX / (cap_height(style) * px_per_unit) * 10) / 10


def _floor(size: float) -> float:
    return math.floor(size * 10 + 1e-9) / 10


def fit_size(style: Treatment, lines: tuple[str, ...], room: float, start: float) -> float:
    """The largest size up to ``start`` (to one decimal) at which every line fits ``room``."""
    best = start
    for line in lines:
        shown = cased(style, line)
        room_for_glyphs = room - len(shown) * style.spacing
        best = min(best, room_for_glyphs / (_unit(style, shown) or 1.0))
    return _floor(best)


@dataclass(frozen=True)
class Block:
    """A name set in one or two lines at one size."""

    lines: tuple[str, ...]
    size: float
    width: float  # the widest line's set width

    @property
    def gap(self) -> float:
        """The distance between two baselines."""
        return self.size * LINE_GAP

    def height(self, cap: float) -> float:
        """From the first line's capitals down past the last line's descenders."""
        return cap * self.size + (len(self.lines) - 1) * self.gap + DESCENDER * self.size

    def baselines(self, centre: float, cap: float) -> list[float]:
        """The baselines that centre the capitals' band of the whole block on ``centre``."""
        span = (len(self.lines) - 1) * self.gap
        first = centre - span / 2 + cap * self.size / 2
        return [first + i * self.gap for i in range(len(self.lines))]


def set_lines(
    style: Treatment, name: str, room: float, max_size: float, px_per_unit: float
) -> Block:
    """``name`` as large as fits ``room``, up to ``max_size``, never under :func:`min_size`.

    A face whose least legible size is above ``max_size`` is set at that least size
    at most (a short name never grows past what legibility asks).

    One line if it reaches the least legible size, else two lines broken at the
    space that best balances them; a name neither sets at that size raises, so the
    drawing never has a wordmark under the rule or a shortened one.
    """
    least = min_size(style, px_per_unit)
    options: list[tuple[str, ...]] = [(name,)]
    split = brand_mark.split_name(name)
    if split is not None:
        options.append(split)
    for lines in options:
        size = fit_size(style, lines, room, max(max_size, least))
        if size >= least:
            return Block(lines, size, max(width(style, line, size) for line in lines))
    raise ValueError(f"{name!r} fits {room:g} units in no layout at {least} or more")


def text(
    style: Treatment,
    line: str,
    x: float,
    baseline: float,
    size: float,
    color: str,
    anchor: str = "start",
) -> str:
    """One line of a wordmark; ``(x, baseline)`` is the anchor, the width is pinned.

    ``size`` is written at one decimal, and the width is that written size's.
    """
    size = float(f"{size:.1f}")
    attrs = [
        f'x="{x:.1f}" y="{baseline:.1f}"',
        f'font-family="{FAMILIES[style.font].stack}"',
        f'font-size="{size:g}"',
        f'font-weight="{style.weight}"',
        f'fill="{color}"',
        f'text-anchor="{anchor}"',
        f'textLength="{width(style, line, size):.1f}"',
        'lengthAdjust="spacingAndGlyphs"',
    ]
    if style.spacing:
        attrs.append(f'letter-spacing="{style.spacing:g}"')
    if style.case == "smallcaps":
        attrs.append('font-variant="small-caps"')
    if style.italic:
        attrs.append('font-style="italic"')
    return f"<text {' '.join(attrs)}>{escape(cased(style, line), quote=False)}</text>"
