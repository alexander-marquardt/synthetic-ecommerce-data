"""All-thread rod: deepened from a breadth row into a modelled type (#53).

The breadth row offered seven thread sizes, two materials and two lengths. A
distributor's rod space is wider, and it is the thread that fixes it:

* four series, each a thread table: inch coarse (UNC) and inch fine (UNF) read
  from ASME B1.1, metric coarse and metric fine read from ISO 262. A fine
  metric line draws from ONE pitch ladder, so two pitches of one diameter are
  never siblings of a line (they draw alike at a rod's scale);
* the material and finish a rod is stocked in, with a grade or property class
  for the steels (carbon and alloy), and none for stainless and brass;
* a stocked length, a line attribute: a rod is sold cut to a length, 1 ft to
  6 ft in inch and 500 mm to 2 m in metric.

Thread Size is read from a table, so ``dimension_provenance`` names the thread
table it came from (:attr:`Series.provenance`). A rod's length is a stocked
length, not a table's value, and no dimensional standard is claimed: the line
says no standard fixes it, as the key stock's does.

No pack quantity is published (#14): a line is one rod per SKU.
"""

from __future__ import annotations

import contextlib
import math
from collections.abc import Mapping
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from synthetic_ecommerce_data.core import standards_library as library
from synthetic_ecommerce_data.core.dimensions import (
    DimensionParseError,
    parse_length,
    parse_thread,
)
from synthetic_ecommerce_data.core.drawing.model import Figure
from synthetic_ecommerce_data.core.model import keyword_attribute, length_attribute
from synthetic_ecommerce_data.core.price import PriceModel
from synthetic_ecommerce_data.core.typespec import TypeSpec
from synthetic_ecommerce_data.domains.industrial.drafts import retired
from synthetic_ecommerce_data.domains.industrial.drawing import primitives as P  # noqa: N812
from synthetic_ecommerce_data.domains.industrial.drawing.figures import Drawn
from synthetic_ecommerce_data.domains.industrial.newtypes import (
    MM_PER_INCH,
    NO_STANDARD,
    _weighted,
    _window,
    feed_style,
    table_provenance,
)
from synthetic_ecommerce_data.domains.industrial.vocab import AttrSpec

if TYPE_CHECKING:
    from synthetic_ecommerce_data.domains.industrial.generate import LineDraft

#: (Material, Finish, Grade or None): the combinations one series is stocked in.
Combo = tuple[str, str, "str | None"]

ITEM = "All-Thread Rod"

INCH_TABLE = "ASME B1.1"
METRIC_TABLE = "ISO 262"


@dataclass(frozen=True)
class Series:
    """One stocked series: its thread rows, its thread type, its combinations and lengths."""

    name: str
    system: str
    thread_type: str
    #: Ranges of thread designations. A line draws from ONE range, so two fine
    #: pitches of one diameter are never in one line.
    ranges: tuple[tuple[str, ...], ...]
    combos: tuple[Combo, ...]
    #: Stocked lengths, in the series' unit (inches, or millimetres).
    lengths: tuple[float, ...]

    @property
    def provenance(self) -> str:
        """Where the thread came from, and that the length is a stocked one."""
        table = INCH_TABLE if self.system == "in" else METRIC_TABLE
        thread = table_provenance(("Thread Size", table))
        return f"{thread}; Length is a stocked length; {NO_STANDARD}"


# --- the thread tables ----------------------------------------------------------------

_THREADS = library.table("asme_b1_1_unified_threads")
_INCH_SIZES = ["#10", "1/4", "5/16", "3/8", "7/16", "1/2", "9/16", "5/8", "3/4", "7/8", "1"]
_UNC = tuple(f"{row['size']}-{row['unc_tpi']}" for row in _THREADS.select(_INCH_SIZES))
_UNF = tuple(f"{row['size']}-{row['unf_tpi']}" for row in _THREADS.select(_INCH_SIZES))

_ISO = library.table("iso_262_metric_threads")
_METRIC_SIZES = [
    "M3", "M4", "M5", "M6", "M8", "M10", "M12", "M14", "M16", "M18", "M20", "M22", "M24",
    "M27", "M30", "M33", "M36",
]  # fmt: skip
_METRIC_COARSE = tuple(f"{r['size']}x{r['coarse_pitch_mm']:g}" for r in _ISO.select(_METRIC_SIZES))
_FINE_ROWS = [r for r in _ISO.select(_METRIC_SIZES) if r.get("fine_pitches_mm")]
#: Fine ladders: the first fine pitch of each diameter, then the second of the
#: few diameters that have two.
_METRIC_FINE = tuple(
    tuple(
        f"{r['size']}x{r['fine_pitches_mm'][i]:g}"
        for r in _FINE_ROWS
        if i < len(r["fine_pitches_mm"])
    )
    for i in range(2)
)

