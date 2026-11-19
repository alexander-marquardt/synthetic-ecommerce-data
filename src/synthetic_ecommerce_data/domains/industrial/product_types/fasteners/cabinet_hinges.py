"""Cabinet hinges: home hardware for the general-retail catalogue (#958, slice 2).

A cabinet hinge is the pivot a kitchen cabinet, cupboard or wardrobe door swings on. A
hardware listing sells it by its length and names its style, its metal and its color.

**Lengths.** The lengths a style is stocked in are the ones hardware listings carry
(:data:`INCH_LENGTHS`): a butt hinge runs 1-1/2" to 3-1/2", a flush hinge 2" to 3". No
standard fixes them, so no line claims one and the provenance says so (:data:`PROVENANCE`). A
length is published in inches, the way the catalogue's other ``Length`` values are, so the
facet ranges across them.

**Lines.** A line is one brand's hinges of one style, one metal and one color. Its SKUs are a
run of lengths. The (style, material) combinations are rotated, so every one of them is
built, and so are the colors.

**Colors.** The hinge comes in each of the six main colors (gen#275): red, blue, green,
yellow, black and white (:data:`COLORS`), a painted or powder-coated finish over the metal.
The color rotation steps one further at each full turn of the combinations, so every
combination is built in more than one color (:func:`hinge_color`).

**Decoys.** Every type carries text-match decoys (gen#294). In every :data:`DECOY_PERIOD`
lines, :data:`DECOY_SLOTS` of them name a piece of furniture a hinge goes on before the item
("Wardrobe Series Cabinet Hinge"). A search for that word then finds a cabinet hinge, which a
category policy can remove. The attributes stay true, so no check exempts them.

**Price.** GENERATED, not measured: the price census has no cabinet hinges. A hinge costs
about its length to the 0.8 power, anchored at 4 USD for a 2-1/2" standard-tier hinge.
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

KEY = "cabinet_hinges"
ITEM = "Cabinet Hinge"
CATEGORY: tuple[str, ...] = ("Fasteners", "Cabinet Hardware", "Cabinet Hinges")

#: What every record says about where its length came from.
PROVENANCE = f"Length is a conventional stocked size; {NO_STANDARD}"

#: The styles, and the lengths each is stocked in, in inches.
INCH_LENGTHS: dict[str, tuple[float, ...]] = {
    "Butt": (1.5, 2.0, 2.5, 3.0, 3.5),
    "Flush": (2.0, 2.5, 3.0),
    "Surface Mount": (2.0, 2.5, 3.0, 3.5),
    "Overlay": (2.0, 2.25, 2.5, 2.75),
}
STYLES: tuple[str, ...] = tuple(INCH_LENGTHS)

#: The metals a hinge is made of.
MATERIALS: tuple[str, ...] = ("Steel", "Brass", "Stainless Steel")

#: The six main colors (gen#275), and the swatch the drawing fills the leaves with.
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

#: Text-match decoys (gen#294): the lines at these positions of every period name the
#: furniture a hinge goes on before the item.
DECOY_PERIOD = 6
DECOY_SLOTS: tuple[int, ...] = (1, 4)
#: The things a decoy title names: none is a cabinet hinge.
DECOY_NOUNS: tuple[str, ...] = ("Cupboard", "Wardrobe", "Armoire", "Hutch")


def decoy_item(gen: Any, type_key: str) -> str:
    """The item as the title says it: plain, or with a piece of furniture's noun before it."""
    if gen._rotate(f"decoy:{type_key}", DECOY_PERIOD) not in DECOY_SLOTS:
        return ITEM
    noun = DECOY_NOUNS[gen._rotate(f"decoy_noun:{type_key}", len(DECOY_NOUNS))]
    return f"{noun} Series {ITEM}"


def hinge_color(n: int) -> str:
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
    color = hinge_color(gen._rotate(f"color:{type_key}", len(COMBOS) * len(COLORS)))
    brand = brands.pick_brand(rng, type_key, gen._exhausted)
    draft = LineDraft(
        item=decoy_item(gen, type_key),
        brand=brand,
        series=f"CH{rng.randint(100, 999)}",
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


#: GENERATED, NOT MEASURED: about 4 USD for a 2-1/2" standard-tier hinge, and the length to
#: the 0.8 power.
PRICE = PriceModel(4.0, 2.5, 0.8, 0.3, 0.1, measured=False)


def _length(record: dict[str, str]) -> float | None:
    """The record's length in inches; ``None`` when unreadable."""
    try:
        return parse_length(str(record.get("Length", ""))).inches
    except DimensionParseError:
        return None


def figure(record: dict[str, str]) -> Drawn:
    """The hinge face on and opened flat, filled with the record's color and as tall as its
    length: two leaves either side of the knuckle. A butt hinge has two equal leaves, a flush
    hinge a narrower leaf that nests in the other, a surface-mount hinge two flared leaves, and
    an overlay hinge a cranked leaf that steps out to lap the cabinet face."""
    inches = _length(record)
    source = "record" if inches else "partial"
    h = inches or 2.5
    fig = Figure(size_in=h)
    fill = COLORS.get(str(record.get("Color", "")), "#2a2a2e")
    style = str(record.get("Style", ""))
    k0, k1 = 0.42 * h, 0.5 * h
    if style == "Surface Mount":
        fig.poly([(k0, 0.12 * h), (0.0, 0.0), (0.0, h), (k0, 0.88 * h)], "part", fill)
        fig.poly([(k1, 0.12 * h), (0.92 * h, 0.0), (0.92 * h, h), (k1, 0.88 * h)], "part", fill)
    elif style == "Flush":
        fig.rect(0.0, 0.0, k0, h, "part", fill)
        fig.rect(k1, 0.12 * h, 0.8 * h, 0.88 * h, "part", fill)
    elif style == "Overlay":
        fig.rect(0.0, 0.0, k0, h, "part", fill)
        fig.poly(
            [
                (k1, 0.0),
                (0.62 * h, 0.0),
                (0.72 * h, 0.1 * h),
                (0.92 * h, 0.1 * h),
                (0.92 * h, 0.9 * h),
                (0.72 * h, 0.9 * h),
                (0.62 * h, h),
                (k1, h),
            ],
            "part",
            fill,
        )
    else:
        fig.rect(0.0, 0.0, k0, h, "part", fill)
        fig.rect(k1, 0.0, 0.92 * h, h, "part", fill)
    fig.rect(k0, 0.0, k1, h, "dark")
    holes = [(0.2 * h, y * h) for y in (0.22, 0.5, 0.78)]
    holes += [(0.72 * h, y * h) for y in (0.3, 0.7)]
    fig.discs(holes, 0.04 * h, "dark")
    return Drawn(fig, source)


SPEC = TypeSpec(
    KEY,
    label=ITEM,
    category=CATEGORY,
    standards_family="fastener",
    vocab=VOCAB,
    figure=figure,
    extent=(4.0, 4.0),
    make=_make,
    share=0.0055,
    price=PRICE,
    claims=None,
    may_claim=frozenset(),
    key_attributes=("Length",),
    compat=False,
    use_lines=(
        "Hangs a kitchen cabinet, cupboard or wardrobe door so it swings open and shut.",
        "Fastens to the door and the cabinet frame with wood screws through its leaves.",
    ),
)
