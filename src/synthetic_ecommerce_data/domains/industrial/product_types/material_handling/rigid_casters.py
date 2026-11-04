"""Rigid plate casters: deepened from a breadth row into a modelled type (#835).

The breadth row offered five wheel sizes, two materials and three loads on
two SKUs. No dimensional standard covers a caster: ANSI/ICWM writes a
caster's performance tests, not its sizes. So the spec space is a maker's
stock catalogue, the way a distributor stocks one. Every row below was read
from one public catalogue: the Durable Superior Casters "Industrial, Food
Service, Institutional" catalogue 2017-2018, as Caster Depot republishes it
(https://www.casterdepot.com/media/pdf/2016-durable-catalog_cd.pdf), read on
2026-11-04. Each rigid plate series is one :class:`Series`:

* the 11/12 General Duty series (printed page 21): 2" and 2-1/2" wheels;
* the 13/14 Light-Medium Duty plate series (pages 25 to 27): 3" to 5"
  wheels, 1-1/4" tread;
* the 43/44 Medium Heavy Duty series (pages 70 to 73): 4" to 8" wheels on a
  2" tread, and 6" to 10" wheels on a 2-1/2" tread.

The catalogue's tables give each wheel its tread width and the caster's
overall height (one per wheel diameter in a series). Each table row gives a
wheel type its load capacity per caster and the bearings it is offered with.
A line is one wheel material and one bearing in one series. Its SKUs are the
wheel diameters the table offers that pair on, so a line never offers a
wheel the maker does not.

**Names.** ``Wheel Dia.`` is the census's own key for this type
(``P2_price_census.json``, ``breadth_categories.rigid_casters``,
``key_dimension_attribute``). ``Tread Width`` and ``Bearing Type`` are the
catalogue's column headings, and ``Wheel Material`` is the catalogue's
"Wheel Type" column, named for what it holds. ``Overall Height`` and
``Load Capacity`` are census names. A load is published in lbf, as every load
in the catalog is. The census has no caster attribute names, so
``names.NAME_EXCEPTIONS`` and ``names.TYPE_SPECIFIC`` cite this catalogue for
the four it lacks.

**Values.** A wheel type is published under a generic name. The catalogue's
"Mold-On Rubber" is a "vulcanized rubber tread on cast iron core" (page 133),
so it is published as Rubber on Cast Iron. Its "Polyon" is a "polyurethane
tread chemically bonded to cast iron core" (page 143), so it is published as
Polyurethane on Cast Iron. The trademarked wheels (Poly-Pro, MaxRok and the
rest) are not built. The bearing names are the tables' own: Plain Bore (the
legend's name for the tables' "Plain"), Sleeve, Ball, Precision Ball (the
tables' "Precision") and Roller. A 43/44 wheel is built with the two bearings
the table offers it with: code 04 (roller) and code 60 (precision ball).

**Not built.** Stem mounts: the rigid charts read here are plate charts.
Swivel casters and brakes are other types. The plate's own size and bolt
pattern are not published: the census has no name for either.

**Brands.** The type keeps the ``hand_tool`` pool its breadth row had (#835).
The five pools are fixed (``core.brands.FAMILIES``) and none is for material
handling. The ``motion`` pool's product word "Replacement" would claim a fit
that no field backs.
"""

from __future__ import annotations

import contextlib
from collections.abc import Mapping
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from synthetic_ecommerce_data.core.dimensions import DimensionParseError, parse_length
from synthetic_ecommerce_data.core.drawing.model import Figure
from synthetic_ecommerce_data.core.model import (
    keyword_attribute,
    length_attribute,
    numeric_attribute,
)
from synthetic_ecommerce_data.core.price import PriceModel
from synthetic_ecommerce_data.core.typespec import TypeSpec
from synthetic_ecommerce_data.domains.industrial.drawing.figures import Drawn
from synthetic_ecommerce_data.domains.industrial.newtypes import (
    NO_STANDARD,
    _weighted,
    _window,
    feed_style,
    table_provenance,
)
from synthetic_ecommerce_data.domains.industrial.vocab import AttrSpec

if TYPE_CHECKING:
    from synthetic_ecommerce_data.domains.industrial.generate import LineDraft

ITEM = "Rigid Caster"

SIZE = "Wheel Dia."
TREAD = "Tread Width"
HEIGHT = "Overall Height"
LOAD = "Load Capacity"
MATERIAL = "Wheel Material"
BEARING = "Bearing Type"
MOUNTING = "Mounting Style"

