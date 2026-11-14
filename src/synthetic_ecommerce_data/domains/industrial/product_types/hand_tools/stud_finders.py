"""Stud finders: a homeowner tool for the general-retail catalogue (#971, slice 2).

A stud finder is a palm-sized scanner slid along a wall to find the wood or metal stud
behind the drywall before a shelf or a picture is hung. A hardware listing sells it by
how deep it scans, and names how it finds the stud, how it shows it, and what else it
scans for.

**Styles and tiers.** Three styles (:data:`STYLES`): an edge-finding scanner, which marks
each edge of the stud; a center-finding scanner, which marks its middle; and a magnetic
finder, which finds the screws and nails in the stud with a pivoting magnet and needs no
battery. An electronic scanner is one of two tiers, named by the scan modes it lists
(``Application Modes``): a basic one scans for studs and live AC wire; a multi-scan one adds
a deep scan and a metal scan. Each tier is sold in its own scan depths
(:data:`DEPTHS_IN`): 3/4 or 1 in for a basic scanner, 1-1/2 or 2 in for a multi-scan one,
and 3/4 or 1 in for a magnetic finder. No standard fixes these depths, so no line claims
one and the provenance says so (:data:`PROVENANCE`). The census names the depth ``Scan
Depth (In.)``, so a depth is published in inches only.

**Lines.** A line is one brand's finders of one style, one indicator (a single LED, LED
arrows or an LCD screen; a magnetic finder's is its pivoting magnet) and one tier, in one
body color. Its SKUs are the tier's scan depths. The 13 (style, indicator, modes)
combinations are rotated in an order whose first six lines already hold every style,
indicator and mode set (:data:`COMBOS`), so a small build offers each of them too.

**Colors.** The body comes in each of the six main colors (gen#275): red, blue, green,
yellow, black and white (:data:`COLORS`). The color rotation steps one further at each
full turn of the combinations, so each combination is built in every color
(:func:`body_color`).

**Decoys.** Every type carries text-match decoys (gen#294). In every :data:`DECOY_PERIOD`
lines, :data:`DECOY_SLOTS` of them name another layout or electrical tool before the item
("Laser Series Stud Finder"). A search for that tool's word then finds a stud finder,
which a category policy can remove. The attributes stay true, so no check exempts them.

**Price.** GENERATED, not measured: the price census has no stud finders. A finder costs
about its scan depth to the 0.9 power, anchored at 25 USD for a 1 in standard-tier
scanner.
"""

from __future__ import annotations

from typing import Any

from synthetic_ecommerce_data.core.dimensions import DimensionParseError, parse_length
from synthetic_ecommerce_data.core.drawing.model import Figure
from synthetic_ecommerce_data.core.price import PriceModel
from synthetic_ecommerce_data.core.typespec import TypeSpec
from synthetic_ecommerce_data.domains.industrial.drawing.figures import Drawn
from synthetic_ecommerce_data.domains.industrial.newtypes import NO_STANDARD
from synthetic_ecommerce_data.domains.industrial.vocab import AttrSpec

KEY = "stud_finders"
ITEM = "Stud Finder"
CATEGORY: tuple[str, ...] = ("Measuring & Inspecting", "Stud Finders")

#: The census's name for how deep a finder scans; its values are inches.
DEPTH = "Scan Depth (In.)"

#: What every record says about where its scan depth came from.
PROVENANCE = f"Scan depth is a conventional stocked size; {NO_STANDARD}"

#: How the finder finds the stud.
STYLES: tuple[str, ...] = ("Edge Finding", "Center Finding", "Magnetic")
#: How an electronic scanner shows the stud. A magnetic finder's indicator is its magnet.
INDICATORS: tuple[str, ...] = ("Single LED", "LED Arrows", "LCD Screen")
MAGNET = "Pivoting Magnet"

#: The scan modes each tier lists, and the depths, in inches, it is sold in.
MODES: dict[str, str] = {
    "Basic": "Stud Scan, AC Scan",
    "Multi-Scan": "Stud Scan, Deep Scan, Metal Scan, AC Scan",
    "Magnetic": "Metal Scan",
}
DEPTHS_IN: dict[str, tuple[float, ...]] = {
    "Basic": (0.75, 1.0),
    "Multi-Scan": (1.5, 2.0),
    "Magnetic": (0.75, 1.0),
}

