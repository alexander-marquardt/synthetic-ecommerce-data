"""Hand files, deepened from a breadth row into a modelled type (#836, slice 3).

A hand file is a hardened steel bar whose faces are cut with rows of teeth. A
distributor sells it by shape, by cut grade (how coarse the teeth are) and by
length.

**Sizes.** A file's size is its length, measured without the tang. ISO 234-1
(dimensions) and ISO 234-2 (cut characteristics), the standards the issue
names, were not read: both are sold, and the standards library holds no file
table. So the lengths are the conventional ladders a distributor stocks, 4
to 14 in and 100 to 300 mm. Each shape stocks a run of them
(:data:`SHAPES`), and no record publishes a width, a thickness or a teeth
count the standard would give. No line claims a standard, and the
provenance says that none fixes these values (:data:`PROVENANCE`).

**Names.** ``Length``, ``Shape``, ``Material`` and ``Tooth Type`` are census
names. The census has no file family and no name for a file's cut grade:
its ``Grade`` is a bolt's strength class, and its ``Cutting Type`` is an end
mill's. So the type publishes ``Cut Type`` from ``names.NAME_EXCEPTIONS``. It
is the name a distributor's spec table gives the grade (Penn Tool's page for
the Nicholson 5125 half round file:
https://www.penntoolco.com/nicholson-12-second-cut-american-pattern-half-round-file-5125/,
read on 2026-11-04: ``CUT TYPE: Second``, ``SHAPE: Half-Round``,
``LENGTH: 12"``).

**Single or double cut.** The same page states the rule :func:`tooth_type`
follows: "All 4", 6" and smooth files are single cut. Bastard cut and second
cut files larger then 6" are double cut." A metric file follows the same
rule at its inch length, and a mill file is single cut at every length, which
is what makes it a mill file.

**Lines.** A line is one brand's files of one shape and one cut grade, in one
unit system. The (shape, cut, system) combinations are rotated, not drawn, so
every shape and cut is built.

**Price.** The census measured 118 hand file prices while the type was a
breadth row. They stay its census (``price.DEEPENED_CENSUS``), and the model
is fitted to them (:data:`PRICE`).
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, NamedTuple

from synthetic_ecommerce_data.core.dimensions import DimensionParseError, parse_length
from synthetic_ecommerce_data.core.drawing.model import Figure
from synthetic_ecommerce_data.core.price import PriceModel
from synthetic_ecommerce_data.core.typespec import TypeSpec
from synthetic_ecommerce_data.domains.industrial.drafts import retired
from synthetic_ecommerce_data.domains.industrial.drawing.figures import Drawn
from synthetic_ecommerce_data.domains.industrial.newtypes import MM_PER_INCH, NO_STANDARD
from synthetic_ecommerce_data.domains.industrial.vocab import AttrSpec

KEY = "hand_files"
ITEM = "Hand File"

#: What every record says about where its length came from.
PROVENANCE = f"Length is a conventional stocked length; {NO_STANDARD}"

#: The conventional lengths, inch (inches) and metric (mm).
INCH_LENGTHS = (4.0, 6.0, 8.0, 10.0, 12.0, 14.0)
MM_LENGTHS = (100.0, 150.0, 200.0, 250.0, 300.0)

#: The cut grades, coarse to fine.
CUTS = ("Bastard", "Second", "Smooth")


class Shape(NamedTuple):
    """One shape, and the run of lengths it stocks (shortest and longest, in
    inches then in mm); a shape with no metric run is sold in inch only."""

    name: str
    inch: tuple[float, float]
    mm: tuple[float, float] | None


#: Every shape a brand can offer. A mill file is an American pattern shape,
#: sold in inch lengths only; a three square file is made in the short ones.
SHAPES = (
    Shape("Flat", (4.0, 14.0), (100.0, 300.0)),
    Shape("Hand", (6.0, 12.0), (150.0, 300.0)),
    Shape("Mill", (4.0, 14.0), None),
    Shape("Half Round", (4.0, 14.0), (100.0, 300.0)),
    Shape("Round", (4.0, 12.0), (100.0, 250.0)),
    Shape("Square", (4.0, 12.0), (100.0, 250.0)),
    Shape("Three Square", (4.0, 10.0), (100.0, 200.0)),
)
#: Every line a brand can offer: a shape and a cut in a unit system.
COMBOS = tuple(
    (shape, cut, system)
    for system in ("in", "mm")
    for shape in SHAPES
    if system == "in" or shape.mm is not None
    for cut in CUTS
)


def lengths_in(shape: Shape, metric: bool) -> tuple[float, ...]:
    """``shape``'s stocked lengths in one unit system, in inches."""
    if metric:
        assert shape.mm is not None, shape.name
        low, high = shape.mm
        return tuple(mm / MM_PER_INCH for mm in MM_LENGTHS if low <= mm <= high)
    low, high = shape.inch
    return tuple(length for length in INCH_LENGTHS if low <= length <= high)


