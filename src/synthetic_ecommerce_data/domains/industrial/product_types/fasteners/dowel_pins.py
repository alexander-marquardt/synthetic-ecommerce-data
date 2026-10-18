"""Dowel pins, deepened from a breadth row into a modelled type (#53).

Three standards, every row read from a table a reviewer can open:

* ISO 2338 (unhardened, tolerance m6 or h8) and ISO 8734 (hardened, m6):
  the diameters, chamfers, nominal lengths and per-diameter length ranges
  are FreeCAD_FastenersWB's ``FsData/iso2338def.csv`` and
  ``FsData/iso8734def.csv`` at commit ``fddd07af``, the commit
  ``data/fastener_standards.json`` pins. Their Table 1 matches the ISO
  2338:1997 and ISO 8734:1997 preview PDFs; the materials, hardness and
  finishes are those previews' Table 2.
* ASME B18.8.2 hardened ground machine dowel pins: the Engineers Edge
  reproduction of the standard's table
  (``machine_dowel_pins_chart_ansi_asme__13076.htm``): the standard and
  oversize series diameters and each size's range of preferred lengths, at
  the steps its footnote b gives.

Left out on purpose: ISO 2338's diameters over 25 mm (30, 40, 50), larger
than any ISO 8734 or inch pin, and B18.8.2's 5/64" and 5/32", which the table
marks nonpreferred and gives no lengths. B18.8.2 fixes no hardness in that
table; the one figure the distributors' pages agree on is a surface of
Rockwell C60 minimum (their core figures disagree), so that is all an inch
line publishes. No pack quantity is published.

The census has no dowel pin prices: the type prices as the socket head cap
screw does (``price.BORROWS``), a hardened fastener priced by diameter and
length. That price is generated, not measured.
"""

from __future__ import annotations

import math
from collections.abc import Mapping
from fractions import Fraction
from typing import Any, NamedTuple

from synthetic_ecommerce_data.core.dimensions import DimensionParseError, parse_length
from synthetic_ecommerce_data.core.drawing.model import Figure
from synthetic_ecommerce_data.core.typespec import TypeSpec
from synthetic_ecommerce_data.domains.industrial.drafts import retired
from synthetic_ecommerce_data.domains.industrial.drawing.figures import Drawn
from synthetic_ecommerce_data.domains.industrial.newtypes import table_provenance
from synthetic_ecommerce_data.domains.industrial.product_types.fasteners import screw_socket_head
from synthetic_ecommerce_data.domains.industrial.vocab import AttrSpec

KEY = "dowel_pins"
MM = 25.4

ISO_2338 = "ISO 2338"
ISO_8734 = "ISO 8734"
B18_8_2 = "ASME B18.8.2"


class MetricRow(NamedTuple):
    """One diameter of an ISO table: d and c (mm), and the shortest and longest l."""

    d: float
    c: float
    min_l: int
    max_l: int


#: FastenersWB ``iso2338def.csv`` (sections ``ISO2338def`` and
#: ``ISO2338range``): d, c, min_L, max_L, mm. The rows over 25 mm are left out.
ISO_2338_ROWS = (
    MetricRow(0.6, 0.12, 2, 6), MetricRow(0.8, 0.16, 2, 8), MetricRow(1, 0.2, 4, 10),
    MetricRow(1.2, 0.25, 4, 12), MetricRow(1.5, 0.3, 4, 16), MetricRow(2, 0.35, 6, 20),
    MetricRow(2.5, 0.4, 6, 24), MetricRow(3, 0.5, 8, 30), MetricRow(4, 0.63, 8, 40),
    MetricRow(5, 0.8, 10, 50), MetricRow(6, 1.2, 12, 60), MetricRow(8, 1.6, 14, 80),
    MetricRow(10, 2, 18, 95), MetricRow(12, 2.5, 22, 140), MetricRow(16, 3, 26, 180),
    MetricRow(20, 3.5, 35, 200), MetricRow(25, 4, 50, 200),
)  # fmt: skip
#: ``ISO2338length``: the nominal lengths, mm.
ISO_2338_LENGTHS = (
    2, 3, 4, 5, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32, 35, 40, 45, 50,
    55, 60, 65, 70, 75, 80, 85, 90, 95, 100, 120, 140, 160, 180, 200,
)  # fmt: skip
#: FastenersWB ``iso8734def.csv`` (``ISO8734def`` and ``ISO8734range``), mm.
ISO_8734_ROWS = (
    MetricRow(1, 0.2, 3, 10), MetricRow(1.5, 0.3, 4, 16), MetricRow(2, 0.35, 5, 20),
    MetricRow(2.5, 0.4, 6, 24), MetricRow(3, 0.5, 8, 30), MetricRow(4, 0.63, 10, 40),
    MetricRow(5, 0.8, 12, 50), MetricRow(6, 1.2, 14, 60), MetricRow(8, 1.6, 18, 80),
    MetricRow(10, 2, 22, 100), MetricRow(12, 2.5, 26, 100), MetricRow(16, 3, 40, 100),
    MetricRow(20, 3.5, 50, 100),
)  # fmt: skip
#: ``ISO8734length``: the nominal lengths, mm.
ISO_8734_LENGTHS = (
    3, 4, 5, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32, 35, 40, 45, 50, 55,
    60, 65, 70, 75, 80, 85, 90, 95, 100,
)  # fmt: skip


