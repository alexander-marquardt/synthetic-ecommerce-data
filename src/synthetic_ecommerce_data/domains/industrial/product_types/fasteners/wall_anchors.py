"""Wall anchors: home hardware for the R&I catalogue (#958, slice 3).

A wall anchor is the plastic sleeve a homeowner sets in drywall, plaster or brick so a screw
holds there: to hang a shelf, a mirror, a curtain rod or a towel bar. A hardware listing sells
it by its length and names its style, its plastic and its color.

**Lengths.** The lengths a style is stocked in are the ones hardware listings carry
(:data:`INCH_LENGTHS`): a ribbed anchor runs 3/4" to 1-1/2", a self-drilling drywall anchor
1" to 1-3/4", a winged toggle 1-1/4" to 2-1/2", and a conical anchor 3/4" to 2". No standard
fixes them, so no line claims one and the provenance says so (:data:`PROVENANCE`). A length is
published in inches, the way the catalogue's other ``Length`` values are, so the facet ranges
across them.

**Lines.** A line is one brand's anchors of one style, one plastic and one color. Its SKUs are
a run of lengths. The (style, material) combinations are rotated, so every one of them is
built, and so are the colors.

**Colors.** Plastic anchors are sold color-coded, and this one comes in each of the six main
colors (gen#275): red, blue, green, yellow, black and white (:data:`COLORS`). The color
rotation steps one further at each full turn of the combinations, so every combination is
built in more than one color (:func:`anchor_color`).

**Decoys.** Every type carries text-match decoys (gen#294). In every :data:`DECOY_PERIOD`
lines, :data:`DECOY_SLOTS` of them name a room before the item ("Nursery Series Wall
Anchor"). A search for that word then finds a wall anchor, which a category policy can
remove. The attributes stay true, so no check exempts them.

**Seed decoy.** ``nylon_wall_anchors`` (a "Screw Anchor" under ``Plastic Wall Anchors``)
stays what it is, a two-SKU decoy for the industrial seed query "screws" (#462): this type is
the homeowner depth, filed in its own leaf beside it.

**Price.** GENERATED, not measured: the price census has no wall anchors. A pack costs about
its length to the 0.6 power, anchored at 5 USD for a 1" standard-tier anchor.
"""

from __future__ import annotations

from typing import Any

from synthetic_ecommerce_data.core.dimensions import DimensionParseError, parse_length
from synthetic_ecommerce_data.core.drawing.model import Figure
from synthetic_ecommerce_data.core.price import PriceModel
from synthetic_ecommerce_data.core.typespec import TypeSpec
from synthetic_ecommerce_data.domains.industrial.drawing.figures import Drawn
from synthetic_ecommerce_data.domains.industrial.newtypes import NO_STANDARD, feed_style
from synthetic_ecommerce_data.domains.industrial.vocab import AttrSpec

KEY = "wall_anchors"
ITEM = "Wall Anchor"
CATEGORY: tuple[str, ...] = ("Fasteners", "Anchors", "Wall Anchors")

#: What every record says about where its length came from.
PROVENANCE = f"Length is a conventional stocked size; {NO_STANDARD}"

#: The styles, and the lengths each is stocked in, in inches.
INCH_LENGTHS: dict[str, tuple[float, ...]] = {
    "Ribbed": (0.75, 0.875, 1.0, 1.25, 1.5),
    "Self-Drilling": (1.0, 1.25, 1.5, 1.75),
    "Winged Toggle": (1.25, 1.5, 2.0, 2.5),
    "Conical": (0.75, 1.0, 1.25, 1.5, 2.0),
}
STYLES: tuple[str, ...] = tuple(INCH_LENGTHS)

#: The plastics an anchor is molded from.
MATERIALS: tuple[str, ...] = ("Nylon", "Polyolefin", "ABS Plastic")

#: The six main colors (gen#275), and the swatch the drawing fills the anchor with.
COLORS: dict[str, str] = {
    "Red": "#c8322b",
    "Blue": "#2f6db5",
    "Green": "#3c8d4f",
    "Yellow": "#f2c230",
    "Black": "#2a2a2e",
    "White": "#ffffff",
}

