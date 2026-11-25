"""Household tool sets: a homeowner tool for the R&I catalogue (#971, slice 3).

A household tool set is the kit a homeowner keeps in a cupboard: a hammer, screwdrivers, a
few wrenches and pliers, hex keys and a run of sockets and bits, in one container. A
hardware listing sells it by piece count, and names the container and the tools' steel.

**Sizes.** The piece counts are the ones homeowner sets are stocked in: 8, 23, 39, 65, 102
and 148 pieces (:data:`PIECE_COUNTS`). No standard fixes them, so no line claims one and the
provenance says so (:data:`PROVENANCE`). The count is published as ``Piece Count``, the name
the assortment kits already publish.

**Lines.** A line is one brand's sets in one container, with one tool steel and one case
color. Its SKUs are a run of piece counts. The (container, steel) combinations are rotated,
so every one of them is built, and so are the colors.

**Colors.** The container comes in each of the six main colors (gen#275): red, blue, green,
yellow, black and white (:data:`COLORS`). The color rotation steps one further at each full
turn of the combinations, so over 108 lines every combination is built in every color, not
the same color each time (:func:`case_color`).

**Decoys.** Every type carries text-match decoys (gen#294). In every :data:`DECOY_PERIOD`
lines, :data:`DECOY_SLOTS` of them name a power tool before the item ("Drill Series
Household Tool Set"). A household set holds no power tool, so a search for that tool's word
then finds a set that a category policy can remove. The attributes stay true, so no check
exempts them.

**Price.** GENERATED, not measured: the price census has no household tool sets. A set
costs about its piece count to the 0.45 power, anchored at 35 USD for a 39-piece
standard-tier set.
"""

from __future__ import annotations

from typing import Any

from synthetic_ecommerce_data.core.price import PriceModel
from synthetic_ecommerce_data.core.typespec import TypeSpec
from synthetic_ecommerce_data.domains.industrial.drawing.case_figures import EXTENT, household_set
from synthetic_ecommerce_data.domains.industrial.drawing.figures import Drawn
from synthetic_ecommerce_data.domains.industrial.newtypes import NO_STANDARD
from synthetic_ecommerce_data.domains.industrial.vocab import AttrSpec

KEY = "household_tool_sets"
ITEM = "Household Tool Set"
CATEGORY: tuple[str, ...] = ("Hand Tools", "Tool Sets & Kits", "Household Tool Sets")

#: What every record says about where its piece count came from.
PROVENANCE = f"Piece Count is a conventional stocked set size; {NO_STANDARD}"

#: The piece counts a household set is stocked in.
PIECE_COUNTS: tuple[int, ...] = (8, 23, 39, 65, 102, 148)

#: The containers a set is sold in, and the steels its tools are made of.
CONTAINERS: tuple[str, ...] = (
    "Blow-Molded Case",
    "Zippered Case",
    "Plastic Tool Box",
    "Metal Tool Box",
    "Roll-Up Pouch",
    "Canvas Tool Bag",
)
MATERIALS: tuple[str, ...] = ("Chrome Vanadium Steel", "Carbon Steel", "Alloy Steel")

#: The six main colors (gen#275), and the swatch the drawing fills the container with.
COLORS: dict[str, str] = {
    "Red": "#c8322b",
    "Blue": "#2f6db5",
    "Green": "#3c8d4f",
    "Yellow": "#f2c230",
    "Black": "#2a2a2e",
    "White": "#eceff1",
}

