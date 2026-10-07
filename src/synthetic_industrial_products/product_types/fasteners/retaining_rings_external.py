"""External retaining rings: a breadth category deepened into a modelled type (#53).

The spec space is two series a distributor stocks, each in spring steel with
a phosphate finish or in stainless steel:

* metric rows are read from FreeCAD_FastenersWB at the commit
  ``data/fastener_standards.json`` records, ``FsData/din471def.csv`` (DIN 471,
  retaining rings for shafts): Size is the table's ``Dia`` (the shaft
  diameter d1), Thickness its ``S``, Groove Dia. its ``groove_dia`` (d2) and
  Inside Dia. its ``d_3`` (the ring's free inside diameter). The rows run from
  3 mm to 100 mm, every row the table has in that range. A metric line claims
  DIN 471.
* inch rows are a conventional shaft-size ladder, 1/8" to 2" in fractional
  steps. No readable ASME B18.27.1 table was found (FastenersWB has none), so
  an inch SKU publishes no Thickness, Groove Dia. or Inside Dia., and an inch
  line claims no dimensional standard, as the inch lock nut claims none.

No pack quantity is published: a second variant dimension is #14, and the
washer's census model this type prices on carries no pack term.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from fractions import Fraction
from typing import TYPE_CHECKING, Any

from ...catalog.model import keyword_attribute, length_attribute
from ...catalog.newtypes import MM_PER_INCH, NO_STANDARD, _weighted, _window, feed_style
from ...catalog.newtypes import table_provenance
from ...catalog.typespec import TypeSpec
from ...catalog.vocab import AttrSpec
from ...dimensions import DimensionParseError, parse_length
from ...drawing.figures import Drawn
from ...drawing.model import Figure, arc

if TYPE_CHECKING:
    from ...catalog.generate import LineDraft

STANDARD = "DIN 471"

#: (Material, Finish): the combinations both series are stocked in, and how
#: often a line is drafted in each.
COMBOS: tuple[tuple[tuple[str, str], float], ...] = (
    (("Spring Steel", "Phosphate"), 0.7),
    (("Stainless Steel", "Plain"), 0.3),
)

# --- metric: FastenersWB din471def.csv (Dia, S, d_3, groove_dia), mm ----------

#: (shaft diameter d1, thickness s, free inside diameter d3, groove diameter d2).
_DIN_471: tuple[tuple[float, float, float, float], ...] = (
    (3, 0.4, 2.7, 2.8), (4, 0.4, 3.7, 3.8), (5, 0.6, 4.7, 4.8), (6, 0.7, 5.6, 5.7),
    (7, 0.8, 6.5, 6.7), (8, 0.8, 7.4, 7.6), (9, 1, 8.4, 8.6), (10, 1, 9.3, 9.6),
    (11, 1, 10.2, 10.5), (12, 1, 11, 11.5), (13, 1, 11.9, 12.4), (14, 1, 12.9, 13.4),
    (15, 1, 13.8, 14.3), (16, 1, 14.7, 15.2), (17, 1, 15.7, 16.2), (18, 1.2, 16.5, 17),
    (19, 1.2, 17.5, 18), (20, 1.2, 18.5, 19), (21, 1.2, 19.5, 20), (22, 1.2, 20.5, 21),
    (23, 1.2, 21.5, 22), (24, 1.2, 22.2, 22.9), (25, 1.2, 23.2, 23.9),
    (26, 1.2, 24.2, 24.9), (27, 1.2, 24.9, 25.6), (28, 1.5, 25.9, 26.6),
    (29, 1.5, 26.9, 27.6), (30, 1.5, 27.9, 28.6), (31, 1.5, 28.6, 29.3),
    (32, 1.5, 29.6, 30.3), (33, 1.5, 30.5, 31.3), (34, 1.5, 31.5, 32.3),
    (35, 1.5, 32.2, 33), (36, 1.75, 33.2, 34), (37, 1.75, 34.2, 35), (38, 1.75, 35.2, 36),
    (39, 1.75, 36, 37), (40, 1.75, 36.5, 37.5), (41, 1.75, 37.5, 38.5),
    (42, 1.75, 38.5, 39.5), (44, 1.75, 40.5, 41.5), (45, 1.75, 41.5, 42.5),
    (46, 1.75, 42.5, 43.5), (47, 1.75, 43.5, 44.5), (48, 1.75, 44.5, 45.5),
    (50, 2, 45.8, 47), (52, 2, 47.8, 49.5), (54, 2, 49.8, 51), (55, 2, 50.8, 52),
    (56, 2, 51.8, 53), (57, 2, 52.8, 54), (58, 2, 53.8, 55), (60, 2, 55.8, 57),
    (62, 2, 57.8, 59), (63, 2, 58.8, 60), (65, 2.5, 60.8, 62), (67, 2.5, 62.5, 64),
    (68, 2.5, 63.5, 65), (70, 2.5, 65.5, 67), (72, 2.5, 67.5, 69), (75, 2.5, 70.5, 72),
    (77, 2.5, 72.5, 74), (78, 2.5, 73.5, 75), (80, 2.5, 74.5, 76.5), (82, 2.5, 76.5, 78.5),
    (85, 3, 79.5, 81.5), (87, 3, 81.5, 83.5), (88, 3, 82.5, 84.5), (90, 3, 84.5, 86.5),
    (92, 3, 86.5, 88.5), (95, 3, 89.5, 91.5), (97, 3, 91.5, 93.5), (98, 3, 92.5, 94.5),
    (100, 3, 94.5, 96.5),
)  # fmt: skip

# --- inch: a conventional shaft-size ladder, 1/8" to 2" ------------------------

#: Every 1/32" to 1/2", every 1/16" above it.
_INCH_SHAFTS: tuple[Fraction, ...] = tuple(
    [Fraction(n, 32) for n in range(4, 16)] + [Fraction(n, 16) for n in range(8, 33)]
)


def _inch_size(shaft: Fraction) -> str:
    """``1/4 in``, ``1 in``, ``1-1/4 in``: the breadth row's spelling."""
    whole, part = divmod(shaft, 1)
    if part == 0:
        return f"{whole} in"
    frac = f"{part.numerator}/{part.denominator}"
    return f"{whole}-{frac} in" if whole else f"{frac} in"