class InchRow(NamedTuple):
    """One B18.8.2 size: the pin diameter A's max and min in each series, and
    its preferred lengths as inclusive (shortest, longest) runs, inches."""

    size: str
    standard_max: str
    standard_min: str
    oversize_max: str
    oversize_min: str
    runs: tuple[tuple[str, str], ...]


#: ASME B18.8.2 (Engineers Edge reproduction): nominal size, A max and min in
#: the standard and oversize series, and "Range of Preferred Lengths".
B18_8_2_ROWS = (
    InchRow("1/16", "0.0628", "0.0626", "0.0636", "0.0634", (("3/16", "3/4"),)),
    InchRow("3/32", "0.0941", "0.0939", "0.0949", "0.0947", (("5/16", "1"),)),
    InchRow("1/8", "0.1253", "0.1251", "0.1261", "0.1259", (("3/8", "2"),)),
    InchRow("3/16", "0.1878", "0.1876", "0.1886", "0.1884", (("1/2", "2"),)),
    InchRow("1/4", "0.2503", "0.2501", "0.2511", "0.2509", (("1/2", "5/2"),)),
    InchRow("5/16", "0.3128", "0.3126", "0.3136", "0.3134", (("1/2", "5/2"),)),
    InchRow("3/8", "0.3753", "0.3751", "0.3761", "0.3759", (("1/2", "3"),)),
    InchRow("7/16", "0.4378", "0.4376", "0.4386", "0.4384", (("7/8", "3"),)),
    InchRow("1/2", "0.5003", "0.5001", "0.5011", "0.5009", (("3/4", "3/4"), ("1", "4"))),
    InchRow("5/8", "0.6253", "0.6251", "0.6261", "0.6259", (("5/4", "5"),)),
    InchRow("3/4", "0.7503", "0.7501", "0.7511", "0.7509", (("3/2", "6"),)),
    InchRow("7/8", "0.8753", "0.8751", "0.8761", "0.8759", (("2", "2"), ("5/2", "6"))),
    InchRow("1", "1.0003", "1.0001", "1.0011", "1.0009", (("2", "2"), ("5/2", "5"), ("6", "6"))),
)  # fmt: skip
#: Footnote b's length steps: 1/16" to 3/8", 1/8" to 1", 1/4" to 2-1/2", then 1/2".
B18_8_2_LENGTHS = tuple(
    [Fraction(k, 16) for k in range(3, 7)]
    + [Fraction(k, 8) for k in range(4, 9)]
    + [Fraction(k, 4) for k in range(5, 11)]
    + [Fraction(k, 2) for k in range(6, 13)]
)


def metric_lengths(standard: str, row: MetricRow) -> tuple[int, ...]:
    """The nominal lengths ``standard``'s range admits for ``row``, mm."""
    nominal = ISO_2338_LENGTHS if standard == ISO_2338 else ISO_8734_LENGTHS
    return tuple(length for length in nominal if row.min_l <= length <= row.max_l)


def inch_lengths(row: InchRow) -> tuple[Fraction, ...]:
    """The footnote-b steps inside ``row``'s preferred runs, inches."""
    runs = [(Fraction(low), Fraction(high)) for low, high in row.runs]
    return tuple(v for v in B18_8_2_LENGTHS if any(low <= v <= high for low, high in runs))


def inch_tolerance(row: InchRow, oversize: bool) -> str:
    """A's limits over the nominal size, as the table's max and min give them."""
    nominal = Fraction(row.size)
    high, low = (
        (row.oversize_max, row.oversize_min) if oversize else (row.standard_max, row.standard_min)
    )
    over = [Fraction(v) - nominal for v in (low, high)]
    return " to ".join(f'+{float(v):.4f}"' for v in over)


