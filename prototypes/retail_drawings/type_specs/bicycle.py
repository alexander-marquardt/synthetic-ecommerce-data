"""Bicycle (gen#352, gen#685): road, mountain, kids and electric bikes in a Sports & Outdoors group.

The range is built by code from a table of axes (gen#685), not authored row by row: :data:`KINDS`
holds each kind's trims (gears, wheel size, frame material and brake), and :func:`build` crosses
them with the brands and the model year. Every brand sells every trim; for each trim one brand, in
turn, still sells last year's model, so the range carries two model years. That is 7 trims times
3 brands, 21 bikes, and no two of them share brand, kind, gears, wheel and year. The price follows
from the parts (:func:`_price`): the kind sets a base, a carbon frame, disc brakes and more gears
each cost more, the brand costs nothing, and last year's model sells for less.

Each bike is a template (``derivable`` False): the scaled build does not multiply it. An adult bike
is sold by frame size (centimeters); a kids' bike by wheel size (inches), as the toy bikes are
(gen#271). Each bike is four colors times three sizes, twelve SKUs. The wheel size of an adult bike
is a fixed attribute. A balance bike stays in Toys. :mod:`kit_sports` draws them.

Each bike is sold under its brand's series and model number (gen#625, :mod:`bicycle_model_numbers`):
the title reads brand, series, model number, spec, then the bike, "Wrenfield Aero Elite RD28-22-26
28in 22 Speed Carbon Road Bike", and each part is an attribute too. The long title is on purpose:
the short-titled accessories (``bike_saddle``, ``bike_pedals``, ...) outrank it on a plain text
match for ``bicycle`` or ``bike``.
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

import dataclasses

import bicycle_model_numbers as bmn
from breadth_rows import Row
from cycling_helpers import BIKES, _count, _inch
from sports_helpers import (
    _H,
    _L,
    _W,
    BLACK,
    BLUE,
    GREEN,
    ORANGE,
    RED,
    WHITE,
    YELLOW,
    _a,
    _axis,
    _row,
)
from type_registry import Option, TypeSpec


@dataclasses.dataclass(frozen=True)
class Trim:
    """One build of a kind: its gears, wheel size (inches; None for a kids' bike, whose wheel is its
    size axis), frame material and brake."""

    gears: int
    wheel: int | None
    material: str
    brake: str


@dataclasses.dataclass(frozen=True)
class Kind:
    """One kind of bike: what it is called, where it sits, how it is sized and drawn, and its trims.

    ``sizes`` is the size axis and ``steps`` what each size adds to the bike's price; ``base`` is
    the kind's price before its parts; ``blurb`` describes the bike, given its trim.
    """

    name: str
    noun: str
    leaf: str
    style: str
    colors: tuple
    size_key: str
    sizes: tuple[int, ...]
    steps: tuple[float, ...]
    base: float
    blurb: str
    trims: tuple[Trim, ...]


#: The kinds, in :data:`bicycle_model_numbers.KINDS` order.
KINDS: tuple[Kind, ...] = (
    Kind("Road", "Road Bike", "Road Bikes", "road", (RED, BLACK, WHITE, BLUE), "frame_cm", (50, 54, 58), (0, 0, 10), 249.0,
         "A light {material} road bicycle with drop bars, {brake} brakes and {gears} gears for fast rides on tarmac.",
         (Trim(18, 28, "Aluminum", "Rim"), Trim(22, 28, "Carbon", "Disc"))),
    Kind("Mountain", "Hardtail Mountain Bike", "Mountain Bikes", "mountain", (GREEN, ORANGE, BLACK, YELLOW), "frame_cm", (41, 46, 51), (0, 0, 10), 149.0,
         "A hardtail {material} mountain bicycle with front suspension, wide tires, {brake} brakes and {gears} gears for trails and fire roads.",
         (Trim(21, 26, "Aluminum", "Disc"), Trim(24, 29, "Carbon", "Disc"))),
    Kind("Electric", "City Electric Bike", "Electric Bikes", "electric", (BLACK, WHITE, BLUE, GREEN), "frame_cm", (48, 52, 56), (0, 0, 30), 999.0,
         "An {material} electric bicycle with a hub motor, a removable battery on the down tube, {brake} brakes and {gears} gears for the commute.",
         (Trim(7, 28, "Aluminum", "Disc"), Trim(8, 26, "Aluminum", "Disc"))),
    Kind("Kids", "Kids Bike with Stabilizers", "Kids Bikes", "kids", (RED, BLUE, YELLOW, GREEN), "wheel_size_in", (16, 20, 24), (0, 20, 40), 119.0,
         "A {material} kids bicycle with a single gear, a front basket, {brake} brakes and removable stabilizers. In three wheel sizes: 16, 20 and 24 inches.",
         (Trim(1, None, "Steel", "Coaster"),)),
)  # fmt: skip

#: The brands; each sells every trim.
BRANDS = (_W, _H, _L)

#: What a part adds to the kind's base price. The brand adds nothing.
MATERIAL = {"Steel": 0.0, "Aluminum": 100.0, "Carbon": 600.0}
BRAKE = {"Coaster": 0.0, "Rim": 20.0, "Disc": 60.0}
PER_GEAR = 12.0
#: Last year's model sells for this share of this year's.
LAST_YEAR = 0.85


def _price(kind: Kind, trim: Trim, year: int) -> float:
    """The bike's price from its parts, rounded to a whole number ending in 9: 569, 1159.

    Each part step is at least ten even after last year's markdown, so a bike whose parts dominate
    another's still costs more after the rounding.
    """
    raw = kind.base + MATERIAL[trim.material] + BRAKE[trim.brake] + PER_GEAR * (trim.gears - 1)
    if year != bmn.MODEL_YEAR:
        raw *= LAST_YEAR
    return float(round(raw / 10) * 10 - 1)


def _numbered(row: Row, year: int = bmn.MODEL_YEAR) -> Row:
    """The row under its series and model number, read from its own attributes (gen#625)."""
    got = {x[0]: x[2] for x in row.attrs}
    kind, gears = got["bike_type"], int(got["gears"])
    wheel = int(got["wheel_size"]) if "wheel_size" in got else None
    code = bmn.encode(row.brand, kind, wheel, gears, year)
    series = bmn.series_for(row.brand, kind)
    extra = (_a("model_number", "Model number", code), _a("model_year", "Model year", str(year)))
    return dataclasses.replace(
        row, code="BIK" + "".join(ch for ch in code if ch.isalnum()),
        title=f"{row.brand} {series} {code} {bmn.spec(gears, wheel)} {row.title}",
        attrs=(*row.attrs, *extra), product_line=series,
        color_codes=tuple((c[0], code) for c in row.colors),
    )  # fmt: skip


def _bike(kind: Kind, trim: Trim, brand: str, year: int) -> Row:
    """One brand's bike of a trim in a model year, numbered."""
    price = _price(kind, trim, year)
    wheel = () if trim.wheel is None else (_inch("wheel_size", "Wheel size", trim.wheel),)
    attrs = (
        _a("bike_type", "Bike type", kind.name), _a("frame_material", "Frame material", trim.material),
        _count("gears", "Gears", trim.gears), *wheel, _a("brake_type", "Brake type", trim.brake),
    )  # fmt: skip
    blurb = kind.blurb.format(material=trim.material.lower(), brake=trim.brake.lower(), gears=trim.gears)
    sizes = _axis(*((size, price + step) for size, step in zip(kind.sizes, kind.steps, strict=True)))
    row = _row("BIK", f"{trim.material} {kind.noun}", brand, (*BIKES, kind.leaf), "Bicycle", price, "bicycle",
               blurb, kind.colors, attrs, sizes, kind.size_key, (("style", kind.style),))  # fmt: skip
    return _numbered(row, year)


def build() -> tuple[Row, ...]:
    """The bicycle rows: every brand sells every trim of every kind; for the ``i``-th trim, brand
    ``i mod 3`` sells last year's model and the others this year's.

    Raises when two bikes share brand, kind, gears, wheel and year, or a row code.
    """
    trims = [(kind, trim) for kind in KINDS for trim in kind.trims]
    rows = [
        _bike(kind, trim, brand, bmn.MODEL_YEAR - 1 if b == i % len(BRANDS) else bmn.MODEL_YEAR)
        for i, (kind, trim) in enumerate(trims)
        for b, brand in enumerate(BRANDS)
    ]
    axes, codes = set(), set()
    for row in rows:
        got = bmn.decode(row.color_codes[0][1])
        key = (got["brand"], got["kind"], got["gears"], got["wheel"], got["year"])
        if key in axes or row.code in codes:
            raise ValueError(f"bicycle: {row.title} repeats another bike's axes or code")
        axes.add(key)
        codes.add(row.code)
    return tuple(rows)


SPEC = TypeSpec(
    key="bicycle",
    department="Sports & Outdoors",
    product_type="Bicycle",
    options=(Option("frame_cm", "frame_size", "Frame size", "CMT"),),
    rows=build(),
)
