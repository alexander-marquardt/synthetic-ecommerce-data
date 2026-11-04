"""Hex bit sockets, deepened from a breadth row into a modelled type (#836, slice 1).

A hex bit socket is a square-drive socket with a hex key bit pressed into it:
it drives a hex socket screw from a ratchet, as a hex key does by hand.

**Sizes.** The bit's size is its width across flats, a hex key size: the inch
sizes are read from the standards library's ``asme_b18_3_hex_key_in`` series
and the metric ones from ``iso_2936_hex_key_mm`` (``library.pick`` refuses a
size the series lacks). Each drive carries the run of sizes a distributor
stocks on it, in :data:`LADDERS`: the small keys on 1/4 in drive, the middle on
3/8 in and the large on 1/2 in, overlapping as the drives do. The ladders are
the conventional ones, not a table: ASME B107.110, the hand socket standard
the issue names, sets performance and proof torque, and its tables were not
read (the standard is sold, and no public copy was found), so no line claims
it and no record publishes a length the standard would give (overall length,
bit length). The drive is published as a word (``1/4 in``), not a length,
because a metric socket keeps an inch square drive.

**Lines.** A line is one brand's sockets on one drive, in one unit system, as
a hand socket with a hex or a ball end, or an impact socket (hex end only:
a ball end does not take impact). A hand socket is chrome vanadium steel,
chrome plated; an impact socket is alloy (chrome molybdenum) steel with a
black oxide finish. The combinations are rotated, not drawn, so every drive,
system and kind is built.

**Price.** The census has no hex bit sockets: the type prices as the hex key
does (``price.BORROWS``), by the same key size. That price is generated, not
measured.
"""

from __future__ import annotations

from collections.abc import Mapping
from fractions import Fraction
from typing import Any

from synthetic_ecommerce_data.core import standards_library as library
from synthetic_ecommerce_data.core.dimensions import DimensionParseError, parse_length
from synthetic_ecommerce_data.core.drawing.model import Figure, regular_polygon
from synthetic_ecommerce_data.core.typespec import TypeSpec
from synthetic_ecommerce_data.domains.industrial.drafts import retired
from synthetic_ecommerce_data.domains.industrial.drawing.figures import Drawn
from synthetic_ecommerce_data.domains.industrial.newtypes import MM_PER_INCH, table_provenance
from synthetic_ecommerce_data.domains.industrial.vocab import AttrSpec

KEY = "hex_bit_sockets"
ITEM = "Hex Bit Socket"

B18_3 = "ASME B18.3"
ISO_2936 = "ISO 2936"
INCH_TABLE = library.table("asme_b18_3_hex_key_in")
MM_TABLE = library.table("iso_2936_hex_key_mm")
INCH_KEYS: tuple[str, ...] = tuple(INCH_TABLE.values)
MM_KEYS: tuple[float, ...] = tuple(MM_TABLE.values)

#: Each drive's stocked bit sizes: (drive, inch keys, metric keys in mm).
LADDERS: tuple[tuple[str, tuple[str, ...], tuple[float, ...]], ...] = (
    (
        "1/4 in",
        tuple(INCH_TABLE.pick(["3/32", "7/64", "1/8", "9/64", "5/32", "3/16", "7/32", "1/4"])),
        tuple(MM_TABLE.pick([2.0, 2.5, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0])),
    ),
    (
        "3/8 in",
        tuple(INCH_TABLE.pick(["1/8", "5/32", "3/16", "7/32", "1/4", "5/16", "3/8"])),
        tuple(MM_TABLE.pick([3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 10.0])),
    ),
    (
        "1/2 in",
        tuple(INCH_TABLE.pick(["1/4", "5/16", "3/8", "7/16", "1/2", "9/16", "5/8"])),
        tuple(MM_TABLE.pick([6.0, 7.0, 8.0, 10.0, 12.0, 14.0, 17.0, 19.0])),
    ),
)

#: A line's kind: (Type, Tip Style, Material, Finish).
KINDS = (
    ("Standard", "Hex End", "Chrome Vanadium Steel", "Chrome Plated"),
    ("Standard", "Ball End", "Chrome Vanadium Steel", "Chrome Plated"),
    ("Impact", "Hex End", "Alloy Steel", "Black Oxide"),
)
#: Every line a brand can offer: a drive, a unit system and a kind.
COMBOS = tuple(
    (drive, system, kind) for drive, _, _ in LADDERS for system in ("in", "mm") for kind in KINDS
)


def sizes_in(drive: str, metric: bool) -> tuple[float, ...]:
    """``drive``'s stocked bit sizes in one unit system, in inches."""
    _, inch, mm = next(row for row in LADDERS if row[0] == drive)
    if metric:
        return tuple(size / MM_PER_INCH for size in mm)
    return tuple(float(Fraction(size)) for size in inch)


