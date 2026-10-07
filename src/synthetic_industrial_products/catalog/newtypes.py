"""The product types added by elastic/prism-industrial-products#103, stage 1.

Four types, chosen so a one-word search crosses unrelated branches of the tree
(the "ball" and "hex" and "wheel" collisions the maintainer asked for):

=========================  =====================================================
``nut_hex``                Fasteners > Nuts > Hex Nuts                      (hex)
``bearing_radial_ball``    Motion Control & Fluid Power > Bearings >
                           Radial Ball Bearings                            (ball)
``wheel_depressed_center`` Abrasives > Grinding & Cut-Off > Grinding &
                           Cut-Off Wheels > Depressed-Center Wheels       (wheel)
``hex_key``                Hand Tools > Screwdrivers & Hex Keys > Hex & Torx
                           Keys > Hex Keys & Accessories > Hex Keys  (hex, ball)
=========================  =====================================================

How these differ from the original twelve, deliberately:

* **Each brand's feed spells lengths its own way** (:func:`feed_style`): one
  brand writes ``3/8"``, another ``3/8 in``, another ``0.375"``. Consistent
  within a brand, different across brands -- the variation between supplier
  feeds that the census records (maintainer ruling D4, 2026-09-28). The
  original twelve keep the catalog's single spelling.
* **Attribute names are the census's generic ones** (:mod:`.names`).
* **Dimensions are generated from conventional sizes.** The values follow the
  familiar size ladders (the 60/62/63 bearing series boundary sizes, stocked
  wheel diameters, hex key sizes), so the provenance field says "generated".
  The exception is the hex nut, whose finished and jam rows are standards'
  table rows (checked against FreeCAD_FastenersWB, see :func:`nut_row`): its
  provenance names the table each published dimension was read from
  (:func:`nut_provenance`), and a line whose every row is one standard's
  claims that standard. A heavy hex nut, whose sizes are derived, claims none.
"""

from __future__ import annotations

import random
from collections.abc import Callable
from dataclasses import dataclass
from fractions import Fraction
from typing import TYPE_CHECKING

from .formats import LengthStyle
from .model import keyword_attribute, length_attribute, multi_attribute, numeric_attribute

if TYPE_CHECKING:
    from .generate import Generator, LineDraft

MM_PER_INCH = 25.4

#: What a provenance says when no standard gives its values. A line that
#: claims a dimensional standard never says it (``tests/type_gates.py``).
NO_STANDARD = "no standard fixes these values"

GENERATED_PROVENANCE = f"generated from conventional sizes; {NO_STANDARD}"


def table_provenance(*sources: tuple[str, str]) -> str:
    """``dimension_provenance`` for dimensions read from standards' tables.

    ``sources`` pairs each published dimension with the standard whose table
    it was read from; dimensions from one table are named together, as
    ``Width Across Flats and Height read from the ISO 7040 table``.
    """
    by_table: dict[str, list[str]] = {}
    for dimension, standard in sources:
        by_table.setdefault(standard, []).append(dimension)
    return "; ".join(
        f"{' and '.join(dims)} read from the {standard} table"
        for standard, dims in by_table.items()
    )


#: How each brand's feed writes lengths: the inch style and the metric style.
#: Each is a spelling the census observes (07_value_format_variation.json).
_FEEDS: tuple[tuple[LengthStyle, LengthStyle], ...] = (
    (LengthStyle("in", '"', "fraction"), LengthStyle("mm", "mm", "integer")),
    (LengthStyle("in", " in", "fraction"), LengthStyle("mm", " mm", "integer")),
    (LengthStyle("in", '"', "decimal", places=3), LengthStyle("mm", "mm", "decimal", places=2)),
    (LengthStyle("in", " in.", "fraction"), LengthStyle("mm", " mm", "decimal", places=1)),
)


def feed_style(brand: str, system: str, brands: tuple[str, ...]) -> LengthStyle:
    inch, metric = _FEEDS[brands.index(brand) % len(_FEEDS)]
    return inch if system == "in" else metric


def _weighted(rng: random.Random, table):
    return rng.choices([v for v, _ in table], weights=[w for _, w in table], k=1)[0]


def _window(gen: Generator, key: str, pool: list, count: int) -> list:
    """A contiguous run of ``count`` from ``pool`` at a rotating start: full coverage."""
    count = max(1, min(count, len(pool)))
    start = gen._rotate(key, len(pool))
    return [pool[(start + k) % len(pool)] for k in range(count)]


@dataclass(frozen=True)
class NewType:
    category: tuple[str, ...]
    build: Callable[[Generator, str, tuple[str, ...]], LineDraft]
    standards_family: str


# --- hex nuts ------------------------------------------------------------------