#: The chart every published dimension and load is read from, as a record names it.
CHART = "supplier's rigid plate caster chart"
PROVENANCE = (
    table_provenance(*((name, CHART) for name in (SIZE, TREAD, HEIGHT, LOAD))) + "; " + NO_STANDARD
)

RUBBER_IRON = "Rubber on Cast Iron"
URETHANE_IRON = "Polyurethane on Cast Iron"
PLAIN, SLEEVE, BALL, PRECISION, ROLLER = "Plain Bore", "Sleeve", "Ball", "Precision Ball", "Roller"


@dataclass(frozen=True)
class Series:
    """One rigid plate series: each wheel's tread and height, and what each
    (wheel material, bearing) pair is offered at."""

    name: str
    #: Wheel diameter (in) -> (tread width, overall height), both in inches.
    wheels: Mapping[float, tuple[float, float]]
    #: (wheel material, bearing) -> {wheel diameter: load capacity in lb}.
    offers: Mapping[tuple[str, str], Mapping[float, int]]


def _loads(diameters: tuple[float, ...], loads: tuple[int, ...]) -> dict[float, int]:
    return dict(zip(diameters, loads, strict=True))


#: 11/12 General Duty, page 21: every wheel read here has a plain bore.
_GENERAL = Series(
    "general",
    {2.0: (15 / 16, 2 + 7 / 16), 2.5: (1 + 1 / 16, 3.25)},
    {
        ("Hard Rubber", PLAIN): {2.0: 100, 2.5: 175},
        ("Polyolefin", PLAIN): {2.0: 100, 2.5: 125},
        ("Semi-Steel", PLAIN): {2.0: 150, 2.5: 200},
    },
)

#: 13/14 Light-Medium Duty plate series, pages 25 to 27: a 1-1/4" tread.
_LM = (3.0, 3.5, 4.0, 5.0)
_LIGHT_MEDIUM = Series(
    "light-medium",
    {3.0: (1.25, 4.125), 3.5: (1.25, 4.625), 4.0: (1.25, 5 + 3 / 16), 5.0: (1.25, 6.125)},
    {
        ("Hard Rubber", PLAIN): _loads(_LM, (300, 300, 350, 350)),
        ("Hard Rubber", BALL): {3.0: 300, 4.0: 350},
        ("Polyolefin", PLAIN): {3.0: 250, 3.5: 300, 4.0: 350},
        ("Polyolefin", SLEEVE): _loads(_LM, (300, 300, 350, 350)),
        ("Polyolefin", BALL): {3.0: 300, 4.0: 350},
        ("Nylon", SLEEVE): {3.0: 300, 4.0: 350},
        ("Nylon", PRECISION): {3.0: 300, 4.0: 350, 5.0: 350},
        ("Semi-Steel", PLAIN): _loads(_LM, (350, 350, 300, 350)),
        ("Semi-Steel", SLEEVE): {3.0: 350, 4.0: 300},
    },
)

#: 43/44 Medium Heavy Duty, 2" tread, pages 70 to 73. The 8" wheel is the
#: table's standard 10-1/8" height (diameter code 80).
_MH = (4.0, 5.0, 6.0, 8.0)
_RUBBER_IRON = _loads(_MH, (400, 400, 550, 600))
_POLYOLEFIN = {4.0: 500, 6.0: 700, 8.0: 900}
_NYLON = _loads(_MH, (800, 900, 1000, 1100))
_PHENOLIC = _loads(_MH, (800, 1000, 1200, 1400))
_URETHANE_IRON = _loads(_MH, (800, 1100, 1200, 1400))
_MEDIUM_HEAVY = Series(
    "medium-heavy",
    {4.0: (2.0, 5.625), 5.0: (2.0, 6.5), 6.0: (2.0, 7.5), 8.0: (2.0, 10.125)},
    {
        (RUBBER_IRON, ROLLER): _RUBBER_IRON,
        (RUBBER_IRON, PRECISION): _RUBBER_IRON,
        ("Polyolefin", ROLLER): _POLYOLEFIN,
        ("Polyolefin", PRECISION): _POLYOLEFIN,
        ("Nylon", ROLLER): _NYLON,
        ("Nylon", PRECISION): _NYLON,
        ("Phenolic", ROLLER): _PHENOLIC,
        ("Phenolic", PRECISION): _PHENOLIC,
        (URETHANE_IRON, ROLLER): _URETHANE_IRON,
        (URETHANE_IRON, PRECISION): _URETHANE_IRON,
        ("Semi-Steel", ROLLER): _loads(_MH, (700, 1000, 1200, 1400)),
        ("Ductile Steel", ROLLER): _loads(_MH, (1500, 1500, 1500, 1500)),
        ("Forged Steel", ROLLER): {5.0: 1500, 6.0: 1500, 8.0: 1500},
    },
)

