"""When two brands' drawings are visibly different, and how many brands that allows (#55).

A drawing's brand channels are its house style: the ink, the paper, the frame,
the mark and the four text-free levers the brand book declares
(:data:`..brands.WEIGHTS`, :data:`..brands.DASHES`, :data:`..brands.MARGINS`,
:data:`..brands.TEXTURES`). Twelve inks and four frames gave 48 pairs; the
levers multiply that, but counting combinations is not the limit.
DISTINGUISHABILITY is, so the rule is measurable:

Two brands are visibly different when ANY ONE STRONG LEVER differs:

* the frame (five treatments, apart at the 180 px tile);
* the mark (one pair per brand, pinned 24 pixels apart at the tile by
  ``tests/test_brand_marks.py``);
* the ink, but only when the two inks are at least :data:`MIN_INK_DELTA_E`
  apart (CIELAB distance) under normal vision AND under protanopia,
  deuteranopia and tritanopia (:func:`ink_delta_e`). Two inks nearer than that
  in any one of the four are one ink to some reader, and count as a WEAK lever;

or when at least :data:`WEAK_LEVERS_NEEDED` (3) WEAK levers differ: the paper
tint, the outline weight, the dash pattern, the frame margin, the texture, and
a confusable ink.

The ink-to-paper contrast floor (3:1) is a separate ground, held for every ink
against every paper (``tests/test_house_style_levers_55.py``).
"""

from __future__ import annotations

import functools
import itertools
import math
from typing import NamedTuple

from synthetic_ecommerce_data.core import brands

#: Brands the deepened catalog (#53) is sized for: three times the 45 of the
#: 100K build. #53 aims at "several hundred thousand SKUs", about three times
#: 100K, and a type whose spec space its makers exhaust grows by more makers.
BRANDS_NEEDED = 135
#: Weak levers that must differ when no strong one does.
WEAK_LEVERS_NEEDED = 3
#: The least CIELAB (CIE76) distance between two inks that count as an ink
#: difference, across the four kinds of vision in :data:`VISION`. 15 is a
#: clearly visible difference on a thin stroke; the 12 inks have 66 pairs, of
#: which :func:`confusable_ink_pairs` lists those under it.
MIN_INK_DELTA_E = 15.0

#: Color-vision models: normal, protanopia, deuteranopia, tritanopia. The
#: matrices are Machado, Oliveira and Fernandes (2009) at severity 1.0, applied
#: to linear sRGB.
VISION: tuple[str, ...] = ("none", "prot", "deut", "trit")
_MACHADO: dict[str, tuple[tuple[float, float, float], ...]] = {
    "none": ((1, 0, 0), (0, 1, 0), (0, 0, 1)),
    "prot": (
        (0.152286, 1.052583, -0.204868),
        (0.114503, 0.786281, 0.099216),
        (-0.003882, -0.048116, 1.051998),
    ),
    "deut": (
        (0.367322, 0.860646, -0.227968),
        (0.280085, 0.672501, 0.047413),
        (-0.011820, 0.042940, 0.968881),
    ),
    "trit": (
        (1.255528, -0.076749, -0.178779),
        (-0.078411, 0.930809, 0.147602),
        (0.004733, 0.691367, 0.303900),
    ),
}


class Style(NamedTuple):
    """One brand's house style: every lever as the index the book declares."""

    ink: int
    paper: int
    frame: int
    #: The brand's mark; two brands' marks differ when these are unequal.
    mark: object
    outline: int
    dash: int
    margin: int
    texture: int


def style_of(brand: str) -> Style:
    """``brand``'s house style from the brand book."""
    from synthetic_ecommerce_data.core.drawing.brand_mark import mark_for

    book = brands.BY_NAME[brand]
    return Style(
        book.ink,
        brands.PAPERS.index(brands.paper_of(brand)),
        book.frame,
        mark_for(brand),
        book.outline,
        book.dash,
        book.margin,
        book.texture,
    )


def _linear(channel: int) -> float:
    c = channel / 255
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def _lab(hex_color: str, vision: str) -> tuple[float, float, float]:
    rgb = [_linear(int(hex_color[i : i + 2], 16)) for i in (1, 3, 5)]
    r, g, b = (
        min(1.0, max(0.0, sum(row[j] * rgb[j] for j in range(3)))) for row in _MACHADO[vision]
    )
    x = 0.4124 * r + 0.3576 * g + 0.1805 * b
    y = 0.2126 * r + 0.7152 * g + 0.0722 * b
    z = 0.0193 * r + 0.1192 * g + 0.9505 * b

    def f(t: float) -> float:
        return t ** (1 / 3) if t > 216 / 24389 else (24389 / 27 * t + 16) / 116

    fx, fy, fz = f(x / 0.95047), f(y), f(z / 1.08883)
    return 116 * fy - 16, 500 * (fx - fy), 200 * (fy - fz)


def ink_delta_e(a: str, b: str, vision: tuple[str, ...] = VISION) -> float:
    """The least CIELAB distance of inks ``a`` and ``b`` over the ``vision`` models."""
    return min(math.dist(_lab(a, v), _lab(b, v)) for v in vision)


@functools.cache
def inks_are_safe(a: str, b: str) -> bool:
    """Whether two different inks are an ink difference under every kind of vision."""
    return a != b and ink_delta_e(a, b) >= MIN_INK_DELTA_E


def confusable_ink_pairs() -> list[tuple[str, str]]:
    """The book's ink pairs that are one ink to some reader, nearest first."""
    pairs = [(a, b) for a, b in itertools.combinations(brands.INKS, 2) if not inks_are_safe(a, b)]
    return sorted(pairs, key=lambda p: ink_delta_e(*p))


def visibly_different(a: Style, b: Style) -> bool:
    """The rule: a strong lever differs, or :data:`WEAK_LEVERS_NEEDED` weak ones do."""
    if a.frame != b.frame or a.mark != b.mark:
        return True
    ink_a, ink_b = brands.INKS[a.ink], brands.INKS[b.ink]
    if inks_are_safe(ink_a, ink_b):
        return True
    weak = sum(
        x != y
        for x, y in (
            (a.ink, b.ink),
            (a.paper, b.paper),
            (a.outline, b.outline),
            (a.dash, b.dash),
            (a.margin, b.margin),
            (a.texture, b.texture),
        )
    )
    return weak >= WEAK_LEVERS_NEEDED


@functools.cache
def pack() -> list[Style]:
    """A set of styles that share ONE mark and are pairwise visibly different.

    Greedy over every combination of the other levers, in lever order, so the
    set is the same on every machine. It is a lower bound on the space: the
    first greedy choice is not the largest set. Brands with different marks are
    different by the rule, so the whole space is this count times the marks
    (:func:`capacity_with_marks`), but the headline does not lean on them.
    """
    space = itertools.product(
        range(len(brands.INKS)),
        range(len(brands.PAPERS)),
        range(len(brands.ALL_FRAMES)),
        range(len(brands.WEIGHTS)),
        range(len(brands.DASHES)),
        range(len(brands.MARGINS)),
        range(len(brands.TEXTURES)),
    )
    chosen: list[Style] = []
    for ink, paper, frame, outline, dash, margin, texture in space:
        candidate = Style(ink, paper, frame, None, outline, dash, margin, texture)
        if all(visibly_different(candidate, other) for other in chosen):
            chosen.append(candidate)
    return chosen


def capacity() -> int:
    """How many brands the lever space holds under the rule, without counting the mark."""
    return len(pack())


def capacity_with_marks(marks: int) -> int:
    """``capacity()`` for each of ``marks`` distinct marks: brands with different marks differ."""
    return capacity() * marks
