"""Roller chain sprockets, finished bore, hub on one side (type B): a
table-driven type (#101, :mod:`...catalog.tabletype`).

**Source.** Twenty product pages of a chain distributor, one per row below,
at ``https://usarollerchain.com/products/<chain>bs<teeth>-<bore>-sprocket``
(for instance ``40bs15-34-sprocket``; retrieved 2026-10-07). Each page lists
the sprocket's hub style (B on every one), outside diameter, bore, hub
diameter and length through bore. ``Bore Dia.``, ``Hub Diameter`` and
``Length Through Bore`` are those pages' figures. Each page offers several
finished bores for one sprocket; one is stated per row: 5/8" for a 35 chain,
3/4" for a 40, 1" for a 50 and 1-1/4" for a 60.

**Outside diameter.** Computed, not read: ``P x (0.6 + cot(180 / N))`` for a
pitch ``P`` and ``N`` teeth, the relation usually given for an ASME B29.1
sprocket, whose pitch diameter is ``P / sin(180 / N)``. ASME's text was not
read. The relation is checked against all twenty pages: each prints its
outside diameter to a hundredth of an inch, and every computed value is
within 0.005" of it (40 chain, 12 teeth: 2.166 against 2.170; 50 chain, 15
teeth: 3.315 against 3.320; 60 chain, 24 teeth: 6.147 against 6.150).

**Shared with the roller chain.** ``ANSI Number`` and ``Pitch`` are the
roller chain type's attributes, with its values (``40``) and its spelling
(``1/2"``), and ``Pitch`` carries its machine key, so one filter value finds
a chain and the sprockets it runs on. The pitch of each chain number is read
from that type's table, not restated.

Steel with a black oxide finish, as the pages describe them, sold singly.
Left out: plain (stock) bore and type A plate sprockets, split taper
sprockets and their bushings, idler sprockets, stainless and plastic
sprockets, the other finished bores of each sprocket, the 80 chain and
larger, and the keyway size, which the 35 chain's pages do not print.

The price is a declared ladder, not measured (see ``tabletype``): about
26 USD for the 35 chain's 12 tooth sprocket at the standard brand tier,
rising with the outside diameter.

The table mechanism builds the length columns. The chain number and the
tooth count are not lengths, so :func:`_make` adds them to each SKU it
drafts, which is the one thing this module does beyond declaring its table.
"""

from __future__ import annotations

import dataclasses
import math
from collections.abc import Callable, Mapping
from fractions import Fraction
from typing import Any

from synthetic_ecommerce_data.core.drawing.model import Figure, arc
from synthetic_ecommerce_data.core.model import keyword_attribute
from synthetic_ecommerce_data.domains.industrial.product_types.motion.roller_chain import (
    ANSI,
    PITCH_KEY,
    STANDARD,
)
from synthetic_ecommerce_data.domains.industrial.tabletype import TableType, Variant, spec
from synthetic_ecommerce_data.domains.industrial.vocab import AttrSpec

SOURCE_URL = "https://usarollerchain.com/products/40bs15-34-sprocket"

SIZE = "Outside Dia."
PITCH = "Pitch"
BORE = "Bore Dia."
HUB = "Hub Diameter"
THROUGH = "Length Through Bore"
NUMBER = "ANSI Number"
TEETH = "Number of Teeth"

