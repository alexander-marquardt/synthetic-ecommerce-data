"""Publish a magnitude the way a catalog publishes it.

Catalogs do not publish numbers, they publish strings. This module writes the
string, and it writes exactly ONE string per magnitude per unit system.

That last property is the point of this module and is easy to lose. The
measured corpus does carry several spellings of one magnitude -- ``3/8"``
beside ``3/8 in`` beside ``0.3750"`` -- because it is a union of feeds from
suppliers who each made their own choice. This generator used to reproduce
that by DRAWING a spelling at random per value, which is a different thing:
it put three spellings of one size inside one column of one catalog, so a
discrete facet over the published value offered 147 buckets for 49 drive
sizes (elastic/prism#9285, measured).

The reference distributor's own data does not look like that. Their facet values are a
clean ladder -- ``1/64, 1/32, 3/64, 1/16, 5/64, 3/32, 7/64, 1/8`` for
``Mill Diameter (Inch)`` -- one spelling per value, captured in
``square-end-mill-unfiltered.json`` and unanimous across all 23 of their
facets. So the noise was never faithful; it was invented.

**The rule now: the spelling is a FUNCTION of the magnitude, not a draw.**
Same magnitude, same system, same string, every time. Two things follow, and
both are deliberate:

*one suffix per system*
    The modal observed suffix wins. Imperial is the inch double-prime -- 79
    of the 131 milling-diameter records against 35 for `` in`` and 17 metric
    (:file:`07_value_format_variation.json`, ``by_attribute_concept``).
    Metric is ``mm`` with no space, 0.80 of the metric weight.

*the tidiest shape that states the magnitude EXACTLY*
    Already this module's own principle -- see :func:`_as_fraction` -- now
    applied to the choice of shape as well as to the choice of denominator.
    An inch magnitude on the 1/64 ladder is a fraction (``3/4"``) or a mixed
    number (``1-1/2"``) or a whole number (``3"``); one that is not gets a
    decimal (``0.0210"``). A metric magnitude is an integer (``6mm``) or a
    two-place decimal (``12.70mm``). Nothing is rounded to reach a shape.

What this is NOT is a normaliser. Nothing here rewrites a value it is handed;
it writes a value from a number, once, cleanly. The renderer's rule that a
published value is shown as the catalog published it
(:meth:`dimensions.Dimension.display`) is untouched and must stay untouched:
the fix for a fragmented facet is clean input, never a renderer that tidies.
See elastic/prism#9284 for the ruling.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from fractions import Fraction

MM_PER_INCH = 25.4

#: Denominators a catalog will actually print for an inch dimension. A tool
#: catalog writes 13/16", never 0.8125" rounded to a 64th it does not land on.
_INCH_DENOMINATORS = (2, 4, 8, 16, 32, 64)


class UnpublishableMagnitude(ValueError):
    """The magnitude cannot be written in the requested shape without lying.

    Raised rather than rounded. A rounded dimension is a number the record does
    not contain, and every consumer downstream -- the drawing especially --
    would then disagree with the record it was drawn from.
    """


@dataclass(frozen=True)
class LengthStyle:
    """One way of writing a length: a unit suffix and a magnitude shape."""

    #: "in" or "mm" -- which unit the magnitude is expressed in.
    system: str
    #: The literal token the string ends with: '"', " in", "in", "mm", " mm", "".
    suffix: str
    #: "fraction", "mixed", "decimal" or "integer".
    shape: str
    #: Decimal places, for the decimal shape only.
    places: int = 4

    @property
    def unitless(self) -> bool:
        return self.suffix == ""


#: THE imperial spelling. Not a distribution -- one style, because one
#: magnitude must produce one string. The shape says ``fraction`` and
#: :func:`format_length_best` walks fraction -> mixed -> integer -> decimal,
#: so the shape that actually lands is decided by the magnitude:
#: ``3/4"``, ``1-1/2"``, ``3"``, ``0.0210"``.
IMPERIAL_CANONICAL = LengthStyle("in", '"', "fraction")

#: THE metric spelling, on the same principle: ``integer`` first, so a whole
#: number of millimetres is ``6mm`` and everything else falls through to the
#: two-place decimal the corpus writes -- ``12.70mm``.
METRIC_CANONICAL = LengthStyle("mm", "mm", "integer")


def canonical_style(system: str) -> LengthStyle:
    """The one spelling this catalog publishes for *system*.

    A function rather than a dict lookup at the call site so that "which
    spelling does this catalog use" has exactly one answer and one place to
    read it.
    """
    if system == "in":
        return IMPERIAL_CANONICAL
    if system == "mm":
        return METRIC_CANONICAL
    raise ValueError(f"no canonical spelling declared for unit system {system!r}")


def _as_fraction(inches: float) -> Fraction:
    """The tidiest inch fraction that represents this magnitude exactly.

    Exactly: a magnitude that is not a multiple of 1/64 has no fractional
    spelling, and inventing one would publish a dimension the product does not
    have.
    """
    for denominator in _INCH_DENOMINATORS:
        scaled = inches * denominator
        if math.isclose(scaled, round(scaled), rel_tol=0, abs_tol=1e-9):
            return Fraction(round(scaled), denominator)
    raise UnpublishableMagnitude(
        f"{inches} in is not a multiple of 1/{_INCH_DENOMINATORS[-1]}; "
        "it has no fractional spelling and will not be rounded into one"
    )


def _fraction_text(value: Fraction, *, allow_whole: bool) -> str:
    whole, remainder = divmod(value.numerator, value.denominator)
    if remainder == 0:
        if not allow_whole:
            raise UnpublishableMagnitude(f"{value} is a whole number, not a vulgar fraction")
        return str(whole)
    if whole and not allow_whole:
        raise UnpublishableMagnitude(f"{value} is a mixed number, not a vulgar fraction")
    if whole:
        return f"{whole}-{remainder}/{value.denominator}"
    return f"{remainder}/{value.denominator}"


def format_length(inches: float, style: LengthStyle) -> str:
    """Write ``inches`` in ``style``, or raise if that shape would misstate it."""
    magnitude = inches if style.system == "in" else inches * MM_PER_INCH

    if style.shape == "decimal":
        return f"{magnitude:.{style.places}f}{style.suffix}"

    if style.shape == "integer":
        if not math.isclose(magnitude, round(magnitude), rel_tol=0, abs_tol=1e-9):
            raise UnpublishableMagnitude(f"{magnitude} is not a whole number of {style.system}")
        return f"{round(magnitude)}{style.suffix}"

    if style.system != "in":
        raise UnpublishableMagnitude("metric dimensions are not written as fractions")

    value = _as_fraction(inches)
    if style.shape == "fraction":
        return _fraction_text(value, allow_whole=False) + style.suffix
    if style.shape == "mixed":
        whole = value.numerator // value.denominator
        if whole == 0:
            raise UnpublishableMagnitude(f"{value} has no whole part; it is not a mixed number")
        return _fraction_text(value, allow_whole=True) + style.suffix
    raise UnpublishableMagnitude(f"unknown magnitude shape {style.shape!r}")


def format_length_best(inches: float, style: LengthStyle) -> str:
    """Write ``inches`` in ``style``, falling back along shapes that stay exact.

    The fallback order never rounds: it moves to a shape that can state this
    magnitude exactly (a 1-1/2 that was asked for as a vulgar fraction becomes
    a mixed number; a 0.0210 that has no fractional spelling becomes a
    decimal). What it will not do is round to reach the requested shape.
    """
    order = {
        "fraction": ("fraction", "mixed", "integer", "decimal"),
        "mixed": ("mixed", "fraction", "integer", "decimal"),
        "integer": ("integer", "mixed", "fraction", "decimal"),
        "decimal": ("decimal",),
    }[style.shape]
    for shape in order:
        # Keep the caller's precision when the shape they asked for is the one
        # being tried; only a fallback shape needs a default number of places.
        places = style.places if shape == style.shape else (4 if style.system == "in" else 2)
        candidate = LengthStyle(style.system, style.suffix, shape, places=places)
        try:
            return format_length(inches, candidate)
        except UnpublishableMagnitude:
            continue
    raise UnpublishableMagnitude(f"{inches} in cannot be published in any shape")


def format_count(value: int) -> str:
    return str(value)


def format_angle(degrees: float) -> str:
    """Angles are published with their unit word, as ``30 Degrees``."""
    if math.isclose(degrees, round(degrees), rel_tol=0, abs_tol=1e-9):
        return f"{round(degrees)} Degrees"
    return f"{degrees:g} Degrees"
