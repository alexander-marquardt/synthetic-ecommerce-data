"""Tape measures: a homeowner tool for the general-retail catalogue (#971, slice 1).

A tape measure is a steel blade, printed with a scale, coiled in a case. It has a hook on
the blade's end and a lock that holds the blade out. A hardware listing sells it by blade
length, and names its blade width, case and lock.

**Sizes.** The blade lengths are the ones hardware listings stock: 10 to 35 ft for an
inch tape, 3 to 10 m for a metric one (:data:`INCH_FEET`, :data:`METRIC_METRES`). The
blade width goes with the length (:data:`INCH_WIDTH`, :data:`METRIC_WIDTH_MM`): a short
pocket tape has a narrow blade, and a long one has a wide blade so that it stands out
further. No standard fixes either, so no line claims one and the provenance says so
(:data:`PROVENANCE`). A length is published in feet or metres, the way a listing writes
it (``25 ft``, ``5 m``), and carries its value in inches like every other length.

**Lines.** A line is one brand's tape measures with one case material, one lock and one
case color, in one unit system. Its SKUs are a run of blade lengths. The (material, lock,
system) combinations are rotated, so every one of them is built, and so are the colors.

**Colors.** The case comes in each of the six main colors (gen#275): red, blue, green,
yellow, black and white (:data:`COLORS`). The color rotation steps one further at each full
turn of the combinations, so over 108 lines every combination is built in every color, not
the same color each time (:func:`case_color`).

**Decoys.** Every type carries text-match decoys (gen#294). In every :data:`DECOY_PERIOD`
lines, :data:`DECOY_SLOTS` of them name another measuring tool before the item ("Level
Series Tape Measure"). A search for that tool's word then finds a tape measure, which a
category policy can remove. The attributes stay true, so no check exempts them.

**Price.** GENERATED, not measured: the price census has no tape measures. A tape costs
about its length to the 0.55 power, anchored at 19 USD for a 25 ft standard-tier tape.
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

KEY = "tape_measures"
ITEM = "Tape Measure"
CATEGORY: tuple[str, ...] = ("Measuring & Inspecting", "Hand Measuring", "Tape Measures")

#: What every record says about where its length and blade width came from.
PROVENANCE = f"Length and Width are conventional stocked sizes; {NO_STANDARD}"

#: The blade lengths an inch tape is stocked in, in feet, and its blade width, in inches.
INCH_WIDTH: dict[int, float] = {10: 0.5, 12: 0.75, 16: 0.75, 25: 1.0, 30: 1.0, 35: 1.25}
INCH_FEET: tuple[int, ...] = tuple(INCH_WIDTH)

#: The blade lengths a metric tape is stocked in, in metres, and its blade width, in mm.
METRIC_WIDTH_MM: dict[int, int] = {3: 16, 5: 19, 8: 25, 10: 25}
METRIC_METRES: tuple[int, ...] = tuple(METRIC_WIDTH_MM)

#: The case materials, and the locks that hold the blade out.
MATERIALS: tuple[str, ...] = ("ABS Plastic", "Rubber-Coated ABS", "Chrome-Plated ABS")
LOCKS: tuple[str, ...] = ("Slide Lock", "Auto Lock", "Push Button Lock")
SYSTEMS: tuple[str, ...] = ("in", "mm")

#: The six main colors (gen#275), and the swatch the drawing fills the case with.
COLORS: dict[str, str] = {
    "Red": "#c8322b",
    "Blue": "#2f6db5",
    "Green": "#3c8d4f",
    "Yellow": "#f2c230",
    "Black": "#2a2a2e",
    "White": "#ffffff",
}

#: Every line a brand can offer, without its color: a material and a lock in a unit system.
#: All 18 in an order whose first six lines already hold every material, lock and system,
#: so a small build offers each of them too.
COMBOS: tuple[tuple[str, str, str], ...] = tuple(
    (MATERIALS[i % 3], LOCKS[(i + i // 6) % 3], SYSTEMS[i % 2]) for i in range(18)
)

#: Text-match decoys (gen#294): the lines at these positions of every period name another
#: measuring tool before the item.
DECOY_PERIOD = 6
DECOY_SLOTS: tuple[int, ...] = (0, 3)
#: The tools a decoy title names: none is a tape measure.
DECOY_NOUNS: tuple[str, ...] = ("Level", "Laser", "Ruler", "Square")


def decoy_item(gen: Any, type_key: str) -> str:
    """The item as the title says it: plain, or with another tool's noun before it."""
    if gen._rotate(f"decoy:{type_key}", DECOY_PERIOD) not in DECOY_SLOTS:
        return ITEM
    noun = DECOY_NOUNS[gen._rotate(f"decoy_noun:{type_key}", len(DECOY_NOUNS))]
    return f"{noun} Series {ITEM}"