#: ``(chain number, teeth, bore, hub diameter, length through bore)``, inches,
#: as the pages print them.
SPROCKETS: tuple[tuple[str, int, Fraction, Fraction, Fraction], ...] = (
    ("35", 12, Fraction(5, 8), Fraction(39, 32), Fraction(3, 4)),
    ("35", 15, Fraction(5, 8), Fraction(43, 32), Fraction(3, 4)),
    ("35", 18, Fraction(5, 8), Fraction(55, 32), Fraction(3, 4)),
    ("35", 20, Fraction(5, 8), Fraction(31, 16), Fraction(3, 4)),
    ("35", 24, Fraction(5, 8), Fraction(2), Fraction(7, 8)),
    ("40", 12, Fraction(3, 4), Fraction(25, 16), Fraction(7, 8)),
    ("40", 15, Fraction(3, 4), Fraction(29, 16), Fraction(7, 8)),
    ("40", 18, Fraction(3, 4), Fraction(37, 16), Fraction(1)),
    ("40", 20, Fraction(3, 4), Fraction(21, 8), Fraction(1)),
    ("40", 24, Fraction(3, 4), Fraction(13, 4), Fraction(1)),
    ("50", 12, Fraction(1), Fraction(127, 64), Fraction(1)),
    ("50", 15, Fraction(1), Fraction(19, 8), Fraction(1)),
    ("50", 18, Fraction(1), Fraction(23, 8), Fraction(1)),
    ("50", 20, Fraction(1), Fraction(3), Fraction(1)),
    ("50", 24, Fraction(1), Fraction(3), Fraction(5, 4)),
    ("60", 12, Fraction(5, 4), Fraction(19, 8), Fraction(5, 4)),
    ("60", 15, Fraction(5, 4), Fraction(23, 8), Fraction(5, 4)),
    ("60", 18, Fraction(5, 4), Fraction(7, 2), Fraction(5, 4)),
    ("60", 20, Fraction(5, 4), Fraction(31, 8), Fraction(5, 4)),
    ("60", 24, Fraction(5, 4), Fraction(4), Fraction(5, 4)),
)
#: The pitch of each chain number, from the roller chain's table.
PITCH_OF = {number: pitch for number, pitch, _, _ in ANSI}

#: Proportions the drawing uses for what no column gives. The roller a tooth
#: gap seats, as a share of the pitch (5/8 for a 40 chain and larger); the
#: keyway's width as a share of the bore, and its depth as a share of that
#: width (the pages that print a keyway give 3/16" x 3/32" in a 3/4" bore and
#: 1/4" x 1/8" in a 1" bore).
ROLLER = 0.6
KEYWAY = 0.25
KEYWAY_DEPTH = 0.5
#: Where a tooth's outline turns, as shares of the angle one tooth takes: the
#: gap's floor ends, the flank crosses the pitch circle, the tip begins.
FLOOR, FLANK, TIP = 0.16, 0.27, 0.39


def outside_diameter(pitch: float, teeth: int) -> float:
    """See the module docstring. To a thousandth of an inch."""
    return round(pitch * (0.6 + 1 / math.tan(math.pi / teeth)), 3)


def teeth_of(outside: float, pitch: float) -> int:
    """The tooth count an outside diameter and a pitch state:
    :func:`outside_diameter` read the other way."""
    return max(6, round(math.pi / math.atan(pitch / max(outside - 0.6 * pitch, pitch))))


def _row(number: str, teeth: int, *rest: Fraction) -> tuple[float, ...]:
    pitch = float(PITCH_OF[number])
    return (outside_diameter(pitch, teeth), pitch, *(float(value) for value in rest))


#: ``(outside diameter, pitch, bore, hub diameter, length through bore)``,
#: inches, smallest first. No two sprockets share an outside diameter.
ROWS = tuple(sorted(_row(*sprocket) for sprocket in SPROCKETS))
#: The chain number and tooth count of each row, by its outside diameter.
IDENTITY = {_row(*sprocket)[0]: sprocket[:2] for sprocket in SPROCKETS}