# --- the combinations a rod is stocked in --------------------------------------------

_STEEL_ZP = ("Steel", "Zinc Plated")
_STEEL_PLAIN = ("Steel", "Plain")
_INCH_COMBOS: tuple[Combo, ...] = (
    (*_STEEL_ZP, "Grade 2"),
    (*_STEEL_PLAIN, "Grade 2"),
    ("Alloy Steel", "Plain", "Grade B7"),
    ("18-8 Stainless Steel", "Plain", None),
    ("316 Stainless Steel", "Plain", None),
    ("Brass", "Plain", None),
)
_METRIC_COMBOS: tuple[Combo, ...] = (
    (*_STEEL_ZP, "Class 4.8"),
    (*_STEEL_PLAIN, "Class 4.8"),
    ("Alloy Steel", "Plain", "Class 8.8"),
    ("18-8 Stainless Steel", "Plain", None),
    ("316 Stainless Steel", "Plain", None),
    ("Brass", "Plain", None),
)
#: Stocked lengths: 1, 2, 3 and 6 ft; 0.5, 1 and 2 m.
_INCH_LENGTHS = (12.0, 24.0, 36.0, 72.0)
_METRIC_LENGTHS = (500.0, 1000.0, 2000.0)

#: (series, weight): how often a line is drafted in each.
SERIES: tuple[tuple[Series, float], ...] = (
    (Series("inch-unc", "in", "UNC", (_UNC,), _INCH_COMBOS, _INCH_LENGTHS), 0.40),
    (Series("inch-unf", "in", "UNF", (_UNF,), _INCH_COMBOS, _INCH_LENGTHS), 0.14),
    (
        Series(
            "metric-coarse",
            "mm",
            "Metric Coarse",
            (_METRIC_COARSE,),
            _METRIC_COMBOS,
            _METRIC_LENGTHS,
        ),
        0.33,
    ),
    (
        Series("metric-fine", "mm", "Metric Fine", _METRIC_FINE, _METRIC_COMBOS, _METRIC_LENGTHS),
        0.13,
    ),
)

VOCAB = (
    AttrSpec("Material", "line"),
    AttrSpec("Finish", "line", 0.9),
    AttrSpec("Grade", "line", 0.9),
    AttrSpec("Thread Type", "line", 0.8),
    AttrSpec("Thread Direction", "line", 0.55),
    AttrSpec("Length", "line", kind="length"),
    AttrSpec("Thread Size", "sku"),
)