#: Every line a brand can offer, without its color: a style and a material. All 12, in an
#: order whose first four lines already hold every style and material, so a small build
#: offers each of them too.
COMBOS: tuple[tuple[str, str], ...] = tuple(
    (STYLES[i % 4], MATERIALS[(i + i // 4) % 3]) for i in range(12)
)

#: Text-match decoys (gen#294): the lines at these positions of every period name a room
#: before the item.
DECOY_PERIOD = 6
DECOY_SLOTS: tuple[int, ...] = (1, 4)
#: The rooms a decoy title names: none is an anchor.
DECOY_NOUNS: tuple[str, ...] = ("Nursery", "Hallway", "Gallery", "Studio")


def decoy_item(gen: Any, type_key: str) -> str:
    """The item as the title says it: plain, or with a room's noun before it."""
    if gen._rotate(f"decoy:{type_key}", DECOY_PERIOD) not in DECOY_SLOTS:
        return ITEM
    noun = DECOY_NOUNS[gen._rotate(f"decoy_noun:{type_key}", len(DECOY_NOUNS))]
    return f"{noun} Series {ITEM}"


def anchor_color(n: int) -> str:
    """The color of the ``n``-th line. The combination rotation turns every ``len(COMBOS)``
    lines, a multiple of the six colors, so a color rotating beside it would pair each
    combination with one color only. This one steps one further at every turn."""
    return tuple(COLORS)[(n + n // len(COMBOS)) % len(COLORS)]


def _spec(name: str, scope: str, presence: float = 1.0, kind: str = "keyword") -> AttrSpec:
    return AttrSpec(name=name, scope=scope, presence=presence, kind=kind)


VOCAB = (
    _spec("Color", "line"),
    _spec("Style", "line"),
    _spec("Material", "line"),
    _spec("Length", "sku", kind="length"),
)


def _make(gen: Any, type_key: str, category: tuple[str, ...]) -> Any:
    # Imported here: generate.py imports the type tables, which discover this module.
    from synthetic_ecommerce_data.core import brands
    from synthetic_ecommerce_data.core.model import keyword_attribute, length_attribute
    from synthetic_ecommerce_data.domains.industrial.generate import BRANDS, ChildDraft, LineDraft

    rng = gen.rng
    style, material = COMBOS[gen._rotate(f"combo:{type_key}", len(COMBOS))]
    color = anchor_color(gen._rotate(f"color:{type_key}", len(COMBOS) * len(COLORS)))
    brand = brands.pick_brand(rng, type_key, gen._exhausted)
    draft = LineDraft(
        item=decoy_item(gen, type_key),
        brand=brand,
        series=f"WA{rng.randint(100, 999)}",
        category=category,
        provenance=PROVENANCE,
    )
    draft.line_attrs = [
        keyword_attribute("Color", color),
        keyword_attribute("Style", style),
        keyword_attribute("Material", material),
    ]
    draft.descriptors = [("Style", style), ("Color", color)]
    published = feed_style(brand, "in", BRANDS)
    pool = list(INCH_LENGTHS[style])
    count = min(gen._variant_count(), len(pool))
    for inches in gen._offered_run(f"lengths:{style}", pool, count):
        child = ChildDraft(system="in")
        child.primary = length_attribute("Length", gen._publish(inches, published))
        child.attrs = [child.primary]
        draft.children.append(child)
    return draft


#: GENERATED, NOT MEASURED: about 5 USD for a pack of 1" standard-tier anchors, and the length
#: to the 0.6 power.
PRICE = PriceModel(5.0, 1.0, 0.6, 0.3, 0.1, measured=False)


def _length(record: dict[str, str]) -> float | None:
    """The record's length in inches; ``None`` when unreadable."""
    try:
        return parse_length(str(record.get("Length", ""))).inches
    except DimensionParseError:
        return None


def figure(record: dict[str, str]) -> Drawn:
    """The anchor side on, its collar at the left and its tip at the right, as long as its
    length and filled with the record's color. A ribbed anchor is a straight sleeve with ribs
    across it and a blunt tip; a self-drilling anchor is a coarse-threaded body that tapers to
    a drill point; a winged toggle is a slim sleeve whose two wings fold back from its tip; and
    a conical anchor is a sleeve that tapers from the collar to its tip, split along its
    length."""
    inches = _length(record)
    source = "record" if inches else "partial"
    a = inches or 1.0
    fig = Figure(size_in=a)
    fill = COLORS.get(str(record.get("Color", "")), "#2a2a2e")
    style = str(record.get("Style", ""))
    mid = 0.25 * a
    c = 0.08 * a  # the collar's thickness
    fig.rect(0.0, 0.0, c, 2 * mid, "part", fill)
    if style == "Ribbed":
        h = 0.1 * a
        fig.rect(c, mid - h, a - h, mid + h, "part", fill)
        fig.poly([(a - h, mid - h), (a, mid), (a - h, mid + h)], "part", fill)
        step = (a - c - h) / 6
        fig.lines([((c + step * i, mid - h), (c + step * i, mid + h)) for i in range(1, 6)])
        return Drawn(fig, source)
    if style == "Self-Drilling":
        h = 0.16 * a
        body = [
            (c, mid - h),
            (0.7 * a, mid - 0.6 * h),
            (a, mid),
            (0.7 * a, mid + 0.6 * h),
            (c, mid + h),
        ]
        fig.poly(body, "part", fill)
        step = (0.7 * a - c) / 5
        fig.lines([((c + step * i, mid - h), (c + step * (i + 1), mid + h)) for i in range(4)])
        return Drawn(fig, source)
    if style == "Winged Toggle":
        h = 0.06 * a
        fig.rect(c, mid - h, a, mid + h, "part", fill)
        for sign in (-1.0, 1.0):
            fig.poly(
                [
                    (a, mid + sign * h),
                    (0.45 * a, mid + sign * 0.24 * a),
                    (0.42 * a, mid + sign * 0.2 * a),
                    (0.9 * a, mid + sign * h),
                ],
                "part",
                fill,
            )
        return Drawn(fig, source)
    h0, h1 = 0.14 * a, 0.06 * a
    fig.poly([(c, mid - h0), (a, mid - h1), (a, mid + h1), (c, mid + h0)], "part", fill)
    fig.lines([((0.4 * a, mid), (a, mid))])
    return Drawn(fig, source)


SPEC = TypeSpec(
    KEY,
    label=ITEM,
    category=CATEGORY,
    standards_family="fastener",
    vocab=VOCAB,
    figure=figure,
    extent=(2.6, 1.35),
    make=_make,
    share=0.0055,
    price=PRICE,
    claims=None,
    may_claim=frozenset(),
    key_attributes=("Length",),
    compat=False,
    use_lines=(
        "Holds a screw in drywall, plaster or brick, so a shelf, a mirror or a towel bar hangs "
        "where no stud is.",
        "Push or drive the anchor into the wall and turn a screw into it; the anchor spreads "
        "behind or around the screw and grips the wall.",
    ),
)