#: The six main colors (gen#275), and the swatch the drawing fills the body with.
COLORS: dict[str, str] = {
    "Red": "#c8322b",
    "Blue": "#2f6db5",
    "Green": "#3c8d4f",
    "Yellow": "#f2c230",
    "Black": "#2a2a2e",
    "White": "#ffffff",
}

#: The twelve electronic lines a brand can offer, without their color: an edge- or
#: center-finding scanner, one of three indicators, in the basic or the multi-scan tier.
#: In an order whose first four lines already hold both styles, both tiers and three
#: indicators: the (style, indicator) pairs turn every six lines, and the tier of the
#: ``i``-th line is the other one from line ``i - 6``'s.
_ELECTRONIC: tuple[tuple[str, str, str], ...] = tuple(
    (STYLES[i % 2], INDICATORS[i % 3], ("Basic", "Multi-Scan")[(i // 2) % 2]) for i in range(12)
)
#: Every line a brand can offer, without its color: the twelve electronic ones, with the
#: magnetic finder third, so a small build offers it too.
COMBOS: tuple[tuple[str, str, str], ...] = (
    *_ELECTRONIC[:2],
    ("Magnetic", MAGNET, "Magnetic"),
    *_ELECTRONIC[2:],
)

#: Text-match decoys (gen#294): the lines at these positions of every period name another
#: tool before the item.
DECOY_PERIOD = 6
DECOY_SLOTS: tuple[int, ...] = (1, 4)
#: The tools a decoy title names: none is a stud finder.
DECOY_NOUNS: tuple[str, ...] = ("Laser", "Moisture Meter", "Voltage Tester", "Multimeter")


def decoy_item(gen: Any, type_key: str) -> str:
    """The item as the title says it: plain, or with another tool's noun before it."""
    if gen._rotate(f"decoy:{type_key}", DECOY_PERIOD) not in DECOY_SLOTS:
        return ITEM
    noun = DECOY_NOUNS[gen._rotate(f"decoy_noun:{type_key}", len(DECOY_NOUNS))]
    return f"{noun} Series {ITEM}"


def body_color(n: int) -> str:
    """The body color of the ``n``-th line, ``n`` counted over ``len(COMBOS) * len(COLORS)``
    lines. The ``j``-th combination of the ``k``-th turn takes color ``j + k``, so over six
    turns each combination meets every color. (``n + n // len(COMBOS)``, the levels' form,
    is the same only when the combinations are a multiple of six: with 13 it steps two
    colors a turn, and each combination met three.)"""
    turn, combo = divmod(n, len(COMBOS))
    return tuple(COLORS)[(combo + turn) % len(COLORS)]


def _spec(name: str, scope: str, presence: float = 1.0, kind: str = "keyword") -> AttrSpec:
    return AttrSpec(name=name, scope=scope, presence=presence, kind=kind)


VOCAB = (
    _spec("Color", "line"),
    _spec("Style", "line"),
    _spec("Indicator", "line"),
    _spec("Application Modes", "line"),
    _spec(DEPTH, "sku", kind="length"),
)


def _make(gen: Any, type_key: str, category: tuple[str, ...]) -> Any:
    # Imported here: generate.py imports the type tables, which discover this module.
    from synthetic_ecommerce_data.core import brands
    from synthetic_ecommerce_data.core.model import keyword_attribute
    from synthetic_ecommerce_data.domains.industrial.generate import ChildDraft, LineDraft

    rng = gen.rng
    style, indicator, tier = COMBOS[gen._rotate(f"combo:{type_key}", len(COMBOS))]
    color = body_color(gen._rotate(f"color:{type_key}", len(COMBOS) * len(COLORS)))
    brand = brands.pick_brand(rng, type_key, gen._exhausted)
    draft = LineDraft(
        item=decoy_item(gen, type_key),
        brand=brand,
        series=f"SF{rng.randint(100, 999)}",
        category=category,
        provenance=PROVENANCE,
    )
    draft.line_attrs = [
        keyword_attribute("Color", color),
        keyword_attribute("Style", style),
        keyword_attribute("Indicator", indicator),
        keyword_attribute("Application Modes", MODES[tier]),
    ]
    draft.descriptors = [("Style", style), ("Color", color)]
    pool = list(DEPTHS_IN[tier])
    count = min(gen._variant_count(), len(pool))
    style_in = gen._style("in")
    # The run rotates per (style, indicator, tier, color): rotated per tier alone, a
    # one-SKU line of one combination and color met the same depth each time, and half the
    # specs were never built.
    run = f"depths:{style}:{indicator}:{tier}:{color}"
    for depth in gen._offered_run(run, pool, count):
        child = ChildDraft(system="in")
        child.primary = gen._length(DEPTH, depth, style_in)
        child.attrs = [child.primary]
        draft.children.append(child)
    return draft


#: GENERATED, NOT MEASURED: about 25 USD for a 1 in standard-tier scanner, and the scan
#: depth to the 0.9 power (a 3/4 in finder near 19 USD, a 2 in multi-scan one near 47).
PRICE = PriceModel(25.0, 1.0, 0.9, 0.3, 0.1, measured=False)


def _inches(record: dict[str, str], name: str) -> float | None:
    """``name`` in inches; ``None`` when unreadable."""
    try:
        return parse_length(str(record.get(name, "")).strip()).inches
    except DimensionParseError:
        return None


#: The body's drawn (width, height), in inches, by style: a magnetic finder is the smaller.
BODY: dict[str, tuple[float, float]] = {
    "Edge Finding": (2.4, 5.2),
    "Center Finding": (2.6, 5.6),
    "Magnetic": (1.6, 3.2),
}


def _depth_scale(fig: Figure, wide: float, high: float, depth: float | None) -> None:
    """The depth scale printed on the body, drawn last so the grip does not cover it: a strip
    0.8 in long per inch of scan depth, so two SKUs of a line draw apart."""
    base = 0.12 * high
    fig.rect(0.74 * wide, base, 0.84 * wide, base + 0.8 * (depth or 1.0), "plain")


def figure(record: dict[str, str]) -> Drawn:
    """The finder from its face, filled with the record's color. An electronic scanner is a
    tall body with a dark grip across its lower half and its indicator near the top: one
    LED, two arrows pointing at each other, or an LCD window. A multi-scan scanner draws a
    mode button under its indicator. A magnetic finder is a smaller body with a round window
    and the pivoting magnet across it. Each draws a depth scale on its body, longer for a
    deeper scan."""
    depth = _inches(record, DEPTH)
    source = "record" if depth else "partial"
    style = str(record.get("Style", "Edge Finding"))
    wide, high = BODY.get(style, BODY["Edge Finding"])
    fig = Figure(size_in=high)
    fill = COLORS.get(str(record.get("Color", "")), "#f2c230")
    corner = 0.25 * wide
    fig.poly(
        [
            (corner, 0.0),
            (wide - corner, 0.0),
            (wide, corner),
            (wide, high - corner),
            (wide - corner, high),
            (corner, high),
            (0.0, high - corner),
            (0.0, corner),
        ],
        "part",
        fill,
    )
    mid = 0.5 * wide
    indicator = record.get("Indicator")
    if indicator == MAGNET:
        fig.disc((mid, 0.6 * high), 0.32 * wide, "plain")
        fig.rect(mid - 0.28 * wide, 0.6 * high - 0.05, mid + 0.28 * wide, 0.6 * high + 0.05, "dark")
        _depth_scale(fig, wide, high, depth)
        return Drawn(fig, source)
    fig.rect(0.12 * wide, 0.1 * high, 0.88 * wide, 0.45 * high, "dark")
    top = 0.78 * high
    if indicator == "LCD Screen":
        fig.rect(0.2 * wide, top - 0.35, 0.8 * wide, top + 0.35, "plain")
    elif indicator == "LED Arrows":
        for sign in (-1.0, 1.0):
            tip = mid + sign * 0.08 * wide
            back = mid + sign * 0.32 * wide
            fig.poly([(tip, top), (back, top + 0.18), (back, top - 0.18)], "dark")
    else:
        fig.disc((mid, top), 0.12, "dark")
    if "Deep Scan" in str(record.get("Application Modes", "")):
        fig.disc((mid, 0.6 * high), 0.16, "plain")
    _depth_scale(fig, wide, high, depth)
    return Drawn(fig, source)


SPEC = TypeSpec(
    KEY,
    label=ITEM,
    category=CATEGORY,
    standards_family="hand_tool",
    vocab=VOCAB,
    figure=figure,
    extent=(2.7, 5.7),
    make=_make,
    share=0.0065,
    price=PRICE,
    claims=None,
    may_claim=frozenset(),
    key_attributes=(DEPTH,),
    compat=False,
    use_lines=(
        "Finds the wood or metal stud behind drywall before a shelf, a TV mount or a picture "
        "is hung.",
        "Warns of a live AC wire behind the wall before drilling.",
    ),
)
