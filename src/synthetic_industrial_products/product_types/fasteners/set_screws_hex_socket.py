"""Hex socket set screws, deepened from a breadth row into a modelled type (#53).

The spec space is the standards' own: ISO 4026 (flat), 4027 (cone), 4028 (dog)
and 4029 (cup point) for metric, ASME B18.3 (B18.3.5A-D) for inch. Sizes,
pitches, socket keys, point diameters and the length ranges are transcribed
from FreeCAD_FastenersWB at the commit ``data/fastener_standards.json`` already
cites (fddd07af): ``FsData/iso4026def.csv``, ``iso4028def.csv`` and
``asmeb18.3.5def.csv``, with the nominal-length lists of the same files and of
``inch_fs_length.csv``. Nothing is interpolated. Left out on purpose: ISO's
non-preferred bracketed sizes (M1.8, M14, M18, M22), inch sizes over 1", and
inch lengths over 6" (the source ranges run to 14").

Materials and finishes are the three a distributor stocks set screws in. The
price uses the shared path for now; the type adopts the measured price model
of #52 when PR #58 merges.
"""

from __future__ import annotations

import math
from typing import Any

from ...catalog.standards import UNF_THREADS_PER_INCH
from ...catalog.typespec import TypeSpec
from ...catalog.vocab import AttrSpec
from ...dimensions import DimensionParseError, parse_length, parse_thread
from ...drawing.figures import Drawn
from ...drawing.model import Figure, regular_polygon

KEY = "set_screws_hex_socket"
MM = 25.4

#: Metric rows: (size, pitch mm, socket key s mm, flat/dog point dia dp mm).
METRIC = (
    ("M1.6", 0.35, 0.7, 0.8), ("M2", 0.4, 0.9, 1.0), ("M2.5", 0.45, 1.3, 1.5),
    ("M3", 0.5, 1.5, 2.0), ("M4", 0.7, 2.0, 2.5), ("M5", 0.8, 2.5, 3.5),
    ("M6", 1.0, 3.0, 4.0), ("M8", 1.25, 4.0, 5.5), ("M10", 1.5, 5.0, 7.0),
    ("M12", 1.75, 6.0, 8.5), ("M16", 2.0, 8.0, 12.0), ("M20", 2.5, 10.0, 15.0),
    ("M24", 3.0, 12.0, 18.0),
)  # fmt: skip
#: ISO 4026/4027/4029 range (Min_L, Max_L) mm; ISO 4028 (dog) has its own.
METRIC_RANGE = {
    "M1.6": (2, 5), "M2": (3, 10), "M2.5": (3, 10), "M3": (3, 20), "M4": (4, 20),
    "M5": (5, 25), "M6": (6, 35), "M8": (8, 40), "M10": (10, 40), "M12": (16, 40),
    "M16": (20, 40), "M20": (20, 50), "M24": (25, 60),
}  # fmt: skip
DOG_RANGE = {
    "M1.6": (2, 8), "M2": (2.5, 10), "M2.5": (3, 12), "M3": (4, 16), "M4": (5, 30),
    "M5": (6, 25), "M6": (8, 30), "M8": (8, 40), "M10": (10, 50), "M12": (12, 60),
    "M16": (16, 60), "M20": (20, 60), "M24": (25, 60),
}  # fmt: skip
METRIC_LENGTHS = (2, 2.5, 3, 4, 5, 6, 8, 10, 12, 16, 20, 25, 30, 35, 40, 45, 50, 55, 60)

#: Inch rows (ASME B18.3.5): (size, threads per inch, socket key s mm, point dia dp mm).
INCH = (
    ("#0", 80, 0.7112, 0.762), ("#1", 64, 0.889, 0.9271), ("#2", 56, 0.889, 1.0922),
    ("#3", 48, 1.27, 1.2573), ("#4", 40, 1.27, 1.4224), ("#5", 40, 1.5748, 1.5748),
    ("#6", 32, 1.5748, 1.7526), ("#8", 32, 1.9812, 2.0701), ("#10", 24, 2.3876, 2.413),
    ("1/4", 20, 3.175, 3.175), ("5/16", 18, 3.9624, 4.1656), ("3/8", 16, 4.7752, 5.1562),
    ("7/16", 14, 5.5626, 6.1468), ("1/2", 13, 6.35, 7.1247), ("5/8", 11, 7.9248, 9.1186),
    ("3/4", 10, 9.525, 11.1125), ("7/8", 9, 12.7, 13.1064), ("1", 8, 14.2748, 15.0876),
)  # fmt: skip
INCH_RANGE = {
    "#0": (1 / 16, 1.5), "#1": (1 / 16, 1.5), "#2": (1 / 16, 2.5), "#3": (1 / 8, 2.5),
    "#4": (1 / 8, 4), "#5": (3 / 16, 4), "#6": (1 / 8, 4), "#8": (1 / 8, 5),
    "#10": (3 / 16, 8), "1/4": (3 / 8, 10), "5/16": (1 / 2, 10), "3/8": (1 / 2, 12),
    "7/16": (3 / 4, 12), "1/2": (3 / 4, 12), "5/8": (3 / 4, 14), "3/4": (1, 14),
    "7/8": (1.5, 14), "1": (1.5, 14),
}  # fmt: skip
INCH_LENGTHS = (
    1 / 16, 3 / 32, 1 / 8, 5 / 32, 3 / 16, 1 / 4, 3 / 8, 7 / 16, 1 / 2, 3 / 4, 1, 1.25, 1.375,
    1.5, 1.625, 1.75, 2, 2.25, 2.5, 2.75, 3, 3.25, 3.5, 3.75, 4, 4.25, 4.5, 4.75, 5, 5.25,
    5.5, 6,
)  # fmt: skip

