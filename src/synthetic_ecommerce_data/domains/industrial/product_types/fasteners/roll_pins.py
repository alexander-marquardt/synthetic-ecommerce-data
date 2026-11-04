"""Roll pins (spring pins), deepened from a breadth row into a modelled type (#829).

The breadth row offered four inch diameters, two materials and two lengths. A
distributor's spring-pin space is a size table per kind and duty, and each
table here is one a reviewer can open:

* ISO 8752 (slotted, heavy duty), ISO 13337 (slotted, light duty), ISO 8750
  (coiled, standard duty) and ISO 8748 (coiled, heavy duty): the diameters,
  the nominal lengths and each diameter's range of lengths are
  FreeCAD_FastenersWB's ``FsData/iso8752def.csv``, ``iso13337def.csv``,
  ``iso8750def.csv`` and ``iso8748def.csv`` at commit ``fddd07af``, the commit
  ``core/standards_library/tables/fastener_standards.json`` and the dowel pins
  pin. The four tables share one list of nominal lengths.
* ASME B18.8.2 slotted spring pins: the ten nominal diameters, 1/16" to 1/2",
  of SPIROL's datasheet "Slotted Spring Pins" (``SPIROL-Slotted-Spring-Pins-us.pdf``,
  "Produced in accordance with ASME B18.8.2"), with its material hardnesses.
  Its list of nominal lengths is read too, but its grid of which length each
  diameter is stocked in is shaded cells that do not extract. So an inch pin's
  length is a stocked length from that list, between :data:`MIN_OVER_DIAMETER`
  and :data:`MAX_OVER_DIAMETER` diameters, and no length claims the table.

Left out on purpose: ISO 13337's diameters over 25 mm (28 to 50), larger than
any other table's pin and, drawn, four times the width of a 1/2" one; ASME
B18.8.2's coiled pins (no table was read); and a metric pin's hardness (the
ISO tables read carry none). No pack quantity is published (#14): a line is
one pin per SKU.
"""

from __future__ import annotations

import math
from collections.abc import Mapping
from fractions import Fraction
from typing import Any, NamedTuple

from synthetic_ecommerce_data.core.dimensions import DimensionParseError, parse_length
from synthetic_ecommerce_data.core.drawing.model import Figure
from synthetic_ecommerce_data.core.price import PriceModel
from synthetic_ecommerce_data.core.typespec import TypeSpec
from synthetic_ecommerce_data.domains.industrial.drafts import retired
from synthetic_ecommerce_data.domains.industrial.drawing.figures import Drawn
from synthetic_ecommerce_data.domains.industrial.newtypes import MM_PER_INCH, table_provenance
from synthetic_ecommerce_data.domains.industrial.vocab import AttrSpec

KEY = "roll_pins"
ITEM = "Roll Pin"
#: The cotter pin's label for a pin's diameter (``names.NAME_EXCEPTIONS``): one
#: concept, one key (#497).
DIA = "Pin Dia."

B18_8_2 = "ASME B18.8.2"
ISO_8752 = "ISO 8752"
ISO_13337 = "ISO 13337"
ISO_8750 = "ISO 8750"
ISO_8748 = "ISO 8748"

#: A roll pin is a rolled strip: one slot down its length, or coiled about twice.
SLOTTED = "Slotted"
COILED = "Coiled"
KINDS = (SLOTTED, COILED)


class MetricRow(NamedTuple):
    """One diameter of an ISO table: d, and the shortest and longest l, mm."""

    d: float
    min_l: int
    max_l: int


