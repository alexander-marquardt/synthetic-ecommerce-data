"""ER collets, deepened from a breadth row into a modelled type (#831).

An ER collet is the slotted spring collet of the ER system (ISO 15488, DIN
6499 form B): an 8 degree taper that seats in a colletholder and a 30 degree
cone the clamping nut closes, gripping a tool shank over a range one collapse
below its nominal bore.

**Sizes.** Every published size and dimension is a row of the standards
library's ``iso_15488_er_collets`` table, read from REGO-FIX's public ER System
product catalog (the maker of the original ER collet; its tables are headed
DIN 6499-B / ISO 15488, which is sold and was not read): each series' metric
and inch nominal bores with their clamping range (pp. 87-95), each series'
outside diameter D1 and length L (p. 161), and the runout TIR by clamping
diameter (p. 83). A collet's ``Size`` is its nominal bore, its ``Grip Range``
the row's clamping range, and its ``Outside Diameter`` and ``Overall Length``
its series' D1 and L.

**Lines.** A line is one brand's collets of one series, in one unit system
(ER 50 has no inch row), in one accuracy class. ``Standard`` holds the DIN
6499 runout, which loosens from 0.015 to 0.025 mm with the clamping diameter;
``Precision`` holds 0.010 mm and ``Ultra Precision`` 0.005 mm, the catalogue's
ER standard and ER-UP collets. The combinations are rotated, not drawn, so
every series, unit system and class is built. The sealed (ER-DM), tapping
(ER-GB) and microbore (ER-MB) collets are not modelled.

**Material.** The catalogue names none; collets are hardened spring steel
(65Mn or 50CrV4), an alloy steel, published as ``Alloy Steel``.

**Price.** The census has no ER collets: the model below is GENERATED, NOT
MEASURED.
"""

from __future__ import annotations

import contextlib
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
from synthetic_ecommerce_data.domains.industrial.newtypes import MM_PER_INCH, table_provenance
from synthetic_ecommerce_data.domains.industrial.vocab import AttrSpec

KEY = "er_collets"
ITEM = "ER Collet"

TABLE = library.table("iso_15488_er_collets")
#: The standards a line claims, and the label its provenance names the table by.
STANDARDS = ("ISO 15488", "DIN 6499")
SOURCE = " / ".join(STANDARDS)
#: The dimensions every record publishes, each read from the table.
DIMENSIONS = ("Size", "Grip Range", "Outside Diameter", "Overall Length", "Concentricity Tolerance")

#: Each series' outside diameter D1 and length L, in mm.
SERIES: dict[str, tuple[float, float]] = {s: (d1, length) for s, d1, length in TABLE.data["series"]}
#: (series, smallest nominal mm, largest nominal mm, L mm): rows shorter than their series.
SHORT = tuple(tuple(row) for row in TABLE.data["short_collets"]["rows"])
#: (over mm, up to mm, test length mm, DIN 6499 TIR, ER TIR, ER-UP TIR).
RUNOUT = tuple(tuple(row) for row in TABLE.data["runout"])
#: The accuracy classes, and the runout column of :data:`RUNOUT` each holds.
CLASSES = ("Standard", "Precision", "Ultra Precision")
_RUNOUT_COLUMN = {"Standard": 3, "Precision": 4, "Ultra Precision": 5}


def nominal_inches(row: tuple) -> float:
    """A row's nominal bore in inches."""
    _, nominal, system, *_ = row
    return float(Fraction(nominal)) if system == "in" else float(nominal) / MM_PER_INCH


#: Each (series, unit system)'s rows, smallest bore first, in the table's order.
LADDERS: dict[tuple[str, str], tuple[tuple, ...]] = {}
for _row in TABLE.rows:
    LADDERS.setdefault((_row[0], _row[2]), ())
    LADDERS[(_row[0], _row[2])] += (tuple(_row),)
for _rows in LADDERS.values():
    assert list(_rows) == sorted(_rows, key=nominal_inches), _rows[0][:3]


def published_series(series: str) -> str:
    """``ER 32`` as a distributor writes it: ``ER32``."""
    return series.replace(" ", "")


def row_of(published_type: str, metric: bool, size_in: float) -> tuple | None:
    """The table row a record's published Type (its series), unit system and size name."""
    series = next((s for s in SERIES if published_series(s) == published_type), None)
    for row in LADDERS.get((series or "", "mm" if metric else "in"), ()):
        if abs(nominal_inches(row) - size_in) < 0.0006:
            return row
    return None


def din_runout_mm(clamp_mm: float) -> float:
    """The DIN 6499 runout of a collet of ``clamp_mm`` nominal bore: its
    clamping-diameter row's. The table's first row starts over 1 mm; the 1 mm
    collets, the smallest it lists, take that row."""
    return next(row[3] for row in RUNOUT if clamp_mm <= row[1])