def provenance(metric: bool) -> str:
    return table_provenance(("Size", ISO_2936 if metric else B18_3))


def _spec(name: str, scope: str, presence: float = 1.0, kind: str = "keyword") -> AttrSpec:
    return AttrSpec(name=name, scope=scope, presence=presence, kind=kind)


VOCAB = (
    _spec("Type", "line"),
    _spec("Tip Style", "line"),
    _spec("Drive Size", "line"),
    _spec("Material", "line", 0.85),
    _spec("Finish", "line", 0.8),
    _spec("Size", "sku", kind="length"),
)


def _make(gen: Any, type_key: str, category: tuple[str, ...]) -> Any:
    # Imported here: generate.py imports the type tables, which discover this module.
    from synthetic_ecommerce_data.core import brands
    from synthetic_ecommerce_data.core.model import keyword_attribute
    from synthetic_ecommerce_data.domains.industrial.generate import ChildDraft, LineDraft

    rng = gen.rng
    drive, system, (kind, tip, material, finish) = COMBOS[
        gen._rotate(f"combo:{type_key}", len(COMBOS))
    ]
    metric = system == "mm"
    brand = brands.pick_brand(rng, type_key, gen._exhausted)
    draft = LineDraft(
        item=ITEM,
        brand=brand,
        series=f"{'IB' if kind == 'Impact' else 'HB'}{rng.randint(100, 999)}",
        category=category,
        provenance=provenance(metric),
    )
    draft.line_attrs = [
        retired(keyword_attribute("Item", ITEM)),  # keeps the stream stable for #497
        keyword_attribute("Type", kind),
        keyword_attribute("Tip Style", tip),
        keyword_attribute("Drive Size", drive),
        keyword_attribute("Material", material),
        keyword_attribute("Finish", finish),
    ]
    draft.descriptors = [("Type", kind), ("Tip Style", tip)]
    pool = list(sizes_in(drive, metric))
    count = min(gen._variant_count(), len(pool))
    style = gen._style(system)
    for size_in in gen._offered_run(f"sizes:{drive}:{system}", pool, count):
        child = ChildDraft(system=system)
        child.primary = gen._length("Size", size_in, style)
        child.attrs = [child.primary]
        draft.children.append(child)
    return draft


#: The drawing's proportions by drive, in inches: the socket body's diameter
#: and length, which no record publishes (a distributor's 1/4, 3/8 and 1/2 in
#: hand sockets measure about these).
BODY = {"1/4 in": (0.50, 1.0), "3/8 in": (0.69, 1.1), "1/2 in": (0.88, 1.5)}
#: The bit's exposed length, in key sizes, above a floor.
BIT_LENGTH = (2.2, 0.35)


def _size(record: Mapping[str, str]) -> float | None:
    try:
        return parse_length(record["Size"]).inches
    except (KeyError, DimensionParseError):
        return None


def figure(record: dict[str, str]) -> Drawn:
    """The socket standing on its bit: the body, the hex bit below it with a
    ball when it has one, and the bit's hex end view beside it."""
    size = _size(record)
    s = size or 0.25
    diameter, body = BODY.get(record.get("Drive Size", ""), BODY["3/8 in"])
    diameter = max(diameter, 1.3 * s)
    bit = max(BIT_LENGTH[0] * s, BIT_LENGTH[1])
    r = diameter / 2
    fig = Figure(size_in=bit + body)
    fig.rect(-s / 2, 0.0, s / 2, bit)
    fig.rect(-r, bit, r, bit + body)
    # The square drive opening, drawn on the body's top face.
    fig.lines([((-r, bit + 0.85 * body), (r, bit + 0.85 * body))])
    if "ball" in str(record.get("Tip Style", "")).lower():
        fig.disc((0.0, 0.0), 0.6 * s)
    fig.poly(regular_polygon((r + 1.2 * s, bit / 2), s / 3**0.5, 6, 30))
    return Drawn(fig, "partial" if size else "nominal")


SPEC = TypeSpec(
    KEY,
    category=("Hand Tools", "Sockets & Ratchets", "Hex Bit Sockets"),
    standards_family="hand_tool",
    vocab=VOCAB,
    figure=figure,
    # Measured at the default and ``--lines 39000`` builds (docs/adding-a-type.md
    # "Figure and extent"): the largest drawn is 2.24 x 3.59 in, a 19 mm ball end
    # on 1/2 in drive with its end view beside it.
    extent=(2.35, 3.7),
    make=_make,
    share=0.0135,
    # The census has no hex bit sockets: the hex key's model, borrowed
    # (``price.BORROWS``) on the same key size, so the price is generated.
    borrows="hex_key",
    claims=None,
    may_claim=frozenset(),
    key_attributes=("Size",),
    compat=False,
    use_lines=(
        "Drives hex socket screws from a ratchet or a torque wrench.",
        "Turns socket head cap screws where a hex key gives too little torque.",
    ),
)
