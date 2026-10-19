"""Nylon-insert lock nuts: the first breadth category deepened into a modelled type (#53).

The spec space is six series a distributor stocks, each a standard's table or,
for inch, a conventional size ladder:

* metric rows are read from FreeCAD_FastenersWB at the commit
  ``core/standards_library/tables/fastener_standards.json`` records: ``iso7040def.csv`` (regular),
  ``iso10512def.csv`` (regular, fine pitch), ``iso10511def.csv`` (thin) and
  ``nyloc_def.csv`` (DIN 985, thin). Width Across Flats is the table's
  ``s_max`` (``s_nom`` for DIN 985) and Height its ``h_max`` (``h``), the
  height over the insert. A metric line claims its table's standard.
* inch rows take the ASME B18.2.2 hex nut's width across flats. No readable
  source gives the inch nylon-insert nut's height (FastenersWB has no ASME
  B18.16.6 table), so an inch SKU publishes no Height and an inch line claims
  no dimensional standard, as the heavy hex nut claims none
  (:func:`...catalog.newtypes.nut_row`).

Every value is read from a table, so ``dimension_provenance`` names, per
published dimension, the standard whose table it came from
(:attr:`Series.provenance`), and never says no standard fixes it.

No pack quantity is published (#14): a line is one nut per SKU.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from fractions import Fraction
from typing import TYPE_CHECKING, Any

from synthetic_ecommerce_data.core import standards_library as library
from synthetic_ecommerce_data.core.model import keyword_attribute, length_attribute
from synthetic_ecommerce_data.core.price import ENDINGS, PriceModel
from synthetic_ecommerce_data.core.typespec import TypeSpec
from synthetic_ecommerce_data.domains.industrial.drafts import retired
from synthetic_ecommerce_data.domains.industrial.drawing.figures import hex_nut
from synthetic_ecommerce_data.domains.industrial.newtypes import (
    MM_PER_INCH,
    _nominal,
    _weighted,
    _window,
    feed_style,
    table_provenance,
)
from synthetic_ecommerce_data.domains.industrial.vocab import AttrSpec

if TYPE_CHECKING:
    from synthetic_ecommerce_data.domains.industrial.generate import LineDraft

#: (Material, Finish, Grade or None): the combinations one series is stocked in.
Combo = tuple[str, str, "str | None"]


@dataclass(frozen=True)
class Series:
    """One stocked series: its rows, its thread type, its style and its combinations."""

    name: str
    system: str
    thread_type: str
    style: str
    #: The dimensional standard every row is read from; empty for inch.
    standard: str
    #: Ranges of (thread, width across flats, height or None), in the series'
    #: unit. A line draws from ONE range: two fine pitches of one diameter
    #: draw alike at a nut's scale and must not be siblings.
    ranges: tuple[tuple[tuple[str, float, float | None], ...], ...]
    combos: tuple[Combo, ...]

    @property
    def provenance(self) -> str:
        """Where each published dimension was read from: the series' own table
        for metric; for inch, the hex nut's widths and no height at all."""
        if self.standard:
            return table_provenance(
                ("Width Across Flats", self.standard), ("Height", self.standard)
            )
        return (
            f"{table_provenance(('Width Across Flats', _INCH_FLATS_STANDARD))}; "
            "no Height is published, as no readable ASME B18.16.6 table gives one"
        )


# --- metric: read from FastenersWB (thread, s_max, h_max), mm --------------------