#: Point style -> (metric standard, inch standard section).
POINTS = {
    "Cup Point": ("ISO 4029", "ASME B18.3.5D"),
    "Flat Point": ("ISO 4026", "ASME B18.3.5A"),
    "Cone Point": ("ISO 4027", "ASME B18.3.5B"),
    "Dog Point": ("ISO 4028", "ASME B18.3.5C"),
}
#: Material -> (finishes it is sold in, hardness). Alloy steel set screws are
#: through-hardened (ASTM F912, ISO 898-5 class 45H); stainless is not.
MATERIALS = {
    "Alloy Steel": (("Black Oxide", "Zinc Plated"), "Rockwell C45-C53"),
    "18-8 Stainless Steel": (("Plain",), ""),
    "316 Stainless Steel": (("Plain",), ""),
}
#: Every third line of an inch size with a fine series is UNF.
FINE_PERIOD = 3
#: The drawing's extent; a longer part is drawn compressed with a break. The
#: width holds the largest size (1"): the break marks reach 1.15 r left of the
#: axis and the end view's right edge sits at 1.9 x major, 2.475" in all.
EXTENT = (2.5, 3.2)


def _spec(name: str, scope: str, presence: float = 1.0, kind: str = "keyword") -> AttrSpec:
    return AttrSpec(name=name, scope=scope, presence=presence, kind=kind)


VOCAB = (
    _spec("Item", "line"),
    _spec("Type", "line"),
    _spec("Point Type", "line"),
    _spec("Drive Type", "line"),
    _spec("Material", "line"),
    _spec("Finish", "line", 0.82),
    _spec("Thread Direction", "line", 0.64),
    _spec("Thread Type", "line", 0.70),
    _spec("Rockwell Hardness", "line", 0.48),
    _spec("Meets/Exceeds", "line", 0.40),
    _spec("Dia./Thread Size", "sku"),
    _spec("Length", "sku", kind="length"),
    # Entailed by ``Drive Type`` (see the socket screw vocabulary), so unconditional.
    _spec("Drive Size", "sku", kind="length"),
    _spec("Point Dia.", "sku", 0.6, kind="length"),
)