#: A metric line's grade: (Type, Material, finishes, hardness), from each
#: standard's Table 2. ISO 8734's Type A is through-hardened and Type B
#: case-hardened (its HV1 figure is the surface's); C1 is a martensitic
#: stainless steel (ISO 3506-1), and ISO 2338's A1 an austenitic one.
ISO_2338_GRADES = (
    ("Unhardened", "Steel", ("Plain", "Black Oxide", "Zinc Plated"), "125-245 HV30"),
    ("Unhardened", "18-8 Stainless Steel", ("Plain",), "210-280 HV30"),
)
ISO_8734_GRADES = (
    ("Through Hardened", "Steel", ("Plain",), "550-650 HV30"),
    ("Case Hardened", "Steel", ("Plain",), "600-700 HV1 (surface)"),
    ("Hardened", "Stainless Steel", ("Plain",), "460-560 HV30"),
)
#: ISO 2338's two diameter tolerance classes; ISO 8734 is m6 only.
ISO_2338_TOLERANCES = ("m6", "h8")
#: B18.8.2's carbon or alloy steel, by the one figure its sources agree on.
INCH_MATERIAL = "Steel"
INCH_HARDNESS = "Rockwell C60 min. (surface)"
#: Every third line of an inch size is the oversize series.
OVERSIZE_PERIOD = 3
#: The series a line is drawn from, in rotation: half inch, a quarter each ISO.
SERIES = (B18_8_2, ISO_8734, B18_8_2, ISO_2338)
#: A pin longer than KNEE inches is drawn compressed, with a break, into at
#: most KNEE + TAIL: a 200 mm pin would otherwise dwarf every short one.
KNEE = 2.4
TAIL = 0.45
#: The drawing's extent, measured at the default and ``--lines 39000`` builds
#: (docs/adding-a-type.md "Figure and extent"): the largest drawn is 2.47 x
#: 2.84 in, the 1" pin's break marks, side view, gap and end view across and
#: a 200 mm pin compressed down the page.
EXTENT = (2.6, 2.95)


def _spec(name: str, scope: str, presence: float = 1.0, kind: str = "keyword") -> AttrSpec:
    return AttrSpec(name=name, scope=scope, presence=presence, kind=kind)


#: One label and one machine key (``dowel_dia``) for the diameter in either unit
#: system (#497): each value states its own unit, as a length does everywhere else.
DIA = "Dowel Dia."

VOCAB = (
    _spec("Type", "line"),
    _spec("Material", "line"),
    _spec("Finish", "line", 0.82),
    # Always published: it is what tells a standard pin from an oversize one.
    _spec("Dia. Tolerance", "line"),
    _spec("Hardness", "line", 0.6),
    _spec(DIA, "sku", kind="length"),
    _spec("Length", "sku", kind="length"),
)


def provenance(standard: str) -> str:
    """Every published dimension of a line is its standard's table's."""
    return table_provenance(*((name, standard) for name in (DIA, "Length", "Dia. Tolerance")))


