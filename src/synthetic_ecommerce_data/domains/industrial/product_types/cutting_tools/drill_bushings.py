"""Drill bushings, deepened from a breadth row into a modelled type (#831).

A drill bushing is the hardened sleeve a drill jig guides a drill through:
pressed into the jig plate, or slipped into a liner pressed there so a worn
or second-operation bushing changes in seconds. ASME B94.33 numbers each by
its type, its body in sixty-fourths and its length in sixteenths: ``P-48-8``
is a headless press-fit bushing of a 3/4" body, 1/2" long.

**Sizes.** Every published body, length and head is a row of the standards
library's ``asme_b94_33_jig_bushings_in`` table, read from the makers'
B94.33 tables (B94.33 itself is sold and was not read): Boneham's ANSI drill
bushing pages for the P, H, SF and HL types, and AmesWeb's Type L table. A
row is one type and body, its finished outside diameter, its head for the H
and HL types, the lengths it is made in, and, for a bushing that guides a
drill, the range of bores it is made in. The bores are drill sizes: the
number and letter drills of ``asme_b94_11m_drill_series_in`` and the
fractional sizes by sixty-fourths, to the 1-7/8" the largest SF body takes.

**Lines.** A line is one brand's bushings of one type, body, bore range and
length; its SKUs are a run of the drill sizes in that range that its drawing
tells apart (:func:`ladder`, #50): a ``#28`` drill and a ``9/64`` one are
0.0001" apart and would draw alike, so they are never siblings. A liner guides
no drill: its bore is the renewable bushing's body, so a liner line is one
brand's liners of one type and length, and its SKUs are the bodies made in
that length. The combinations are rotated, not drawn, so every type is built.

**Material.** The pages name hardened steel at 60-65 HRC, published as
``Steel``, the breadth row's value.

**Price.** The census has no bushings: the model below is GENERATED, NOT
MEASURED.
"""

from __future__ import annotations

import contextlib
import functools
import math
from collections.abc import Mapping
from fractions import Fraction
from typing import Any

from synthetic_ecommerce_data.core import standards_library as library
from synthetic_ecommerce_data.core.dimensions import DimensionParseError, parse_length
from synthetic_ecommerce_data.core.drawing.model import Figure
from synthetic_ecommerce_data.core.price import PriceModel
from synthetic_ecommerce_data.core.typespec import TypeSpec
from synthetic_ecommerce_data.domains.industrial.drawing.figures import Drawn
from synthetic_ecommerce_data.domains.industrial.newtypes import table_provenance
from synthetic_ecommerce_data.domains.industrial.vocab import AttrSpec

KEY = "drill_bushings"
ITEM = "Drill Bushing"

TABLE = library.table("asme_b94_33_jig_bushings_in")
DRILLS = library.table("asme_b94_11m_drill_series_in")
#: The standard a line claims, and the label its provenance names the table by.
STANDARDS = ("ASME B94.33",)
SOURCE = STANDARDS[0]
#: The dimensions a record publishes, each read from the table.
DIMENSIONS = ("Size", "Outside Dia.", "Length", "Overall Length", "Head Dia.", "Head Height")

#: Each B94.33 type's published (Type, Head Type), in the order lines rotate through them.
TYPES: dict[str, tuple[str, str]] = {
    code: (spec["type"], spec["head"]) for code, spec in TABLE.data["types"].items()
}
#: The rows, in the table's order: by type, then body, then bore.
ROWS: tuple[dict, ...] = tuple(TABLE.rows)
#: The rows whose finished outside diameter is kept as printed and never published.
OD_AS_PRINTED = frozenset(
    label for label, note in TABLE.data["misprints"]["rows"] if "outside diameter" in note
)


def is_liner(row: Mapping[str, Any]) -> bool:
    """A liner's bore is a renewable bushing's body, not a drill size."""
    return "id_nominal" in row


def length_name(row: Mapping[str, Any]) -> str:
    """The name a row's length code is published under: a headed liner's is
    its overall length, every other type's its length under any head."""
    return "Overall Length" if row["type"] == "HL" else "Length"


def ansi_number(row: Mapping[str, Any], length: int) -> str:
    return f"{row['type']}-{row['body']}-{length}"