#: (thread, width across flats in, height in) -- finished hex nuts, inch.
_NUT_UNC = (
    ("#6-32", 5 / 16, 7 / 64),
    ("#8-32", 11 / 32, 1 / 8),
    ("#10-24", 3 / 8, 1 / 8),
    ("1/4-20", 7 / 16, 7 / 32),
    ("5/16-18", 1 / 2, 17 / 64),
    ("3/8-16", 9 / 16, 21 / 64),
    ("7/16-14", 11 / 16, 3 / 8),
    ("1/2-13", 3 / 4, 7 / 16),
    ("5/8-11", 15 / 16, 35 / 64),
    ("3/4-10", 1 + 1 / 8, 41 / 64),
    ("1-8", 1 + 1 / 2, 55 / 64),
)
_NUT_UNF = (
    ("#10-32", 3 / 8, 1 / 8),
    ("1/4-28", 7 / 16, 7 / 32),
    ("5/16-24", 1 / 2, 17 / 64),
    ("3/8-24", 9 / 16, 21 / 64),
    ("1/2-20", 3 / 4, 7 / 16),
)
#: (thread, width across flats mm, height mm) -- metric.
_NUT_METRIC = (
    ("M3x0.5", 5.5, 2.4),
    ("M4x0.7", 7.0, 3.2),
    ("M5x0.8", 8.0, 4.7),
    ("M6x1", 10.0, 5.2),
    ("M8x1.25", 13.0, 6.8),
    ("M10x1.5", 16.0, 8.4),
    ("M12x1.75", 18.0, 10.8),
    ("M16x2", 24.0, 14.8),
    ("M20x2.5", 30.0, 18.0),
    ("M24x3", 36.0, 21.5),
)

#: Metric FINE-pitch hex nuts (ISO 8673): the coarse nut's width across flats
#: and height over an ISO 262 fine thread -- the near-miss pitches a bolt of
#: the same diameter comes in (:data:`.compat.METRIC_FINE_PITCHES`).
#:
#: Two ranges, each naming a diameter ONCE. M10x1.25 and M10x1 are the same
#: drawing at a nut's scale -- a pitch is not visible across its flats -- so
#: one line offering both would put two identical pictures side by side
#: (``test_siblings_whose_drawn_values_differ_never_draw_alike``). A line is
#: one range or the other.
_NUT_METRIC_FINE = (
    (
        ("M8x1", 13.0, 6.8),
        ("M10x1.25", 16.0, 8.4),
        ("M12x1.5", 18.0, 10.8),
        ("M16x1.5", 24.0, 14.8),
        ("M20x1.5", 30.0, 18.0),
    ),
    (
        ("M10x1", 16.0, 8.4),
        ("M12x1.25", 18.0, 10.8),
        ("M20x2", 30.0, 18.0),
    ),
)


#: The dimensional standard each FINISHED-hex table above reproduces, row for
#: row (checked against FreeCAD_FastenersWB at the commit
#: ``data/fastener_standards.json`` records: ``iso4032def.csv``,
#: ``iso8673def.csv``, and ``asmeb18.2.2.4def.csv`` / ``asmeb18.2.2.1def.csv``
#: -- ASME B18.2.2 carries the #6-#10 hex machine screw nuts too).
_FINISHED_STANDARD = {
    ("mm", False): "ISO 4032",
    ("mm", True): "ISO 8673",
    ("in", False): "ASME B18.2.2",
    ("in", True): "ASME B18.2.2",
}

#: A jam (thin) nut keeps its finished nut's width across flats and takes the
#: height its OWN standard gives, per nominal diameter. Read from the same
#: FastenersWB commit: ``iso4035def.csv`` (coarse) and ``iso8675def.csv``
#: (fine; the same heights per diameter), and ``asmeb18.2.2.4def.csv``'s jam
#: column. ASME B18.2.2 has no jam nut below 1/4", so a #6-#10 jam nut keeps
#: a derived height and claims no dimensional standard.
_JAM_HEIGHT_MM = {
    "M3": 1.8, "M4": 2.2, "M5": 2.7, "M6": 3.2, "M8": 4.0, "M10": 5.0,
    "M12": 6.0, "M16": 8.0, "M20": 10.0, "M24": 12.0,
}  # fmt: skip
_JAM_HEIGHT_IN = {
    "1/4": 5 / 32, "5/16": 3 / 16, "3/8": 7 / 32, "7/16": 1 / 4, "1/2": 5 / 16,
    "5/8": 3 / 8, "3/4": 27 / 64, "1": 35 / 64,
}  # fmt: skip
_JAM_STANDARD = {
    ("mm", False): "ISO 4035",
    ("mm", True): "ISO 8675",
    ("in", False): "ASME B18.2.2",
    ("in", True): "ASME B18.2.2",
}


def _nominal(thread: str) -> str:
    """``M12x1.75`` -> ``M12``; ``1/2-13`` -> ``1/2``."""
    return thread.split("x")[0] if thread.startswith("M") else thread.split("-")[0]


def nut_row(
    style_name: str, thread: str, flats: float, height: float, *, metric: bool, fine: bool
) -> tuple[float, float, str]:
    """A nut's (width across flats, height) in the table's unit, and the
    dimensional standard those two values ARE -- or ``""`` when they are not
    any standard's row.

    A standard is claimed only for a row read from it. A heavy hex nut's
    dimensions here are DERIVED from the finished nut's (wider across flats,
    10% taller); they match neither ISO 4033 (the finished nut's widths, a
    taller height) nor the structural heavy hex series, so a heavy hex nut
    claims no dimensional standard at all.
    """
    system = "mm" if metric else "in"
    if style_name == "Heavy Hex":
        return flats + (2.0 if metric else 1 / 8), height * 1.1, ""
    if style_name == "Jam":
        table = _JAM_HEIGHT_MM if metric else _JAM_HEIGHT_IN
        jam = table.get(_nominal(thread))
        if jam is None:
            return flats, height * 0.6, ""
        return flats, jam, _JAM_STANDARD[(system, fine)]
    return flats, height, _FINISHED_STANDARD[(system, fine)]


