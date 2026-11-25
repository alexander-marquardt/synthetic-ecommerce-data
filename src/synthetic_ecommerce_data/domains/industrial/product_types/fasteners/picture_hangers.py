"""Picture hangers: home hardware for the R&I catalogue (#958, slice 1).

A picture hanger is the small piece of hardware that holds a frame on a wall: a hook driven
in with a nail, a sawtooth strip or a D-ring fixed to the back of the frame, or a kit of
hooks, wire and nails. A hardware listing sells it by the weight it holds and names its
style, its metal and its color.

**Ratings.** The weights a style is rated for are the ones hardware listings stock
(:data:`LB_RATINGS`): a sawtooth strip holds a light frame, a nail hook or a D-ring a heavy
mirror. No standard fixes them, so no line claims one and the provenance says so
(:data:`PROVENANCE`). A rating is published in pounds-force (``30 lbf``), the unit every
other ``Load Capacity`` in the catalogue carries (casters, shackles, turnbuckles), so the facet
holds one quantity kind and ranges across them. Kilograms are not offered: the industrial unit
table reads neither ``kg`` nor ``kgf``.

**Lines.** A line is one brand's hangers of one style, one metal and one color. Its SKUs are
a run of weight ratings. The (style, material) combinations are rotated, so every one of them
is built, and so are the colors.

**Colors.** The hanger comes in each of the six main colors (gen#275): red, blue, green,
yellow, black and white (:data:`COLORS`). The color rotation steps one further at each full
turn of the combinations, so every combination is built in more than one color
(:func:`hanger_color`).

**Decoys.** Every type carries text-match decoys (gen#294). In every :data:`DECOY_PERIOD`
lines, :data:`DECOY_SLOTS` of them name a thing a hanger holds before the item ("Mirror
Series Picture Hanger"). A search for that word then finds a picture hanger, which a category
policy can remove. The attributes stay true, so no check exempts them.

**Price.** GENERATED, not measured: the price census has no picture hangers. A hanger costs
about its rating to the 0.45 power, anchored at 6 USD for a 30 lb standard-tier hanger.
"""

from __future__ import annotations

from typing import Any

from synthetic_ecommerce_data.core.price import PriceModel
from synthetic_ecommerce_data.core.typespec import TypeSpec
from synthetic_ecommerce_data.domains.industrial.drawing.figures import Drawn
from synthetic_ecommerce_data.domains.industrial.drawing.hanger_figures import EXTENT, hanger
from synthetic_ecommerce_data.domains.industrial.newtypes import NO_STANDARD
from synthetic_ecommerce_data.domains.industrial.vocab import AttrSpec

KEY = "picture_hangers"
ITEM = "Picture Hanger"
CATEGORY: tuple[str, ...] = ("Fasteners", "Picture Hanging", "Picture Hangers")

#: What every record says about where its rating came from.
PROVENANCE = f"Load Capacity is a conventional stocked rating; {NO_STANDARD}"

#: The styles, and the ratings each is stocked in, in pounds. A sawtooth strip holds a light
#: frame; a nail hook, a D-ring or a kit a heavy one.
LB_RATINGS: dict[str, tuple[int, ...]] = {
    "Nail Hook": (10, 20, 30, 50, 75, 100),
    "Sawtooth Hanger": (10, 15, 20, 25, 30),
    "D-Ring Hanger": (20, 30, 50, 75, 100),
    "Hanging Kit": (20, 30, 50, 75, 100),
}
STYLES: tuple[str, ...] = tuple(LB_RATINGS)

#: The metals a hanger is made of.
MATERIALS: tuple[str, ...] = ("Steel", "Stainless Steel", "Brass")

#: The six main colors (gen#275), and the swatch the drawing fills the hanger with.
COLORS: dict[str, str] = {
    "Red": "#c8322b",
    "Blue": "#2f6db5",
    "Green": "#3c8d4f",
    "Yellow": "#f2c230",
    "Black": "#2a2a2e",
    "White": "#eceff1",
}

