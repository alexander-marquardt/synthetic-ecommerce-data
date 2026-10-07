"""Roller chain connecting links and offset links: a table-driven type (#101,
:mod:`...catalog.tabletype`).

**Source.** The single strand table of the chain size chart the roller chain
type cites (``roller_chain.SOURCE_URL``, retrieved 2026-10-07). It presents
ASME B29.1's standard series; the standard itself was not read. Its single
strand table has fourteen sizes, 25 to 240 and the narrow 41. Ten are stated
here, 25 to 160: the sizes a link is commonly stocked in. The 41 chain is left
out because the roller chain type does not build it, and 180, 200 and 240
because no link listing was seen for them.

* ``Pitch`` and ``Inside Width`` are the chart's pitch and roller width, read
  from ``roller_chain.ANSI`` and not restated, so a link and the chain it
  joins can never disagree. ``ANSI Number`` is the chain number. All three
  carry the name, the machine key and the spelling the roller chain type
  gives them, so one filter finds a chain and its links.
* ``Style`` is ``Single Strand``, as a single strand chain publishes it. The
  chart's multiple strand tables give a link no dimension of its own beyond
  the chain's, and a double strand link is left out.
* The chart's plate height, plate thickness and pin diameter are used to
  scale the drawing (``PLATE``) and are not published: they are that
  distributor's chain's figures, and no second table was read to check them.

**The two links.** A connecting link is a pin link whose cover plate comes
off, so it joins two roller link ends. An offset link has cranked plates,
narrow at one end and wide at the other, so it makes a chain an odd number
of pitches long. Which one a line sells is its ``Item``.

Steel and 18-8 stainless, sold singly and in packs of 2 and 5: a
distributor's offer, not a table.

The price is a declared ladder, not measured (see ``tabletype``): about 2.65
USD for one steel connecting link for 25 chain at the standard brand tier,
rising with the pitch. The ladder has one factor per material, so an offset
link costs what the connecting link of its size does. It costs more in
practice; the mechanism has no place to say so.

The table mechanism builds a size's two lengths in a brand's own spelling.
This module rewrites them as the roller chain type publishes them and adds
the link's kind to each line (:func:`_make`), which is the one thing it does
beyond declaring its table.
"""

from __future__ import annotations

import dataclasses
from collections.abc import Callable, Mapping
from typing import Any

from ...catalog.model import keyword_attribute, length_attribute
from ...catalog.tabletype import TableType, Variant, lengths, spec
from ...catalog.vocab import AttrSpec
from ...dimensions import parse_length
from ...drawing.figures import Drawn
from ...drawing.model import Figure, arc
from . import roller_chain

PITCH = "Pitch"
WIDTH = "Inside Width"
NUMBER = "ANSI Number"
STYLE = "Style"
ITEM = "Item"

CONNECTING = "Roller Chain Connecting Link"
OFFSET = "Roller Chain Offset Link"
KINDS = (CONNECTING, OFFSET)
SINGLE = roller_chain.STRANDS[1]


FIRST, LAST = "25", "160"
_NUMBERS = [row[0] for row in roller_chain.ANSI]
#: The roller chain type's rows for the sizes a link is built in.
SIZES = roller_chain.ANSI[_NUMBERS.index(FIRST) : _NUMBERS.index(LAST) + 1]
#: ``(pitch, width between the roller link plates)`` in inches.
ROWS = tuple((float(pitch), float(width)) for _, pitch, _, width in SIZES)

#: Chain number -> ``(plate height, plate thickness, pin diameter)`` in inches,
#: as the chart prints them. Drawn, never published (see the module docstring).
PLATE = {
    "25": (0.228, 0.029, 0.091),
    "35": (0.356, 0.050, 0.141),
    "40": (0.475, 0.058, 0.156),
    "50": (0.594, 0.079, 0.200),
    "60": (0.712, 0.093, 0.234),
    "80": (0.950, 0.125, 0.312),
    "100": (1.188, 0.157, 0.375),
    "120": (1.425, 0.189, 0.437),
    "140": (1.663, 0.219, 0.500),
    "160": (1.901, 0.255, 0.563),
}
#: The bushing diameters the chart prints for the two rollerless chains,
#: drawn where an offset link's roller would be.
BUSHING = {"25": 0.130, "35": 0.200}

# The chart gives none of the proportions below: they are nominal.
#: The gap between the side view and the view from above, in plate heights.
GAP = 0.3
#: How far a pin stands proud of each plate, in plate thicknesses.
STUB = 1.0
#: Half the length of an offset plate's crank, in pitches.
CRANK = 0.1
#: Chords in a plate's half-round end (see ``roller_chain._ARC``).
_ARC = 6

#: Not ``table_provenance``: that says "read from the ASME B29.1 table", and
#: ASME's text was not read, only a distributor's chart of its dimensions.
PROVENANCE = (
    f"{PITCH} and {WIDTH} are {roller_chain.STANDARD} dimensions as published "
    f"in the size chart at {roller_chain.SOURCE_URL} (retrieved 2026-10-07)"
)


def _index(pitch: float) -> int:
    """The row whose pitch is nearest ``pitch`` (inches)."""
    return min(range(len(ROWS)), key=lambda i: abs(ROWS[i][0] - pitch))


def depth(width: float, thick: float) -> float:
    """A link from above, pin end to pin end: the roller width, the two roller
    link plates and the two pin link plates it spans, and a stub each side."""
    return width + 4 * thick + 2 * STUB * thick