def nut_provenance(style_name: str, system: str, fine: bool, row_standards: set[str]) -> str:
    """Where a hex nut line's Width Across Flats and Height came from.

    ``row_standards`` holds what :func:`nut_row` returned for the line's rows:
    a standard for a row read from its table, ``""`` for a derived one.
    """
    finished = _FINISHED_STANDARD[(system, fine)]
    if style_name == "Heavy Hex":
        wider = "2 mm" if system == "mm" else "1/8 in"
        return (
            f"Width Across Flats and Height derived from the {finished} table "
            f"({wider} wider, 10% taller); {NO_STANDARD}"
        )
    if style_name != "Jam":
        return table_provenance(("Width Across Flats", finished), ("Height", finished))
    jam = _JAM_STANDARD[(system, fine)]
    if "" not in row_standards:
        return table_provenance(("Width Across Flats", finished), ("Height", jam))
    derived = (
        f"60% of the {finished} finished nut's height where the {jam} jam nut table "
        "has no row; no standard fixes those heights"
    )
    if jam in row_standards:
        return (
            f"{table_provenance(('Width Across Flats', finished), ('Height', jam))}, or {derived}"
        )
    return f"{table_provenance(('Width Across Flats', finished))}; Height {derived}"


def build_nut(gen: Generator, type_key: str, category: tuple[str, ...]) -> LineDraft:
    from .brands import pick_brand
    from .generate import BRANDS, ChildDraft, LineDraft

    rng = gen.rng
    brand = pick_brand(rng, type_key, gen._exhausted)
    metric = rng.random() < 0.3
    fine = rng.random() < 0.25
    style_name = _weighted(rng, (("Finished Hex", 0.7), ("Heavy Hex", 0.15), ("Jam", 0.15)))
    material = _weighted(
        rng,
        (
            ("Steel", 0.45),
            ("18-8 Stainless Steel", 0.25),
            ("316 Stainless Steel", 0.08),
            ("Brass", 0.07),
            ("Alloy Steel", 0.15),
        ),
    )
    stainless = "Stainless" in material
    if material in ("Steel", "Alloy Steel"):
        finish = _weighted(
            rng,
            (("Zinc Plated", 0.45), ("Plain", 0.2), ("Black Oxide", 0.15), ("Zinc Yellow", 0.2)),
        )
    else:
        finish = "Plain"
    grades = {
        (True, "Alloy Steel"): "Class 10",
        (True, "Steel"): "Class 8",
        (False, "Alloy Steel"): "Grade 8",
        (False, "Steel"): "Grade 5",
    }
    # Stainless and brass nuts carry no strength grade.
    grade = None if stainless else grades.get((metric, material))
    item = {"Finished Hex": "Hex Nut", "Heavy Hex": "Heavy Hex Nut", "Jam": "Hex Jam Nut"}[
        style_name
    ]
    draft = LineDraft(
        item=item,
        brand=brand,
        series=f"HN{rng.randint(100, 999)}",
        category=category,
    )
    draft.line_attrs = [
        keyword_attribute("Item", item),
        keyword_attribute("Type", style_name),
        keyword_attribute("Material", material),
        keyword_attribute("Finish", finish),
        keyword_attribute(
            "Thread Type",
            ("Metric Fine" if fine else "Metric Coarse") if metric else ("UNF" if fine else "UNC"),
        ),
        keyword_attribute("Thread Direction", "Right Hand"),
        numeric_attribute("Package Quantity", str(qty := rng.choice((25, 50, 100))), float(qty)),
    ]
    if grade is not None:
        draft.line_attrs.append(keyword_attribute("Grade", grade))
    draft.descriptors = [("Material", material)]
    system = "mm" if metric else "in"
    style = feed_style(brand, system, BRANDS)
    if metric and fine:
        fine_range = gen._rotate("nut:metric-fine-range", len(_NUT_METRIC_FINE))
        table = _NUT_METRIC_FINE[fine_range]
        key = f"nut:mm:fine{fine_range}"
    else:
        table = _NUT_METRIC if metric else (_NUT_UNF if fine else _NUT_UNC)
        key = f"nut:{system}:{'fine' if fine else 'coarse'}"
    row_standards: set[str] = set()
    for thread, table_flats, table_height in _window(gen, key, list(table), gen._variant_count()):
        flats, height, row_standard = nut_row(
            style_name, thread, table_flats, table_height, metric=metric, fine=fine
        )
        row_standards.add(row_standard)
        flats_in = flats / MM_PER_INCH if metric else flats
        height_in = height / MM_PER_INCH if metric else height
        child = ChildDraft(system=system)
        child.primary = keyword_attribute("Thread Size", thread)
        child.attrs = [
            child.primary,
            length_attribute("Width Across Flats", gen._publish(flats_in, style)),
            length_attribute("Height", gen._publish(height_in, style)),
        ]
        draft.children.append(child)
    draft.provenance = nut_provenance(style_name, system, fine, row_standards)
    # The line claims a dimensional standard only when EVERY row it offers is
    # that standard's: one #10 jam nut in a 1/4-1/2 window makes it claim none.
    if len(row_standards) == 1:
        draft.standard = row_standards.pop()
    return draft


# --- radial ball bearings --------------------------------------------------------

