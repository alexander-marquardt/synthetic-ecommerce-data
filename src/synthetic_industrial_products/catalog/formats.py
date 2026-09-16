"""Publish a magnitude the way a catalog publishes it.

Catalogs do not publish numbers, they publish strings, and the same magnitude
appears as ``3/8"``, ``3/8 in``, ``0.3750"`` or ``9.53mm`` depending on which
era of the markup produced the page and which supplier supplied the row. The
measured corpus separates two independent choices, and this module keeps them
independent too:

*unit suffix*
    Which unit token the string ends with. Measured over the records carrying
    a milling diameter this partitions exactly: 79 ``"``, 35 `` in``, 17 ``mm``
    (:file:`07_value_format_variation.json`, ``by_attribute_concept``), and
    79 + 35 + 17 = 131 = the number of such records.

*magnitude shape*
    Whether the number is written as a vulgar fraction, a mixed number, a
    decimal or a bare integer.

Those two are tagged independently in the source statistics -- ``3/8"`` counts
as *both* ``bare_fraction`` and ``trailing_double_quote`` -- so the shape tag
counts in that file are NOT one exclusive distribution and must not be read as
one. The suffix tags are exclusive, and are what this module samples.
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


#: The imperial styles observed, with the weights the suffix partition gives
#: them. ``"`` outnumbers `` in`` roughly 79:35 in the milling-diameter column.
IMPERIAL_STYLES: tuple[tuple[LengthStyle, float], ...] = (
    (LengthStyle("in", '"', "fraction"), 0.34),
    (LengthStyle("in", '"', "mixed"), 0.14),
    (LengthStyle("in", '"', "decimal", places=4), 0.09),
    (LengthStyle("in", '"', "integer"), 0.03),
    (LengthStyle("in", " in", "fraction"), 0.15),
    (LengthStyle("in", " in", "mixed"), 0.06),
    (LengthStyle("in", " in", "integer"), 0.05),
    (LengthStyle("in", "in", "fraction"), 0.06),
    (LengthStyle("in", " in", "decimal", places=4), 0.04),
    (LengthStyle("in", "", "fraction"), 0.02),
    (LengthStyle("in", "", "mixed"), 0.02),
)

#: Metric styles. The corpus writes these as 3.00mm, 6mm and 12.70 mm.
METRIC_STYLES: tuple[tuple[LengthStyle, float], ...] = (
    (LengthStyle("mm", "mm", "decimal", places=2), 0.55),
    (LengthStyle("mm", "mm", "integer"), 0.25),
    (LengthStyle("mm", " mm", "decimal", places=2), 0.12),
    (LengthStyle("mm", " mm", "integer"), 0.08),
)


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