def _inches(text: str) -> float:
    return float(sum(Fraction(part) for part in text.split()))


def _fraction(sixty_fourths: int) -> str:
    whole, rest = divmod(sixty_fourths, 64)
    part = str(Fraction(rest, 64)) if rest else ""
    return "-".join(p for p in (str(whole) if whole else "", part) if p)


def _holes() -> tuple[tuple[str, float], ...]:
    """Every drill size a bushing is bored to, smallest first: the number and
    letter drills, and the fractional sizes by sixty-fourths to the largest
    bore the table lists. A letter drill of a fractional size (E, 1/4") is
    the fractional size."""
    largest = max(row["bore_max_in"] for row in ROWS if not is_liner(row))
    fractional = [(_fraction(n), n / 64) for n in range(1, round(largest * 64) + 1)]
    exact = {round(inches, 4) for _, inches in fractional}
    lettered = [
        (drill["drill"], drill["dia_in"])
        for drill in (*DRILLS.data["number"], *DRILLS.data["letter"])
        if round(drill["dia_in"], 4) not in exact
    ]
    return tuple(sorted((*fractional, *lettered), key=lambda hole: hole[1]))


HOLES = _holes()
_HOLE = dict(HOLES)


def hole_of(drill: str) -> tuple[str, float]:
    """The drill size a record's ``Drill Size`` names, with its diameter."""
    return drill, _HOLE[drill]


#: How far past a printed four-place bore limit a drill size may sit: 17/32"
#: is printed 0.5312.
_BORE_SLACK = 0.0001


def holes_of(row: Mapping[str, Any]) -> tuple[tuple[str, float], ...]:
    """The drill sizes inside a row's bore range."""
    low, high = row["bore_min_in"] - _BORE_SLACK, row["bore_max_in"] + _BORE_SLACK
    return tuple(hole for hole in HOLES if low <= hole[1] <= high)


#: The table's largest drawing plus 0.1", rounded up to 0.05" (docs/adding-a-type.md
#: "Figure and extent"): HL-176's 2-7/8" head, and H-144-48's 3" under a 3/8" head. The
#: default and ``--lines 39000`` builds draw at most 2.75 x 3.38 in.
EXTENT = (2.95, 3.5)


@functools.cache
def bore_step(row_index: int, length: int) -> float:
    """The least bore step a line of row ``row_index`` and length code ``length`` draws apart,
    at every angle a bushing turns by (#50).

    A bore line moves by half the step, times the scale, along the direction the angle turns it
    to, so along one axis by at least that over the square root of two. The drawing writes each
    coordinate at one decimal (``svg.num``), and two values more than 0.1 apart never round
    alike. A bushing small enough for the magnifier is drawn again ``k`` times larger, where a
    step ``k`` times smaller moves a line as far. Every SKU of the line shares its body, so its
    box, its lens and its ``k``. The step is the largest that bound needs at any angle of the
    type's orientation: 0.0079" for a body too large for a lens, at 45 degrees, where the
    turned extent is drawn smallest.
    """
    from synthetic_ecommerce_data.core.drawing import product_look, sheet

    place = 0.1
    x0, y0, x1, y1 = figure(_body_record(ROWS[row_index], length)).figure.bounds()
    steps = []
    for angle in product_look.ORIENTATIONS["any"]:
        a = math.radians(angle)
        scale = sheet.type_scale(product_look.turned(*EXTENT, angle))
        lens = sheet.magnifier((x1 - x0) * scale, (y1 - y0) * scale, angle)
        scale *= max(1.0, lens.k) if lens else 1.0
        steps.append(2 * place / (scale * max(abs(math.cos(a)), abs(math.sin(a)))))
    return max(steps)


def _body_record(row: Mapping[str, Any], length: int) -> dict[str, str]:
    """The drawn values every bushing of a row's line of ``length`` shares, as a record: its
    body, its head and its length, and the row's least bore."""
    record = {
        "Head Type": TYPES[row["type"]][1],
        length_name(row): f'{length / 16:.4f}"',
        "Outside Dia.": f'{_inches(row["od_nominal"]):.4f}"',
        "Size": f'{row["bore_min_in"]:.4f}"',
    }
    if "head_dia" in row:
        record["Head Dia."] = f'{_inches(row["head_dia"]):.4f}"'
        record["Head Height"] = f'{_inches(row["head_thickness"]):.4f}"'
    return record


