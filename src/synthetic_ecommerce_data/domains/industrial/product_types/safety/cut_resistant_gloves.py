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

from synthetic_ecommerce_data.core.drawing.model import Figure, Point, arc
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


#: Nominal proportions of the drawn glove, for what no source gives. Of the glove's length: the
#: cuff, the palm and the longest finger. Of the hand's circumference: the palm's width, half of
#: it, for a glove laid flat is its tube pressed flat.
CUFF = 0.22
PALM = 0.42
FINGER = 0.36
WIDTH = 0.5
#: Each finger's length, index to little, as a share of the longest; how far its knuckle sits
#: below the middle finger's, in the same share; and its lean, in degrees from the thumb's side.
FINGERS = (0.9, 1.0, 0.94, 0.76)
KNUCKLES = (0.05, 0.0, 0.03, 0.12)
LEANS = (-4.0, -1.0, 3.0, 7.0)
MM_PER_INCH = 25.4
#: The pair: each glove's lean from upright in degrees, and its offset from the middle as a share
#: of the length. Both thumbs point the same way: one glove shows its back, one its palm.
SPLAY = 4.0
APART = 0.13
#: The usual color of each palm coating; the guide states none. An uncoated palm is bare knit.
COATING_FILL = {
    "Polyurethane": "#c9ccce",
    "Latex": "#3f6f9e",
    "Nitrile": "#3b3e42",
    "Synthetic Leather": "#b98a5a",
}


class _Glove(NamedTuple):
    """One glove upright, cuff edge at y = 0, thumb to the left, and what lies on it."""

    outline: list[Point]
    #: The palm coating: the outline above the cuff, dipped to a wavy edge.
    coat: list[Point]
    ribs: list[tuple[Point, Point]]
    dots: list[Point]
    #: The shadow down the little finger's side and the highlight down the thumb's.
    shade: list[Point]
    gloss: list[Point]


def _glove(size: HandSize) -> _Glove:
    """The glove of ``size``, laid flat at its hand circumference and minimum length. One outline,
    drawn round from the cuff's edge: up the little finger's side, over each fingertip, down the
    index side, round the thumb and back to the cuff (#873). The page's y runs down."""
    length = size.min_length_mm / MM_PER_INCH
    width = WIDTH * size.number
    cuff, palm, finger = CUFF * length, PALM * length, FINGER * length
    half, pitch = width / 2, width / len(FINGERS)
    top, wrist = -(cuff + palm), 0.82 * width / 2
    hem: list[Point] = [(-0.97 * wrist, -cuff), (-wrist, 0.0), (wrist, 0.0), (0.97 * wrist, -cuff)]
    hand: list[Point] = [hem[-1]]
    hand += _bend(hand[-1], (half, -cuff - 0.1 * palm), (half, -cuff - 0.5 * palm))
    for k in reversed(range(len(FINGERS))):
        turn = math.radians(LEANS[k])
        up, across = (math.sin(turn), -math.cos(turn)), (math.cos(turn), math.sin(turn))
        base, tip = 0.48 * pitch, 0.46 * pitch
        root = (-half + (k + 0.5) * pitch, top + KNUCKLES[k] * finger)
        start = (root[0] + across[0] * base, root[1] + across[1] * base)
        low = max(hand[-1][1], start[1]) + 0.2 * pitch if k < 3 else (hand[-1][1] + start[1]) / 2
        middle = (half if k == 3 else (hand[-1][0] + start[0]) / 2, low)
        hand += _bend(hand[-1], middle, start, 3)
        reach = 0.97 * FINGERS[k] * finger - tip
        centre = (root[0] + up[0] * reach, root[1] + up[1] * reach)
        hand += arc(centre, tip, LEANS[k], LEANS[k] - 180.0, 8)
        hand.append((root[0] - across[0] * base, root[1] - across[1] * base))
    hand += _bend(hand[-1], (-half, top + 0.15 * palm), (-half, -cuff - 0.74 * palm))
    # The thumb leans out from the palm's side, below the fingers: a capsule on a slant.
    lean = math.radians(42.0)
    out, side = (-math.sin(lean), -math.cos(lean)), (math.cos(lean), -math.sin(lean))
    thumb, radius = 0.66 * finger, 0.48 * pitch
    root = (-half + 0.25 * pitch, -cuff - 0.45 * palm)
    centre = (root[0] + out[0] * (thumb - radius), root[1] + out[1] * (thumb - radius))
    start_deg = math.degrees(math.atan2(side[1], side[0]))
    hand += arc(centre, radius, start_deg, start_deg - 180.0, 8)
    hand.append((root[0] - side[0] * radius, root[1] - side[1] * radius))
    hand += _bend(hand[-1], (-0.97 * half, -cuff - 0.12 * palm), hem[0])
    # The dip stops short of the cuff, in a wave across the wrist.
    edge = -cuff - 0.16 * palm
    above = [p for p in hand if p[1] < edge]
    waves = 8
    left, right = above[-1][0], above[0][0]
    wave = [
        (left + (right - left) * n / waves, edge + (0.03 * palm if n % 2 else -0.03 * palm))
        for n in range(1, waves)
    ]
    ribs = [
        ((x, -0.08 * cuff), (x, -0.92 * cuff)) for x in (wrist * (n / 5 - 1) for n in range(1, 10))
    ]
    ribs.append((hem[0], hem[-1]))
    dots = [
        (-half + (n + 0.5) * width / 8, -cuff - (0.22 + 0.13 * row) * palm)
        for row in range(6)
        for n in range(1, 7)
    ]
    shade = [hem[2], *hand[:5], (0.97 * half, top + 0.22 * palm)]
    shade += _bend(shade[-1], (0.5 * half, -cuff - 0.45 * palm), (0.6 * wrist, 0.0))
    gloss = [(-0.62 * half, top + 0.14 * palm), (-0.34 * half, top + 0.1 * palm)]
    gloss += _bend(gloss[-1], (-0.5 * half, -cuff - 0.5 * palm), (-0.42 * half, -cuff - 0.2 * palm))
    gloss += _bend(gloss[-1], (-0.75 * half, -cuff - 0.5 * palm), gloss[0])
    return _Glove([*hem[:3], *hand[:-1]], above + wave, ribs, dots, shade, gloss)


