"""Hex socket set screws, deepened from a breadth row into a modelled type (#53).

The spec space is the standards' own: ISO 4026 (flat), 4027 (cone), 4028 (dog)
and 4029 (cup point) for metric, ASME B18.3 for inch. Every size, pitch, socket
key, point diameter and metric length range is read from
``data/set_screw_standards.json``, which cites the table and row of each
value: ISO 4026-4029:2003 Table 1 and the B18.3 hexagon socket set screw
table. Nothing is interpolated. Left out on purpose: ISO's non-preferred
bracketed sizes (M1.8, M14, M18, M22), inch sizes over 1", and inch lengths
over 6".

Two choices the tables leave open:

* the point diameter published is the table's maximum on both systems: dp max
  for ISO 4026 and 4028, C max (flat) and P max (dog) for B18.3. A dog point's
  diameter is P, not the cup and flat point's C.
* B18.3 fixes no length range per size, so the inch ranges are FastenersWB's
  (the file the JSON cites), and an inch line's provenance says so. That
  list has no 5/16", 5/8" or 7/8" length and starts 1/4" screws at 3/8"; the
  gap is the source's, recorded in the JSON, and is not filled in here.

The sizes each table offers are declared as ``SIZES`` beside the data file,
and ``line_standard`` reads a record's standard back from its point and
thread, so the coverage sweep can hold every declared size to a document.

Materials and finishes are the three a distributor stocks set screws in. The
price is the measured model of #52, fitted to the price census (#69).
"""

from __future__ import annotations

import json
import math
from collections.abc import Mapping
from fractions import Fraction
from functools import cache
from importlib import resources
from typing import Any, NamedTuple

from synthetic_ecommerce_data.core.dimensions import DimensionParseError, parse_length, parse_thread
from synthetic_ecommerce_data.core.drawing.model import Figure, regular_polygon
from synthetic_ecommerce_data.core.price import ENDINGS, PriceModel
from synthetic_ecommerce_data.core.typespec import TypeSpec
from synthetic_ecommerce_data.domains.industrial import compat
from synthetic_ecommerce_data.domains.industrial.drafts import retired
from synthetic_ecommerce_data.domains.industrial.drawing.figures import Drawn
from synthetic_ecommerce_data.domains.industrial.newtypes import table_provenance
from synthetic_ecommerce_data.domains.industrial.standards import UNF_THREADS_PER_INCH
from synthetic_ecommerce_data.domains.industrial.vocab import AttrSpec

KEY = "set_screws_hex_socket"
MM = 25.4

#: The data file's key for the inch table.
INCH_TABLE = "ASME B18.3 set screws"
#: What an inch line's lengths are read from, since B18.3 fixes no range.
INCH_LENGTH_SOURCE = "FreeCAD_FastenersWB's inch set screw ranges, as ASME B18.3 fixes none"


class Row(NamedTuple):
    """One size of one table, in inches: what a SKU of that size publishes."""

    size: str
    #: Millimetres for a metric row, threads per inch for an inch row.
    pitch: float
    key_in: float
    #: The flat point's diameter (dp max, C max) and the dog point's (dp max, P max).
    flat_dia_in: float
    dog_dia_in: float
    lengths_in: tuple[float, ...]


@cache
def _data() -> dict:
    text = resources.files("synthetic_ecommerce_data.domains.industrial.data").joinpath(
        "set_screw_standards.json"
    )
    return json.loads(text.read_text("utf-8"))


def _inch(value: str) -> float:
    return float(Fraction(value))


def length_range_mm(standard: str, size: str) -> tuple[float, float]:
    """The shortest and longest length ``standard``'s Table 1 defines for ``size``, mm."""
    (row,) = (r for r in _data()[standard]["rows"] if r["size"] == size)
    return row["length_min_mm"], row["length_max_mm"]


@cache
def metric_rows(standard: str) -> tuple[Row, ...]:
    """``standard``'s rows (ISO 4026-4029), each with the lengths its range admits."""
    table = _data()[standard]
    nominal = table["_meta"]["nominal_lengths_mm"]
    # dp is a column of ISO 4026 and 4028 only; both share it, size for size.
    dp = {r["size"]: r["point_dia_max_mm"] for r in _data()["ISO 4026"]["rows"]}
    rows = []
    for r in table["rows"]:
        low, high = r["length_min_mm"], r["length_max_mm"]
        dia = float(dp[r["size"]]) / MM
        rows.append(Row(
            size=r["size"],
            pitch=r["pitch_mm"],
            key_in=float(r["socket_key_mm"]) / MM,
            flat_dia_in=dia,
            dog_dia_in=dia,
            lengths_in=tuple(mm / MM for mm in nominal if low <= mm <= high),
        ))  # fmt: skip
    return tuple(rows)