#: (bearing number, bore mm, outside dia mm, width mm) -- the 60/62/63 series,
#: from the small single-digit bores (5 to 9 mm) through 100 mm. The boundary
#: dimensions are ISO 15's for each number's diameter series; the bore is the
#: one its bore code names (a single digit is the bore in mm; 00, 01, 02 and 03
#: are 10, 12, 15 and 17 mm; 04 and up are five times the code). A distributor
#: stocks these sizes miniature through large bore: the 10-35 mm ladder alone
#: spread a catalog's bores 3x where the census's bearing prices spread 16.1x
#: (#64). A number is left out where the ratings' maker (below) does not
#: publish the open bearing, never given a made-up rating: SKF lists 628 only
#: with seals or shields.
_BEARINGS_METRIC = (
    ("607", 7, 19, 6),
    ("608", 8, 22, 7),
    ("609", 9, 24, 7),
    ("625", 5, 16, 5),
    ("626", 6, 19, 6),
    ("627", 7, 22, 7),
    ("629", 9, 26, 8),
    ("6000", 10, 26, 8),
    ("6001", 12, 28, 8),
    ("6002", 15, 32, 9),
    ("6003", 17, 35, 10),
    ("6004", 20, 42, 12),
    ("6005", 25, 47, 12),
    ("6006", 30, 55, 13),
    ("6007", 35, 62, 14),
    ("6008", 40, 68, 15),
    ("6009", 45, 75, 16),
    ("6010", 50, 80, 16),
    ("6011", 55, 90, 18),
    ("6012", 60, 95, 18),
    ("6013", 65, 100, 18),
    ("6014", 70, 110, 20),
    ("6015", 75, 115, 20),
    ("6016", 80, 125, 22),
    ("6017", 85, 130, 22),
    ("6018", 90, 140, 24),
    ("6019", 95, 145, 24),
    ("6020", 100, 150, 24),
    ("6200", 10, 30, 9),
    ("6201", 12, 32, 10),
    ("6202", 15, 35, 11),
    ("6203", 17, 40, 12),
    ("6204", 20, 47, 14),
    ("6205", 25, 52, 15),
    ("6206", 30, 62, 16),
    ("6207", 35, 72, 17),
    ("6208", 40, 80, 18),
    ("6209", 45, 85, 19),
    ("6210", 50, 90, 20),
    ("6211", 55, 100, 21),
    ("6212", 60, 110, 22),
    ("6213", 65, 120, 23),
    ("6214", 70, 125, 24),
    ("6215", 75, 130, 25),
    ("6216", 80, 140, 26),
    ("6217", 85, 150, 28),
    ("6218", 90, 160, 30),
    ("6219", 95, 170, 32),
    ("6220", 100, 180, 34),
    ("6300", 10, 35, 11),
    ("6301", 12, 37, 12),
    ("6302", 15, 42, 13),
    ("6303", 17, 47, 14),
    ("6304", 20, 52, 15),
    ("6305", 25, 62, 17),
    ("6306", 30, 72, 19),
    ("6307", 35, 80, 21),
    ("6308", 40, 90, 23),
    ("6309", 45, 100, 25),
    ("6310", 50, 110, 27),
    ("6311", 55, 120, 29),
    ("6312", 60, 130, 31),
    ("6313", 65, 140, 33),
    ("6314", 70, 150, 35),
    ("6315", 75, 160, 37),
    ("6316", 80, 170, 39),
    ("6317", 85, 180, 41),
    ("6318", 90, 190, 43),
    ("6319", 95, 200, 45),
    ("6320", 100, 215, 47),
)
#: (bearing number, bore in, outside dia in, width in) -- inch R series.
_BEARINGS_INCH = (
    ("R4", 1 / 4, 5 / 8, 0.196),
    ("R6", 3 / 8, 7 / 8, 0.2812),
    ("R8", 1 / 2, 1 + 1 / 8, 0.3125),
    ("R10", 5 / 8, 1 + 3 / 8, 0.3438),
    ("R12", 3 / 4, 1 + 5 / 8, 0.4375),
)
#: Load ratings and limiting speed, per bearing number: (dynamic C kN, static
#: C0 kN, limiting speed rpm for the OPEN bearing). A TABLE, not a formula:
#: every metric row is one maker's on one basis, SKF's deep groove ball
#: bearing product pages (``https://www.skf.com/group/products/rolling-
#: bearings/ball-bearings/deep-groove-ball-bearings/productid-<number>``,
#: retrieved 2026-10-07), because two makers' speed ratings are not on one
#: basis and a table that mixes them breaks the series' order at the seam.
#: The inch R rows are the figures distributors list for the R series. No
#: jitter: two bearings of one number are rated alike, whoever makes them, and
#: a rating is never what makes two SKUs different.
BEARING_RATINGS: dict[str, tuple[float, float, int]] = {
    "607": (2.34, 0.95, 53000),
    "608": (3.45, 1.37, 48000),
    "609": (3.90, 1.66, 43000),
    "625": (1.14, 0.38, 60000),
    "626": (2.34, 0.95, 50000),
    "627": (3.45, 1.37, 45000),
    "629": (4.75, 1.96, 38000),
    "6000": (4.75, 1.96, 40000),
    "6001": (5.40, 2.36, 38000),
    "6002": (5.85, 2.85, 32000),
    "6003": (6.37, 3.25, 28000),
    "6004": (9.95, 5.00, 24000),
    "6005": (11.9, 6.55, 20000),
    "6006": (13.8, 8.30, 17000),
    "6007": (16.8, 10.2, 15000),
    "6008": (17.8, 11.0, 14000),
    "6009": (22.1, 14.6, 12000),
    "6010": (22.9, 16.0, 11000),
    "6011": (29.6, 21.2, 10000),
    "6012": (30.7, 23.2, 9500),
    "6013": (31.9, 25.0, 9000),
    "6014": (39.7, 31.0, 8000),
    "6015": (41.6, 33.5, 7500),
    "6016": (49.4, 40.0, 7000),
    "6017": (52.0, 43.0, 6700),
    "6018": (60.5, 50.0, 6300),
    "6019": (63.7, 54.0, 6000),
    "6020": (63.7, 54.0, 5600),
    "6200": (5.40, 2.36, 36000),
    "6201": (7.28, 3.10, 32000),
    "6202": (8.06, 3.75, 28000),
    "6203": (9.95, 4.75, 24000),
    "6204": (13.5, 6.55, 20000),
    "6205": (14.8, 7.80, 18000),
    "6206": (20.3, 11.2, 15000),
    "6207": (27.0, 15.3, 13000),
    "6208": (32.5, 19.0, 11000),
    "6209": (35.1, 21.6, 11000),
    "6210": (37.1, 23.2, 10000),
    "6211": (46.2, 29.0, 9000),
    "6212": (55.3, 36.0, 8000),
    "6213": (58.5, 40.5, 7500),
    "6214": (63.7, 45.0, 7000),
    "6215": (68.9, 49.0, 6700),
    "6216": (72.8, 55.0, 6000),
    "6217": (87.1, 64.0, 5600),
    "6218": (101.0, 73.5, 5300),
    "6219": (114.0, 81.5, 5000),
    "6220": (127.0, 93.0, 4800),
    "6300": (8.52, 3.40, 32000),
    "6301": (10.1, 4.15, 28000),
    "6302": (11.9, 5.40, 24000),
    "6303": (14.3, 6.55, 22000),
    "6304": (16.8, 7.80, 19000),
    "6305": (23.4, 11.6, 16000),
    "6306": (29.6, 16.0, 13000),
    "6307": (35.1, 19.0, 12000),
    "6308": (42.3, 24.0, 11000),
    "6309": (55.3, 31.5, 9500),
    "6310": (65.0, 38.0, 8500),
    "6311": (74.1, 45.0, 8000),
    "6312": (85.2, 52.0, 7000),
    "6313": (97.5, 60.0, 6700),
    "6314": (111.0, 68.0, 6300),
    "6315": (119.0, 76.5, 5600),
    "6316": (130.0, 86.5, 5300),
    "6317": (140.0, 96.5, 5000),
    "6318": (151.0, 108.0, 4800),
    "6319": (159.0, 118.0, 4500),
    "6320": (174.0, 140.0, 4300),
    "R4": (1.14, 0.46, 48000),
    "R6": (3.30, 1.40, 36000),
    "R8": (5.07, 2.37, 28000),
    "R10": (6.23, 3.30, 24000),
    "R12": (9.36, 4.80, 20000),
}
LBF_PER_KN = 224.809