#: Every line a brand can offer, without its color: a container and a tool steel. All 18,
#: in an order whose first six lines already hold every container and steel, so a small
#: build offers each of them too.
COMBOS: tuple[tuple[str, str], ...] = tuple(
    (CONTAINERS[i % len(CONTAINERS)], MATERIALS[(i + i // len(CONTAINERS)) % len(MATERIALS)])
    for i in range(len(CONTAINERS) * len(MATERIALS))
)

#: Text-match decoys (gen#294): the lines at these positions of every period name a power
#: tool before the item.
DECOY_PERIOD = 6
DECOY_SLOTS: tuple[int, ...] = (2, 5)
#: The tools a decoy title names: none is in a household set.
DECOY_NOUNS: tuple[str, ...] = ("Drill", "Sander", "Grinder", "Router")


def decoy_item(gen: Any, type_key: str) -> str:
    """The item as the title says it: plain, or with a power tool's noun before it."""
    if gen._rotate(f"decoy:{type_key}", DECOY_PERIOD) not in DECOY_SLOTS:
        return ITEM
    noun = DECOY_NOUNS[gen._rotate(f"decoy_noun:{type_key}", len(DECOY_NOUNS))]
    return f"{noun} Series {ITEM}"


def case_color(n: int) -> str:
    """The container color of the ``n``-th line. The combination rotation turns every
    ``len(COMBOS)`` lines, a multiple of the six colors, so a color rotating beside it would
    pair each combination with one color only. This one steps one further at every turn."""
    return tuple(COLORS)[(n + n // len(COMBOS)) % len(COLORS)]


def _spec(name: str, scope: str, presence: float = 1.0, kind: str = "keyword") -> AttrSpec:
    return AttrSpec(name=name, scope=scope, presence=presence, kind=kind)


VOCAB = (
    _spec("Color", "line"),
    _spec("Container Type", "line"),
    _spec("Material", "line"),
    _spec("Piece Count", "sku"),
)


def _make(gen: Any, type_key: str, category: tuple[str, ...]) -> Any:
    # Imported here: generate.py imports the type tables, which discover this module.
    from synthetic_ecommerce_data.core import brands
    from synthetic_ecommerce_data.core.model import keyword_attribute, numeric_attribute
    from synthetic_ecommerce_data.domains.industrial.generate import ChildDraft, LineDraft

    rng = gen.rng
    container, material = COMBOS[gen._rotate(f"combo:{type_key}", len(COMBOS))]
    color = case_color(gen._rotate(f"color:{type_key}", len(COMBOS) * len(COLORS)))
    brand = brands.pick_brand(rng, type_key, gen._exhausted)
    draft = LineDraft(
        item=decoy_item(gen, type_key),
        brand=brand,
        series=f"HS{rng.randint(100, 999)}",
        category=category,
        provenance=PROVENANCE,
    )
    draft.line_attrs = [
        keyword_attribute("Color", color),
        keyword_attribute("Container Type", container),
        keyword_attribute("Material", material),
    ]
    draft.descriptors = [("Color", color)]
    pool = [float(count) for count in PIECE_COUNTS]
    count = min(gen._variant_count(), len(pool))
    for pieces in gen._offered_run(f"pieces:{type_key}", pool, count):
        child = ChildDraft(system="in")
        child.primary = numeric_attribute("Piece Count", str(int(pieces)), pieces)
        child.attrs = [child.primary]
        draft.children.append(child)
    return draft


#: GENERATED, NOT MEASURED: about 35 USD for a standard-tier 39-piece set, and the piece
#: count to the 0.45 power.
PRICE = PriceModel(35.0, 39.0, 0.45, 0.3, 0.1, measured=False)


def _pieces(record: dict[str, str]) -> int | None:
    try:
        return int(str(record.get("Piece Count", "")).strip())
    except ValueError:
        return None


def figure(record: dict[str, str]) -> Drawn:
    """The set seen from the front, open and lit: its container in the record's color, its tools
    and one bit for each piece. A larger set is drawn larger, and each container has its own
    outline and fittings (``case_figures``)."""
    pieces = _pieces(record)
    fill = COLORS.get(str(record.get("Color", "")), COLORS["Yellow"])
    drawn = household_set(record, fill, pieces or 23, PIECE_COUNTS)
    return Drawn(drawn, "record" if pieces else "partial")


SPEC = TypeSpec(
    KEY,
    label=ITEM,
    category=CATEGORY,
    standards_family="hand_tool",
    vocab=VOCAB,
    figure=figure,
    extent=EXTENT,
    make=_make,
    share=0.0055,
    price=PRICE,
    claims=None,
    may_claim=frozenset(),
    key_attributes=("Piece Count",),
    compat=False,
    use_lines=(
        "Keeps the tools for small jobs around the house in one place.",
        "Hangs pictures, tightens loose screws and assembles furniture.",
    ),
)