@dataclass(frozen=True)
class Series:
    """One stocked series: its system, its dimensional standard and its rows."""

    name: str
    system: str
    #: The dimensional standard every row is read from; empty for inch.
    standard: str
    #: (Size, thickness, inside dia., groove dia.); the last three in inches,
    #: or None where no readable table gives them.
    rows: tuple[tuple[str, float | None, float | None, float | None], ...]

    @property
    def provenance(self) -> str:
        """Where each published dimension was read from."""
        if self.standard:
            return table_provenance(
                ("Size", self.standard),
                ("Thickness", self.standard),
                ("Groove Dia.", self.standard),
                ("Inside Dia.", self.standard),
            )
        return (
            "Size from a conventional inch shaft-size ladder; no Thickness, Groove Dia. "
            "or Inside Dia. is published, as no readable ASME B18.27.1 table gives one; "
            f"{NO_STANDARD}"
        )


def _mm(value: float) -> float:
    return value / MM_PER_INCH


SERIES: tuple[tuple[Series, float], ...] = (
    (
        Series(
            "din471",
            "mm",
            STANDARD,
            tuple((f"{d:g} mm", _mm(s), _mm(d3), _mm(d2)) for d, s, d3, d2 in _DIN_471),
        ),
        0.5,
    ),
    (
        Series("inch", "in", "", tuple((_inch_size(f), None, None, None) for f in _INCH_SHAFTS)),
        0.5,
    ),
)

ITEM = "External Retaining Ring"

#: ``Size`` is the breadth row's size attribute: the shaft the ring fits.
VOCAB = (
    AttrSpec("Item", "line"),
    AttrSpec("Type", "line", 0.8),
    AttrSpec("Material", "line"),
    AttrSpec("Finish", "line", 0.9),
    AttrSpec("Size", "sku", kind="length"),
    AttrSpec("Thickness", "sku", 0.9, kind="length"),
    AttrSpec("Groove Dia.", "sku", 0.85, kind="length"),
    AttrSpec("Inside Dia.", "sku", 0.8, kind="length"),
)