@cache
def inch_rows() -> tuple[Row, ...]:
    """The B18.3 rows, each with the lengths its (FastenersWB) range admits, to 6"."""
    table = _data()[INCH_TABLE]
    nominal = [_inch(v) for v in table["_meta"]["nominal_lengths_in"]]
    rows = []
    for r in table["rows"]:
        low, high = _inch(r["length_min_in"]), _inch(r["length_max_in"])
        rows.append(Row(
            size=r["size"],
            pitch=r["threads_per_inch"],
            key_in=_inch(r["socket_key_in"]),
            flat_dia_in=_inch(r["cup_flat_point_dia_max_in"]),
            dog_dia_in=_inch(r["dog_point_dia_max_in"]),
            lengths_in=tuple(v for v in nominal if low - 1e-9 <= v <= high + 1e-9),
        ))  # fmt: skip
    return tuple(rows)


def provenance(standard: str, point: str, metric: bool) -> str:
    """Where each published dimension of a line came from."""
    dimensions = ["Drive Size", *(["Point Dia."] if point in POINT_DIA_POINTS else [])]
    if metric:
        return table_provenance(*((name, standard) for name in ("Length", *dimensions)))
    return (
        f"{table_provenance(*((name, 'ASME B18.3') for name in dimensions))}; "
        f"Length from {INCH_LENGTH_SOURCE}"
    )


#: Point style -> (metric standard, inch standard section).
POINTS = {
    "Cup Point": ("ISO 4029", "ASME B18.3.5D"),
    "Flat Point": ("ISO 4026", "ASME B18.3.5A"),
    "Cone Point": ("ISO 4027", "ASME B18.3.5B"),
    "Dog Point": ("ISO 4028", "ASME B18.3.5C"),
}
#: The sizes each table offers, stated apart from the data file: the coverage
#: sweep holds every one to reaching a document, so a row dropped from the
#: file reds the sweep instead of quietly shrinking what it checks.
METRIC_SIZES = (
    "M1.6", "M2", "M2.5", "M3", "M4", "M5", "M6", "M8", "M10", "M12", "M16", "M20", "M24",
)  # fmt: skip
INCH_SIZES = (
    "#0", "#1", "#2", "#3", "#4", "#5", "#6", "#8", "#10",
    "1/4", "5/16", "3/8", "7/16", "1/2", "5/8", "3/4", "7/8", "1",
)  # fmt: skip
SIZES = {
    **{metric: METRIC_SIZES for metric, _ in POINTS.values()},
    **{inch: INCH_SIZES for _, inch in POINTS.values()},
}


def line_standard(record: Mapping[str, str]) -> str:
    """The standard a published record was built to: its point's, in its thread's system."""
    metric = record["Dia./Thread Size"].startswith("M")
    return POINTS[record["Point Type"]][0 if metric else 1]


#: The points a SKU publishes ``Point Dia.`` for.
POINT_DIA_POINTS = ("Flat Point", "Dog Point")
#: Material -> (finishes it is sold in, hardness). Alloy steel set screws are
#: through-hardened (ASTM F912, ISO 898-5 class 45H); stainless is not.
MATERIALS = {
    "Alloy Steel": (("Black Oxide", "Zinc Plated"), "Rockwell C45-C53"),
    "18-8 Stainless Steel": (("Plain",), ""),
    "316 Stainless Steel": (("Plain",), ""),
}
#: Every third line of an inch size with a fine series is UNF.
FINE_PERIOD = 3
#: The drawing's extent; a longer part is drawn compressed with a break. The
#: width holds the largest size (1"): the break marks reach 1.15 r left of the
#: axis and the end view's right edge sits at 1.9 x major, 2.475" in all.
EXTENT = (2.5, 3.2)


def _spec(name: str, scope: str, presence: float = 1.0, kind: str = "keyword") -> AttrSpec:
    return AttrSpec(name=name, scope=scope, presence=presence, kind=kind)


