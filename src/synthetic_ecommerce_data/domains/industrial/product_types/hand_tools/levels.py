"""Levels: a homeowner tool for the general-retail catalogue (#971, slice 2).

A spirit level is a straight frame with bubble vials set in it: one reads level, one
plumb. A hardware listing sells it by length, and names its frame shape, its frame
material and whether its edge is magnetic.

**Shapes and sizes.** Three frame shapes, each stocked in its own lengths
(:data:`INCH_LENGTHS`, :data:`METRIC_LENGTHS_MM`): a torpedo level, short and tapered, in
9 or 12 in (230 or 300 mm); a box-beam level, a hollow rectangular frame, in 24, 48 and
72 in (600, 1200 and 1800 mm); and an I-beam level in 24 and 48 in (600 and 1200 mm). No
standard fixes these lengths, so no line claims one and the provenance says so
(:data:`PROVENANCE`).

**Lines.** A line is one brand's levels of one shape, one frame material, one feature
(a magnetic edge or none) and one frame color, in one unit system. Its SKUs are a run of
the shape's lengths. The 36 (shape, material, feature, system) combinations are rotated
in an order whose first six lines already hold every shape, material, feature and
system (:data:`COMBOS`), so a small build offers each of them too.

**Colors.** The frame comes in each of the six main colors (gen#275): red, blue, green,
yellow, black and white (:data:`COLORS`). The color rotation steps one further at each
full turn of the combinations, so each combination is built in every color, not the same
color each time (:func:`frame_color`).

**Decoys.** Every type carries text-match decoys (gen#294). In every :data:`DECOY_PERIOD`
lines, :data:`DECOY_SLOTS` of them name another layout tool before the item ("Square
Series Level"). A search for that tool's word then finds a level, which a category
policy can remove. The attributes stay true, so no check exempts them.

**Price.** GENERATED, not measured: the price census has no levels. A level costs about
its length to the 0.75 power, anchored at 20 USD for a 24 in standard-tier level.
"""

from __future__ import annotations

from typing import Any

from synthetic_ecommerce_data.core.dimensions import DimensionParseError, parse_length
from synthetic_ecommerce_data.core.drawing.model import Figure
from synthetic_ecommerce_data.core.price import PriceModel
from synthetic_ecommerce_data.core.typespec import TypeSpec
from synthetic_ecommerce_data.domains.industrial.drawing.figures import Drawn
from synthetic_ecommerce_data.domains.industrial.newtypes import MM_PER_INCH, NO_STANDARD
from synthetic_ecommerce_data.domains.industrial.vocab import AttrSpec

KEY = "levels"
ITEM = "Level"
CATEGORY: tuple[str, ...] = ("Measuring & Inspecting", "Levels")

#: What every record says about where its length came from.
PROVENANCE = f"Length is a conventional stocked size; {NO_STANDARD}"

#: The frame shapes, and the lengths each is stocked in: inches for an inch level, mm for a
#: metric one.
SHAPES: tuple[str, ...] = ("Torpedo", "Box Beam", "I-Beam")
INCH_LENGTHS: dict[str, tuple[int, ...]] = {
    "Torpedo": (9, 12),
    "Box Beam": (24, 48, 72),
    "I-Beam": (24, 48),
}
METRIC_LENGTHS_MM: dict[str, tuple[int, ...]] = {
    "Torpedo": (230, 300),
    "Box Beam": (600, 1200, 1800),
    "I-Beam": (600, 1200),
}

#: The frame materials, and whether the frame's working edge is magnetic.
MATERIALS: tuple[str, ...] = ("Aluminum", "Magnesium", "Plastic")
FEATURES: tuple[str, ...] = ("Magnetic Edge", "Non-Magnetic")
SYSTEMS: tuple[str, ...] = ("in", "mm")

#: The six main colors (gen#275), and the swatch the drawing fills the frame with.
COLORS: dict[str, str] = {
    "Red": "#c8322b",
    "Blue": "#2f6db5",
    "Green": "#3c8d4f",
    "Yellow": "#f2c230",
    "Black": "#2a2a2e",
    "White": "#ffffff",
}

