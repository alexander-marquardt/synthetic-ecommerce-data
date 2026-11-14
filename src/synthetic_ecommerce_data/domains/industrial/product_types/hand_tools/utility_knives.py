"""Utility knives: a homeowner tool for the general-retail catalogue (#971, slice 3).

A utility knife is a handle that holds a replaceable blade: it opens boxes, scores drywall
and trims carpet. A hardware listing sells it by its style, names the blade width and the
handle, and says how many blades come in the pack.

**Styles and blade widths.** A retractable, folding or fixed-blade knife takes the standard
trapezoid blade, 19 mm wide. A snap-off knife takes a segmented blade, and is sold in the
three widths those blades come in: 9, 18 and 25 mm (:data:`KINDS`). No standard fixes them,
so no line claims one and the provenance says so (:data:`PROVENANCE`). The width is
published in mm, the way a listing writes it (``18 mm``), and carried in inches like every
other length.

**Lines.** A line is one brand's knives of one style and blade width, with one handle
material and one handle color. Its SKUs are the blade counts it is sold with: the knife with
3, 5, 10 or 20 blades (:data:`BLADE_COUNTS`). The (style, width, material) combinations are
rotated, so every one of them is built, and so are the colors.

**Colors.** The handle comes in each of the six main colors (gen#275): red, blue, green,
yellow, black and white (:data:`COLORS`). The color rotation steps one further at each full
turn of the combinations, so over 108 lines every combination is built in every color, not
the same color each time (:func:`handle_color`).

**Decoys.** Every type carries text-match decoys (gen#294). In every :data:`DECOY_PERIOD`
lines, :data:`DECOY_SLOTS` of them name another cutting or scraping tool before the item
("Scraper Series Utility Knife"). A search for that tool's word then finds a utility knife,
which a category policy can remove. The attributes stay true, so no check exempts them.

**Price.** GENERATED, not measured: the price census has no utility knives. A knife costs
about its blade count to the 0.15 power, anchored at 12 USD for a standard-tier knife with
5 blades.
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

KEY = "utility_knives"
ITEM = "Utility Knife"
CATEGORY: tuple[str, ...] = ("Hand Tools", "Cutters", "Utility Knives")

#: What every record says about where its blade width came from.
PROVENANCE = f"Width is the conventional width of the blade the style takes; {NO_STANDARD}"

#: Every style a line is built in, with the blade width (mm) it takes: the trapezoid blade
#: for a retractable, folding or fixed-blade knife, a segmented blade for a snap-off one. In
#: an order whose first four entries already hold every style.
KINDS: tuple[tuple[str, int], ...] = (
    ("Retractable", 19),
    ("Snap-Off", 18),
    ("Folding", 19),
    ("Fixed Blade", 19),
    ("Snap-Off", 9),
    ("Snap-Off", 25),
)

#: The handle materials.
MATERIALS: tuple[str, ...] = ("Aluminum", "Zinc Alloy", "Nylon")

#: The blade counts a knife is sold with: the knife and its blades, in one pack.
BLADE_COUNTS: tuple[int, ...] = (3, 5, 10, 20)

#: The six main colors (gen#275), and the swatch the drawing fills the handle with.
COLORS: dict[str, str] = {
    "Red": "#c8322b",
    "Blue": "#2f6db5",
    "Green": "#3c8d4f",
    "Yellow": "#f2c230",
    "Black": "#2a2a2e",
    "White": "#ffffff",
}

#: Every line a brand can offer, without its color: a style and its blade width, in a handle
#: material. All 18, in an order whose first six lines already hold every style, width and
#: material, so a small build offers each of them too.
COMBOS: tuple[tuple[tuple[str, int], str], ...] = tuple(
    (KINDS[i % len(KINDS)], MATERIALS[(i + i // len(KINDS)) % len(MATERIALS)])
    for i in range(len(KINDS) * len(MATERIALS))
)

#: Text-match decoys (gen#294): the lines at these positions of every period name another
#: tool before the item.
DECOY_PERIOD = 6
DECOY_SLOTS: tuple[int, ...] = (1, 4)
#: The tools a decoy title names: none is a utility knife.
DECOY_NOUNS: tuple[str, ...] = ("Scraper", "Chisel", "Saw", "Hammer")


def decoy_item(gen: Any, type_key: str) -> str:
    """The item as the title says it: plain, or with another tool's noun before it."""
    if gen._rotate(f"decoy:{type_key}", DECOY_PERIOD) not in DECOY_SLOTS:
        return ITEM
    noun = DECOY_NOUNS[gen._rotate(f"decoy_noun:{type_key}", len(DECOY_NOUNS))]
    return f"{noun} Series {ITEM}"


