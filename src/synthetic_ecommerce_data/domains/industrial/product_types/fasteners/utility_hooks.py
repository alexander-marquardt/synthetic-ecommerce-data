"""Utility hooks: home hardware for the R&I catalogue (#958, slice 3).

A utility hook is the hook a homeowner screws into a wall, under a cabinet or into a ceiling
to hang a coat, a mug, a towel or a tool. A hardware listing sells it by its length and names
its style, its metal and its color.

**Lengths.** The lengths a style is stocked in are the ones hardware listings carry
(:data:`INCH_LENGTHS`): a cup hook runs 1" to 2", a J-shaped hook 2" to 8", a double-prong
coat hook 3" to 6", and an S-shaped hook 2" to 6". No standard fixes them, so no line claims
one and the provenance says so (:data:`PROVENANCE`). A length is published in inches, the way
the catalogue's other ``Length`` values are, so the facet ranges across them.

**Lines.** A line is one brand's hooks of one style, one metal and one color. Its SKUs are a
run of lengths. The (style, material) combinations are rotated, so every one of them is
built, and so are the colors.

**Colors.** The hook comes in each of the six main colors (gen#275): red, blue, green, yellow,
black and white (:data:`COLORS`), a vinyl-coated or painted finish over the metal. The color
rotation steps one further at each full turn of the combinations, so every combination is
built in more than one color (:func:`hook_color`).

**Decoys.** Every type carries text-match decoys (gen#294). In every :data:`DECOY_PERIOD`
lines, :data:`DECOY_SLOTS` of them name a room before the item ("Laundry Series Utility
Hook"). A search for that word then finds a utility hook, which a category policy can remove.
The attributes stay true, so no check exempts them.

**Price.** GENERATED, not measured: the price census has no utility hooks. A hook costs about
its length to the 0.8 power, anchored at 3 USD for a 3" standard-tier hook.
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

KEY = "utility_hooks"
ITEM = "Utility Hook"
CATEGORY: tuple[str, ...] = ("Fasteners", "Hooks", "Utility Hooks")

#: What every record says about where its length came from.
PROVENANCE = f"Length is a conventional stocked size; {NO_STANDARD}"

#: The styles, and the lengths each is stocked in, in inches.
INCH_LENGTHS: dict[str, tuple[float, ...]] = {
    "Cup": (1.0, 1.25, 1.5, 2.0),
    "J-Shaped": (2.0, 3.0, 4.0, 6.0, 8.0),
    "Double Prong": (3.0, 4.0, 5.0, 6.0),
    "S-Shaped": (2.0, 3.0, 4.0, 5.0, 6.0),
}
STYLES: tuple[str, ...] = tuple(INCH_LENGTHS)

#: The metals a hook is made of.
MATERIALS: tuple[str, ...] = ("Steel", "Brass", "Zinc Alloy")

#: The six main colors (gen#275), and the swatch the drawing fills the hook with.
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
#: The rooms a decoy title names: none is a hook.
DECOY_NOUNS: tuple[str, ...] = ("Mudroom", "Entryway", "Laundry", "Patio")


def decoy_item(gen: Any, type_key: str) -> str:
    """The item as the title says it: plain, or with a room's noun before it."""
    if gen._rotate(f"decoy:{type_key}", DECOY_PERIOD) not in DECOY_SLOTS:
        return ITEM
    noun = DECOY_NOUNS[gen._rotate(f"decoy_noun:{type_key}", len(DECOY_NOUNS))]
    return f"{noun} Series {ITEM}"