_ISO_7040 = (
    ("M3x0.5", 5.5, 4.5), ("M4x0.7", 7.0, 6.0), ("M5x0.8", 8.0, 6.8), ("M6x1", 10.0, 8.0),
    ("M8x1.25", 13.0, 9.5), ("M10x1.5", 16.0, 11.9), ("M12x1.75", 18.0, 14.9),
    ("M14x2", 21.0, 17.0), ("M16x2", 24.0, 19.1), ("M20x2.5", 30.0, 22.8),
    ("M24x3", 36.0, 27.1), ("M30x3.5", 46.0, 32.6), ("M36x4", 55.0, 38.9),
)  # fmt: skip
_ISO_10511 = (
    ("M3x0.5", 5.5, 3.9), ("M4x0.7", 7.0, 5.0), ("M5x0.8", 8.0, 5.0), ("M6x1", 10.0, 6.0),
    ("M8x1.25", 13.0, 6.76), ("M10x1.5", 16.0, 8.56), ("M12x1.75", 18.0, 10.23),
    ("M14x2", 21.0, 11.32), ("M16x2", 24.0, 12.42), ("M20x2.5", 30.0, 14.9),
    ("M24x3", 36.0, 17.8), ("M30x3.5", 46.0, 22.2), ("M36x4", 55.0, 25.5),
)  # fmt: skip
#: Two ranges, each naming a diameter once (see :attr:`Series.ranges`).
_ISO_10512 = (
    (
        ("M8x1", 13.0, 9.5), ("M10x1.25", 16.0, 11.9), ("M12x1.5", 18.0, 14.9),
        ("M14x1.5", 21.0, 17.0), ("M16x1.5", 24.0, 19.1), ("M20x1.5", 30.0, 22.8),
        ("M24x2", 36.0, 27.1), ("M30x2", 46.0, 32.6), ("M36x2", 55.0, 38.9),
    ),
    (("M10x1", 16.0, 11.9), ("M12x1.25", 18.0, 14.9)),
)  # fmt: skip
#: (thread, s_nom, h): M3 to M36, without the M7 no distributor stocks.
_DIN_985 = (
    ("M3x0.5", 5.5, 4.0), ("M4x0.7", 7.0, 5.0), ("M5x0.8", 8.0, 5.0), ("M6x1", 10.0, 6.0),
    ("M8x1.25", 13.0, 8.0), ("M10x1.5", 16.0, 10.0), ("M12x1.75", 18.0, 12.0),
    ("M14x2", 22.0, 14.0), ("M16x2", 24.0, 16.0), ("M18x2.5", 27.0, 18.5),
    ("M20x2.5", 30.0, 20.0), ("M22x2.5", 34.0, 22.0), ("M24x3", 36.0, 24.0),
    ("M27x3", 41.0, 27.0), ("M30x3.5", 46.0, 30.0), ("M33x3.5", 50.0, 33.0),
    ("M36x4", 55.0, 36.0),
)  # fmt: skip

# --- inch: the ASME B18.2.2 hex nut's width across flats, inches -----------------

_INCH_FLATS_STANDARD = "ASME B18.2.2"

#: The finished hex nut's widths (ASME B18.2.2), from the standards library: the sizes
#: ``nut_hex`` stocks, then the sizes that table does not carry.
_FLATS_IN = {
    row["size"]: float(Fraction(row["flats_in"]))
    for row in library.table("asme_b18_2_2_hex_nuts_in").select(
        ["#6", "#8", "#10", "1/4", "5/16", "3/8", "7/16", "1/2", "5/8", "3/4", "1"]
        + ["#4", "9/16", "7/8"]
    )
}
_THREADS = library.table("asme_b1_1_unified_threads")
_UNC = tuple(
    f"{row['size']}-{row['unc_tpi']}"
    for row in _THREADS.select(
        ["#4", "#6", "#8", "#10", "1/4", "5/16", "3/8", "7/16", "1/2"]
        + ["9/16", "5/8", "3/4", "7/8", "1"]
    )
)
_UNF = tuple(
    f"{row['size']}-{row['unf_tpi']}"
    for row in _THREADS.select(
        ["#10", "1/4", "5/16", "3/8", "7/16", "1/2", "9/16", "5/8", "3/4", "7/8", "1"]
    )
)
#: The thin inch series starts at 1/4".
_THIN_FROM = "1/4"


def _inch(threads: tuple[str, ...]) -> tuple[tuple[str, float, None], ...]:
    return tuple((t, _FLATS_IN[_nominal(t)], None) for t in threads)


def _thin(threads: tuple[str, ...]) -> tuple[str, ...]:
    return tuple(t for t in threads if not t.startswith("#"))