def build(gen: Any, type_key: str, category: tuple[str, ...]) -> LineDraft:
    """One line: a series, one stocked combination and length, a window of its threads."""
    # Imported here: generate imports the type tables, which discover this module.
    from synthetic_ecommerce_data.core.brands import pick_brand
    from synthetic_ecommerce_data.domains.industrial.generate import BRANDS, ChildDraft, LineDraft

    rng = gen.rng
    brand = pick_brand(rng, type_key, gen._exhausted)
    series = _weighted(rng, SERIES)
    # One rotation over (combination, length) pairs: a small build still visits
    # every material and every stocked length before it repeats either.
    pair = gen._rotate(f"rod:{series.name}:stock", len(series.combos) * len(series.lengths))
    material, finish, grade = series.combos[pair % len(series.combos)]
    length = series.lengths[(pair // len(series.combos)) % len(series.lengths)]
    draft = LineDraft(
        item=ITEM,
        brand=brand,
        series=f"TR{rng.randint(100, 999)}",
        category=category,
        provenance=series.provenance,
    )
    metric = series.system == "mm"
    style = feed_style(brand, series.system, BRANDS)
    length_attr = length_attribute(
        "Length", gen._publish(length / MM_PER_INCH if metric else length, style)
    )
    draft.line_attrs = [
        retired(keyword_attribute("Item", ITEM)),  # keeps the stream stable
        keyword_attribute("Material", material),
        keyword_attribute("Finish", finish),
        keyword_attribute("Thread Type", series.thread_type),
        keyword_attribute("Thread Direction", "Right Hand"),
        length_attr,
    ]
    if grade is not None:
        draft.line_attrs.append(keyword_attribute("Grade", grade))
    draft.descriptors = [("Material", material), ("Length", length_attr.value)]
    which = gen._rotate(f"rod:{series.name}:range", len(series.ranges))
    rows = list(series.ranges[which])
    for thread in _window(gen, f"rod:{series.name}:{which}", rows, gen._variant_count()):
        child = ChildDraft(system=series.system)
        child.primary = keyword_attribute("Thread Size", thread)
        child.attrs = [child.primary]
        draft.children.append(child)
    return draft


# --- the drawing ------------------------------------------------------------------

#: A rod is drawn compressed, with a break, into KNEE + TAIL inches at most: a
#: 72" rod at scale would leave its thread a smear. The tail grows slowly enough
#: (SCALE inches) that a 72" rod still draws longer than a 12" one.
KNEE = 3.0
TAIL = 0.6
SCALE = 24.0
#: The most crests drawn along a rod.
MAX_CRESTS = 60
#: The drawing's extent, measured at the default and ``--lines 39000`` builds
#: (docs/adding-a-type.md "Figure and extent"): the largest drawn is 1.63 x
#: 3.574 in at both, an M36 rod's break marks across and a 72" rod compressed
#: down the page.
EXTENT = (1.75, 3.7)

_NOMINAL_THREAD = "1/4-20"
_NOMINAL_LENGTH_IN = 12.0


def figure(record: dict[str, str]) -> Drawn:
    """The rod seen from the side, threaded end to end and broken to fit."""
    thread = None
    with contextlib.suppress(KeyError, DimensionParseError):
        thread = parse_thread(record["Thread Size"])
    length = None
    with contextlib.suppress(KeyError, DimensionParseError):
        length = parse_length(record["Length"]).inches
    if thread is None:
        thread = parse_thread(_NOMINAL_THREAD)
    full = length or _NOMINAL_LENGTH_IN
    drawn = full if full <= KNEE else KNEE + TAIL * (1 - math.exp(-(full - KNEE) / SCALE))
    r = thread.major.inches / 2
    c = min(thread.pitch_in, r / 2)
    fig = Figure(size_in=max(drawn, 4 * r))
    fig.poly(
        [
            (-r + c, 0.0),
            (r - c, 0.0),
            (r, c),
            (r, drawn - c),
            (r - c, drawn),
            (-r + c, drawn),
            (-r, drawn - c),
            (-r, c),
        ],
        "part",
    )
    crests = P.thread_crests(r, c, drawn - c, max(thread.pitch_in, drawn / MAX_CRESTS))
    fig.lines(crests)
    if full > KNEE:
        cut = drawn * 0.45
        amplitude = min(0.04, r * 0.2)
        P.break_mark(fig, r, cut, amplitude)
        P.break_mark(fig, r, cut + 0.1, amplitude)
    source = "record" if length and "Thread Size" in record else "nominal"
    return Drawn(fig, source)


# --- price ------------------------------------------------------------------------

#: The census ending mix of the 248 threaded rods (``breadth_categories.threaded_rod``),
#: restated here as the roller chain restates its own: the type was a breadth
#: row, so :data:`...core.price.ENDINGS` does not carry it.
ENDINGS = {
    "other": 0.5202,
    "other .x5": 0.3105,
    ".00": 0.0565,
    ".50": 0.0444,
    "other .x9": 0.0282,
    ".95": 0.0242,
    ".97": 0.0081,
    ".98": 0.0081,
}

#: Hand-fitted to the census's 248 rods (p50 33.52, p10 6.511, p90 140.855,
#: log-log slope of price on the major diameter 0.583); the anchor is a 1/2"
#: standard-tier steel rod at 36". A rod sells by the foot, so the price
#: scales with the published length (the pack slope). A fitted type would use
#: ``scripts/fit_price_model.py``; this one is set by ``price_report``.
PRICE = PriceModel(
    # @fit-begin
    44.0, 0.5, 0.583, 0.8, 0.15,
    # @fit-end
    endings=ENDINGS,
    pack_attribute="Length",
    pack_slope=1.0,
    pack_ref=36.0,
)  # fmt: skip


def claims(facts: Mapping[str, str], *, metric: bool, provenance: str, standard: str) -> list[str]:
    """No standard is claimed: a rod's length is a stocked length, and its thread
    is a table's, not a product standard's."""
    return []


SPEC = TypeSpec(
    "threaded_rod",
    category=("Raw Materials", "Threaded Rod & Studs", "All-Thread Rods"),
    standards_family="fastener",
    vocab=VOCAB,
    figure=figure,
    extent=EXTENT,
    make=build,
    share=0.0145,
    price=PRICE,
    claims=claims,
    key_attributes=("Thread Size",),
    threaded="Thread Size",
    fastener=True,
    compat=False,
    use_lines=(
        "Cut to length with a hacksaw and deburr the end so a nut threads on cleanly.",
        "Takes a nut of the same thread size.",
    ),
)