#: Closures: name, part-number suffix, the limiting-speed factor against the
#: open bearing (a shield does not touch the inner ring and leaves it as is; a
#: contact seal rubs and lowers it -- the makers' tables list the sealed
#: variant at about 70%), and the draw weight.
_CLOSURES = (
    ("Double Seal", "-2RS", 0.70, 0.45),
    ("Double Shield", "-ZZ", 1.0, 0.35),
    ("Open", "", 1.0, 0.20),
)


def build_bearing(gen: Generator, type_key: str, category: tuple[str, ...]) -> LineDraft:
    from .brands import pick_brand
    from .generate import BRANDS, ChildDraft, LineDraft

    rng = gen.rng
    brand = pick_brand(rng, type_key, gen._exhausted)
    inch = rng.random() < 0.18
    table = _BEARINGS_INCH if inch else _BEARINGS_METRIC
    number, bore, od, width = table[gen._rotate(f"bearing:{inch}", len(table))]
    to_in = 1.0 if inch else 1 / MM_PER_INCH
    bore_in, od_in, width_in = bore * to_in, od * to_in, width * to_in
    system = "in" if inch else "mm"
    style = feed_style(brand, system, BRANDS)
    material = _weighted(rng, (("Chrome Steel", 0.8), ("440C Stainless Steel", 0.2)))
    dynamic_kn, static_kn, limit = BEARING_RATINGS[number]
    dynamic = int(round(dynamic_kn * LBF_PER_KN, -1))
    static = int(round(static_kn * LBF_PER_KN, -1))
    item = "Radial Ball Bearing"
    draft = LineDraft(
        item=item,
        brand=brand,
        # The product's own series, NOT the bearing number: a series is an
        # identifier the uniqueness walk may renumber, and a bearing number is
        # a fact about the part (its bore, OD and width) that must never move.
        series=f"RB{rng.randint(100, 999)}",
        category=category,
        provenance=GENERATED_PROVENANCE,
    )
    draft.line_attrs = [
        keyword_attribute("Item", item),
        keyword_attribute("Type", "Deep Groove"),
        keyword_attribute("Bearing Number", number),
        # The bearing series (60/62/63, or R for the inch series). It shares a
        # sanitised key with the product's own ``series`` column; the flat field
        # map namespaces it (``attr_series``) rather than drop it.
        keyword_attribute("Series", "R" if inch else number[:2]),
        length_attribute("Bore Dia.", gen._publish(bore_in, style)),
        length_attribute("Outside Dia.", gen._publish(od_in, style)),
        length_attribute("Width", gen._publish(width_in, style)),
        keyword_attribute("Material", material),
        keyword_attribute("Cage Material", rng.choice(("Steel", "Nylon", "Brass"))),
        keyword_attribute(
            "ABEC Rating", _weighted(rng, (("ABEC 1", 0.5), ("ABEC 3", 0.35), ("ABEC 5", 0.15)))
        ),
        keyword_attribute("Row Type", "Single Row"),
        keyword_attribute("Lubricant", "Grease"),
        numeric_attribute("Dynamic Load Capacity", f"{dynamic:,} lbf", float(dynamic)),
        numeric_attribute("Static Load Capacity", f"{static:,} lbf", float(static)),
    ]
    draft.descriptors = [("Material", material)]
    count = min(gen._variant_count(), len(_CLOSURES))
    pool = list(_CLOSURES)
    chosen = []
    for _ in range(count):
        pick = _weighted(rng, [(c, c[3]) for c in pool])
        pool.remove(pick)
        chosen.append(pick)
    for name, _, speed, _ in chosen:
        rpm = int(round(limit * speed, -2))
        child = ChildDraft(system=system)
        child.primary = keyword_attribute("Closure Type", name)
        child.attrs = [child.primary, numeric_attribute("Max. RPM", f"{rpm:,}", float(rpm))]
        draft.children.append(child)
    return draft