def draw(values: Mapping[str, float], kind: str = CONNECTING) -> Figure:
    """One link from the side, and below it the same link from above.

    From the side both links are a plate one pitch long about two pins; an
    offset link has one pin, and an open bushing at its narrow end. From
    above a connecting link's plates are straight, and an offset link's are
    cranked in about a roller at one end.
    """
    pitch, width = values[PITCH], values[WIDTH]
    row = _index(pitch)
    number, _, roller, _ = SIZES[row]
    # A record whose pitch is no row's keeps the nearest row's proportions.
    scale = pitch / ROWS[row][0]
    height, thick, pin = (scale * value for value in PLATE[number])
    roller_dia = scale * (float(roller) if roller is not None else BUSHING[number])
    radius = height / 2
    fig = Figure(size_in=pitch)
    fig.poly([*arc((0.0, 0.0), radius, 90, 270, _ARC), *arc((pitch, 0.0), radius, -90, 90, _ARC)])
    fig.disc((0.0, 0.0), pin / 2, "hole" if kind == OFFSET else "plain")
    fig.disc((pitch, 0.0), pin / 2, "plain")
    # From above. A plate is an edge view, so it is plain, as the pins are.
    top = radius + GAP * height
    near = top + STUB * thick
    far = top + depth(width, thick) - STUB * thick
    left, right = -radius, pitch + radius
    if kind == OFFSET:
        bend0, bend1 = pitch / 2 - CRANK * pitch, pitch / 2 + CRANK * pitch
        for edge, step in ((near, thick), (far, -thick)):
            # Wide at the pin, and one plate thickness in at the roller.
            fig.poly(
                (
                    (left, edge + step),
                    (bend0, edge + step),
                    (bend1, edge),
                    (right, edge),
                    (right, edge + step),
                    (bend1, edge + step),
                    (bend0, edge + 2 * step),
                    (left, edge + 2 * step),
                ),
                "plain",
            )
        fig.rect(-roller_dia / 2, near + 2 * thick, roller_dia / 2, far - 2 * thick, "plain")
        pins = (pitch,)
    else:
        fig.bars(((left, near, right, near + thick), (left, far - thick, right, far)), "plain")
        pins = (0.0, pitch)
    for x in pins:
        fig.rect(x - pin / 2, top, x + pin / 2, top + depth(width, thick), "plain")
    return fig


TABLE = TableType(
    "roller_chain_links",
    category=("Motion Control & Fluid Power", "Chain & Sprockets", "Roller Chain Links"),
    item=CONNECTING,
    standards_family="motion",
    standard=roller_chain.STANDARD,
    columns=(PITCH, WIDTH),
    rows=ROWS,
    variants=(
        Variant("Steel", "Plain", 1.0),
        Variant("18-8 Stainless Steel", "Plain", 3.0),
    ),
    packs=(1, 2, 5),
    base_price=2.65,
    size_slope=0.67,
    pack_slope=0.9,
    draw=draw,
    # The largest drawn: a 160 link is 3.901 in wide and 5.252 in tall.
    extent=(3.95, 5.3),
    share=0.020,
    default_lines=52,
    default_skus=94,
    series="RL",
    unit="in",
    use_lines=(
        "Fits roller chain of the same ANSI chain number.",
        "A connecting link joins two chain ends; an offset link adds one pitch.",
    ),
)


def _figure(record: dict[str, str]) -> Drawn:
    values, source = lengths(TABLE, record)
    kind = record.get(ITEM, CONNECTING)
    if kind not in KINDS:
        kind, source = CONNECTING, "partial" if source == "record" else source
    return Drawn(draw(values, kind), source)


def _make(base: Callable[..., Any]) -> Callable[..., Any]:
    def make(gen: Any, type_key: str, category: tuple[str, ...]) -> Any:
        draft = base(gen, type_key, category)
        line = {attribute.name: attribute for attribute in draft.line_attrs}
        material, pack = line["Material"].value, line["Package Quantity"].value
        # Rotated within each material and pack, so both links are built in
        # every one of them: one rotation over all lines would keep step with
        # the table's own and pair each link with half the packs.
        kind = KINDS[gen._rotate(f"kind:{type_key}:{material}:{pack}", len(KINDS))]
        draft.item = kind
        draft.line_attrs = [
            keyword_attribute(ITEM, kind) if a.name == ITEM else a for a in draft.line_attrs
        ]
        draft.line_attrs.insert(1, keyword_attribute(STYLE, SINGLE))
        draft.descriptors = [(STYLE, SINGLE), ("Material", material)]
        draft.provenance = PROVENANCE
        for child in draft.children:
            number, pitch, _, width = SIZES[_index(parse_length(child.primary.value).inches)]
            child.primary = dataclasses.replace(
                length_attribute(PITCH, gen._publish(float(pitch), roller_chain.SPELLING)),
                key=roller_chain.PITCH_KEY,
            )
            child.attrs = [
                child.primary,
                keyword_attribute(NUMBER, number),
                length_attribute(WIDTH, gen._publish(float(width), roller_chain.SPELLING)),
            ]
        return draft

    return make


_BASE = spec(TABLE)
(_CHAIN_PITCH,) = (s for s in roller_chain.VOCAB if s.name == PITCH)
SPEC = dataclasses.replace(
    _BASE,
    vocab=(
        # The table declares each column a length, and the catalog's
        # unit-mixing defect rewrites a type's own lengths. The roller chain
        # declares its Pitch a keyword, so its pitches are never rewritten:
        # declared the same way here, a link's pitch reads as its chain's does.
        *(_CHAIN_PITCH if s.name == PITCH else s for s in _BASE.vocab),
        AttrSpec(name=STYLE, scope="line", presence=1.0, kind="keyword"),
        AttrSpec(name=NUMBER, scope="sku", presence=1.0, kind="keyword"),
    ),
    figure=_figure,
    make=_make(_BASE.make),
)