def hook_color(n: int) -> str:
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
    color = hook_color(gen._rotate(f"color:{type_key}", len(COMBOS) * len(COLORS)))
    brand = brands.pick_brand(rng, type_key, gen._exhausted)
    draft = LineDraft(
        item=decoy_item(gen, type_key),
        brand=brand,
        series=f"UH{rng.randint(100, 999)}",
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


#: GENERATED, NOT MEASURED: about 3 USD for a 3" standard-tier hook, and the length to the
#: 0.8 power.
PRICE = PriceModel(3.0, 3.0, 0.8, 0.3, 0.1, measured=False)


def _length(record: dict[str, str]) -> float | None:
    """The record's length in inches; ``None`` when unreadable."""
    try:
        return parse_length(str(record.get("Length", ""))).inches
    except DimensionParseError:
        return None


def _ring(fig: Figure, centre: tuple[float, float], r: float, t: float, a0: float, a1: float,
          fill: str) -> None:
    """A bent wire of thickness ``t`` along the circle of radius ``r`` from ``a0`` to ``a1``
    degrees (y runs down, so 90 is the bottom of the circle)."""
    fig.poly(arc(centre, r, a0, a1, 24) + arc(centre, r - t, a1, a0, 24), "part", fill)


def figure(record: dict[str, str]) -> Drawn:
    """The hook side on, filled with the record's color, as long as its length. A cup hook is a
    threaded shank screwed up into a shelf, with an open curl below it; a J-shaped hook is a
    wall plate with an arm that turns up at its end; a double-prong coat hook is a wall plate
    with a short upper and a long lower arm, each with a ball tip; and an S-shaped hook is two
    curls, the upper open at its lower right and the lower open at its upper left."""
    inches = _length(record)
    source = "record" if inches else "partial"
    a = inches or 3.0
    fig = Figure(size_in=a)
    fill = COLORS.get(str(record.get("Color", "")), "#2a2a2e")
    style = str(record.get("Style", ""))
    t = 0.08 * a
    if style == "Cup":
        fig.rect(0.3 * a, 0.0, 0.3 * a + 3 * t, t, "part", fill)
        fig.rect(0.3 * a + t, t, 0.3 * a + 2 * t, 0.5 * a, "part", fill)
        r = 0.25 * a
        _ring(fig, (0.3 * a + t + r, 0.5 * a), r, t, 180.0, 0.0, fill)
        return Drawn(fig, source)
    if style == "S-Shaped":
        r = 0.25 * a
        _ring(fig, (0.5 * a, 0.25 * a), r, t, 90.0, 380.0, fill)
        _ring(fig, (0.5 * a, 0.75 * a), r, t, 270.0, 560.0, fill)
        return Drawn(fig, source)
    fig.rect(0.0, 0.0, 0.12 * a, 0.5 * a, "part", fill)
    for y in (0.08 * a, 0.42 * a):  # one disc each: a grouped run nests a <g>
        fig.disc((0.06 * a, y), 0.025 * a, "dark")
    if style == "Double Prong":
        fig.rect(0.12 * a, 0.12 * a, 0.6 * a, 0.12 * a + t, "part", fill)
        fig.disc((0.6 * a, 0.12 * a + 0.5 * t), t, "part", fill)
        fig.rect(0.12 * a, 0.32 * a, a - t, 0.32 * a + t, "part", fill)
        fig.disc((a - t, 0.32 * a + 0.5 * t), t, "part", fill)
        return Drawn(fig, source)
    r = 0.15 * a
    fig.rect(0.12 * a, 0.3 * a, a - r, 0.3 * a + t, "part", fill)
    _ring(fig, (a - r, 0.3 * a + t - r), r, t, 90.0, -45.0, fill)
    return Drawn(fig, source)


SPEC = TypeSpec(
    KEY,
    label=ITEM,
    category=CATEGORY,
    standards_family="fastener",
    vocab=VOCAB,
    figure=figure,
    extent=(8.1, 6.1),
    make=_make,
    share=0.0055,
    price=PRICE,
    claims=None,
    may_claim=frozenset(),
    key_attributes=("Length",),
    compat=False,
    use_lines=(
        "Hangs a coat, a towel, a mug or a tool on a wall, under a cabinet or from a ceiling.",
        "Screws into a wall stud, a cabinet or a wall anchor and holds what hangs from it.",
    ),
)
