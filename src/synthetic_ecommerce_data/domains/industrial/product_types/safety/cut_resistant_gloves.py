"""Cut-resistant gloves: knit work gloves rated to ANSI/ISEA 105, deepened
from breadth (#834, the safety family of #53).

A glove is built from its model line, not from a size table: ANSI/ISEA 105
rates a glove's cut resistance (levels A1 to A9) and says nothing of its
sizes, so a type of these is the set of model lines makers stock.

**Model lines.** :data:`MODEL_LINES` are the gloves of the "Cut Resistant
Glove Guide" at https://www.uline.com/guide/CutResistantGloveGuides, read
2026-11-04: each row there gives a glove's ANSI cut level, its shell yarn,
its knit gauge and its coating. A row here is one distinct combination of the
four; the guide's item numbers are beside it. Shell yarns are published by
their generic names, not the guide's trade names: Dyneema is ``HPPE``,
Dyneema Diamond and Dyneema blends are ``HPPE Blend``, Kevlar is ``Aramid``
and a Kevlar blend ``Aramid Blend``.

**Dropped.** The guide's sleeves, its steel mesh glove (not cut rated), its
jersey gloves (no knit gauge), its SuperFabric gloves (a coated guard fabric,
not a knit shell), its goatskin glove (a leather glove), and the one glove
with two coatings (PVC and nitrile on one palm). The guide gives no color for
most models, so no color is published.

**Sizes.** The six hand sizes of EN ISO 21420 (6 to 11), by the names glove
listings print them, X-Small to XX-Large. A line offers a run of neighbouring
sizes. A size's number is its hand circumference in inches; the drawing reads
it, and the standard's minimum glove length for the size, from
:data:`HAND_SIZES`.

**Names.** ``Material`` is the shell yarn and ``Coating`` the palm coating,
both census names. The census has no name for the cut level or a knit's
gauge (``Gauge`` is a screw's wire gauge there), so ``ANSI Cut Level`` and
``Knit Gauge`` are ``names.NAME_EXCEPTIONS`` entries, named as ANSI/ISEA 105
and the guide's ``Gauge`` column state them.
"""

from __future__ import annotations

import math
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, NamedTuple

from synthetic_ecommerce_data.core.drawing.model import Figure, arc
from synthetic_ecommerce_data.core.model import keyword_attribute
from synthetic_ecommerce_data.core.price import PriceModel
from synthetic_ecommerce_data.core.typespec import TypeSpec
from synthetic_ecommerce_data.domains.industrial.drawing.figures import Drawn
from synthetic_ecommerce_data.domains.industrial.vocab import AttrSpec

if TYPE_CHECKING:
    from synthetic_ecommerce_data.domains.industrial.generate import LineDraft

KEY = "cut_resistant_gloves"
ITEM = "Cut-Resistant Glove"
STANDARD = "ANSI/ISEA 105"
GUIDE = "https://www.uline.com/guide/CutResistantGloveGuides"


class ModelLine(NamedTuple):
    """One glove model: what every size of it shares."""

    cut_level: str
    material: str
    gauge: int
    coating: str


#: The guide's gloves, one row per distinct model, by cut level.
MODEL_LINES: tuple[ModelLine, ...] = (
    ModelLine("A2", "HPPE", 13, "Polyurethane"),  # S-14249, S-20703, S-19711
    ModelLine("A2", "HPPE", 15, "Polyurethane"),  # S-21574
    ModelLine("A2", "HPPE", 13, "Latex"),  # S-23342
    ModelLine("A2", "HPPE Blend", 18, "Polyurethane"),  # S-19705
    ModelLine("A2", "HPPE Blend", 18, "Uncoated"),  # S-25233
    ModelLine("A2", "HPPE Blend", 15, "Nitrile"),  # S-22150, S-24024
    ModelLine("A2", "Acrylic", 3, "Latex"),  # S-19884, S-19885
    ModelLine("A2", "Acrylic", 13, "Nitrile"),  # S-22778
    ModelLine("A2", "Acrylic", 13, "Latex"),  # S-25681
    ModelLine("A2", "Aramid", 10, "Latex"),  # S-9867
    ModelLine("A2", "Aramid", 13, "Nitrile"),  # S-16858
    ModelLine("A3", "HPPE Blend", 18, "Nitrile"),  # S-25662
    ModelLine("A3", "HPPE Blend", 18, "Polyurethane"),  # S-24007
    ModelLine("A3", "HPPE Blend", 15, "Nitrile"),  # S-23323, S-23911
    ModelLine("A3", "HPPE Blend", 13, "Nitrile"),  # S-20768
    ModelLine("A3", "HPPE Blend", 6, "Synthetic Leather"),  # S-23343
    ModelLine("A3", "HPPE Blend", 4, "Synthetic Leather"),  # S-25684
    ModelLine("A3", "Aramid", 7, "Uncoated"),  # S-7893
    ModelLine("A3", "Aramid", 7, "PVC Dots"),  # S-9866
    ModelLine("A3", "Aramid", 10, "Latex"),  # S-15331
    ModelLine("A4", "HPPE Blend", 15, "Nitrile"),  # S-24006
    ModelLine("A4", "HPPE Blend", 13, "Nitrile"),  # S-22779, S-24002
    ModelLine("A4", "Aramid Blend", 18, "Nitrile"),  # S-25683
    ModelLine("A5", "HPPE Blend", 18, "Nitrile"),  # S-25682
    ModelLine("A5", "HPPE", 4, "Synthetic Leather"),  # S-25680
    ModelLine("A5", "Aramid Blend", 13, "Nitrile"),  # S-19706, S-19707
    ModelLine("A6", "HPPE Blend", 13, "Nitrile"),  # S-22780
    ModelLine("A6", "HPPE Blend", 10, "Uncoated"),  # S-19248
    ModelLine("A8", "HPPE Blend", 13, "Nitrile"),  # S-24003
)


