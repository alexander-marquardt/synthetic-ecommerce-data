"""Shelf brackets: home hardware for the general-retail catalogue (#958, slice 3).

A shelf bracket is the arm a shelf rests on, screwed to a wall or a stud. A hardware listing
sells it by the length of its arm and names its style, its metal and its color.

**Lengths.** The arm lengths a style is stocked in are the ones hardware listings carry
(:data:`INCH_LENGTHS`): an L-shaped bracket runs 4" to 12", a heavy-duty one 8" to 16", a
floating-shelf bracket's rods 4" to 8". No standard fixes them, so no line claims one and the
provenance says so (:data:`PROVENANCE`). A length is published in inches, the way the
catalogue's other ``Length`` values are, so the facet ranges across them.

**Lines.** A line is one brand's brackets of one style, one metal and one color. Its SKUs are
a run of lengths. The (style, material) combinations are rotated, so every one of them is
built, and so are the colors.

**Colors.** The bracket comes in each of the six main colors (gen#275): red, blue, green,
yellow, black and white (:data:`COLORS`), a painted or powder-coated finish over the metal.
The color rotation steps one further at each full turn of the combinations, so every
combination is built in more than one color (:func:`bracket_color`).

**Decoys.** Every type carries text-match decoys (gen#294). In every :data:`DECOY_PERIOD`
lines, :data:`DECOY_SLOTS` of them name a place a shelf goes before the item ("Garage Series
Shelf Bracket"). A search for that word then finds a shelf bracket, which a category policy
can remove. The attributes stay true, so no check exempts them.

**Price.** GENERATED, not measured: the price census has no shelf brackets. A bracket costs
about its length to the 0.9 power, anchored at 5 USD for an 8" standard-tier bracket.
"""

from __future__ import annotations

from typing import Any

from synthetic_ecommerce_data.core.dimensions import DimensionParseError, parse_length
from synthetic_ecommerce_data.core.drawing.model import Figure, arc
from synthetic_ecommerce_data.core.price import PriceModel
from synthetic_ecommerce_data.core.typespec import TypeSpec
from synthetic_ecommerce_data.domains.industrial.drawing.figures import Drawn
from synthetic_ecommerce_data.domains.industrial.newtypes import NO_STANDARD, feed_style
from synthetic_ecommerce_data.domains.industrial.vocab import AttrSpec

KEY = "shelf_brackets"
ITEM = "Shelf Bracket"
CATEGORY: tuple[str, ...] = ("Fasteners", "Shelving Hardware", "Shelf Brackets")

#: What every record says about where its length came from.
PROVENANCE = f"Length is a conventional stocked size; {NO_STANDARD}"

#: The styles, and the arm lengths each is stocked in, in inches.
INCH_LENGTHS: dict[str, tuple[float, ...]] = {
    "L-Shaped": (4.0, 5.0, 6.0, 8.0, 10.0, 12.0),
    "Heavy Duty": (8.0, 10.0, 12.0, 14.0, 16.0),
    "Decorative": (6.0, 8.0, 10.0, 12.0),
    "Floating": (4.0, 5.0, 6.0, 8.0),
}
STYLES: tuple[str, ...] = tuple(INCH_LENGTHS)

#: The metals a bracket is made of.
MATERIALS: tuple[str, ...] = ("Steel", "Aluminum", "Cast Iron")

#: The six main colors (gen#275), and the swatch the drawing fills the bracket with.
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

#: Text-match decoys (gen#294): the lines at these positions of every period name a place a
#: shelf goes before the item.
DECOY_PERIOD = 6
DECOY_SLOTS: tuple[int, ...] = (2, 5)
#: The things a decoy title names: none is a shelf bracket.
DECOY_NOUNS: tuple[str, ...] = ("Pantry", "Garage", "Closet", "Bookcase")


def decoy_item(gen: Any, type_key: str) -> str:
    """The item as the title says it: plain, or with a place's noun before it."""
    if gen._rotate(f"decoy:{type_key}", DECOY_PERIOD) not in DECOY_SLOTS:
        return ITEM
    noun = DECOY_NOUNS[gen._rotate(f"decoy_noun:{type_key}", len(DECOY_NOUNS))]
    return f"{noun} Series {ITEM}"


def bracket_color(n: int) -> str:
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
    color = bracket_color(gen._rotate(f"color:{type_key}", len(COMBOS) * len(COLORS)))
    brand = brands.pick_brand(rng, type_key, gen._exhausted)
    draft = LineDraft(
        item=decoy_item(gen, type_key),
        brand=brand,
        series=f"SB{rng.randint(100, 999)}",
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


#: GENERATED, NOT MEASURED: about 5 USD for an 8" standard-tier bracket, and the length to
#: the 0.9 power.
PRICE = PriceModel(5.0, 8.0, 0.9, 0.3, 0.1, measured=False)


def _length(record: dict[str, str]) -> float | None:
    """The record's length in inches; ``None`` when unreadable."""
    try:
        return parse_length(str(record.get("Length", ""))).inches
    except DimensionParseError:
        return None


def figure(record: dict[str, str]) -> Drawn:
    """The bracket side on, filled with the record's color, its arm as long as its length:
    the shelf rests on the arm along the top, and the leg runs down the wall on the left. An
    L-shaped bracket is the bare arm and leg, a heavy-duty one adds a triangular gusset between
    them, a decorative one a curved brace, and a floating-shelf bracket is a wall plate with
    two rods that slide into the shelf."""
    inches = _length(record)
    source = "record" if inches else "partial"
    a = inches or 8.0
    fig = Figure(size_in=a)
    fill = COLORS.get(str(record.get("Color", "")), "#2a2a2e")
    style = str(record.get("Style", ""))
    leg = 0.75 * a
    t = 0.07 * a
    if style == "Floating":
        fig.rect(0.0, 0.0, 0.12 * a, 0.4 * a, "part", fill)
        for y in (0.08 * a, 0.28 * a):
            fig.rect(0.12 * a, y, a, y + 0.04 * a, "part", fill)
        for y in (0.04 * a, 0.36 * a):  # one disc each: a grouped run nests a <g>
            fig.disc((0.06 * a, y), 0.025 * a, "dark")
        return Drawn(fig, source)
    if style == "Heavy Duty":
        t = 0.1 * a
        fig.poly([(t, t), (0.65 * a, t), (t, 0.65 * leg)], "part", fill)
    elif style == "Decorative":
        r = 0.55 * leg
        centre = (t + r, t + r)
        outer = arc(centre, r, 180.0, 270.0)
        inner = arc(centre, r - 0.06 * a, 270.0, 180.0)
        fig.poly(outer + inner, "part", fill)
    fig.rect(0.0, 0.0, a, t, "part", fill)
    fig.rect(0.0, 0.0, t, leg, "part", fill)
    for y in (0.3 * leg, 0.85 * leg):
        fig.disc((0.5 * t, y), 0.3 * t, "dark")
    return Drawn(fig, source)


SPEC = TypeSpec(
    KEY,
    label=ITEM,
    category=CATEGORY,
    standards_family="fastener",
    vocab=VOCAB,
    figure=figure,
    extent=(16.1, 12.1),
    make=_make,
    share=0.0055,
    price=PRICE,
    claims=None,
    may_claim=frozenset(),
    key_attributes=("Length",),
    compat=False,
    use_lines=(
        "Holds a wall shelf in a kitchen, garage, closet or living room.",
        "Screws to a wall stud and carries the shelf on its arm.",
    ),
)