def build(gen: Any, type_key: str, category: tuple[str, ...]) -> LineDraft:
    """One line: a series, one stocked combination, a window of its sizes."""
    # Imported here: generate imports the type tables, which discover this module.
    from ...catalog.brands import pick_brand
    from ...catalog.generate import BRANDS, ChildDraft, LineDraft

    rng = gen.rng
    brand = pick_brand(rng, type_key, gen._exhausted)
    series = _weighted(rng, SERIES)
    material, finish = _weighted(rng, COMBOS)
    draft = LineDraft(
        item=ITEM,
        brand=brand,
        series=f"XR{rng.randint(100, 999)}",
        category=category,
        provenance=series.provenance,
        standard=series.standard,
    )
    draft.line_attrs = [
        keyword_attribute("Item", ITEM),
        keyword_attribute("Type", "Basic"),
        keyword_attribute("Material", material),
        keyword_attribute("Finish", finish),
    ]
    draft.descriptors = [("Material", material)]
    style = feed_style(brand, series.system, BRANDS)
    for size, thickness, inside, groove in _window(
        gen, f"retaining-ring:{series.name}", list(series.rows), gen._variant_count()
    ):
        child = ChildDraft(system=series.system)
        child.primary = length_attribute("Size", size)
        child.attrs = [child.primary]
        for name, inches in (
            ("Thickness", thickness),
            ("Groove Dia.", groove),
            ("Inside Dia.", inside),
        ):
            if inches is not None:
                child.attrs.append(length_attribute(name, gen._publish(inches, style)))
        draft.children.append(child)
    return draft


# --- the drawing ---------------------------------------------------------------

#: The ring's radial section and its lugs are drawn at these proportions of
#: the inside diameter: no published value gives them.
_SECTION = 0.14
_GAP_DEG = 34.0


def _length_or(record: dict[str, str], name: str, fallback: float) -> tuple[float, bool]:
    try:
        return parse_length(record[name]).inches, True
    except (KeyError, DimensionParseError):
        return fallback, False


def ring(record: dict[str, str]) -> Drawn:
    """The ring's face (an open circle with a lug at each end) and its edge.

    The face's bore is the published Inside Dia., the edge's height the
    published Thickness. An inch SKU publishes neither, so both are drawn at
    a DIN 471 proportion of its Size and the drawing is ``partial``.
    """
    size, read = _length_or(record, "Size", 0.5)
    inside, ok_i = _length_or(record, "Inside Dia.", 0.93 * size)
    thickness, ok_t = _length_or(record, "Thickness", 0.06 * size)
    if not 0 < inside < size:
        inside, ok_i = 0.93 * size, False
    source = "record" if read and ok_i and ok_t else ("partial" if read else "nominal")
    r_in = inside / 2
    section = _SECTION * inside
    r_out = r_in + section
    start, end = 90 + _GAP_DEG / 2, 450 - _GAP_DEG / 2
    fig = Figure(size_in=2 * r_out)
    fig.poly(arc((0.0, 0.0), r_out, start, end, 48) + arc((0.0, 0.0), r_in, end, start, 48))
    lug = 0.75 * section
    for angle in (start, end):
        centre = (
            (r_in + section / 2) * math.cos(math.radians(angle)),
            (r_in + section / 2) * math.sin(math.radians(angle)),
        )
        fig.disc(centre, lug)
        fig.disc(centre, 0.45 * lug, "hole")
    edge = -(r_out + lug + 0.3 * r_out)
    fig.rect(-r_out, edge - thickness, r_out, edge, "plain")
    return Drawn(fig, source)


SPEC = TypeSpec(
    "retaining_rings_external",
    category=("Fasteners", "Retaining Rings", "External Retaining Rings"),
    standards_family="fastener",
    vocab=VOCAB,
    figure=ring,
    extent=(1.0, 1.0),
    make=build,
    share=0.015,
    use_lines=(
        "Snaps into a groove on a shaft to hold a part in place along it.",
        "Installs and removes with external retaining ring pliers through the lug holes.",
    ),
)