def runout_mm(row: tuple, accuracy: str) -> float:
    if accuracy == "Standard":
        return din_runout_mm(row[3])
    return RUNOUT[0][_RUNOUT_COLUMN[accuracy]]


def length_mm(row: tuple) -> float:
    """A row's collet length L: its series', or a shorter collet's."""
    series = row[0]
    for short_series, low, high, length in SHORT:
        if series == short_series and row[2] == "mm" and low <= row[3] <= high:
            return length
    return SERIES[series][1]


def _trim(value: float) -> str:
    return f"{value:.4f}".rstrip("0").rstrip(".")


def published(row: tuple, accuracy: str) -> dict[str, str]:
    """The values a row publishes besides its size and the line's dimensions
    the generator formats: the clamping range and the runout."""
    _, _, system, max_mm, min_mm, max_in, min_in = row
    tir = runout_mm(row, accuracy)
    if system == "mm":
        return {
            "Grip Range": f"{_trim(min_mm)}-{_trim(max_mm)}mm",
            "Concentricity Tolerance": f"{_trim(tir)}mm",
        }
    return {
        "Grip Range": f'{_trim(min_in)}-{_trim(max_in)}"',
        "Concentricity Tolerance": f'{_trim(tir / MM_PER_INCH)}"',
    }


#: Every line a brand can offer: a (series, unit system) ladder and a class.
#: Ordered so every ladder comes round within 15 lines and every class within
#: 3, and all 45 pairs within 45.
_PAIRS = tuple(LADDERS)
COMBOS = tuple(
    (_PAIRS[k % len(_PAIRS)], CLASSES[(k + k // len(_PAIRS)) % len(CLASSES)])
    for k in range(len(_PAIRS) * len(CLASSES))
)

#: The inch bores the breadth row stocked (its ``size_values``), which the
#: default build must still reach (docs/adding-a-type.md).
FEATURED = ("1/8", "3/16", "1/4", "3/8", "1/2")


def _starts(series: str, system: str) -> tuple[int, ...]:
    """The order a ladder's size runs start in: its featured bores first, from
    the first one at or past the ladder's own place among the inch ladders,
    then the rest. The first lines of the seven inch ladders start on
    different featured bores, so a build of a few lines per ladder reaches
    all five."""
    ladder = LADDERS[(series, system)]
    featured = [i for i, row in enumerate(ladder) if row[1] in FEATURED]
    if featured:
        inch = [pair for pair in _PAIRS if pair[1] == "in"]
        first = inch.index((series, system)) % len(FEATURED)
        ranks = [FEATURED.index(ladder[i][1]) for i in featured]
        turn = next((k for k, rank in enumerate(ranks) if rank >= first), 0)
        featured = featured[turn:] + featured[:turn]
    return (*featured, *(i for i in range(len(ladder)) if i not in featured))


def provenance() -> str:
    return table_provenance(*((name, SOURCE) for name in DIMENSIONS))


def _spec(name: str, scope: str, presence: float = 1.0, kind: str = "keyword") -> AttrSpec:
    return AttrSpec(name=name, scope=scope, presence=presence, kind=kind)


VOCAB = (
    _spec("Type", "line"),
    _spec("Class", "line"),
    _spec("Material", "line", 0.85),
    _spec("Outside Diameter", "line", 0.8, kind="length"),
    _spec("Overall Length", "sku", 0.8, kind="length"),
    _spec("Size", "sku", kind="length"),
    _spec("Grip Range", "sku", 0.9),
    _spec("Concentricity Tolerance", "sku", 0.85, kind="length"),
)


def _make(gen: Any, type_key: str, category: tuple[str, ...]) -> Any:
    # Imported here: generate.py imports the type tables, which discover this module.
    from synthetic_ecommerce_data.core import brands
    from synthetic_ecommerce_data.core.model import keyword_attribute, length_attribute
    from synthetic_ecommerce_data.domains.industrial.generate import ChildDraft, LineDraft

    rng = gen.rng
    (series, system), accuracy = COMBOS[gen._rotate(f"combo:{type_key}", len(COMBOS))]
    brand = brands.pick_brand(rng, type_key, gen._exhausted)
    d1_mm, _ = SERIES[series]
    style = gen._style(system)
    draft = LineDraft(
        item=ITEM,
        brand=brand,
        series=f"{'UP' if accuracy == 'Ultra Precision' else 'EC'}{rng.randint(100, 999)}",
        category=category,
        provenance=provenance(),
    )
    draft.line_attrs = [
        keyword_attribute("Type", published_series(series)),
        keyword_attribute("Class", accuracy),
        keyword_attribute("Material", "Alloy Steel"),
        gen._length("Outside Diameter", d1_mm / MM_PER_INCH, style),
    ]
    draft.descriptors = [("Type", published_series(series)), ("Class", accuracy)]
    ladder = list(LADDERS[(series, system)])
    count = min(gen._variant_count(), len(ladder))
    starts = _starts(series, system)
    start = min(starts[gen._rotate(f"sizes:{series}:{system}", len(starts))], len(ladder) - count)
    for row in ladder[start : start + count]:
        child = ChildDraft(system=system)
        child.primary = gen._length("Size", nominal_inches(row), style)
        values = published(row, accuracy)
        child.attrs = [
            child.primary,
            keyword_attribute("Grip Range", values["Grip Range"]),
            length_attribute("Concentricity Tolerance", values["Concentricity Tolerance"]),
            gen._length("Overall Length", length_mm(row) / MM_PER_INCH, style),
        ]
        draft.children.append(child)
    return draft


#: The drawing's proportions, which no record publishes: the front (30 degree)
#: cone's length over L and its face diameter over D1, as the catalogue's
#: p. 161 drawing gives them for ER 32 (L1 7.16 of L 40, D3 29.2 of D1 33).
FRONT_CONE = 0.18
FRONT_FACE = 0.885
#: The rear taper's half angle, degrees.
TAPER = 8.0


def _inches(record: Mapping[str, str], name: str) -> float | None:
    with contextlib.suppress(KeyError, DimensionParseError):
        return parse_length(record[name]).inches
    return None


def figure(record: dict[str, str]) -> Drawn:
    """The collet from the side, nose up: the 8 degree taper widening from the
    rear to D1, the 30 degree cone closing to the nose face, and the bore."""
    d1 = _inches(record, "Outside Diameter")
    length = _inches(record, "Overall Length")
    bore = _inches(record, "Size")
    source = "record" if d1 and length and bore else "partial" if d1 or bore else "nominal"
    if not d1:
        d1 = max(1.3 * bore, 0.4) if bore else 1.3
    length = length or 1.2 * d1
    bore = min(bore or 0.4 * d1, 0.75 * d1)
    r = d1 / 2
    shoulder = length * (1 - FRONT_CONE)
    rear = max(r - shoulder * math.tan(math.radians(TAPER)), 0.55 * bore)
    face = r * FRONT_FACE
    fig = Figure(size_in=length)
    fig.poly(
        [(-rear, 0.0), (rear, 0.0), (r, shoulder), (face, length), (-face, length), (-r, shoulder)]
    )
    half = bore / 2
    fig.lines([((-half, 0.0), (-half, length)), ((half, 0.0), (half, length))])
    # A slot from the nose and one from the rear, as the collet alternates them.
    fig.lines([((0.0, length), (0.0, 0.25 * length)), ((0.6 * r, 0.0), (0.6 * r, 0.7 * length))])
    return Drawn(fig, source)


# --- price ------------------------------------------------------------------------

#: What an accuracy class multiplies the price by. GENERATED, not measured:
#: a maker's ultra precision collet lists at about one and a half to two times
#: its standard one.
CLASS_FACTORS = {"Standard": 1.0, "Precision": 1.4, "Ultra Precision": 2.0}

#: GENERATED, NOT MEASURED: the price census has no ER collets. The anchor is a
#: standard-tier, standard-class 1/2" collet at about 22 USD; the 0.25 log-log
#: slope on the nominal bore prices a 36 mm ER 50 collet at about 2.4 times a
#: 1 mm ER 11 one, the gap of the larger series.
PRICE = PriceModel(
    22.0,
    0.5,
    0.25,
    0.15,
    0.05,
    measured=False,
    option_attribute="Class",
    option_factors=CLASS_FACTORS,
)


def claims(facts: Mapping[str, str], *, metric: bool, provenance: str, standard: str) -> list[str]:
    """Every row is read from the catalogue's DIN 6499-B / ISO 15488 tables."""
    return list(STANDARDS)


SPEC = TypeSpec(
    KEY,
    # The type's derived block is tap_spiral_point's (core/typespec.py).
    part_number_block=1951,
    category=("Tool Holding", "Collets", "ER Collets"),
    standards_family="cutting_tool",
    vocab=VOCAB,
    figure=figure,
    # Measured at the default and ``--lines 39000`` builds (docs/adding-a-type.md
    # "Figure and extent"): the largest drawn is 2.05 x 2.46 in, an ER 50 collet.
    extent=(2.15, 2.6),
    make=_make,
    share=0.015,
    price=PRICE,
    claims=claims,
    may_claim=frozenset(STANDARDS),
    key_attributes=("Size",),
    compat=False,
    use_lines=(
        "Holds a straight-shank tool in an ER colletholder, closed by its clamping nut.",
        "Grips any shank within its clamping range, one collapse below its nominal bore.",
    ),
)