#: FastenersWB ``iso8752def.csv`` (``ISO8752def`` and ``ISO8752range``), mm.
ISO_8752_ROWS = (
    MetricRow(1, 4, 20), MetricRow(1.5, 4, 20), MetricRow(2, 4, 30), MetricRow(2.5, 4, 30),
    MetricRow(3, 4, 40), MetricRow(3.5, 4, 40), MetricRow(4, 4, 50), MetricRow(4.5, 5, 50),
    MetricRow(5, 5, 80), MetricRow(6, 10, 100), MetricRow(8, 10, 120), MetricRow(10, 10, 160),
)  # fmt: skip
#: FastenersWB ``iso13337def.csv`` (``ISO13337def`` and ``ISO13337range``), mm.
#: The rows over 25 mm (28 to 50) are left out.
ISO_13337_ROWS = (
    MetricRow(2, 4, 30), MetricRow(2.5, 4, 30), MetricRow(3, 4, 40), MetricRow(3.5, 4, 40),
    MetricRow(4, 4, 50), MetricRow(4.5, 6, 50), MetricRow(5, 6, 80), MetricRow(6, 10, 100),
    MetricRow(8, 10, 120), MetricRow(10, 10, 160), MetricRow(12, 10, 180),
    MetricRow(13, 10, 180), MetricRow(14, 10, 200), MetricRow(16, 10, 200),
    MetricRow(18, 10, 200), MetricRow(20, 10, 200), MetricRow(21, 14, 200),
    MetricRow(25, 14, 200),
)  # fmt: skip
#: FastenersWB ``iso8750def.csv`` (``ISO8750def`` and ``ISO8750range``), mm.
ISO_8750_ROWS = (
    MetricRow(0.8, 4, 16), MetricRow(1, 4, 16), MetricRow(1.2, 4, 16), MetricRow(1.5, 4, 24),
    MetricRow(2, 4, 40), MetricRow(2.5, 5, 45), MetricRow(3, 6, 50), MetricRow(3.5, 6, 50),
    MetricRow(4, 8, 60), MetricRow(5, 10, 60), MetricRow(6, 12, 75), MetricRow(8, 16, 120),
    MetricRow(10, 20, 120), MetricRow(12, 24, 160), MetricRow(14, 28, 200),
    MetricRow(16, 32, 200), MetricRow(20, 45, 200),
)  # fmt: skip
#: FastenersWB ``iso8748def.csv`` (``ISO8748def`` and ``ISO8748range``), mm.
ISO_8748_ROWS = (
    MetricRow(1.5, 4, 26), MetricRow(2, 4, 40), MetricRow(2.5, 5, 45), MetricRow(3, 6, 50),
    MetricRow(3.5, 6, 50), MetricRow(4, 8, 60), MetricRow(5, 10, 60), MetricRow(6, 12, 75),
    MetricRow(8, 16, 120), MetricRow(10, 20, 120), MetricRow(12, 24, 160),
    MetricRow(14, 28, 200), MetricRow(16, 35, 200), MetricRow(20, 45, 200),
)  # fmt: skip
#: The ``ISO87xxlength`` / ``ISO13337length`` nominal lengths, the same in all four, mm.
ISO_LENGTHS = (
    4, 5, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32, 35, 40, 45, 50, 55, 60,
    65, 70, 75, 80, 85, 90, 95, 100, 120, 140, 160, 180, 200,
)  # fmt: skip

#: Each ISO table's rows, its kind and its duty.
METRIC_TABLES: dict[str, tuple[MetricRow, ...]] = {
    ISO_8752: ISO_8752_ROWS,
    ISO_13337: ISO_13337_ROWS,
    ISO_8750: ISO_8750_ROWS,
    ISO_8748: ISO_8748_ROWS,
}
METRIC_KIND = {
    ISO_8752: (SLOTTED, "Heavy Duty"),
    ISO_13337: (SLOTTED, "Light Duty"),
    ISO_8750: (COILED, "Standard Duty"),
    ISO_8748: (COILED, "Heavy Duty"),
}


class InchRow(NamedTuple):
    """One ASME B18.8.2 slotted pin size: its nominal diameter, inches."""

    size: str


#: SPIROL's ASME B18.8.2 "Slotted Pin Specifications", nominal diameter.
B18_8_2_ROWS = tuple(
    InchRow(size)
    for size in ("1/16", "5/64", "3/32", "1/8", "5/32", "3/16", "1/4", "5/16", "3/8", "1/2")
)
#: SPIROL's inch "Length" column: 3/16" to 1" by 1/16", to 2" by 1/8", to 3" by 1/4".
INCH_LENGTHS = tuple(
    [Fraction(k, 16) for k in range(3, 17)]
    + [Fraction(k, 8) for k in range(9, 17)]
    + [Fraction(k, 4) for k in range(9, 13)]
)
#: An inch pin is stocked from two to twenty diameters long.
MIN_OVER_DIAMETER = 2
MAX_OVER_DIAMETER = 20