def _make(gen: Any, type_key: str, category: tuple[str, ...]) -> Any:
    # Imported here: generate.py imports the type tables, which discover this module.
    from ...catalog import brands
    from ...catalog.generate import ChildDraft, LineDraft
    from ...catalog.model import keyword_attribute

    rng = gen.rng
    metric = gen._rotate(f"system:{type_key}", 2) == 0
    points = list(POINTS)
    point = points[gen._rotate(f"point:{type_key}:{metric}", len(points))]
    standard = POINTS[point][0 if metric else 1]
    rows = METRIC if metric else INCH
    size, pitch, key_mm, dp_mm = rows[gen._rotate(f"size:{type_key}:{standard}", len(rows))]
    materials = list(MATERIALS)
    material = materials[gen._rotate(f"material:{type_key}:{standard}:{size}", len(materials))]
    finishes, hardness = MATERIALS[material]
    finish = rng.choice(finishes)
    brand = brands.pick_brand(rng, type_key, gen._exhausted)

    if metric:
        thread, thread_type = f"{size}x{pitch:g}", "Metric Coarse"
        low, high = (DOG_RANGE if point == "Dog Point" else METRIC_RANGE)[size]
        lengths = [mm / MM for mm in METRIC_LENGTHS if low <= mm <= high]
    else:
        tpi, thread_type = pitch, "UNF" if size == "#0" else "UNC"
        fine = UNF_THREADS_PER_INCH.get(size)
        if fine and gen._rotate(f"fine:{type_key}:{standard}:{size}", FINE_PERIOD) == 2:
            tpi, thread_type = fine, "UNF"
        thread = f"{size}-{tpi:g}"
        low, high = INCH_RANGE[size]
        lengths = [inch for inch in INCH_LENGTHS if low - 1e-9 <= inch <= high + 1e-9]
    meets = "ASME B18.3" if not metric else standard
    item = "Hex Socket Set Screw"
    draft = LineDraft(
        item=item,
        brand=brand,
        series=f"{standard.replace(' ', '').replace('.', '')}-{rng.randint(10, 99)}",
        category=category,
        provenance=standard,
    )
    draft.line_attrs = [
        keyword_attribute("Item", item),
        keyword_attribute("Type", "Set Screw"),
        keyword_attribute("Point Type", point),
        keyword_attribute("Drive Type", "Hex Socket"),
        keyword_attribute("Material", material),
        keyword_attribute("Finish", finish),
        keyword_attribute("Thread Direction", "Right Hand"),
        keyword_attribute("Thread Type", thread_type),
        *([keyword_attribute("Rockwell Hardness", hardness)] if hardness else []),
        keyword_attribute("Meets/Exceeds", meets),
    ]

    count = min(gen._variant_count(), len(lengths))
    offered = gen._offered_run(f"lengths:{standard}:{size}", lengths, count)
    system = "mm" if metric else "in"
    major_in = parse_thread(thread).major.inches
    for length_in in offered:
        style = gen._style(system)
        child = ChildDraft(system=system)
        child.primary = keyword_attribute("Dia./Thread Size", thread)
        length_attr = gen._length("Length", length_in, style)
        child.attrs = [child.primary, length_attr, gen._length("Drive Size", key_mm / MM, style)]
        if point in ("Flat Point", "Dog Point"):
            child.attrs.append(gen._length("Point Dia.", dp_mm / MM, style))
        child.secondary = {"other_length": length_attr}
        child.price_basis = 0.15 + length_in * 0.15 + major_in * 0.6
        draft.children.append(child)
    return draft


def _value(record: dict[str, str], name: str) -> float | None:
    try:
        return parse_length(record[name]).inches
    except (KeyError, DimensionParseError):
        return None


def figure(record: dict[str, str]) -> Drawn:
    """A headless threaded body, its point, and an end view of the hex socket."""
    try:
        major = parse_thread(record["Dia./Thread Size"]).major.inches
        pitch = parse_thread(record["Dia./Thread Size"]).pitch_in
        read = True
    except (KeyError, DimensionParseError):
        major, pitch, read = 0.25, 0.05, False
    length = _value(record, "Length") or 1.5 * major
    key = _value(record, "Drive Size") or 0.5 * major
    point_dia = _value(record, "Point Dia.") or 0.6 * major
    r = major / 2
    height = EXTENT[1] * 0.95
    knee = 0.8 * height
    drawn = length if length <= knee else knee + 0.15 * height * (1 - math.exp(-(length - knee)))
    fig = Figure(size_in=drawn)
    point = record.get("Point Type", "Cup Point")
    tip = min(drawn / 3, r)
    body_end = drawn - tip
    fig.rect(-r, 0.0, r, body_end, "plain")
    crests = int(body_end / pitch) if pitch > 0 else 0
    fig.lines([((-r, k * pitch), (r, k * pitch + pitch / 2)) for k in range(min(crests, 400))])
    if point == "Cone Point":
        fig.poly([(-r, body_end), (r, body_end), (0.0, drawn)])
    elif point == "Dog Point":
        p = point_dia / 2
        fig.poly([(-r, body_end), (r, body_end), (p, body_end + tip / 3), (-p, body_end + tip / 3)])
        fig.rect(-p, body_end + tip / 3, p, drawn, "plain")
    else:
        p = point_dia / 2
        fig.poly([(-r, body_end), (r, body_end), (p, drawn), (-p, drawn)])
        if point == "Cup Point":
            fig.poly([(-0.6 * p, drawn), (0.6 * p, drawn), (0.0, drawn - tip / 2)], "hole")
    fig.rect(-key / 2, 0.0, key / 2, min(key, body_end / 2), "dark")
    if length > knee:
        cut = drawn * 0.45
        fig.lines([((-1.15 * r, cut + d), (1.15 * r, cut + d + 0.04)) for d in (0.0, 0.08)])
    cx = major * 1.4
    fig.disc((cx, r), r)
    fig.poly(regular_polygon((cx, r), key / math.sqrt(3), 6, 30), "dark")
    source = "record" if read and _value(record, "Length") else ("partial" if read else "nominal")
    return Drawn(fig, source)


SPEC = TypeSpec(
    KEY,
    category=("Fasteners", "Set Screws", "Hex Socket Set Screws"),
    standards_family="fastener",
    vocab=VOCAB,
    figure=figure,
    extent=EXTENT,
    make=_make,
    share=0.10,
    use_lines=(
        "Driven with a hex key.",
        "Holds a collar, pulley or gear on its shaft from inside a tapped hole.",
    ),
)