@functools.cache
def ladder(row_index: int, length: int) -> tuple[tuple[str, float], ...]:
    """The bores a line of row ``row_index`` and length code ``length`` draws its SKUs from:
    every fractional size in the row's range, and each number or letter drill more than
    :func:`bore_step` from every bore kept before it, smallest first. A ``#28`` drill
    (0.1405") and a ``9/64`` one (0.1406") would draw alike, so they are never siblings of a
    line; the fractional sizes, a sixty-fourth apart, hold every breadth-row bore
    (:data:`FEATURED`)."""
    step = bore_step(row_index, length)
    holes = holes_of(ROWS[row_index])
    kept = [hole for hole in holes if hole[0][0].isdigit()]
    for hole in holes:
        if not hole[0][0].isdigit() and all(abs(hole[1] - other[1]) > step for other in kept):
            kept.append(hole)
    return tuple(sorted(kept, key=lambda hole: hole[1]))


def row_of(number: str, size_in: float) -> tuple[dict | None, int]:
    """The row and length code a published ANSI number names; a drill
    bushing's row is the one whose bore range holds ``size_in``."""
    code, body, length = number.rsplit("-", 2)
    for row in ROWS:
        if row["type"] != code or row["body"] != int(body) or int(length) not in row["lengths"]:
            continue
        if is_liner(row) or any(abs(inches - size_in) < 0.0001 for _, inches in holes_of(row)):
            return row, int(length)
    return None, int(length)


#: The bores the breadth row stocked (its ``size_values``), which the
#: default build must still reach (docs/adding-a-type.md).
FEATURED = ("1/8", "3/16", "1/4", "3/8", "1/2")


def _combos() -> tuple[tuple[str, tuple, int], ...]:
    """Every line a brand can offer, as (type, ladder key, length code).

    A drill bushing's ladder key is its row's index; a liner's is ``()``, its
    ladder being every row of its type made in the length. Each type lists its
    rows with a breadth-row bore first, and each row one length before any
    row a second, so a few lines of a type reach many bodies; the types then
    take turns, so every type comes round within five lines."""
    per_type: dict[str, list[tuple[str, tuple, int]]] = {}
    for code in TYPES:
        rows = [i for i, row in enumerate(ROWS) if row["type"] == code]
        if is_liner(ROWS[rows[0]]):
            lengths = sorted({n for i in rows for n in ROWS[i]["lengths"]})
            per_type[code] = [(code, (), n) for n in lengths]
            continue
        rows = [i for i in rows if holes_of(ROWS[i])]
        featured = [i for i in rows if _holds_featured(ROWS[i])]
        ordered = featured + [i for i in rows if i not in featured]
        pairs = [
            (rank, k, i, n)
            for k, i in enumerate(ordered)
            for rank, n in enumerate(_rotated(ROWS[i]["lengths"], k))
        ]
        per_type[code] = [(code, (i,), n) for _, _, i, n in sorted(pairs)]
    out: list[tuple[str, tuple, int]] = []
    for turn in range(max(len(combos) for combos in per_type.values())):
        out += [combos[turn] for combos in per_type.values() if turn < len(combos)]
    return tuple(out)


def _rotated(lengths: list[int], k: int) -> list[int]:
    """A row's lengths from its ``k``-th on, so neighbouring rows start on different lengths."""
    k %= len(lengths)
    return [*lengths[k:], *lengths[:k]]



def _holds_featured(row: Mapping[str, Any]) -> bool:
    return not is_liner(row) and any(drill in FEATURED for drill, _ in holes_of(row))


def _starts(row_index: int, ladder: tuple[tuple[str, float], ...]) -> tuple[int, ...]:
    """The order a ladder's size runs start in: its breadth-row bores first,
    from the first one at or past the row's own place among its type's rows
    that hold one, then the rest. Neighbouring rows start on different
    breadth bores, so a build of a few lines per type reaches all five."""
    featured = [i for i, (drill, _) in enumerate(ladder) if drill in FEATURED]
    if featured:
        code = ROWS[row_index]["type"]
        holders = [
            i for i, row in enumerate(ROWS) if row["type"] == code and _holds_featured(row)
        ]
        first = holders.index(row_index) % len(FEATURED)
        ranks = [FEATURED.index(ladder[i][0]) for i in featured]
        turn = next((k for k, rank in enumerate(ranks) if rank >= first), 0)
        featured = featured[turn:] + featured[:turn]
    return (*featured, *(i for i in range(len(ladder)) if i not in featured))


