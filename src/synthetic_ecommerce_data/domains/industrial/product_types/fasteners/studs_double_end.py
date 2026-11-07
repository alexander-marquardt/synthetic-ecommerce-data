"""Double-end stud: deepened from a breadth row into a modelled type (#829).

The breadth row offered six thread sizes, two materials and two finishes. A
distributor's stud space is wider, and it is the thread that fixes it:

* four series, each a thread table: inch coarse (UNC) and inch fine (UNF) read
  from ASME B1.1, metric coarse and metric fine read from ISO 262, as the
  threaded rod reads them (#73). A fine metric line draws from ONE pitch
  ladder, so two pitches of one diameter are never siblings of a line;
* the material, finish and grade or property class a stud is stocked in;
* a stocked overall length, a line attribute: 1-1/2" to 8" in inch and 30 to
  150 mm in metric. A line's length is one that each of its threads' diameters
  fits into at least :data:`LENGTH_OVER_DIAMETER` times, so no 1" stud is
  1-1/2" long;
* the stud's ``Type``: equal-length threads on both ends, or a tap end (a
  short end that goes into a tapped hole) and a longer nut end.

Thread Size is read from a table, so ``dimension_provenance`` names the thread
table it came from (:attr:`Series.provenance`). A stud's length is a stocked
length, not a table's value. ASME B18.31.2, the inch stud standard, was not
read: no line claims it, and no thread length or body diameter is published.

No pack quantity is published (#14): a line is one stud per SKU.
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
from synthetic_ecommerce_data.domains.industrial.geometry import thread as thread_geom
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

ITEM = "Double-End Stud"

INCH_TABLE = "ASME B1.1"
METRIC_TABLE = "ISO 262"

#: The shortest stud a thread is offered on, in diameters of that thread.
LENGTH_OVER_DIAMETER = 4

#: The two kinds of double-end stud: the same thread length on both ends, or a
#: short tap end and a longer nut end.
EQUAL = "Equal Length Threads"
TAP_END = "Tap End"
KINDS = (EQUAL, TAP_END)


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
    #: Stocked overall lengths, in the series' unit (inches, or millimetres).
    lengths: tuple[float, ...]

    @property
    def provenance(self) -> str:
        """Where the thread came from, and that the length is a stocked one."""
        table = INCH_TABLE if self.system == "in" else METRIC_TABLE
        thread = table_provenance(("Thread Size", table))
        return f"{thread}; Length is a stocked length; {NO_STANDARD}"


# --- the thread tables ----------------------------------------------------------------

_THREADS = library.table("asme_b1_1_unified_threads")
_UNC_SIZES = ["#10", "1/4", "5/16", "3/8", "7/16", "1/2", "9/16", "5/8", "3/4", "7/8", "1"]
_UNF_SIZES = _UNC_SIZES[1:]
_UNC = tuple(f"{row['size']}-{row['unc_tpi']}" for row in _THREADS.select(_UNC_SIZES))
_UNF = tuple(f"{row['size']}-{row['unf_tpi']}" for row in _THREADS.select(_UNF_SIZES))

_ISO = library.table("iso_262_metric_threads")
_METRIC_SIZES = ["M5", "M6", "M8", "M10", "M12", "M14", "M16", "M18", "M20", "M22", "M24"]
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

# --- the combinations a stud is stocked in --------------------------------------------

_INCH_COMBOS: tuple[Combo, ...] = (
    ("Steel", "Zinc Plated", "Grade 2"),
    ("Steel", "Plain", "Grade 2"),
    ("Steel", "Zinc Plated", "Grade 5"),
    ("Alloy Steel", "Plain", "Grade B7"),
    ("Alloy Steel", "Zinc Plated", "Grade B7"),
    ("18-8 Stainless Steel", "Plain", None),
    ("316 Stainless Steel", "Plain", None),
)
_METRIC_COMBOS: tuple[Combo, ...] = (
    ("Steel", "Zinc Plated", "Class 4.8"),
    ("Steel", "Plain", "Class 4.8"),
    ("Steel", "Zinc Plated", "Class 8.8"),
    ("Alloy Steel", "Plain", "Class 8.8"),
    ("18-8 Stainless Steel", "Plain", None),
    ("316 Stainless Steel", "Plain", None),
)
#: Stocked overall lengths: ten in inch, eight in metric.
_INCH_LENGTHS = (1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 6.0, 8.0)
_METRIC_LENGTHS = (30.0, 40.0, 50.0, 60.0, 80.0, 100.0, 120.0, 150.0)

#: (series, weight): how often a line is drafted in each.
SERIES: tuple[tuple[Series, float], ...] = (
    (Series("inch-unc", "in", "UNC", (_UNC,), _INCH_COMBOS, _INCH_LENGTHS), 0.45),
    (Series("inch-unf", "in", "UNF", (_UNF,), _INCH_COMBOS, _INCH_LENGTHS), 0.12),
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
        0.10,
    ),
)

VOCAB = (
    AttrSpec("Material", "line"),
    AttrSpec("Finish", "line", 0.9),
    AttrSpec("Grade", "line", 0.9),
    AttrSpec("Type", "line", 0.85),
    AttrSpec("Thread Type", "line", 0.8),
    AttrSpec("Thread Direction", "line", 0.55),
    AttrSpec("Length", "line", kind="length"),
    AttrSpec("Thread Size", "sku"),
)


def fits(thread: str, length_in: float) -> bool:
    """Whether a stud ``length_in`` inches long is LENGTH_OVER_DIAMETER diameters of the thread."""
    return length_in >= LENGTH_OVER_DIAMETER * parse_thread(thread).major.inches - 1e-9


def build(gen: Any, type_key: str, category: tuple[str, ...]) -> LineDraft:
    """One line: a series, a kind and a stocked combination, a window of its
    threads, and a stocked length every thread of the window fits."""
    # Imported here: generate imports the type tables, which discover this module.
    from synthetic_ecommerce_data.core.brands import pick_brand
    from synthetic_ecommerce_data.domains.industrial.generate import BRANDS, ChildDraft, LineDraft

    rng = gen.rng
    brand = pick_brand(rng, type_key, gen._exhausted)
    series = _weighted(rng, SERIES)
    metric = series.system == "mm"
    # A rotation per axis, so a small build reaches both kinds, every
    # combination, every thread and every length; the combination and the
    # length turn per kind, so neither is tied to the kind's parity.
    kind = KINDS[gen._rotate(f"stud:{series.name}:kind", len(KINDS))]
    stock = f"stud:{series.name}:{kind}"
    material, finish, grade = series.combos[gen._rotate(f"{stock}:combo", len(series.combos))]
    which = gen._rotate(f"stud:{series.name}:range", len(series.ranges))
    rows = list(series.ranges[which])
    threads = _window(gen, f"stud:{series.name}:{which}", rows, gen._variant_count())
    # The longest stocked length always fits the thickest thread, so the list
    # is never empty.
    fitting = [
        length
        for length in series.lengths
        if all(fits(t, length / MM_PER_INCH if metric else length) for t in threads)
    ]
    length = fitting[gen._rotate(f"{stock}:length", len(fitting))]
    draft = LineDraft(
        item=ITEM,
        brand=brand,
        series=f"DS{rng.randint(100, 999)}",
        category=category,
        provenance=series.provenance,
    )
    style = feed_style(brand, series.system, BRANDS)
    length_attr = length_attribute(
        "Length", gen._publish(length / MM_PER_INCH if metric else length, style)
    )
    draft.line_attrs = [
        retired(keyword_attribute("Item", ITEM)),  # keeps the stream stable
        keyword_attribute("Material", material),
        keyword_attribute("Finish", finish),
        keyword_attribute("Type", kind),
        keyword_attribute("Thread Type", series.thread_type),
        keyword_attribute("Thread Direction", "Right Hand"),
        length_attr,
    ]
    if grade is not None:
        draft.line_attrs.append(keyword_attribute("Grade", grade))
    draft.descriptors = [("Material", material), ("Length", length_attr.value)]
    for thread in threads:
        child = ChildDraft(system=series.system)
        child.primary = keyword_attribute("Thread Size", thread)
        child.attrs = [child.primary]
        draft.children.append(child)
    return draft


# --- the drawing ------------------------------------------------------------------

#: A long stud is drawn compressed into KNEE + TAIL inches at most, so its
#: thread stays legible; the tail grows slowly enough (SCALE inches) that an 8"
#: stud still draws longer than a 4" one.
KNEE = 3.0
TAIL = 0.6
SCALE = 6.0
#: The most crests drawn along one threaded end of a coarse-thread stud; a fine one draws
#: more, at its true ratio to the coarse thread of its diameter (``geometry.thread.capped_pitch``,
#: #9).
MAX_CRESTS = 24
#: Each end's threaded length, in diameters, as drawn (not published: no
#: thread length was read). An equal stud carries NUT_END on both ends; a
#: tap-end stud carries TAP on its lower end. Neither end draws past END_CAP of
#: the stud, so a short stud keeps a plain body between them.
NUT_END = 2.0
TAP = 1.25
END_CAP = 0.4
#: The drawing's extent, measured at the default and ``--lines 39000`` builds
#: (docs/adding-a-type.md "Figure and extent"): the largest drawn is 1.0 x
#: 3.339 in at both the default build and --lines 39000: a 1" stud's width
#: and an 8" stud compressed down the page.
EXTENT = (1.1, 3.45)

_NOMINAL_THREAD = "1/2-13"
_NOMINAL_LENGTH_IN = 3.0


def figure(record: dict[str, str]) -> Drawn:
    """The stud seen from the side: a threaded end at each end of a plain body."""
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
    shrink = drawn / full
    d = thread.major.inches
    r = d / 2
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
    lower = TAP if record.get("Type") == TAP_END else NUT_END
    pitch = thread_geom.capped_pitch(thread, drawn * END_CAP / MAX_CRESTS, shrink)
    low_end = min(lower * d * shrink, drawn * END_CAP)
    high_end = min(NUT_END * d * shrink, drawn * END_CAP)
    fig.lines(P.thread_crests(r, c, low_end, pitch))
    fig.lines(P.thread_crests(r, drawn - high_end, drawn - c, pitch))
    source = "record" if length and "Thread Size" in record else "nominal"
    return Drawn(fig, source)


# --- price ------------------------------------------------------------------------

#: GENERATED, NOT MEASURED: the price census has no double-end studs (neither
#: ``deep_types`` nor ``breadth_categories`` of P2_price_census.json). Hand-set
#: from the breadth row's level (1 to 8 USD for 1/4" to 7/16"): the anchor is a
#: standard-tier 1/2-13 Grade 2 steel stud 3" long. A stud is a cut, threaded
#: rod, so its price scales with its length below one for one (the pack slope),
#: and with its diameter more steeply than a rod's 0.583, as a short part's
#: threading is a larger share of its cost.
PRICE = PriceModel(
    3.4,
    0.5,
    1.2,
    0.2,
    0.08,
    measured=False,
    pack_attribute="Length",
    pack_slope=0.6,
    pack_ref=3.0,
)


def claims(facts: Mapping[str, str], *, metric: bool, provenance: str, standard: str) -> list[str]:
    """No standard is claimed: ASME B18.31.2 was not read, and a stud's thread
    is a table's, not a product standard's."""
    return []


SPEC = TypeSpec(
    "studs_double_end",
    category=("Fasteners", "Studs", "Double-End Studs"),
    standards_family="fastener",
    vocab=VOCAB,
    figure=figure,
    extent=EXTENT,
    make=build,
    share=0.0145,
    price=PRICE,
    claims=claims,
    may_claim=frozenset(),
    key_attributes=("Thread Size",),
    threaded="Thread Size",
    fastener=True,
    compat=False,
    use_lines=(
        "Thread one end into a tapped hole and fasten the part on the other end with a nut.",
        "Takes a nut of the same thread size on each end.",
    ),
)