class HandSize(NamedTuple):
    """One EN ISO 21420 hand size."""

    name: str
    #: The size's number: the hand's circumference, in inches.
    number: int
    #: The standard's minimum glove length for the size, in mm.
    min_length_mm: int


HAND_SIZES: tuple[HandSize, ...] = (
    HandSize("X-Small", 6, 220),
    HandSize("Small", 7, 230),
    HandSize("Medium", 8, 240),
    HandSize("Large", 9, 250),
    HandSize("X-Large", 10, 260),
    HandSize("XX-Large", 11, 270),
)
BY_NAME = {size.name: size for size in HAND_SIZES}

PROVENANCE = f"model lines read from {GUIDE} (2026-11-04); sizes are the EN ISO 21420 hand sizes"

VOCAB = (
    AttrSpec("ANSI Cut Level", "line"),
    AttrSpec("Material", "line"),
    AttrSpec("Coating", "line"),
    AttrSpec("Knit Gauge", "line", 0.85),
    AttrSpec("Size", "sku"),
)


def build(gen: Any, type_key: str, category: tuple[str, ...]) -> LineDraft:
    """One line: a brand's glove of one model line, in a run of neighbouring sizes."""
    # Imported here: generate imports the type tables, which discover this module.
    from synthetic_ecommerce_data.core.brands import pick_brand
    from synthetic_ecommerce_data.domains.industrial.generate import ChildDraft, LineDraft

    rng = gen.rng
    brand = pick_brand(rng, type_key, gen._exhausted)
    model = MODEL_LINES[gen._rotate("model", len(MODEL_LINES))]
    draft = LineDraft(
        item=ITEM,
        brand=brand,
        series=f"CR{rng.randint(100, 999)}",
        category=category,
        provenance=PROVENANCE,
    )
    draft.line_attrs = [
        keyword_attribute("ANSI Cut Level", model.cut_level),
        keyword_attribute("Material", model.material),
        keyword_attribute("Coating", model.coating),
        keyword_attribute("Knit Gauge", f"{model.gauge} Gauge"),
    ]
    draft.descriptors = [("ANSI Cut Level", model.cut_level)]
    # A run that never wraps: a glove offered in XX-Large and X-Small and
    # nothing between is not a model anyone stocks.
    count = max(1, min(gen._variant_count(), len(HAND_SIZES)))
    start = gen._rotate(f"size:{count}", len(HAND_SIZES) - count + 1)
    for size in HAND_SIZES[start : start + count]:
        child = ChildDraft()
        child.primary = keyword_attribute("Size", size.name)
        child.attrs = [child.primary]
        draft.children.append(child)
    return draft


#: Nominal proportions of the drawn glove, for what no source gives. Of the
#: glove's length: the cuff, the palm and the longest finger. Of the hand's
#: circumference: the palm's width.
CUFF = 0.24
PALM = 0.36
FINGER = 0.40
WIDTH = 0.42
#: Each finger's length, index to little, as a share of the longest.
FINGERS = (0.9, 1.0, 0.94, 0.76)
MM_PER_INCH = 25.4