#: Every line a brand can offer, without its color: a style and a material. All 12, in an
#: order whose first four lines already hold every style and material, so a small build
#: offers each of them too.
COMBOS: tuple[tuple[str, str], ...] = tuple(
    (STYLES[i % 4], MATERIALS[(i + i // 4) % 3]) for i in range(12)
)

#: Text-match decoys (gen#294): the lines at these positions of every period name a thing a
#: hanger holds before the item.
DECOY_PERIOD = 6
DECOY_SLOTS: tuple[int, ...] = (1, 4)
#: The things a decoy title names: none is a picture hanger.
DECOY_NOUNS: tuple[str, ...] = ("Mirror", "Frame", "Clock", "Canvas")


def decoy_item(gen: Any, type_key: str) -> str:
    """The item as the title says it: plain, or with a held thing's noun before it."""
    if gen._rotate(f"decoy:{type_key}", DECOY_PERIOD) not in DECOY_SLOTS:
        return ITEM
    noun = DECOY_NOUNS[gen._rotate(f"decoy_noun:{type_key}", len(DECOY_NOUNS))]
    return f"{noun} Series {ITEM}"


def hanger_color(n: int) -> str:
    """The color of the ``n``-th line. The combination rotation turns every ``len(COMBOS)``
    lines, a multiple of the six colors, so a color rotating beside it would pair each
    combination with one color only. This one steps one further at every turn."""
    return tuple(COLORS)[(n + n // len(COMBOS)) % len(COLORS)]


def rating(pounds: int) -> tuple[str, float]:
    """The published rating and its value in pounds."""
    return f"{pounds} lbf", float(pounds)


def _spec(name: str, scope: str, presence: float = 1.0, kind: str = "keyword") -> AttrSpec:
    return AttrSpec(name=name, scope=scope, presence=presence, kind=kind)


VOCAB = (
    _spec("Color", "line"),
    _spec("Style", "line"),
    _spec("Material", "line"),
    _spec("Load Capacity", "sku", kind="count"),
)


def _make(gen: Any, type_key: str, category: tuple[str, ...]) -> Any:
    # Imported here: generate.py imports the type tables, which discover this module.
    from synthetic_ecommerce_data.core import brands
    from synthetic_ecommerce_data.core.model import keyword_attribute, numeric_attribute
    from synthetic_ecommerce_data.domains.industrial.generate import ChildDraft, LineDraft

    rng = gen.rng
    style, material = COMBOS[gen._rotate(f"combo:{type_key}", len(COMBOS))]
    color = hanger_color(gen._rotate(f"color:{type_key}", len(COMBOS) * len(COLORS)))
    brand = brands.pick_brand(rng, type_key, gen._exhausted)
    draft = LineDraft(
        item=decoy_item(gen, type_key),
        brand=brand,
        series=f"PH{rng.randint(100, 999)}",
        category=category,
        provenance=PROVENANCE,
    )
    draft.line_attrs = [
        keyword_attribute("Color", color),
        keyword_attribute("Style", style),
        keyword_attribute("Material", material),
    ]
    draft.descriptors = [("Style", style), ("Color", color)]
    pool = [float(size) for size in LB_RATINGS[style]]
    count = min(gen._variant_count(), len(pool))
    for size in gen._offered_run(f"ratings:{style}", pool, count):
        published, pounds = rating(int(size))
        child = ChildDraft(system="in")
        child.primary = numeric_attribute("Load Capacity", published, pounds)
        child.attrs = [child.primary]
        draft.children.append(child)
    return draft


#: GENERATED, NOT MEASURED: about 6 USD for a 30 lb standard-tier hanger, and the rating to
#: the 0.45 power.
PRICE = PriceModel(6.0, 30.0, 0.45, 0.3, 0.1, measured=False)


def _pounds(record: dict[str, str]) -> float | None:
    """The record's rating in pounds; ``None`` when unreadable."""
    value = str(record.get("Load Capacity", "")).strip()
    if not value.endswith(" lbf"):
        return None
    try:
        return float(value[: -len(" lbf")])
    except ValueError:
        return None


def figure(record: dict[str, str]) -> Drawn:
    """The hanger face on and lit, in the record's color and sized to its rating: a heavier one is
    larger, and is held by more nails or screws (``hanger_figures``)."""
    pounds = _pounds(record)
    fill = COLORS.get(str(record.get("Color", "")), COLORS["Black"])
    drawn = hanger(str(record.get("Style", "")), fill, pounds or 30.0)
    return Drawn(drawn, "record" if pounds else "partial")


SPEC = TypeSpec(
    KEY,
    label=ITEM,
    category=CATEGORY,
    standards_family="fastener",
    vocab=VOCAB,
    figure=figure,
    extent=EXTENT,
    make=_make,
    share=0.0055,
    price=PRICE,
    claims=None,
    may_claim=frozenset(),
    key_attributes=("Load Capacity",),
    compat=False,
    use_lines=(
        "Hangs a picture, a mirror or a clock on a wall around the house.",
        "Holds a framed picture level on drywall or plaster.",
    ),
)