# --- depressed-center wheels -----------------------------------------------------

#: (diameter in, maximum rpm) -- stocked sizes and their rated speeds.
_WHEELS = ((4.0, 15200), (4.5, 13300), (5.0, 12200), (6.0, 10200), (7.0, 8600), (9.0, 6600))
_GRITS = (24, 36, 46, 60, 80, 120)


def build_wheel(gen: Generator, type_key: str, category: tuple[str, ...]) -> LineDraft:
    from .brands import pick_brand
    from .generate import BRANDS, ChildDraft, LineDraft

    rng = gen.rng
    brand = pick_brand(rng, type_key, gen._exhausted)
    style = feed_style(brand, "in", BRANDS)
    dia, rpm = _WHEELS[gen._rotate("wheel:dia", len(_WHEELS))]
    cutting = rng.random() < 0.3
    thickness = 1 / 8 if cutting else rng.choice((1 / 4, 1 / 4, 3 / 16))
    hub = dia <= 5.0 and rng.random() < 0.25
    arbor = 7 / 8
    shape = "Type 27" if rng.random() < 0.8 else "Type 28"
    abrasive = _weighted(
        rng,
        (
            ("Aluminum Oxide", 0.45),
            ("Zirconia Alumina", 0.3),
            ("Ceramic", 0.15),
            ("Silicon Carbide", 0.1),
        ),
    )
    item = "Depressed-Center Wheel"
    draft = LineDraft(
        item=item,
        brand=brand,
        series=f"DC{rng.randint(100, 999)}",
        category=category,
        provenance=GENERATED_PROVENANCE,
    )
    draft.line_attrs = [
        keyword_attribute("Item", item),
        keyword_attribute("Type", shape),
        length_attribute("Diameter", gen._publish(dia, style)),
        length_attribute("Thickness", gen._publish(thickness, style)),
        length_attribute("Arbor Hole", gen._publish(arbor, style)),
        keyword_attribute("Connector Type", "5/8-11 Hub" if hub else "Arbor"),
        keyword_attribute("Abrasive Material", abrasive),
        keyword_attribute("Bond Type", "Resinoid" if rng.random() < 0.9 else "Vitrified"),
        numeric_attribute("Max. RPM", f"{rpm:,}", float(rpm)),
        keyword_attribute("Application", "Cutting & Grinding" if cutting else "Grinding"),
        numeric_attribute("Package Quantity", str(qty := rng.choice((10, 25))), float(qty)),
    ]
    draft.descriptors = [("Abrasive Material", abrasive)]
    for grit in sorted(_window(gen, f"wheel:grit:{dia}", list(_GRITS), gen._variant_count())):
        child = ChildDraft(system="in")
        child.primary = numeric_attribute("Grit", str(grit), float(grit))
        grade = "Coarse" if grit <= 36 else ("Medium" if grit <= 60 else "Fine")
        child.attrs = [child.primary, keyword_attribute("Grade", grade)]
        draft.children.append(child)
    return draft


# --- hex keys ----------------------------------------------------------------------

_KEY_INCH = (
    0.050,
    1 / 16,
    5 / 64,
    3 / 32,
    7 / 64,
    1 / 8,
    9 / 64,
    5 / 32,
    3 / 16,
    7 / 32,
    1 / 4,
    5 / 16,
    3 / 8,
    1 / 2,
)
_KEY_MM = (1.5, 2.0, 2.5, 3.0, 4.0, 5.0, 6.0, 8.0, 10.0, 12.0)