VOCAB = (
    _spec("Point Type", "line"),
    _spec("Drive Type", "line"),
    _spec("Material", "line"),
    _spec("Finish", "line", 0.82),
    _spec("Thread Direction", "line", 0.64),
    _spec("Thread Type", "line", 0.70),
    _spec("Hardness", "line", 0.48),
    _spec("Standards", "line", 0.40),
    _spec("Dia./Thread Size", "sku"),
    _spec("Length", "sku", kind="length"),
    # Entailed by ``Drive Type`` (see the socket screw vocabulary), so unconditional.
    _spec("Drive Size", "sku", kind="length"),
    _spec("Point Dia.", "sku", 0.6, kind="length"),
)


def _make(gen: Any, type_key: str, category: tuple[str, ...]) -> Any:
    # Imported here: generate.py imports the type tables, which discover this module.
    from synthetic_ecommerce_data.core import brands
    from synthetic_ecommerce_data.core.model import keyword_attribute
    from synthetic_ecommerce_data.domains.industrial.generate import ChildDraft, LineDraft

    rng = gen.rng
    metric = gen._rotate(f"system:{type_key}", 2) == 0
    points = list(POINTS)
    point = points[gen._rotate(f"point:{type_key}:{metric}", len(points))]
    standard = POINTS[point][0 if metric else 1]
    rows = metric_rows(standard) if metric else inch_rows()
    row = rows[gen._rotate(f"size:{type_key}:{standard}", len(rows))]
    size, pitch, lengths = row.size, row.pitch, list(row.lengths_in)
    materials = list(MATERIALS)
    material = materials[gen._rotate(f"material:{type_key}:{standard}:{size}", len(materials))]
    finishes, hardness = MATERIALS[material]
    finish = rng.choice(finishes)
    brand = brands.pick_brand(rng, type_key, gen._exhausted)

    if metric:
        thread, thread_type = f"{size}x{pitch:g}", "Metric Coarse"
    else:
        tpi, thread_type = pitch, "UNF" if size == "#0" else "UNC"
        fine = UNF_THREADS_PER_INCH.get(size)
        if fine and gen._rotate(f"fine:{type_key}:{standard}:{size}", FINE_PERIOD) == 2:
            tpi, thread_type = fine, "UNF"
        thread = f"{size}-{tpi:g}"
    meets = "ASME B18.3" if not metric else standard
    item = "Hex Socket Set Screw"
    draft = LineDraft(
        item=item,
        brand=brand,
        series=f"{standard.replace(' ', '').replace('.', '')}-{rng.randint(10, 99)}",
        category=category,
        provenance=provenance(standard, point, metric),
        standard=standard,
    )
    draft.line_attrs = [
        retired(keyword_attribute("Item", item)),  # keeps the stream stable for #497
        keyword_attribute("Point Type", point),
        keyword_attribute("Drive Type", "Hex Socket"),
        keyword_attribute("Material", material),
        keyword_attribute("Finish", finish),
        keyword_attribute("Thread Direction", "Right Hand"),
        keyword_attribute("Thread Type", thread_type),
        *([keyword_attribute("Hardness", hardness)] if hardness else []),
        keyword_attribute("Standards", meets),
    ]

    count = min(gen._variant_count(), len(lengths))
    offered = gen._offered_run(f"lengths:{standard}:{size}", lengths, count)
    system = "mm" if metric else "in"
    major_in = parse_thread(thread).major.inches
    # The nominal key, as every other type publishes it: a 5/32 filter must
    # reach the set screws a 5/32 key drives.
    key_in = compat.nominal_key_in(row.key_in, metric)
    point_dia_in = row.dog_dia_in if point == "Dog Point" else row.flat_dia_in
    for length_in in offered:
        style = gen._style(system)
        child = ChildDraft(system=system)
        child.primary = keyword_attribute("Dia./Thread Size", thread)
        length_attr = gen._length("Length", length_in, style)
        child.attrs = [child.primary, length_attr, gen._length("Drive Size", key_in, style)]
        if point in POINT_DIA_POINTS:
            child.attrs.append(gen._length("Point Dia.", point_dia_in, style))
        child.secondary = {"other_length": length_attr}
        child.price_basis = 0.15 + length_in * 0.15 + major_in * 0.6
        draft.children.append(child)
    return draft


def _value(record: dict[str, str], name: str) -> float | None:
    try:
        return parse_length(record[name]).inches
    except (KeyError, DimensionParseError):
        return None


