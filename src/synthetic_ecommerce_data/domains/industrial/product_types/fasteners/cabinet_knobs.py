"""Cabinet knobs: home hardware for the R&I catalogue (#958, slice 3).

A cabinet knob is the single-screw handle on a kitchen cabinet door, a drawer or a dresser.
A hardware listing sells it by its diameter and names its style, its metal and its color.

**Diameters.** The diameters a style is stocked in are the ones hardware listings carry
(:data:`INCH_DIAMETERS`): a square knob runs 3/4" to 1-1/2", a mushroom knob up to 1-3/4". No
standard fixes them, so no line claims one and the provenance says so (:data:`PROVENANCE`). A
diameter is published as a length in inches, the way the catalogue's other ``Diameter`` values
are, so the facet ranges across them.

**Lines.** A line is one brand's knobs of one style, one metal and one color. Its SKUs are a
run of diameters. The (style, material) combinations are rotated, so every one of them is
built, and so are the colors.

**Colors.** The knob comes in each of the six main colors (gen#275): red, blue, green,
yellow, black and white (:data:`COLORS`), a painted or powder-coated finish over the metal.
The color rotation steps one further at each full turn of the combinations, so every
combination is built in more than one color (:func:`knob_color`).

**Decoys.** Every type carries text-match decoys (gen#294). In every :data:`DECOY_PERIOD`
lines, :data:`DECOY_SLOTS` of them name a piece of furniture a knob goes on before the item
("Dresser Series Cabinet Knob"). A search for that word then finds a cabinet knob, which a
category policy can remove. The attributes stay true, so no check exempts them.

**Price.** GENERATED, not measured: the price census has no cabinet knobs. A knob costs about
its diameter to the 0.8 power, anchored at 4.5 USD for a 1-1/4" standard-tier knob.
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

KEY = "cabinet_knobs"
ITEM = "Cabinet Knob"
CATEGORY: tuple[str, ...] = ("Fasteners", "Cabinet Hardware", "Cabinet Knobs")

#: What every record says about where its diameter came from.
PROVENANCE = f"Diameter is a conventional stocked size; {NO_STANDARD}"

#: The styles, and the diameters each is stocked in, in inches.
INCH_DIAMETERS: dict[str, tuple[float, ...]] = {
    "Round": (0.75, 1.0, 1.125, 1.25, 1.375, 1.5),
    "Mushroom": (1.0, 1.125, 1.25, 1.375, 1.5, 1.75),
    "Square": (0.75, 1.0, 1.125, 1.25, 1.5),
    "Drop Ring": (1.0, 1.25, 1.5, 1.75),
}
STYLES: tuple[str, ...] = tuple(INCH_DIAMETERS)

#: The metals a knob is made of.
MATERIALS: tuple[str, ...] = ("Brass", "Stainless Steel", "Aluminum")

#: The six main colors (gen#275), and the swatch the drawing fills the knob with.
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
#: furniture a knob goes on before the item.
DECOY_PERIOD = 6
DECOY_SLOTS: tuple[int, ...] = (2, 5)
#: The things a decoy title names: none is a cabinet knob.
DECOY_NOUNS: tuple[str, ...] = ("Dresser", "Drawer", "Vanity", "Pantry")


def decoy_item(gen: Any, type_key: str) -> str:
    """The item as the title says it: plain, or with a piece of furniture's noun before it."""
    if gen._rotate(f"decoy:{type_key}", DECOY_PERIOD) not in DECOY_SLOTS:
        return ITEM
    noun = DECOY_NOUNS[gen._rotate(f"decoy_noun:{type_key}", len(DECOY_NOUNS))]
    return f"{noun} Series {ITEM}"


def knob_color(n: int) -> str:
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
    _spec("Diameter", "sku", kind="length"),
)