def handle_color(n: int) -> str:
    """The handle color of the ``n``-th line. The combination rotation turns every
    ``len(COMBOS)`` lines, a multiple of the six colors, so a color rotating beside it would
    pair each combination with one color only. This one steps one further at every turn."""
    return tuple(COLORS)[(n + n // len(COMBOS)) % len(COLORS)]


def _spec(name: str, scope: str, presence: float = 1.0, kind: str = "keyword") -> AttrSpec:
    return AttrSpec(name=name, scope=scope, presence=presence, kind=kind)


VOCAB = (
    _spec("Color", "line"),
    _spec("Style", "line"),
    _spec("Material", "line"),
    _spec("Width", "line", kind="length"),
    _spec("Number of Blades", "sku", kind="count"),
)


def _make(gen: Any, type_key: str, category: tuple[str, ...]) -> Any:
    # Imported here: generate.py imports the type tables, which discover this module.
    from synthetic_ecommerce_data.core import brands
    from synthetic_ecommerce_data.core.model import keyword_attribute, numeric_attribute
    from synthetic_ecommerce_data.domains.industrial.generate import ChildDraft, LineDraft

    rng = gen.rng
    (style, width_mm), material = COMBOS[gen._rotate(f"combo:{type_key}", len(COMBOS))]
    color = handle_color(gen._rotate(f"color:{type_key}", len(COMBOS) * len(COLORS)))
    brand = brands.pick_brand(rng, type_key, gen._exhausted)
    draft = LineDraft(
        item=decoy_item(gen, type_key),
        brand=brand,
        series=f"UK{rng.randint(100, 999)}",
        category=category,
        provenance=PROVENANCE,
    )
    draft.line_attrs = [
        keyword_attribute("Color", color),
        keyword_attribute("Style", style),
        keyword_attribute("Material", material),
        gen._length("Width", width_mm / MM_PER_INCH, gen._style("mm")),
    ]
    draft.descriptors = [("Color", color)]
    pool = [float(count) for count in BLADE_COUNTS]
    count = min(gen._variant_count(), len(pool))
    for blades in gen._offered_run(f"blades:{style}", pool, count):
        child = ChildDraft(system="mm")
        child.primary = numeric_attribute("Number of Blades", str(int(blades)), blades)
        child.attrs = [child.primary]
        draft.children.append(child)
    return draft


#: GENERATED, NOT MEASURED: about 12 USD for a standard-tier knife with 5 blades, and the
#: blade count to the 0.15 power.
PRICE = PriceModel(12.0, 5.0, 0.15, 0.3, 0.1, measured=False)


def _width_in(record: dict[str, str]) -> float | None:
    """The blade width in inches; ``None`` when unreadable."""
    try:
        return parse_length(str(record.get("Width", "")).strip()).inches
    except DimensionParseError:
        return None


def _count(record: dict[str, str]) -> int | None:
    try:
        return int(str(record.get("Number of Blades", "")).strip())
    except ValueError:
        return None


def figure(record: dict[str, str]) -> Drawn:
    """The knife from its side, the blade out of the front, and its pack's blades laid out
    below it, five to a row. The handle is filled with the record's color and grows with the
    blade's width. A snap-off blade is drawn long and scored into segments, any other the
    trapezoid blade; a retractable or snap-off knife has its slider on top, a folding one
    its pivot at the front."""
    width = _width_in(record)
    blades = _count(record)
    source = "record" if width and blades else "partial"
    width = width or 0.75
    blades = blades or 1
    style = str(record.get("Style", ""))
    snap = style == "Snap-Off"
    handle = (3.6 if style == "Folding" else 4.5) + 1.2 * width
    height = 0.6 + 0.9 * width
    fig = Figure(size_in=handle)
    fill = COLORS.get(str(record.get("Color", "")), "#f2c230")
    fig.poly(
        [
            (0.0, 0.2 * height),
            (0.15 * handle, 0.0),
            (handle, 0.0),
            (handle, height),
            (0.1 * handle, height),
            (0.0, 0.8 * height),
        ],
        "part",
        fill,
    )
    top = 0.5 * (height - width)
    if snap:
        reach = 1.4
        fig.poly(
            [
                (handle, top),
                (handle + reach, top),
                (handle + reach + 0.6 * width, top + width),
                (handle, top + width),
            ],
            "plain",
        )
        step = 0.3
        fig.lines(
            [
                ((handle + step * k + 0.6 * width, top), (handle + step * k, top + width))
                for k in range(1, int(reach / step) + 1)
            ]
        )
    else:
        fig.poly(
            [
                (handle, top),
                (handle + 0.8, top),
                (handle + 1.15, top + width),
                (handle, top + width),
            ],
            "plain",
        )
    if style in ("Retractable", "Snap-Off"):
        fig.rect(0.4 * handle, -0.12, 0.6 * handle, 0.0, "dark")
    elif style == "Folding":
        fig.rect(handle - 0.3, 0.35 * height, handle - 0.1, 0.65 * height, "dark")
    spare = (1.0, 0.6 * width) if snap else (0.75, width)
    for k in range(blades):
        x = 0.2 + (k % 5) * (spare[0] + 0.15)
        y = height + 0.3 + (k // 5) * (spare[1] + 0.15)
        fig.poly(
            [
                (x, y),
                (x + spare[0] - 0.3 * spare[1], y),
                (x + spare[0], y + spare[1]),
                (x, y + spare[1]),
            ],
            "plain",
        )
    return Drawn(fig, source)


SPEC = TypeSpec(
    KEY,
    label=ITEM,
    category=CATEGORY,
    standards_family="hand_tool",
    vocab=VOCAB,
    figure=figure,
    extent=(7.8, 5.25),
    make=_make,
    share=0.0055,
    price=PRICE,
    claims=None,
    may_claim=frozenset(),
    key_attributes=("Number of Blades",),
    compat=False,
    use_lines=(
        "Opens boxes and packages around the house.",
        "Scores drywall and trims carpet, vinyl and cardboard.",
    ),
)