def tooth_type(shape: str, cut: str, length_in: float) -> str:
    """Single or double cut, by the maker's rule the module docstring quotes."""
    if shape == "Mill" or cut == "Smooth" or length_in <= 6.0 + 1e-6:
        return "Single Cut"
    return "Double Cut"


def _spec(name: str, scope: str, presence: float = 1.0, kind: str = "keyword") -> AttrSpec:
    return AttrSpec(name=name, scope=scope, presence=presence, kind=kind)


VOCAB = (
    _spec("Shape", "line"),
    _spec("Cut Type", "line"),
    _spec("Material", "line", 0.85),
    _spec("Length", "sku", kind="length"),
    # Per SKU: a 6 in and an 8 in bastard file of one line differ in it.
    _spec("Tooth Type", "sku"),
)


def _make(gen: Any, type_key: str, category: tuple[str, ...]) -> Any:
    # Imported here: generate.py imports the type tables, which discover this module.
    from synthetic_ecommerce_data.core import brands
    from synthetic_ecommerce_data.core.model import keyword_attribute
    from synthetic_ecommerce_data.domains.industrial.generate import ChildDraft, LineDraft

    rng = gen.rng
    shape, cut, system = COMBOS[gen._rotate(f"combo:{type_key}", len(COMBOS))]
    metric = system == "mm"
    brand = brands.pick_brand(rng, type_key, gen._exhausted)
    draft = LineDraft(
        item=ITEM,
        brand=brand,
        series=f"HF{rng.randint(100, 999)}",
        category=category,
    )
    draft.line_attrs = [
        retired(keyword_attribute("Item", ITEM)),  # keeps the stream stable for #497
        keyword_attribute("Shape", shape.name),
        keyword_attribute("Cut Type", cut),
        keyword_attribute("Material", "Carbon Steel"),
    ]
    draft.descriptors = [("Shape", shape.name), ("Cut Type", cut)]
    pool = list(lengths_in(shape, metric))
    count = min(gen._variant_count(), len(pool))
    style = gen._style(system)
    run = gen._offered_run(f"lengths:{shape.name}:{cut}:{system}", pool, count)
    for length_in in run:
        child = ChildDraft(system=system)
        child.primary = gen._length("Length", length_in, style)
        child.attrs = [
            child.primary,
            keyword_attribute("Tooth Type", tooth_type(shape.name, cut, length_in)),
        ]
        draft.children.append(child)
    draft.provenance = PROVENANCE
    return draft


#: The census's hand file endings (``breadth_categories.hand_files.endings``).
ENDINGS = {
    "other": 0.5085,
    "other .x5": 0.3051,
    ".00": 0.0763,
    ".50": 0.0424,
    "other .x9": 0.0424,
    ".99": 0.0169,
    ".95": 0.0085,
}

#: Fitted by hand to the census's 118 hand file prices (p10 4.409, p50 21.43,
#: p90 24.9 USD; ``price.DEEPENED_CENSUS``): the anchor and the noise, scored
#: by the p50 and p90/p10 rows at both sizes. The slope on the length is the
#: census's (0.947, ``price_vs_key_dimension``).
PRICE = PriceModel(
    # @fit-begin
    26.0,
    8.0,
    0.947,
    0.55,
    0.1,
    # @fit-end
    endings=ENDINGS,
)


def _length(record: Mapping[str, str]) -> float | None:
    try:
        return parse_length(record["Length"]).inches
    except (KeyError, DimensionParseError):
        return None


#: The drawing's width and thickness, as a share of the length: no record
#: publishes either, so these only proportion the drawing.
WIDTH = 0.1
TANG = 0.3


def figure(record: dict[str, str]) -> Drawn:
    """The file seen from its face: the cut blade, tapered at the point for
    every shape but the flat and the mill, and the tang on the right."""
    length = _length(record)
    blade = length or 8.0
    end = blade * (1 + TANG)
    half = WIDTH * blade / 2
    tip = half if record.get("Shape") in ("Flat", "Mill", "Hand") else half / 2
    fig = Figure(size_in=end)
    fig.poly([(0.0, -tip), (blade, -half), (blade, half), (0.0, tip)])
    fig.poly([(blade, -half / 2), (end, -half / 6), (end, half / 6), (blade, half / 2)])
    return Drawn(fig, "partial" if length else "nominal")


SPEC = TypeSpec(
    KEY,
    category=("Hand Tools", "Files & Rasps", "Hand Files"),
    standards_family="hand_tool",
    vocab=VOCAB,
    figure=figure,
    # Measured at the default and ``--lines 39000`` builds (docs/adding-a-type.md
    # "Figure and extent"): the largest drawn is 18.20 x 1.40 in, a 14 in file
    # with its tang.
    extent=(18.3, 1.5),
    make=_make,
    share=0.0135,
    price=PRICE,
    claims=None,
    may_claim=frozenset(),
    key_attributes=("Length",),
    compat=False,
    use_lines=(
        "Removes metal, deburrs edges and shapes parts by hand.",
        "Sharpens edges and dresses a surface after cutting.",
    ),
)