def draw(values: Mapping[str, float]) -> Figure:
    """The sprocket face on: its teeth, as many as the outside diameter and
    the pitch state, the hub, and the bore with its keyway."""
    outside, pitch = values[SIZE], values[PITCH]
    teeth = teeth_of(outside, pitch)
    pitch_radius = pitch / math.sin(math.pi / teeth) / 2
    root = pitch_radius - ROLLER * pitch / 2
    step = 360.0 / teeth

    def at(radius: float, turns: float) -> tuple[float, float]:
        angle = math.radians(90.0 + turns * step)
        return (radius * math.cos(angle), radius * math.sin(angle))

    fig = Figure(size_in=outside)
    # One tooth gap sits at the top, so a tooth count shows at a glance.
    profile = (
        (root, -FLOOR), (root, FLOOR), (pitch_radius, FLANK),
        (outside / 2, TIP), (outside / 2, 1 - TIP), (pitch_radius, 1 - FLANK),
    )  # fmt: skip
    fig.poly([at(radius, k + share) for k in range(teeth) for radius, share in profile])
    # A record whose hub is wider than its teeth keeps the teeth.
    hub = min(values[HUB] / 2, root)
    fig.poly(arc((0.0, 0.0), hub, 0.0, 360.0, 48), "plain")
    bore = min(values[BORE] / 2, 0.8 * hub)
    half = KEYWAY * bore
    top = math.sqrt(bore * bore - half * half) + 2 * half * KEYWAY_DEPTH
    open_at = math.degrees(math.asin(half / bore))
    fig.poly(
        [*arc((0.0, 0.0), bore, 90.0 + open_at, 450.0 - open_at, 32), (half, top), (-half, top)],
        "hole",
    )
    return fig


TABLE = TableType(
    "roller_chain_sprockets",
    category=("Motion Control & Fluid Power", "Chain & Sprockets", "Roller Chain Sprockets"),
    item="Roller Chain Sprocket",
    standards_family="motion",
    standard=STANDARD,
    columns=(SIZE, PITCH, BORE, HUB, THROUGH),
    rows=ROWS,
    variants=(Variant("Steel", "Black Oxide", 1.0),),
    # Sold singly.
    packs=(1,),
    base_price=26.00,
    size_slope=1.55,
    pack_slope=0.8,
    draw=draw,
    extent=(6.25, 6.25),
    share=0.026,
    series="SP",
    compat=False,
    unit="in",
    use_lines=(
        "Drives or is driven by ANSI roller chain of the same chain number.",
        "Finished bore with a keyway and set screws: fits the shaft as supplied.",
    ),
)

#: Not ``table_provenance``: that says "read from the ASME B29.1 table", and
#: ASME's text was not read.
PROVENANCE = (
    f"{SIZE} computed from {PITCH} and {TEETH} by the {STANDARD} sprocket relation; "
    f"{PITCH} is the {STANDARD} dimension of the chain number; "
    f"{BORE} and {HUB} and {THROUGH} as published on a distributor's product pages, "
    f"for instance {SOURCE_URL} (retrieved 2026-10-07)"
)


def _make(base: Callable[..., Any]) -> Callable[..., Any]:
    def make(gen: Any, type_key: str, category: tuple[str, ...]) -> Any:
        draft = base(gen, type_key, category)
        draft.provenance = PROVENANCE
        for child in draft.children:
            outside = min(IDENTITY, key=lambda size: abs(size - child.primary.value_num))
            number, teeth = IDENTITY[outside]
            child.attrs = [
                dataclasses.replace(a, key=PITCH_KEY) if a.name == PITCH else a
                for a in child.attrs
            ]
            child.primary = child.attrs[0]
            # A brand whose titles name a second dimension names the pitch.
            child.secondary = {"other_length": child.attrs[1]}
            child.attrs.append(keyword_attribute(NUMBER, number))
            child.attrs.append(keyword_attribute(TEETH, str(teeth)))
        return draft

    return make


_BASE = spec(TABLE)
SPEC = dataclasses.replace(
    _BASE,
    vocab=(
        *_BASE.vocab,
        AttrSpec(name=NUMBER, scope="sku", presence=1.0, kind="keyword"),
        AttrSpec(name=TEETH, scope="sku", presence=1.0, kind="keyword"),
    ),
    make=_make(_BASE.make),
)