_STEEL_ZP_PLAIN_8 = (("Steel", "Zinc Plated", "Class 8"), ("Steel", "Plain", "Class 8"))
_ALLOY_ZP_PLAIN_10 = (
    ("Alloy Steel", "Zinc Plated", "Class 10"),
    ("Alloy Steel", "Plain", "Class 10"),
)
_A2 = ("18-8 Stainless Steel", "Plain", None)
_A4 = ("316 Stainless Steel", "Plain", None)
_INCH_COMBOS: tuple[Combo, ...] = (
    ("Steel", "Zinc Plated", "Grade 2"),
    ("Steel", "Plain", "Grade 2"),
    ("Steel", "Zinc Plated", "Grade 5"),
    ("Steel", "Plain", "Grade 5"),
    ("Alloy Steel", "Zinc Yellow", "Grade 8"),
    ("Alloy Steel", "Plain", "Grade 8"),
    _A2,
    _A4,
)

#: (series, weight): how often a line is drafted in each.
SERIES: tuple[tuple[Series, float], ...] = (
    (Series("inch-unc", "in", "UNC", "Standard", "", (_inch(_UNC),), _INCH_COMBOS), 0.24),
    (Series("inch-unf", "in", "UNF", "Standard", "", (_inch(_UNF),), _INCH_COMBOS), 0.16),
    (
        Series(
            "inch-thin-unc",
            "in",
            "UNC",
            "Thin",
            "",
            (_inch(_thin(_UNC)),),
            (("Steel", "Zinc Plated", "Grade 2"), _A2),
        ),
        0.04,
    ),
    (
        Series(
            "inch-thin-unf",
            "in",
            "UNF",
            "Thin",
            "",
            (_inch(_thin(_UNF)),),
            (("Steel", "Zinc Plated", "Grade 2"), _A2),
        ),
        0.04,
    ),
    (
        Series(
            "iso7040",
            "mm",
            "Metric Coarse",
            "Standard",
            "ISO 7040",
            (_ISO_7040,),
            (*_STEEL_ZP_PLAIN_8, *_ALLOY_ZP_PLAIN_10, _A2, _A4),
        ),
        0.17,
    ),
    (
        Series(
            "iso10512",
            "mm",
            "Metric Fine",
            "Standard",
            "ISO 10512",
            _ISO_10512,
            (*_STEEL_ZP_PLAIN_8, *_ALLOY_ZP_PLAIN_10),
        ),
        0.08,
    ),
    (
        Series(
            "iso10511",
            "mm",
            "Metric Coarse",
            "Thin",
            "ISO 10511",
            (_ISO_10511,),
            (("Steel", "Zinc Plated", "Class 04"), ("Steel", "Zinc Plated", "Class 05"), _A2),
        ),
        0.07,
    ),
    (
        Series(
            "din985",
            "mm",
            "Metric Coarse",
            "Thin",
            "DIN 985",
            (_DIN_985,),
            (*_STEEL_ZP_PLAIN_8, ("Alloy Steel", "Zinc Plated", "Class 10"), _A2, _A4),
        ),
        0.20,
    ),
)

ITEM = "Nylon Insert Lock Nut"

#: Generic names, as for the hex nut: ``Type`` for the style (``Nut Style``
#: is refused by the own-noun rule) and ``Height`` for the height.
VOCAB = (
    AttrSpec("Type", "line"),
    AttrSpec("Material", "line"),
    AttrSpec("Finish", "line", 0.9),
    AttrSpec("Grade", "line", 0.9),
    AttrSpec("Thread Type", "line", 0.8),
    AttrSpec("Thread Direction", "line", 0.55),
    AttrSpec("Thread Size", "sku"),
    AttrSpec("Width Across Flats", "sku", kind="length"),
    AttrSpec("Height", "sku", 0.9, kind="length"),
)