#: 43/44 Medium Heavy Duty, 2-1/2" tread, page 73: a roller bearing only (code 06).
_HD = (6.0, 8.0, 10.0)
_HEAVY = Series(
    "heavy",
    {6.0: (2.5, 7.5), 8.0: (2.5, 10.125), 10.0: (2.5, 11.5)},
    {
        (RUBBER_IRON, ROLLER): _loads(_HD, (700, 800, 1000)),
        ("Phenolic", ROLLER): _loads(_HD, (1400, 1500, 1500)),
        (URETHANE_IRON, ROLLER): _loads(_HD, (1500, 1500, 1500)),
        ("Semi-Steel", ROLLER): _loads(_HD, (1500, 1500, 1500)),
    },
)

#: (series, weight): how often a line is drafted in each, about its share of the offers.
SERIES: tuple[tuple[Series, float], ...] = (
    (_GENERAL, 0.12),
    (_LIGHT_MEDIUM, 0.33),
    (_MEDIUM_HEAVY, 0.43),
    (_HEAVY, 0.12),
)


def chart_rows() -> dict[tuple[float, float, str, str], tuple[float, int]]:
    """(wheel dia., tread, wheel material, bearing) -> (overall height, load):
    every row the charts give, as a record publishes it."""
    rows: dict[tuple[float, float, str, str], tuple[float, int]] = {}
    for series, _ in SERIES:
        for (material, bearing), loads in series.offers.items():
            for dia, load in loads.items():
                tread, height = series.wheels[dia]
                rows[(dia, tread, material, bearing)] = (height, load)
    return rows


VOCAB = (
    AttrSpec(MATERIAL, "line"),
    AttrSpec(BEARING, "line"),
    AttrSpec(MOUNTING, "line"),
    AttrSpec(SIZE, "sku", kind="length"),
    AttrSpec(TREAD, "sku", kind="length"),
    AttrSpec(HEIGHT, "sku", kind="length"),
    AttrSpec(LOAD, "sku", kind="count"),
)


def build(gen: Any, type_key: str, category: tuple[str, ...]) -> LineDraft:
    """One line: a series, one (wheel material, bearing) it offers, a window of its wheels."""
    # Imported here: generate imports the type tables, which discover this module.
    from synthetic_ecommerce_data.core.brands import pick_brand
    from synthetic_ecommerce_data.domains.industrial.generate import BRANDS, ChildDraft, LineDraft

    rng = gen.rng
    brand = pick_brand(rng, type_key, gen._exhausted)
    series = _weighted(rng, SERIES)
    # One rotation over the series' pairs: a small build still visits each
    # wheel material and bearing before it repeats one.
    pairs = list(series.offers)
    material, bearing = pairs[gen._rotate(f"caster:{series.name}:pair", len(pairs))]
    loads = series.offers[(material, bearing)]
    draft = LineDraft(
        item=ITEM,
        brand=brand,
        series=f"RC{rng.randint(100, 999)}",
        category=category,
        provenance=PROVENANCE,
    )
    draft.line_attrs = [
        keyword_attribute(MATERIAL, material),
        keyword_attribute(BEARING, bearing),
        keyword_attribute(MOUNTING, "Top Plate"),
    ]
    draft.descriptors = [(MATERIAL, material)]
    style = feed_style(brand, "in", BRANDS)
    wheels = sorted(loads)
    key = f"caster:{series.name}:{material}:{bearing}"
    for dia in _window(gen, key, wheels, gen._variant_count()):
        tread, height = series.wheels[dia]
        child = ChildDraft(system="in")
        child.primary = length_attribute(SIZE, gen._publish(dia, style))
        child.attrs = [
            child.primary,
            length_attribute(TREAD, gen._publish(tread, style)),
            length_attribute(HEIGHT, gen._publish(height, style)),
            numeric_attribute(LOAD, f"{loads[dia]:,} lbf", float(loads[dia])),
        ]
        draft.children.append(child)
    return draft


# --- the drawing ------------------------------------------------------------------