def case_color(n: int) -> str:
    """The case color of the ``n``-th line. The combination rotation turns every
    ``len(COMBOS)`` lines, a multiple of the six colors, so a color rotating beside it would
    pair each combination with one color only. This one steps one further at every turn."""
    return tuple(COLORS)[(n + n // len(COMBOS)) % len(COLORS)]


def blade(system: str, size: int) -> tuple[str, float, float]:
    """The published length, the length in inches and the blade width in inches of a
    ``size`` ft (inch) or ``size`` m (metric) tape."""
    if system == "mm":
        return f"{size} m", size * 1000 / MM_PER_INCH, METRIC_WIDTH_MM[size] / MM_PER_INCH
    return f"{size} ft", size * 12.0, INCH_WIDTH[size]


def sizes(system: str) -> tuple[int, ...]:
    """The stocked lengths of ``system``: feet for an inch tape, metres for a metric one."""
    return METRIC_METRES if system == "mm" else INCH_FEET


def _spec(name: str, scope: str, presence: float = 1.0, kind: str = "keyword") -> AttrSpec:
    return AttrSpec(name=name, scope=scope, presence=presence, kind=kind)


VOCAB = (
    _spec("Color", "line"),
    _spec("Material", "line"),
    _spec("Lock", "line"),
    _spec("Length", "sku", kind="length"),
    _spec("Width", "sku", kind="length"),
)


def _make(gen: Any, type_key: str, category: tuple[str, ...]) -> Any:
    # Imported here: generate.py imports the type tables, which discover this module.
    from synthetic_ecommerce_data.core import brands
    from synthetic_ecommerce_data.core.model import keyword_attribute, numeric_attribute
    from synthetic_ecommerce_data.domains.industrial.generate import ChildDraft, LineDraft

    rng = gen.rng
    material, lock, system = COMBOS[gen._rotate(f"combo:{type_key}", len(COMBOS))]
    color = case_color(gen._rotate(f"color:{type_key}", len(COMBOS) * len(COLORS)))
    brand = brands.pick_brand(rng, type_key, gen._exhausted)
    draft = LineDraft(
        item=decoy_item(gen, type_key),
        brand=brand,
        series=f"TM{rng.randint(100, 999)}",
        category=category,
        provenance=PROVENANCE,
    )
    draft.line_attrs = [
        keyword_attribute("Color", color),
        keyword_attribute("Material", material),
        keyword_attribute("Lock", lock),
    ]
    draft.descriptors = [("Color", color)]
    pool = [float(size) for size in sizes(system)]
    count = min(gen._variant_count(), len(pool))
    style = gen._style(system)
    for size in gen._offered_run(f"lengths:{system}:{lock}", pool, count):
        published, length_in, width_in = blade(system, int(size))
        child = ChildDraft(system=system)
        child.primary = numeric_attribute("Length", published, length_in)
        child.attrs = [child.primary, gen._length("Width", width_in, style)]
        draft.children.append(child)
    return draft


#: GENERATED, NOT MEASURED: about 19 USD for a 25 ft (300 in) standard-tier tape, and the
#: length to the 0.55 power.
PRICE = PriceModel(19.0, 300.0, 0.55, 0.3, 0.1, measured=False)


def _inches(record: dict[str, str], name: str) -> float | None:
    """``name`` in inches, read from a feet, metre or inch value; ``None`` when unreadable."""
    value = str(record.get(name, "")).strip()
    for suffix, factor in ((" ft", 12.0), (" m", 1000 / MM_PER_INCH)):
        if value.endswith(suffix):
            try:
                return float(value[: -len(suffix)]) * factor
            except ValueError:
                return None
    try:
        return parse_length(value).inches
    except DimensionParseError:
        return None


def figure(record: dict[str, str]) -> Drawn:
    """The tape from its side: a rounded case sized to the blade it coils (wider and longer
    blades need a bigger case), the lock on top, a belt clip at the back, and the blade out of
    the front with its hook. A rubber-coated case is drawn with its grip band. The case is
    filled with the record's color."""
    width = _inches(record, "Width")
    length = _inches(record, "Length")
    source = "record" if width and length else "partial"
    width = width or 1.0
    length = length or 300.0
    side = 1.5 + 1.2 * width + 0.02 * length / 12.0
    corner = 0.18 * side
    fig = Figure(size_in=side)
    fill = COLORS.get(str(record.get("Color", "")), "#f2c230")
    fig.poly(
        [
            (corner, 0.0),
            (side, 0.0),
            (side, side - corner),
            (side - corner, side),
            (corner, side),
            (0.0, side - corner),
            (0.0, corner),
        ],
        "part",
        fill,
    )
    if record.get("Material") == "Rubber-Coated ABS":
        fig.rect(0.0, 0.3 * side, 0.12 * side, 0.85 * side, "grip", "#3b3b3b")
    fig.rect(0.55 * side, -0.1 * side, 0.8 * side, 0.0, "dark")
    fig.rect(-0.08 * side, 0.2 * side, 0.0, 0.7 * side, "dark")
    reach = 0.6 * side
    fig.rect(side, side - 0.16, side + reach, side - 0.06, "plain")
    fig.rect(side + reach, side - 0.26, side + reach + 0.06, side, "dark")
    return Drawn(fig, source)


SPEC = TypeSpec(
    KEY,
    label=ITEM,
    category=CATEGORY,
    standards_family="hand_tool",
    vocab=VOCAB,
    figure=figure,
    extent=(6.4, 4.2),
    make=_make,
    share=0.0055,
    price=PRICE,
    claims=None,
    may_claim=frozenset(),
    key_attributes=("Length",),
    compat=False,
    use_lines=(
        "Measures rooms, furniture and walls around the house.",
        "Locks the blade out to mark a cut or hang a picture.",
    ),
)