def _make(gen: Any, type_key: str, category: tuple[str, ...]) -> Any:
    # Imported here: generate.py imports the type tables, which discover this module.
    from synthetic_ecommerce_data.core import brands
    from synthetic_ecommerce_data.core.model import keyword_attribute, length_attribute
    from synthetic_ecommerce_data.domains.industrial.generate import BRANDS, ChildDraft, LineDraft

    rng = gen.rng
    style, material = COMBOS[gen._rotate(f"combo:{type_key}", len(COMBOS))]
    color = knob_color(gen._rotate(f"color:{type_key}", len(COMBOS) * len(COLORS)))
    brand = brands.pick_brand(rng, type_key, gen._exhausted)
    draft = LineDraft(
        item=decoy_item(gen, type_key),
        brand=brand,
        series=f"CK{rng.randint(100, 999)}",
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
    pool = list(INCH_DIAMETERS[style])
    count = min(gen._variant_count(), len(pool))
    for inches in gen._offered_run(f"diameters:{style}", pool, count):
        child = ChildDraft(system="in")
        child.primary = length_attribute("Diameter", gen._publish(inches, published))
        child.attrs = [child.primary]
        draft.children.append(child)
    return draft


#: GENERATED, NOT MEASURED: about 4.5 USD for a 1-1/4" standard-tier knob, and the diameter to
#: the 0.8 power.
PRICE = PriceModel(4.5, 1.25, 0.8, 0.3, 0.1, measured=False)


def _diameter(record: dict[str, str]) -> float | None:
    """The record's diameter in inches; ``None`` when unreadable."""
    try:
        return parse_length(str(record.get("Diameter", ""))).inches
    except DimensionParseError:
        return None


def figure(record: dict[str, str]) -> Drawn:
    """The knob from the side, filled with the record's color and sized to its diameter: a
    stem off the cabinet face under a ball (round), a dome (mushroom), a block (square) or a
    ring hanging from a small boss (drop ring)."""
    inches = _diameter(record)
    source = "record" if inches else "partial"
    d = inches or 1.25
    side = 1.5 * d
    fig = Figure(size_in=side)
    fill = COLORS.get(str(record.get("Color", "")), "#2a2a2e")
    style = str(record.get("Style", ""))
    left, right, mid = 0.25 * d, 1.25 * d, 0.75 * d
    fig.rect(0.0, 0.05 * d, 0.06 * d, 1.45 * d, "dark")
    if style == "Drop Ring":
        fig.rect(0.06 * d, 0.65 * d, 0.3 * d, 0.85 * d, "part", fill)
        fig.disc((0.3 * d + 0.5 * d, 0.75 * d), 0.5 * d, "part", fill)
        fig.disc((0.3 * d + 0.5 * d, 0.75 * d), 0.38 * d, "plain")
        return Drawn(fig, source)
    fig.rect(0.06 * d, 0.62 * d, left + 0.1 * d, 0.88 * d, "part", fill)
    if style == "Mushroom":
        fig.poly(
            [
                (left + 0.1 * d, 0.6 * d),
                (left + 0.45 * d, 0.25 * d),
                (right, 0.25 * d),
                (right, 1.25 * d),
                (left + 0.45 * d, 1.25 * d),
                (left + 0.1 * d, 0.9 * d),
            ],
            "part",
            fill,
        )
    elif style == "Square":
        fig.rect(left + 0.1 * d, 0.25 * d, right, 1.25 * d, "part", fill)
    else:
        fig.disc((mid + 0.05 * d, 0.75 * d), 0.5 * d, "part", fill)
    return Drawn(fig, source)


SPEC = TypeSpec(
    KEY,
    label=ITEM,
    category=CATEGORY,
    standards_family="fastener",
    vocab=VOCAB,
    figure=figure,
    extent=(2.75, 2.75),
    make=_make,
    share=0.0055,
    price=PRICE,
    claims=None,
    may_claim=frozenset(),
    key_attributes=("Diameter",),
    compat=False,
    use_lines=(
        "Opens a kitchen cabinet door, a drawer or a dresser around the house.",
        "Fastens to the door with one machine screw through a predrilled hole.",
    ),
)