def _make(gen: Any, type_key: str, category: tuple[str, ...]) -> Any:
    # Imported here: generate.py imports the type tables, which discover this module.
    from synthetic_ecommerce_data.core import brands
    from synthetic_ecommerce_data.core.model import keyword_attribute
    from synthetic_ecommerce_data.domains.industrial.generate import ChildDraft, LineDraft

    rng = gen.rng
    standard = SERIES[gen._rotate(f"series:{type_key}", len(SERIES))]
    metric = standard != B18_8_2
    finish = ""
    if standard == B18_8_2:
        row = B18_8_2_ROWS[gen._rotate(f"size:{type_key}:{standard}", len(B18_8_2_ROWS))]
        oversize = gen._rotate(f"oversize:{type_key}:{row.size}", OVERSIZE_PERIOD) == 2
        kind, material, hardness = "Hardened Ground", INCH_MATERIAL, INCH_HARDNESS
        tolerance = inch_tolerance(row, oversize)
        diameter_in = float(Fraction(row.size))
        lengths_in = [float(v) for v in inch_lengths(row)]
        size_key = row.size
    else:
        rows = ISO_2338_ROWS if standard == ISO_2338 else ISO_8734_ROWS
        metric_row = rows[gen._rotate(f"size:{type_key}:{standard}", len(rows))]
        size_key = f"{metric_row.d:g}"
        grades = ISO_2338_GRADES if standard == ISO_2338 else ISO_8734_GRADES
        grade = grades[gen._rotate(f"grade:{type_key}:{standard}:{size_key}", len(grades))]
        kind, material, finishes, hardness = grade
        finish = rng.choice(finishes)
        tolerances = ISO_2338_TOLERANCES if standard == ISO_2338 else ("m6",)
        tolerance = tolerances[
            gen._rotate(f"tolerance:{type_key}:{standard}:{size_key}", len(tolerances))
        ]
        diameter_in = metric_row.d / MM
        lengths_in = [mm / MM for mm in metric_lengths(standard, metric_row)]
    brand = brands.pick_brand(rng, type_key, gen._exhausted)

    item = "Dowel Pin"
    draft = LineDraft(
        item=item,
        brand=brand,
        series=f"{standard.replace(' ', '').replace('.', '')}-{rng.randint(10, 99)}",
        category=category,
        provenance=provenance(standard),
        standard=standard,
    )
    draft.line_attrs = [
        retired(keyword_attribute("Item", item)),  # keeps the stream stable for #497
        keyword_attribute("Type", kind),
        keyword_attribute("Material", material),
        *([keyword_attribute("Finish", finish)] if finish else []),
        keyword_attribute("Dia. Tolerance", tolerance),
        keyword_attribute("Hardness", hardness),
    ]

    count = min(gen._variant_count(), len(lengths_in))
    offered = gen._offered_run(f"lengths:{standard}:{size_key}", lengths_in, count)
    system = "mm" if metric else "in"
    for length_in in offered:
        style = gen._style(system)
        child = ChildDraft(system=system)
        child.primary = gen._length(DIA, diameter_in, style)
        length_attr = gen._length("Length", length_in, style)
        child.attrs = [child.primary, length_attr]
        child.secondary = {"other_length": length_attr}
        draft.children.append(child)
    return draft


def _value(record: Mapping[str, str], name: str) -> float | None:
    try:
        return parse_length(record[name]).inches
    except (KeyError, DimensionParseError):
        return None


def figure(record: dict[str, str]) -> Drawn:
    """A side view with chamfered ends, and an end view of the pin's face."""
    diameter = _value(record, DIA)
    length = _value(record, "Length")
    d = diameter or 0.25
    length = length or 4 * d
    r = d / 2
    knee = KNEE
    drawn = length if length <= knee else knee + TAIL * (1 - math.exp(-(length - knee)))
    fig = Figure(size_in=drawn)
    # The chamfer is a fifth of the diameter (ISO's c is 0.16-0.2 d), and
    # never more than a quarter of the drawn length.
    c = min(0.2 * d, drawn / 4)
    fig.poly([
        (-r + c, 0.0), (r - c, 0.0), (r, c), (r, drawn - c),
        (r - c, drawn), (-r + c, drawn), (-r, drawn - c), (-r, c),
    ])  # fmt: skip
    fig.lines([((-r, c), (r, c)), ((-r, drawn - c), (r, drawn - c))])
    if length > knee:
        cut = drawn * 0.45
        fig.lines([((-1.15 * r, cut + k), (1.15 * r, cut + k + 0.04)) for k in (0.0, 0.08)])
    cx = d * 1.4
    fig.disc((cx, r), r)
    fig.disc((cx, r), r - c, "plain")
    source = (
        "record"
        if diameter and _value(record, "Length")
        else ("partial" if diameter else "nominal")
    )
    return Drawn(fig, source)


def claims(
    facts: Mapping[str, str], *, metric: bool, provenance: str, standard: str
) -> tuple[str, ...]:
    """The line's table (ISO 2338, ISO 8734 or ASME B18.8.2); ISO 3506-1 for a
    metric stainless pin, whose A1 and C1 grades it defines."""
    if metric and "Stainless" in facts.get("Material", ""):
        return (standard, "ISO 3506-1")
    return (standard,)


SPEC = TypeSpec(
    KEY,
    category=("Fasteners", "Pins", "Dowel Pins"),
    standards_family="fastener",
    vocab=VOCAB,
    figure=figure,
    extent=EXTENT,
    make=_make,
    share=0.014,
    # The census has no dowel pins: the socket head screw's model, borrowed
    # (``price.BORROWS``), so the price is generated rather than measured.
    price=screw_socket_head.PRICE,
    claims=claims,
    may_claim=frozenset({"ISO 2338", "ISO 8734", "ASME B18.8.2", "ISO 3506-1"}),
    key_attributes=(DIA,),
    unit_primary=DIA,
    use_lines=(
        "Locates two mating parts in reamed holes so they reassemble in the same place.",
        "Pressed into a hole as a pivot, stop or alignment pin.",
    ),
)