#: (Material, Finish): the combinations a pin is stocked in. SPIROL plates
#: carbon steel only; a stainless pin is plain.
COMBOS = (
    ("Steel", "Plain"),
    ("Steel", "Zinc Plated"),
    ("420 Stainless Steel", "Plain"),
    ("18-8 Stainless Steel", "Plain"),
)
#: SPIROL's "Pin Materials and Hardness", for an inch pin: high carbon steel
#: and martensitic (420) stainless. Its austenitic (18-8) pin is "work
#: hardened", a condition and not a figure, so it publishes none.
INCH_HARDNESS = {"Steel": "HV 458-560", "420 Stainless Steel": "HV 423-544"}

#: The table a line is drawn from, in rotation: three inch, one of each ISO.
SERIES = (B18_8_2, ISO_8752, B18_8_2, ISO_8750, B18_8_2, ISO_13337, ISO_8748)


def _spec(name: str, scope: str, presence: float = 1.0, kind: str = "keyword") -> AttrSpec:
    return AttrSpec(name=name, scope=scope, presence=presence, kind=kind)


VOCAB = (
    _spec("Type", "line"),
    _spec("Style", "line", 0.85),
    _spec("Material", "line"),
    _spec("Finish", "line", 0.85),
    _spec("Hardness", "line", 0.6),
    _spec(DIA, "sku", kind="length"),
    _spec("Length", "sku", kind="length"),
)


def metric_lengths(row: MetricRow) -> tuple[int, ...]:
    """The nominal lengths ``row``'s range admits, mm."""
    return tuple(length for length in ISO_LENGTHS if row.min_l <= length <= row.max_l)


def inch_lengths(row: InchRow) -> tuple[Fraction, ...]:
    """The stocked lengths of :data:`MIN_OVER_DIAMETER` to :data:`MAX_OVER_DIAMETER` diameters."""
    d = Fraction(row.size)
    return tuple(v for v in INCH_LENGTHS if MIN_OVER_DIAMETER * d <= v <= MAX_OVER_DIAMETER * d)


def provenance(standard: str) -> str:
    """A metric line's diameter and length are its table's; an inch line's length is stocked."""
    if standard == B18_8_2:
        return f"{table_provenance((DIA, standard))}; Length is a stocked length"
    return table_provenance((DIA, standard), ("Length", standard))


def _make(gen: Any, type_key: str, category: tuple[str, ...]) -> Any:
    # Imported here: generate.py imports the type tables, which discover this module.
    from synthetic_ecommerce_data.core import brands
    from synthetic_ecommerce_data.core.model import keyword_attribute
    from synthetic_ecommerce_data.domains.industrial.generate import ChildDraft, LineDraft

    rng = gen.rng
    standard = SERIES[gen._rotate(f"series:{type_key}", len(SERIES))]
    if standard == B18_8_2:
        row = B18_8_2_ROWS[gen._rotate(f"size:{type_key}:{standard}", len(B18_8_2_ROWS))]
        size_key = row.size
        kind, duty = SLOTTED, None
        diameter_in = float(Fraction(row.size))
        lengths_in = [float(v) for v in inch_lengths(row)]
    else:
        rows = METRIC_TABLES[standard]
        metric_row = rows[gen._rotate(f"size:{type_key}:{standard}", len(rows))]
        size_key = f"{metric_row.d:g}"
        kind, duty = METRIC_KIND[standard]
        diameter_in = metric_row.d / MM_PER_INCH
        lengths_in = [mm / MM_PER_INCH for mm in metric_lengths(metric_row)]
    material, finish = COMBOS[gen._rotate(f"combo:{type_key}:{standard}:{size_key}", len(COMBOS))]
    hardness = INCH_HARDNESS.get(material) if standard == B18_8_2 else None
    brand = brands.pick_brand(rng, type_key, gen._exhausted)

    draft = LineDraft(
        item=ITEM,
        brand=brand,
        series=f"RP{rng.randint(100, 999)}",
        category=category,
        provenance=provenance(standard),
        standard=standard,
    )
    draft.line_attrs = [
        retired(keyword_attribute("Item", ITEM)),  # keeps the stream stable for #497
        keyword_attribute("Type", kind),
        *([keyword_attribute("Style", duty)] if duty else []),
        keyword_attribute("Material", material),
        keyword_attribute("Finish", finish),
        *([keyword_attribute("Hardness", hardness)] if hardness else []),
    ]
    draft.descriptors = [("Material", material)]

    count = min(gen._variant_count(), len(lengths_in))
    offered = gen._offered_run(f"lengths:{standard}:{size_key}", lengths_in, count)
    system = "in" if standard == B18_8_2 else "mm"
    for length_in in offered:
        style = gen._style(system)
        child = ChildDraft(system=system)
        child.primary = gen._length(DIA, diameter_in, style)
        length_attr = gen._length("Length", length_in, style)
        child.attrs = [child.primary, length_attr]
        child.secondary = {"other_length": length_attr}
        draft.children.append(child)
    return draft