COMBOS = _combos()


def provenance() -> str:
    return table_provenance(*((name, SOURCE) for name in DIMENSIONS))


def _spec(name: str, scope: str, presence: float = 1.0, kind: str = "keyword") -> AttrSpec:
    return AttrSpec(name=name, scope=scope, presence=presence, kind=kind)


VOCAB = (
    _spec("Type", "line"),
    _spec("Head Type", "line"),
    _spec("Material", "line", 0.85),
    _spec("Length", "line", 0.9, kind="length"),
    _spec("Overall Length", "line", 0.9, kind="length"),
    _spec("Size", "sku", kind="length"),
    _spec("Drill Size", "sku"),
    _spec("Decimal Equivalent", "sku", 0.74, kind="length"),
    _spec("ANSI Number", "sku"),
    _spec("Outside Dia.", "sku", 0.8, kind="length"),
    _spec("Head Dia.", "sku", 0.8, kind="length"),
    _spec("Head Height", "sku", 0.8, kind="length"),
)


def _body_attrs(gen: Any, row: Mapping[str, Any], length: int, style: Any) -> list:
    from synthetic_ecommerce_data.core.model import keyword_attribute

    attrs = [
        keyword_attribute("ANSI Number", ansi_number(row, length)),
        gen._length("Outside Dia.", _inches(row["od_nominal"]), style),
    ]
    if "head_dia" in row:
        attrs += [
            gen._length("Head Dia.", _inches(row["head_dia"]), style),
            gen._length("Head Height", _inches(row["head_thickness"]), style),
        ]
    return attrs


def _make(gen: Any, type_key: str, category: tuple[str, ...]) -> Any:
    # Imported here: generate.py imports the type tables, which discover this module.
    from synthetic_ecommerce_data.core import brands
    from synthetic_ecommerce_data.core.model import Attribute, keyword_attribute
    from synthetic_ecommerce_data.domains.industrial.generate import ChildDraft, LineDraft

    rng = gen.rng
    code, ladder_key, length = COMBOS[gen._rotate(f"combo:{type_key}", len(COMBOS))]
    kind, head = TYPES[code]
    brand = brands.pick_brand(rng, type_key, gen._exhausted)
    style = gen._style("in")
    draft = LineDraft(
        item=ITEM,
        brand=brand,
        series=f"{code}{rng.randint(100, 999)}",
        category=category,
        provenance=provenance(),
    )
    rows = (
        [ROWS[ladder_key[0]]]
        if ladder_key
        else [row for row in ROWS if row["type"] == code and length in row["lengths"]]
    )
    draft.line_attrs = [
        keyword_attribute("Type", kind),
        keyword_attribute("Head Type", head),
        keyword_attribute("Material", "Steel"),
        gen._length(length_name(rows[0]), length / 16, style),
    ]
    draft.descriptors = [("Type", kind), ("Head Type", head)]
    count = gen._variant_count()
    if ladder_key:
        (row,) = rows
        sizes = ladder(ladder_key[0], length)
        count = min(count, len(sizes))
        starts = _starts(ladder_key[0], sizes)
        key = f"sizes:{code}:{row['body']}:{row['bore_min_in']}"
        start = min(starts[gen._rotate(key, len(starts))], len(sizes) - count)
        for drill, inches in sizes[start : start + count]:
            child = ChildDraft(system="in")
            child.primary = gen._length("Size", inches, style)
            child.attrs = [
                child.primary,
                keyword_attribute("Drill Size", drill),
                Attribute("Decimal Equivalent", f"{inches:.4f}", inches),
                *_body_attrs(gen, row, length, style),
            ]
            draft.children.append(child)
        return draft
    count = min(count, len(rows))
    start = gen._rotate(f"bodies:{code}:{length}", len(rows) - count + 1)
    for row in rows[start : start + count]:
        child = ChildDraft(system="in")
        child.primary = gen._length("Size", _inches(row["id_nominal"]), style)
        child.attrs = [child.primary, *_body_attrs(gen, row, length, style)]
        draft.children.append(child)
    return draft