def build_hex_key(gen: Generator, type_key: str, category: tuple[str, ...]) -> LineDraft:
    from .brands import pick_brand
    from .generate import BRANDS, ChildDraft, LineDraft

    rng = gen.rng
    brand = pick_brand(rng, type_key, gen._exhausted)
    metric = rng.random() < 0.4
    system = "mm" if metric else "in"
    style = feed_style(brand, system, BRANDS)
    ball = rng.random() < 0.4
    long_arm = rng.random() < 0.5
    material = _weighted(
        rng,
        (("Alloy Steel", 0.5), ("Chrome Vanadium Steel", 0.3), ("S2 Tool Steel", 0.2)),
    )
    finish = _weighted(rng, (("Black Oxide", 0.55), ("Chrome Plated", 0.3), ("Bright", 0.15)))
    item = "Ball End Hex Key" if ball else "Hex Key"
    draft = LineDraft(
        item=item,
        brand=brand,
        series=f"{'LB' if long_arm else 'SB'}{rng.randint(10, 99)}",
        category=category,
        provenance=GENERATED_PROVENANCE,
    )
    draft.line_attrs = [
        keyword_attribute("Item", item),
        keyword_attribute("Type", "L-Key"),
        keyword_attribute("Tip Style", "Ball End" if ball else "Hex End"),
        keyword_attribute("Material", material),
        keyword_attribute("Finish", finish),
    ]
    draft.descriptors = [("Tip Style", "Ball End" if ball else "Hex End")]
    pool = [s / MM_PER_INCH for s in _KEY_MM] if metric else list(_KEY_INCH)
    for size_in in _window(gen, f"key:{system}", pool, gen._variant_count()):
        oal = (1.8 + 14 * size_in) if long_arm else (1.2 + 9 * size_in)
        width = 0.45 + 3 * size_in
        child = ChildDraft(system=system)
        child.primary = length_attribute("Size", gen._publish(size_in, style))
        oal_attr = length_attribute("Overall Length", gen._publish(round(oal * 16) / 16, style))
        child.attrs = [
            child.primary,
            oal_attr,
            length_attribute("Overall Width", gen._publish(round(width * 16) / 16, style)),
        ]
        child.secondary = {"other_length": oal_attr}
        draft.children.append(child)
    return draft


# --- assortment kits -----------------------------------------------------------------


def _sixty_fourths(lo: int, hi: int) -> tuple[float, ...]:
    return tuple(float(Fraction(n, 64)) for n in range(lo, hi + 1))


@dataclass(frozen=True)
class Kit:
    """One assortment: its kind, the part type it holds, and the sizes, in inches.

    A kit is ONE SKU. What it holds is its own ``Sizes Included`` field (a
    multi-valued attribute listing every size) and its own ``Number of Pieces`` --
    a real field, so pack wording is allowed on it. It never shares a
    product id with the individual parts, and is not a grouping of them: a
    grouped product offers its sizes as separately purchasable variants, a kit
    sells them together as one item. The sets are the conventional ones a
    distributor lists; a size a set holds need not be sold singly (the
    0.028" and 0.7mm keys of a full set are not), and a size sold singly need
    not be in any set (the 12mm key is not).
    """

    item: str
    part_type: str
    system: str  # "in" or "mm"
    sizes: tuple[float, ...]  # inches, or for a screw assortment the thread designations' diameters
    per_size: int = 1
    designations: tuple[str, ...] = ()


KITS: tuple[Kit, ...] = (
    # ISO 2936 metric key sets. The 12-piece precision set starts below the
    # smallest key the catalog sells singly (1.5mm): 0.7, 0.9 and 1.3mm.
    Kit(
        "Hex Key Set",
        "hex_key",
        "mm",
        tuple(k / MM_PER_INCH for k in (1.5, 2, 2.5, 3, 4, 5, 6, 8, 10)),
    ),
    Kit("Hex Key Set", "hex_key", "mm", tuple(k / MM_PER_INCH for k in (2, 2.5, 3, 4, 5, 6, 8))),
    Kit(
        "Hex Key Set",
        "hex_key",
        "mm",
        tuple(k / MM_PER_INCH for k in (0.7, 0.9, 1.3, 1.5, 2, 2.5, 3, 4, 5, 6, 8, 10)),
    ),
    # ASME B18.3 inch key sets; the 15-piece set starts at 0.028" and 0.035",
    # which the catalog does not sell singly.
    Kit(
        "Hex Key Set",
        "hex_key",
        "in",
        (
            0.028,
            0.035,
            0.050,
            1 / 16,
            5 / 64,
            3 / 32,
            7 / 64,
            1 / 8,
            9 / 64,
            5 / 32,
            3 / 16,
            7 / 32,
            1 / 4,
            5 / 16,
            3 / 8,
        ),
    ),
    Kit(
        "Hex Key Set",
        "hex_key",
        "in",
        (5 / 64, 3 / 32, 1 / 8, 5 / 32, 3 / 16, 7 / 32, 1 / 4, 5 / 16, 3 / 8),
    ),
    # Fractional jobber drill indexes: the classic 29-, 21- and 13-piece sets.
    Kit("Jobber Drill Set", "drill_jobber", "in", _sixty_fourths(4, 32)),
    Kit("Jobber Drill Set", "drill_jobber", "in", _sixty_fourths(4, 24)),
    Kit("Jobber Drill Set", "drill_jobber", "in", _sixty_fourths(4, 16)),
    # A metric index, 1 to 13mm by half millimetres.
    Kit("Jobber Drill Set", "drill_jobber", "mm", tuple(k / 2 / MM_PER_INCH for k in range(2, 27))),
    # Socket head cap screw assortments: a count of each diameter.
    Kit(
        "Socket Head Cap Screw Assortment",
        "screw_socket_head",
        "mm",
        (),
        per_size=50,
        designations=("M3x0.5", "M4x0.7", "M5x0.8", "M6x1", "M8x1.25"),
    ),
    Kit(
        "Socket Head Cap Screw Assortment",
        "screw_socket_head",
        "in",
        (),
        per_size=40,
        designations=("#6-32", "#8-32", "#10-24", "1/4-20", "5/16-18", "3/8-16"),
    ),
    # Tap sets: one tap of each coarse size.
    Kit(
        "Tap Set",
        "tap_spiral_point",
        "mm",
        (),
        designations=("M3x0.5", "M4x0.7", "M5x0.8", "M6x1", "M8x1.25", "M10x1.5", "M12x1.75"),
    ),
    Kit(
        "Tap Set",
        "tap_spiral_point",
        "in",
        (),
        designations=("#6-32", "#8-32", "#10-24", "1/4-20", "5/16-18", "3/8-16", "1/2-13"),
    ),
)