# --- the drawing ------------------------------------------------------------------

#: A pin longer than KNEE inches is drawn compressed into at most KNEE + TAIL,
#: so a 200 mm pin does not dwarf every short one.
KNEE = 2.4
TAIL = 0.45
#: The drawing's extent (docs/adding-a-type.md "Figure and extent"), measured
#: over every row and length the tables admit, so any build fits it: the
#: largest drawn is 2.362 x 2.848 in, a 25 mm pin's side view, gap and end
#: view across and a 200 mm pin compressed down the page.
EXTENT = (2.4, 2.85)


def _value(record: Mapping[str, str], name: str) -> float | None:
    try:
        return parse_length(record[name]).inches
    except (KeyError, DimensionParseError):
        return None


def figure(record: dict[str, str]) -> Drawn:
    """A side view with chamfered ends and the slot or coil seam down it, and
    an end view: a split ring for a slotted pin, a spiral for a coiled one."""
    diameter = _value(record, DIA)
    length = _value(record, "Length")
    d = diameter or 0.25
    full = length or 4 * d
    r = d / 2
    drawn = full if full <= KNEE else KNEE + TAIL * (1 - math.exp(-(full - KNEE)))
    fig = Figure(size_in=drawn)
    c = min(0.15 * d, drawn / 4)
    fig.poly([
        (-r + c, 0.0), (r - c, 0.0), (r, c), (r, drawn - c),
        (r - c, drawn), (-r + c, drawn), (-r, drawn - c), (-r, c),
    ])  # fmt: skip
    # The seam: the slot's two edges, or the coil's outer lap.
    gap = 0.12 * r
    seam = (-gap, gap) if record.get("Type") != COILED else (0.0,)
    fig.lines([((x, c), (x, drawn - c)) for x in seam])
    cx = d * 1.4
    fig.disc((cx, r), r)
    wall = 0.2 * r
    fig.disc((cx, r), r - wall, "plain")
    if record.get("Type") == COILED:
        fig.disc((cx, r), r - 2 * wall)
        fig.disc((cx, r), r - 3 * wall, "plain")
    else:
        fig.poly([(cx - gap, 2 * r), (cx + gap, 2 * r), (cx + gap, 2 * r - wall),
                  (cx - gap, 2 * r - wall)], "plain")  # fmt: skip
    source = "record" if diameter and length else ("partial" if diameter else "nominal")
    return Drawn(fig, source)


# --- price ------------------------------------------------------------------------

#: GENERATED, NOT MEASURED: the price census has no roll pins (neither
#: ``deep_types`` nor ``breadth_categories`` of P2_price_census.json). Hand-set
#: from the breadth row's level (0.10 to 1.50 USD for 1/8" to 3/8"): the anchor
#: is a standard-tier 1/4" steel pin 1" long, each. Its price scales with its
#: length below one for one (the pack slope), as the stud's does.
PRICE = PriceModel(
    0.35,
    0.25,
    1.1,
    0.2,
    0.08,
    measured=False,
    pack_attribute="Length",
    pack_slope=0.5,
    pack_ref=1.0,
    materials={"Steel": 1.0, "420 Stainless Steel": 1.5, "18-8 Stainless Steel": 1.6},
)


def claims(
    facts: Mapping[str, str], *, metric: bool, provenance: str, standard: str
) -> tuple[str, ...]:
    """The line's table: ASME B18.8.2, ISO 8752, ISO 13337, ISO 8750 or ISO 8748."""
    return (standard,)


SPEC = TypeSpec(
    KEY,
    category=("Fasteners", "Pins", "Roll Pins"),
    standards_family="fastener",
    vocab=VOCAB,
    figure=figure,
    extent=EXTENT,
    make=_make,
    share=0.012,
    price=PRICE,
    claims=claims,
    may_claim=frozenset({B18_8_2, ISO_8752, ISO_13337, ISO_8750, ISO_8748}),
    key_attributes=(DIA,),
    unit_primary=DIA,
    compat=False,
    use_lines=(
        "Pressed into a drilled hole, it springs against the wall and holds by its own tension.",
        "Pins a gear, collar or lever to a shaft without a reamed hole.",
    ),
)