#: The drawing's extent (docs/adding-a-type.md "Figure and extent"): the largest
#: drawn is 12.40 x 11.50 in at both the default and the ``--lines 39000`` build,
#: the 10" wheel under its plate, plus 0.1" and rounded to 0.05".
EXTENT = (12.5, 11.6)

_NOMINAL_DIA = 4.0
#: A plate's thickness and its overhang past the wheel, as fractions of the wheel.
_PLATE = 0.04
_OVERHANG = 0.12


def _inches(record: Mapping[str, str], name: str) -> float | None:
    with contextlib.suppress(KeyError, DimensionParseError):
        return parse_length(record[name]).inches
    return None


def figure(record: dict[str, str]) -> Drawn:
    """The caster from the side: the top plate, the rigid fork's leg, the wheel
    on its axle, its tread and hub, at the record's wheel and overall height."""
    dia = _inches(record, SIZE)
    height = _inches(record, HEIGHT)
    source = "record" if dia and height and height > dia else "partial" if dia else "nominal"
    dia = dia or _NOMINAL_DIA
    if not height or height <= dia:
        height = dia * 1.3
    r = dia / 2
    plate = dia * _PLATE
    half = r + dia * _OVERHANG
    axle_y = height - r
    fig = Figure(size_in=height)
    # The fork's leg, from under the plate down to the axle boss.
    leg = r * 0.45
    fig.poly(
        [(-half * 0.8, plate), (half * 0.8, plate), (leg, axle_y), (-leg, axle_y)],
        "plain",
    )
    fig.rect(-half, 0.0, half, plate)
    fig.disc((0.0, axle_y), r)
    fig.disc((0.0, axle_y), r * 0.72, "plain")
    fig.disc((0.0, axle_y), r * 0.18)
    fig.disc((0.0, axle_y), r * 0.07, "hole")
    return Drawn(fig, source)


# --- price ------------------------------------------------------------------------

#: The census ending mix of the 157 rigid casters (``breadth_categories.rigid_casters``),
#: restated here as the threaded rod restates its own: the type was a breadth row,
#: so :data:`...core.price.ENDINGS` does not carry it.
ENDINGS = {
    "other .x5": 0.3694,
    "other": 0.3503,
    ".00": 0.1146,
    ".50": 0.1083,
    ".95": 0.0318,
    "other .x9": 0.0191,
    ".98": 0.0064,
}

#: What a wheel material multiplies the price by. GENERATED, not measured: the
#: census keys a caster's price on its wheel only, so these only order the
#: materials as the chart's loads do, a light plastic or rubber wheel cheapest
#: and a cast iron cored or steel wheel dearest.
WHEEL_FACTORS = {
    "Polyolefin": 0.6,
    "Hard Rubber": 0.7,
    "Nylon": 0.9,
    "Semi-Steel": 0.9,
    RUBBER_IRON: 1.3,
    "Phenolic": 1.3,
    URETHANE_IRON: 1.8,
    "Ductile Steel": 1.8,
    "Forged Steel": 2.2,
}

#: Hand-fitted to the census's 157 casters (p10 20.744, p50 76.2, p90 351.85,
#: log-log slope of price on the wheel diameter 1.016); the anchor is a 4"
#: standard-tier caster with a wheel factor of 1.0. Not fitted by
#: ``scripts/fit_price_model.py``: set by ``price_report``, as the threaded rod's is.
PRICE = PriceModel(
    # @fit-begin
    60.0, 4.0, 1.016, 0.8, 0.15,
    # @fit-end
    endings=ENDINGS,
    option_attribute=MATERIAL,
    option_factors=WHEEL_FACTORS,
)  # fmt: skip


def claims(facts: Mapping[str, str], *, metric: bool, provenance: str, standard: str) -> list[str]:
    """No standard is claimed: no dimensional standard covers a caster."""
    return []


SPEC = TypeSpec(
    "rigid_casters",
    category=("Material Handling & Storage", "Casters & Wheels", "Rigid Casters"),
    standards_family="hand_tool",
    vocab=VOCAB,
    figure=figure,
    extent=EXTENT,
    make=build,
    share=0.015,
    price=PRICE,
    claims=claims,
    may_claim=frozenset(),
    key_attributes=(SIZE,),
    compat=False,
    use_lines=(
        "Bolts under a cart, rack or machine base to roll it in a straight line.",
        "Pair with swivel casters at the other end to steer.",
    ),
)