def build(gen: Any, type_key: str, category: tuple[str, ...]) -> LineDraft:
    """One line: a series, one of its stocked combinations, a window of its sizes."""
    # Imported here: generate imports the type tables, which discover this module.
    from synthetic_ecommerce_data.core.brands import pick_brand
    from synthetic_ecommerce_data.domains.industrial.generate import BRANDS, ChildDraft, LineDraft

    rng = gen.rng
    brand = pick_brand(rng, type_key, gen._exhausted)
    series = _weighted(rng, SERIES)
    material, finish, grade = rng.choice(series.combos)
    draft = LineDraft(
        item=ITEM,
        brand=brand,
        series=f"NL{rng.randint(100, 999)}",
        category=category,
        provenance=series.provenance,
        standard=series.standard,
    )
    draft.line_attrs = [
        # Retired (#497), listed where they stood so their sparsity draws keep
        # the random stream stable.
        retired(keyword_attribute("Item", ITEM)),
        keyword_attribute("Type", series.style),
        retired(keyword_attribute("Lock Type", "Nylon Insert"), presence=0.8),
        retired(keyword_attribute("Insert Material", "Nylon"), presence=0.7),
        keyword_attribute("Material", material),
        keyword_attribute("Finish", finish),
        keyword_attribute("Thread Type", series.thread_type),
        keyword_attribute("Thread Direction", "Right Hand"),
    ]
    if grade is not None:
        draft.line_attrs.append(keyword_attribute("Grade", grade))
    draft.descriptors = [("Material", material)]
    metric = series.system == "mm"
    style = feed_style(brand, series.system, BRANDS)
    which = gen._rotate(f"lock-nut:{series.name}:range", len(series.ranges))
    rows = list(series.ranges[which])
    for thread, flats, height in _window(
        gen, f"lock-nut:{series.name}:{which}", rows, gen._variant_count()
    ):
        flats_in = flats / MM_PER_INCH if metric else flats
        child = ChildDraft(system=series.system)
        child.primary = keyword_attribute("Thread Size", thread)
        child.attrs = [
            child.primary,
            length_attribute("Width Across Flats", gen._publish(flats_in, style)),
        ]
        if height is not None:
            height_in = height / MM_PER_INCH if metric else height
            child.attrs.append(length_attribute("Height", gen._publish(height_in, style)))
        draft.children.append(child)
    return draft


#: The census slope and endings; the anchor and both sigmas fitted by
#: ``scripts/fit_price_model.py`` to the 100 census nylon-insert nuts
#: (``deep_types.lock_nuts_nylon_insert``). 74% of those prices are pack
#: prices the catalog does not model (a line is one nut per SKU), so the shown
#: price is scored against them as it is for the bolt. One brand carries them,
#: so no brand figure is restated and the drill's tiers apply.
PRICE = PriceModel(
    # @fit-begin lock_nuts_nylon_insert
    anchor=17.18,
    anchor_key=0.4,
    slope=1.2,
    group_sigma=0.022,
    sku_sigma=0.153,
    # @fit-end
    endings=ENDINGS["lock_nuts_nylon_insert"],
)


def claims(facts: Mapping[str, str], *, metric: bool, provenance: str, standard: str) -> list[str]:
    """A metric line's dimensional standard is its table's; an inch line's
    rows are no standard's, so ``standard`` is empty for it."""
    grade = facts.get("Grade", "")
    stainless = "Stainless" in facts.get("Material", "")
    out = [standard]
    # ISO 2320: the prevailing-torque function of steel nuts; ISO 898-2
    # the steel nut's property classes, thin (04, 05) and regular (8, 10).
    if metric and not stainless:
        out.append("ISO 2320")
    if metric and grade.startswith("Class"):
        out.append("ISO 898-2")
    if metric and stainless:
        out.append("ISO 3506-2")
    if not metric and grade.startswith("Grade"):
        out.append("SAE J995")
    return out


SPEC = TypeSpec(
    "lock_nuts_nylon_insert",
    category=("Fasteners", "Nuts", "Nylon Insert Lock Nuts"),
    standards_family="fastener",
    vocab=VOCAB,
    figure=hex_nut,
    # M36 ISO 7040, the largest drawn: 2.50" across corners, 4.78" tall.
    extent=(2.6, 4.9),
    make=build,
    share=0.1,
    price=PRICE,
    claims=claims,
    may_claim=frozenset(
        {"ISO 7040", "ISO 10511", "ISO 10512", "DIN 985", "ISO 2320", "ISO 898-2", "ISO 3506-2"}
        | {"SAE J995"}
    ),
    key_attributes=("Thread Size",),
    threaded="Thread Size",
    fastener=True,
    compat=("nut", "Thread Size"),
    use_lines=(
        "The nylon insert grips the thread, so the nut resists loosening under vibration.",
        "Threads onto a bolt or a screw of the same size.",
    ),
)