_KIT_MATERIAL = {
    "hex_key": ("Alloy Steel", "Chrome Vanadium Steel", "S2 Tool Steel"),
    "drill_jobber": ("High Speed Steel", "Cobalt"),
    "screw_socket_head": ("Alloy Steel", "18-8 Stainless Steel"),
    "tap_spiral_point": ("High Speed Steel",),
}
#: The finishes each part type is sold in, as elsewhere in this catalog.
_KIT_FINISH = {
    "hex_key": ("Black Oxide", "Chrome Plated", "Bright"),
    "drill_jobber": ("Bright", "Black Oxide", "TiN"),
    "screw_socket_head": ("Black Oxide", "Plain", "Zinc Plated"),
    "tap_spiral_point": ("Bright", "TiN", "Steam Oxide"),
}
_KIT_CONTAINER = ("Plastic Case", "Metal Index", "Folding Holder", "Pouch")


def build_kit(gen: Generator, type_key: str, category: tuple[str, ...]) -> LineDraft:
    """One assortment kit: one SKU, its sizes a field of its own.

    The attribute names are the census's: ``Sizes Included`` (the contents,
    multi-valued), ``Number of Pieces`` (a real count, which is why pack
    wording may name it) and ``Container Type``.
    """
    from .brands import brands_for
    from .generate import BRANDS, ChildDraft, LineDraft

    rng = gen.rng
    kit = KITS[gen._rotate("kit:kind", len(KITS))]
    makers = [b for b in brands_for(kit.part_type) if (type_key, b.name) not in gen._exhausted]
    makers = makers or list(brands_for(kit.part_type))
    brand = rng.choices(makers, weights=[b.weight for b in makers], k=1)[0].name
    material = rng.choice(_KIT_MATERIAL[kit.part_type])
    finish = "Plain" if "Stainless" in material else rng.choice(_KIT_FINISH[kit.part_type])
    container = rng.choice(_KIT_CONTAINER)
    style = feed_style(brand, kit.system, BRANDS)
    contents = kit.designations or tuple(gen._publish(size, style) for size in kit.sizes)
    pieces = kit.per_size * len(contents)
    # The title says what the kit IS -- "Socket Head Cap Screw Assortment
    # Kit", "Hex Key Set" -- while ``Item`` stays the one facet value.
    title_item = kit.item if kit.item.endswith("Set") else f"{kit.item} Kit"
    draft = LineDraft(
        item=title_item,
        brand=brand,
        series=f"KT{rng.randint(100, 999)}",
        category=category,
        provenance=GENERATED_PROVENANCE,
    )
    draft.line_attrs = [
        # ONE item name for every kit, the kind in ``Type``: four kit names
        # would take ``Item`` past the 25-value facet cap, and ``Item`` is a
        # policy target a shopper must be able to see and reverse.
        keyword_attribute("Item", "Assortment Kit"),
        keyword_attribute("Type", kit.item),
        keyword_attribute("Material", material),
        keyword_attribute("Finish", finish),
        keyword_attribute("Container Type", container),
    ]
    if kit.part_type == "hex_key":
        tip = rng.choice(("Hex End", "Ball End"))
        draft.line_attrs.append(keyword_attribute("Tip Style", tip))
    draft.descriptors = [("Container Type", container)]
    child = ChildDraft(system=kit.system)
    child.primary = numeric_attribute("Number of Pieces", str(pieces), float(pieces))
    child.attrs = [child.primary, multi_attribute("Sizes Included", contents)]
    draft.children.append(child)
    return draft


NEW_TYPES: dict[str, NewType] = {
    "nut_hex": NewType(("Fasteners", "Nuts", "Hex Nuts"), build_nut, "fastener"),
    "bearing_radial_ball": NewType(
        ("Motion Control & Fluid Power", "Bearings", "Radial Ball Bearings"),
        build_bearing,
        "motion",
    ),
    "wheel_depressed_center": NewType(
        ("Abrasives", "Grinding & Cut-Off", "Grinding & Cut-Off Wheels", "Depressed-Center Wheels"),
        build_wheel,
        "abrasive",
    ),
    "kit_assortment": NewType(
        ("Hand Tools", "Tool Sets & Kits", "Assortment Kits"), build_kit, "hand_tool"
    ),
    "hex_key": NewType(
        (
            "Hand Tools",
            "Screwdrivers & Hex Keys",
            "Hex & Torx Keys",
            "Hex Keys & Accessories",
            "Hex Keys",
        ),
        build_hex_key,
        "hand_tool",
    ),
}