def figure(record: dict[str, str]) -> Drawn:
    """The glove seen from the back of the hand, cuff down: drawn at the hand
    circumference and the minimum glove length of its EN ISO 21420 size."""
    size = BY_NAME.get(record.get("Size", ""))
    source = "record" if size else "nominal"
    size = size or BY_NAME["Medium"]
    length = size.min_length_mm / MM_PER_INCH
    width = WIDTH * size.number
    cuff, palm, finger = CUFF * length, PALM * length, FINGER * length
    half = width / 2
    pitch = width / len(FINGERS)
    top = -(cuff + palm)
    wrist = 0.8 * half
    # The page's y runs down: the cuff's edge is y = 0 and the glove is above it. One outline,
    # drawn round from the cuff's edge: up the little finger's side, over each fingertip, down
    # the index side, round the thumb and back to the cuff (#873).
    outline = [(-wrist, 0.0), (wrist, 0.0), (0.97 * wrist, -cuff)]
    outline += _bend(outline[-1], (half, -cuff - 0.1 * palm), (half, -cuff - 0.5 * palm))
    crotch = 0.08 * pitch
    outline += _bend(
        outline[-1], (half, top + 0.2 * palm), (half - pitch / 2 + 0.42 * pitch, top - crotch)
    )
    for k in reversed(range(len(FINGERS))):
        centre = -half + (k + 0.5) * pitch
        tip, base = 0.36 * pitch, 0.42 * pitch
        reach = top - FINGERS[k] * finger + tip
        outline += [(centre + base, top - crotch), (centre + tip, reach)]
        outline += arc((centre, reach), tip, 0.0, -180.0, 8)[1:]
        outline.append((centre - base, top - crotch))
        if k:  # the rounded crotch down to the next finger
            outline += arc((centre - base - crotch, top - crotch), crotch, 0.0, 90.0, 3)[1:]
            outline += arc((centre - base - crotch, top - crotch), crotch, 90.0, 180.0, 3)[1:-1]
    outline += _bend(outline[-1], (-half, top + 0.1 * palm), (-half, -cuff - 0.72 * palm))
    # The thumb leans out from the palm's side, below the fingers: a capsule on a slant.
    lean = math.radians(42.0)
    out = (-math.sin(lean), -math.cos(lean))
    side = (math.cos(lean), -math.sin(lean))
    thumb, radius = 0.6 * finger, 0.45 * pitch
    root = (-half + 0.25 * pitch, -cuff - 0.45 * palm)
    centre = (root[0] + out[0] * (thumb - radius), root[1] + out[1] * (thumb - radius))
    start = math.degrees(math.atan2(side[1], side[0]))
    outline += arc(centre, radius, start, start - 180.0, 10)
    outline.append((root[0] - side[0] * radius, root[1] - side[1] * radius))
    outline += _bend(outline[-1], (-0.97 * half, -cuff - 0.12 * palm), (-0.97 * wrist, -cuff))
    fig = Figure(size_in=length)
    fig.poly(outline)
    ribs = [-wrist + k * pitch / 3 for k in range(1, int(2 * wrist / (pitch / 3)) + 1)]
    fig.lines([((-0.97 * wrist, -cuff), (0.97 * wrist, -cuff))])
    fig.lines(((x, -0.08 * cuff), (x, -0.92 * cuff)) for x in ribs if abs(x) < 0.95 * wrist)
    return Drawn(fig, source)


def _bend(
    start: tuple[float, float], control: tuple[float, float], end: tuple[float, float]
) -> list[tuple[float, float]]:
    """The points after ``start`` of a quadratic curve pulled toward ``control``, to ``end``."""
    steps = 6
    return [
        (
            (1 - t) ** 2 * start[0] + 2 * (1 - t) * t * control[0] + t**2 * end[0],
            (1 - t) ** 2 * start[1] + 2 * (1 - t) * t * control[1] + t**2 * end[1],
        )
        for t in (k / steps for k in range(1, steps + 1))
    ]


def claims(
    facts: Mapping[str, str], *, metric: bool, provenance: str, standard: str
) -> tuple[str, ...]:
    """Every line states its ANSI/ISEA 105 cut level."""
    return (STANDARD,)


#: The census ending mix of the 22 gloves (``breadth_categories.cut_resistant_gloves``),
#: restated as the threaded rod restates its own: the type was a breadth row,
#: so :data:`...core.price.ENDINGS` does not carry it.
ENDINGS = {"other": 0.5455, "other .x5": 0.4545}

#: Hand-set to the census's 22 gloves (p10 9.45, p50 21.45, p90 67.675; every
#: size of one glove the same price, a slope of 0.0 on Size). The anchor is a
#: standard-tier A2 pair. The cut-level ladder is NOT MEASURED: the census
#: does not record a glove's cut level, so a higher level's premium is a
#: declared estimate that keeps a higher level dearer.
PRICE = PriceModel(
    # @fit-begin
    17.5, 1.0, 0.0, 0.6, 0.0,
    # @fit-end
    endings=ENDINGS,
    option_attribute="ANSI Cut Level",
    option_factors={"A2": 1.0, "A3": 1.25, "A4": 1.6, "A5": 2.0, "A6": 2.5, "A8": 3.5},
)  # fmt: skip

SPEC = TypeSpec(
    KEY,
    category=("Safety", "Hand Protection", "Cut-Resistant Gloves"),
    standards_family="hand_tool",
    vocab=VOCAB,
    figure=figure,
    # An XX-Large glove, 270 mm long and its thumb out: 7.07" x 10.63" at both sizes.
    extent=(7.2, 10.75),
    make=build,
    share=0.015,
    price=PRICE,
    claims=claims,
    may_claim=frozenset({STANDARD}),
    key_attributes=("Size",),
    compat=False,
    use_lines=(
        "For handling sheet metal, glass and blades.",
        "Sold as a pair.",
    ),
)