#: Every line a brand can offer, without its color: a shape, a material and a feature in a
#: unit system. All 36, in an order whose first six lines already hold every shape,
#: material, feature and system.
COMBOS: tuple[tuple[str, str, str, str], ...] = tuple(
    (SHAPES[i % 3], MATERIALS[(i + i // 3) % 3], FEATURES[i % 2], SYSTEMS[(i + i // 2) % 2])
    for i in range(36)
)

#: Text-match decoys (gen#294): the lines at these positions of every period name another
#: layout tool before the item.
DECOY_PERIOD = 6
DECOY_SLOTS: tuple[int, ...] = (1, 4)
#: The tools a decoy title names: none is a level.
DECOY_NOUNS: tuple[str, ...] = ("Square", "Ruler", "Protractor", "Chalk Line")


def decoy_item(gen: Any, type_key: str) -> str:
    """The item as the title says it: plain, or with another tool's noun before it."""
    if gen._rotate(f"decoy:{type_key}", DECOY_PERIOD) not in DECOY_SLOTS:
        return ITEM
    noun = DECOY_NOUNS[gen._rotate(f"decoy_noun:{type_key}", len(DECOY_NOUNS))]
    return f"{noun} Series {ITEM}"


def frame_color(n: int) -> str:
    """The frame color of the ``n``-th line. The combination rotation turns every
    ``len(COMBOS)`` lines, a multiple of the six colors, so a color rotating beside it would
    pair each combination with one color only. This one steps one further at every turn."""
    return tuple(COLORS)[(n + n // len(COMBOS)) % len(COLORS)]


def stocked_inches(shape: str, system: str) -> tuple[float, ...]:
    """The lengths ``shape`` is stocked in, in ``system``, each carried in inches."""
    if system == "mm":
        return tuple(mm / MM_PER_INCH for mm in METRIC_LENGTHS_MM[shape])
    return tuple(float(i) for i in INCH_LENGTHS[shape])


def _spec(name: str, scope: str, presence: float = 1.0, kind: str = "keyword") -> AttrSpec:
    return AttrSpec(name=name, scope=scope, presence=presence, kind=kind)


VOCAB = (
    _spec("Color", "line"),
    _spec("Shape", "line"),
    _spec("Material", "line"),
    _spec("Features", "line"),
    _spec("Length", "sku", kind="length"),
)


def _make(gen: Any, type_key: str, category: tuple[str, ...]) -> Any:
    # Imported here: generate.py imports the type tables, which discover this module.
    from synthetic_ecommerce_data.core import brands
    from synthetic_ecommerce_data.core.model import keyword_attribute
    from synthetic_ecommerce_data.domains.industrial.generate import ChildDraft, LineDraft

    rng = gen.rng
    shape, material, feature, system = COMBOS[gen._rotate(f"combo:{type_key}", len(COMBOS))]
    color = frame_color(gen._rotate(f"color:{type_key}", len(COMBOS) * len(COLORS)))
    brand = brands.pick_brand(rng, type_key, gen._exhausted)
    draft = LineDraft(
        item=decoy_item(gen, type_key),
        brand=brand,
        series=f"LV{rng.randint(100, 999)}",
        category=category,
        provenance=PROVENANCE,
    )
    draft.line_attrs = [
        keyword_attribute("Color", color),
        keyword_attribute("Shape", shape),
        keyword_attribute("Material", material),
        keyword_attribute("Features", feature),
    ]
    draft.descriptors = [("Shape", shape), ("Color", color)]
    pool = list(stocked_inches(shape, system))
    count = min(gen._variant_count(), len(pool))
    style = gen._style(system)
    for length_in in gen._offered_run(f"lengths:{shape}:{system}", pool, count):
        child = ChildDraft(system=system)
        child.primary = gen._length("Length", length_in, style)
        child.attrs = [child.primary]
        draft.children.append(child)
    return draft


#: GENERATED, NOT MEASURED: about 20 USD for a 24 in standard-tier level, and the length to
#: the 0.75 power (a 9 in torpedo near 10 USD, a 72 in box beam near 45).
PRICE = PriceModel(20.0, 24.0, 0.75, 0.3, 0.1, measured=False)


def _inches(record: dict[str, str], name: str) -> float | None:
    """``name`` in inches; ``None`` when unreadable."""
    try:
        return parse_length(str(record.get(name, "")).strip()).inches
    except DimensionParseError:
        return None


#: The frame's drawn height, in inches, by shape.
FRAME_HEIGHT: dict[str, float] = {"Torpedo": 0.55, "Box Beam": 0.7, "I-Beam": 0.6}


def figure(record: dict[str, str]) -> Drawn:
    """The level from its face: a frame drawn longer for a longer level, its height and
    outline by shape (a torpedo tapers to its ends, an I-beam shows its two flanges), the
    vials set in it (one at the middle, one at each end), and a dark strip along the bottom
    edge when it is magnetic. The frame is filled with the record's color."""
    length = _inches(record, "Length")
    source = "record" if length else "partial"
    length = length or 24.0
    shape = str(record.get("Shape", "Box Beam"))
    long = 2.0 + 0.06 * length
    high = FRAME_HEIGHT.get(shape, 0.7)
    fig = Figure(size_in=long)
    fill = COLORS.get(str(record.get("Color", "")), "#f2c230")
    if shape == "Torpedo":
        taper = 0.25 * high
        fig.poly(
            [
                (0.0, taper),
                (0.3, 0.0),
                (long - 0.3, 0.0),
                (long, taper),
                (long, high - taper),
                (long - 0.3, high),
                (0.3, high),
                (0.0, high - taper),
            ],
            "part",
            fill,
        )
    else:
        fig.rect(0.0, 0.0, long, high, "part", fill)
        if shape == "I-Beam":
            flange = 0.12 * high
            fig.rect(0.0, 0.0, long, flange, "dark")
            fig.rect(0.0, high - flange, long, high, "dark")
    vial = 0.22 * high
    for centre in (0.5 * long, 0.15 * long, 0.85 * long):
        fig.rect(
            centre - 1.6 * vial, 0.5 * high - vial, centre + 1.6 * vial, 0.5 * high + vial, "plain"
        )
        fig.disc((centre, 0.5 * high), 0.6 * vial, "dark")
    if record.get("Features") == "Magnetic Edge":
        fig.rect(0.1 * long, -0.08, 0.9 * long, 0.0, "dark")
    return Drawn(fig, source)


SPEC = TypeSpec(
    KEY,
    label=ITEM,
    category=CATEGORY,
    standards_family="hand_tool",
    vocab=VOCAB,
    figure=figure,
    extent=(6.4, 0.9),
    make=_make,
    share=0.0065,
    price=PRICE,
    claims=None,
    may_claim=frozenset(),
    key_attributes=("Length",),
    compat=False,
    use_lines=(
        "Checks that a shelf, a picture or a door frame sits level or plumb.",
        "Lays out a straight line along a wall before drilling.",
    ),
)