# --- figure -----------------------------------------------------------------------


def _record_inches(record: Mapping[str, str], name: str) -> float | None:
    with contextlib.suppress(KeyError, DimensionParseError):
        return parse_length(record[name]).inches
    return None


def _body_for(bore: float) -> float:
    """A body diameter for a record that publishes only its bore, as the
    table's press-fit bodies run: 0.09" over the bore for the smallest, 30%
    over it for the largest (P-10 is 0.1578" for a 1/16" bore, P-144 2-1/4"
    for 1-49/64")."""
    return bore + max(0.09, 0.3 * bore)


def _head_for(od: float) -> tuple[float, float]:
    """A head for a record that publishes none (an SF bushing's head is on a
    page that was not read): as the H heads run, 3/32" or a tenth over the
    body, and 3/32" to 3/8" thick."""
    return od + max(3 / 32, 0.1 * od), min(max(3 / 32, od / 8), 3 / 8)


def figure(record: dict[str, str]) -> Drawn:
    """The bushing from the side, head up: the body, its bore, and the head
    of a headed type, as wide as its head diameter."""
    od = _record_inches(record, "Outside Dia.")
    bore = _record_inches(record, "Size")
    length = _record_inches(record, "Length") or _record_inches(record, "Overall Length")
    source = "record" if od and bore and length else "partial" if od or bore else "nominal"
    od = od or (_body_for(bore) if bore else 0.75)
    bore = min(bore or 0.5 * od, 0.85 * od)
    length = length or min(1.2 * od, 3.0)
    head = record.get("Head Type") == "Head"
    head_d = _record_inches(record, "Head Dia.")
    head_t = _record_inches(record, "Head Height")
    if head and not (head_d and head_t):
        head_d, head_t = _head_for(od)
    r, half = od / 2, bore / 2
    overall_from_head = record.get("Overall Length") is not None
    body_top = length - head_t if head and overall_from_head else length
    top = body_top + head_t if head else body_top
    fig = Figure(size_in=max(top, head_d or 0.0))
    fig.rect(-r, 0.0, r, body_top)
    if head:
        fig.rect(-head_d / 2, body_top, head_d / 2, top)
    fig.lines([((-half, 0.0), (-half, top)), ((half, 0.0), (half, top))])
    return Drawn(fig, source)


# --- price ------------------------------------------------------------------------

#: What a B94.33 type multiplies the price by. GENERATED, not measured: a
#: renewable bushing, ground to slip and carrying its lock-screw seat, lists
#: at about one and a half times a press-fit one of its bore.
TYPE_FACTORS = {"Press Fit": 1.0, "Liner": 1.2, "Slip-Fixed Renewable": 1.5}

#: GENERATED, NOT MEASURED: the price census has no bushings. The anchor is a
#: standard-tier press-fit bushing of a 1/2" bore at about 12 USD, inside the
#: breadth row's 2-15 USD; the 0.45 log-log slope prices a 1-3/4" bore at
#: about 1.8 times it and a #60 one at about a third.
PRICE = PriceModel(
    12.0,
    0.5,
    0.45,
    0.15,
    0.05,
    measured=False,
    option_attribute="Type",
    option_factors=TYPE_FACTORS,
)


def claims(facts: Mapping[str, str], *, metric: bool, provenance: str, standard: str) -> list[str]:
    """Every row is read from the makers' ASME B94.33 tables."""
    return list(STANDARDS)


SPEC = TypeSpec(
    KEY,
    category=("Tool Holding", "Bushings", "Drill Bushings"),
    standards_family="cutting_tool",
    vocab=VOCAB,
    figure=figure,
    extent=EXTENT,
    make=_make,
    share=0.016,
    price=PRICE,
    claims=claims,
    may_claim=frozenset(STANDARDS),
    key_attributes=("Size",),
    compat=False,
    use_lines=(
        "Guides a drill or reamer through a drill jig to the hole it locates.",
        "Presses into the jig plate, or slips into a liner pressed there.",
    ),
)