def figure(record: dict[str, str]) -> Drawn:
    """A headless threaded body, its point, and an end view of the hex socket."""
    try:
        major = parse_thread(record["Dia./Thread Size"]).major.inches
        pitch = parse_thread(record["Dia./Thread Size"]).pitch_in
        read = True
    except (KeyError, DimensionParseError):
        major, pitch, read = 0.25, 0.05, False
    length = _value(record, "Length") or 1.5 * major
    key = _value(record, "Drive Size") or 0.5 * major
    point_dia = _value(record, "Point Dia.") or 0.6 * major
    r = major / 2
    height = EXTENT[1] * 0.95
    knee = 0.8 * height
    drawn = length if length <= knee else knee + 0.15 * height * (1 - math.exp(-(length - knee)))
    fig = Figure(size_in=drawn)
    point = record.get("Point Type", "Cup Point")
    tip = min(drawn / 3, r)
    body_end = drawn - tip
    fig.rect(-r, 0.0, r, body_end, "plain")
    crests = int(body_end / pitch) if pitch > 0 else 0
    fig.lines([((-r, k * pitch), (r, k * pitch + pitch / 2)) for k in range(min(crests, 400))])
    if point == "Cone Point":
        fig.poly([(-r, body_end), (r, body_end), (0.0, drawn)])
    elif point == "Dog Point":
        p = point_dia / 2
        fig.poly([(-r, body_end), (r, body_end), (p, body_end + tip / 3), (-p, body_end + tip / 3)])
        fig.rect(-p, body_end + tip / 3, p, drawn, "plain")
    else:
        p = point_dia / 2
        fig.poly([(-r, body_end), (r, body_end), (p, drawn), (-p, drawn)])
        if point == "Cup Point":
            fig.poly([(-0.6 * p, drawn), (0.6 * p, drawn), (0.0, drawn - tip / 2)], "hole")
    fig.rect(-key / 2, 0.0, key / 2, min(key, body_end / 2), "dark")
    if length > knee:
        cut = drawn * 0.45
        fig.lines([((-1.15 * r, cut + d), (1.15 * r, cut + d + 0.04)) for d in (0.0, 0.08)])
    cx = major * 1.4
    fig.disc((cx, r), r)
    fig.poly(regular_polygon((cx, r), key / math.sqrt(3), 6, 30), "dark")
    source = "record" if read and _value(record, "Length") else ("partial" if read else "nominal")
    return Drawn(fig, source)


#: The census slopes (size and length) and endings; the anchor and the three sigmas
#: fitted by ``scripts/fit_price_model.py`` to the 510 census set screws
#: (``deep_types.set_screws_hex_socket``); the size noise is one draw per
#: diameter that its lengths share (``price.SIZE_NOISE``). No brand figure is restated: the
#: only spec two brands share is one nylon line, so the drill's tiers apply.
PRICE = PriceModel(
    # @fit-begin set_screws_hex_socket
    anchor=17.69,
    anchor_key=0.25,
    slope=0.193,
    length_slope=0.216,
    group_sigma=0.083,
    sku_sigma=0.037,
    size_sigma=0.181,
    # @fit-end
    endings=ENDINGS["set_screws_hex_socket"],
)


def claims(
    facts: Mapping[str, str], *, metric: bool, provenance: str, standard: str
) -> tuple[str, ...]:
    """The point's ISO standard (metric) or ASME B18.3 (inch), then the
    material's: ISO 898-5 / ISO 3506-3 metric, ASTM F912 / F880 inch."""
    stainless = "Stainless" in facts.get("Material", "")
    if metric:
        return (standard, "ISO 3506-3" if stainless else "ISO 898-5")
    return ("ASME B18.3", "ASTM F880" if stainless else "ASTM F912")


SPEC = TypeSpec(
    KEY,
    category=("Fasteners", "Set Screws", "Hex Socket Set Screws"),
    standards_family="fastener",
    vocab=VOCAB,
    figure=figure,
    extent=EXTENT,
    make=_make,
    share=0.10,
    sizes=SIZES,
    line_standard=line_standard,
    price=PRICE,
    claims=claims,
    may_claim=frozenset(
        {"ISO 4026", "ISO 4027", "ISO 4028", "ISO 4029", "ASME B18.3", "ISO 898-5", "ISO 3506-3"}
        | {"ASTM F912", "ASTM F880"}
    ),
    key_attributes=("Dia./Thread Size",),
    use_lines=(
        "Driven with a hex key.",
        "Holds a collar, pulley or gear on its shaft from inside a tapped hole.",
    ),
)