def figure(record: dict[str, str]) -> Drawn:
    """The pair, cuffs down and overlapping: the back of one glove behind the palm of the other,
    the palm in its coating, each lit by a highlight and a shadow (#1217). A glove is drawn at the
    hand circumference and the minimum glove length of its EN ISO 21420 size; the pair fills the
    figure area at every size and angle (``fit_turned``)."""
    size = BY_NAME.get(record.get("Size", ""))
    source = "record" if size else "nominal"
    size = size or BY_NAME["Medium"]
    glove = _glove(size)
    length = size.min_length_mm / MM_PER_INCH
    coating = record.get("Coating", "")
    fig = Figure(size_in=length, fit_turned=True)
    for sign in (-1.0, 1.0):
        turn = math.radians(sign * SPLAY)
        c, s = math.cos(turn), math.sin(turn)

        def at(points: list[Point], dx: float = sign * APART * length, c: float = c, s: float = s):
            return [(x * c - y * s + dx, x * s + y * c) for x, y in points]

        fig.poly(at(glove.outline))
        if sign > 0:
            if coating in COATING_FILL:
                fig.poly(at(glove.coat), "grip", COATING_FILL[coating])
            elif coating == "PVC Dots":
                fig.dots(at(glove.dots), 0.045 * WIDTH * size.number)
        fig.lines(tuple(at(list(rib))) for rib in glove.ribs)
        fig.poly(at(glove.shade), "shade")
        fig.poly(at(glove.gloss), "gloss")
    return Drawn(fig, source)


def _bend(
    start: tuple[float, float],
    control: tuple[float, float],
    end: tuple[float, float],
    steps: int = 4,
) -> list[tuple[float, float]]:
    """The points after ``start`` of a quadratic curve pulled toward ``control``, to ``end``."""
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
    # An XX-Large pair, 270 mm long and both thumbs out. The pair is drawn to fit its own turned
    # outline (``fit_turned``), so this is the box it is declared in, not its scale.
    extent=(11.6, 10.9),
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
