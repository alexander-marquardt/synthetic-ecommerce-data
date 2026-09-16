"""Generate the catalog.

The order of work matters and is the same for every product type:

1. A **type builder** produces the physically coherent part -- the line's
   constant attributes and each child's dimensions, built as whole tuples so
   they describe products that could be manufactured.
2. A shared **post-pass** applies everything that is a property of the
   *catalog* rather than of the product: ragged attribute coverage, the
   measurement-system attribute under one of its three spellings, the
   multi-valued ``Standards`` attribute, the internal contradictions real
   catalogs contain, the title, and the image reference.

Keeping those apart is what makes the defect rates meaningful. A defect is
injected into a record that was correct a moment earlier, against the
denominator of records that carry the attribute pair the defect needs -- which
is how the reference statistics measure them, each class against its own
denominator rather than against the whole corpus.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from fractions import Fraction

from . import series, standards, taxonomy
from .config import GeneratorConfig
from .formats import (
    IMPERIAL_STYLES,
    METRIC_STYLES,
    LengthStyle,
    UnpublishableMagnitude,
    format_angle,
    format_length_best,
)
from .model import (
    Attribute,
    Catalog,
    ProductLine,
    Sku,
    keyword_attribute,
    length_attribute,
    multi_attribute,
    numeric_attribute,
)
from .naming import (
    LABEL_FORMS,
    Segment,
    Title,
    abbreviate_value,
    build_title,
    truncate_label,
)
from .vocab import (
    MEASUREMENT_SYSTEM_NAMES,
    MEASUREMENT_SYSTEM_PRESENCE,
    MEASUREMENT_SYSTEM_VALUES,
    STANDARDS_FAMILY,
    STANDARDS_NAME,
    STANDARDS_POOL,
    STANDARDS_PRESENCE,
    VOCAB,
)

MM_PER_INCH = 25.4

#: Synthetic manufacturer names. Every one is invented; none is a real brand.
BRANDS: tuple[str, ...] = (
    "Corvane",
    "Halstead Tool",
    "Ferrox",
    "Bracknell",
    "Osterlund",
    "Vantage Edge",
    "Kelbrook",
    "Marrow & Sons",
    "Tyndall",
    "Redmoor",
)

_SKU_LETTERS = "ABCDEFGHJKLMNPRSTUVWXYZ"


def _weighted(rng: random.Random, table) -> object:
    """Pick from a ``((value, weight), ...)`` table."""
    values = [value for value, _ in table]
    weights = [weight for _, weight in table]
    return rng.choices(values, weights=weights, k=1)[0]


@dataclass
class ChildDraft:
    """A child before the shared post-pass touches it."""

    attrs: list[Attribute] = field(default_factory=list)
    #: The dimension a title would name -- the one a shopper reads as "the"
    #: size of the product.
    primary: Attribute | None = None
    #: Other dimensions on the same child, by the class name the reference
    #: statistics use: other_length, length_of_cut, neck, flute.
    secondary: dict[str, Attribute] = field(default_factory=dict)
    system: str = "in"
    price_basis: float = 1.0


@dataclass
class LineDraft:
    item: str
    brand: str
    series: str
    category: tuple[str, ...]
    line_attrs: list[Attribute] = field(default_factory=list)
    children: list[ChildDraft] = field(default_factory=list)
    provenance: str = ""
    #: Extra title segments the type wants, before the dimension segment.
    descriptors: list[tuple[str, str]] = field(default_factory=list)


class Generator:
    """Deterministic for a given seed: the same config produces the same catalog."""

    def __init__(self, config: GeneratorConfig | None = None) -> None:
        self.config = config or GeneratorConfig()
        self.rng = random.Random(self.config.seed)
        self._used_skus: set[str] = set()
        self._image_pool: list[str] = []
        self.counters: dict[str, int] = {}

    # -- bookkeeping ----------------------------------------------------

    def _bump(self, key: str, amount: int = 1) -> None:
        self.counters[key] = self.counters.get(key, 0) + amount

    def _new_sku(self) -> str:
        """A catalog-shaped SKU code, unique within the run.

        Shaped like the codes this vertical uses -- digits, letters, digits --
        but drawn from a synthetic namespace and checked against the reference
        SKUs the statistics name, so no generated item can collide with a real
        archived one.
        """
        from .noncopy import REFERENCE_SKUS

        while True:
            lead = self.rng.randint(1, 99)
            letters = "".join(self.rng.choice(_SKU_LETTERS) for _ in range(2))
            tail = self.rng.randint(10, 99)
            code = f"{lead}{letters}{tail}"
            if code in self._used_skus or code in REFERENCE_SKUS:
                continue
            self._used_skus.add(code)
            return code

    # -- shared value helpers -------------------------------------------

    def _style(self, system: str) -> LengthStyle:
        table = IMPERIAL_STYLES if system == "in" else METRIC_STYLES
        style = _weighted(self.rng, table)
        assert isinstance(style, LengthStyle)
        return style

    def _publish(self, inches: float, style: LengthStyle) -> str:
        try:
            return format_length_best(inches, style)
        except UnpublishableMagnitude:
            fallback = LengthStyle(style.system, style.suffix, "decimal", places=4)
            return format_length_best(inches, fallback)

    def _length(self, name: str, inches: float, style: LengthStyle) -> Attribute:
        return length_attribute(name, self._publish(inches, style))

    # -- type builders ---------------------------------------------------

    def _build_end_mill(self, type_key: str, category: tuple[str, ...]) -> LineDraft:
        cfg = self.config
        rng = self.rng
        ball = type_key == "end_mill_ball"
        material = category[3] if len(category) > 3 else "Solid Carbide"
        metric = rng.random() < 0.22
        system = "mm" if metric else "in"

        brand = rng.choice(BRANDS)
        flutes = int(_weighted(rng, series.FLUTE_WEIGHTS))  # type: ignore[arg-type]
        helix = rng.choice(series.HELIX_ANGLES)
        coating = rng.choice(("AlTiN", "TiCN", "TiAlN", "TiN", "Uncoated", "Bright", "nACo"))
        style_name = "Ball Nose" if ball else "Square"
        item = f"{material} {style_name} End Mill" if rng.random() < 0.5 else "End Mill"
        series_code = f"{rng.choice('GHKMPR')}{rng.randint(100, 999)}"

        draft = LineDraft(
            item=item,
            brand=brand,
            series=series_code,
            category=category,
            provenance=(
                "generated from the conventional tool series; no standard fixes these values"
            ),
        )
        draft.line_attrs = [
            keyword_attribute("Item", item),
            keyword_attribute("End Mill Style", style_name),
            keyword_attribute("End Mill Material", material),
            keyword_attribute("Finish - Machining", coating),
            numeric_attribute("Number of Flutes", str(flutes), float(flutes)),
            Attribute("Helix Angle", format_angle(helix), helix),
            keyword_attribute(
                "Cutting Direction", "Right Hand" if rng.random() < 0.93 else "Left Hand"
            ),
            keyword_attribute(
                "Single End/Double End", "Single End" if rng.random() < 0.85 else "Double End"
            ),
            keyword_attribute(
                "End Mill Cutting Type",
                "Center Cutting" if rng.random() < 0.8 else "Non-Center Cutting",
            ),
            keyword_attribute(
                "End Mill Application", rng.choice(("Roughing", "Finishing", "Roughing/Finishing"))
            ),
            keyword_attribute(
                "Material Grade - Machining", rng.choice(("General Purpose", "High Performance"))
            ),
            keyword_attribute(
                "Coolant Fed", "Coolant Through" if rng.random() < 0.2 else "Non-Coolant Through"
            ),
            keyword_attribute("List Number", series_code),
        ]
        draft.descriptors = [
            ("End Mill Material", material),
            ("Finish - Machining", coating),
        ]

        # One shank policy per line: a line is either built on matching shanks
        # or on a reduced/oversize shank, and the measured 64.9% equal rate is
        # a property of the catalog, so it is decided here.
        shanks_match = rng.random() < cfg.shank_equals_cutting_dia
        length_class, multiple = rng.choice(series.LENGTH_CLASSES)

        count = rng.randint(*cfg.skus_per_line)
        # A tool whose shank equals its cutting diameter can only exist at a
        # diameter that is ALSO an offered shank size -- a 7/32" cutter has no
        # 7/32" collet to sit in. Drawing a matching-shank line from the full
        # cutting series and then snapping to the nearest shank silently turns
        # most of those lines into reduced-shank ones.
        #
        # The two pools are then capped to the SAME size. They are naturally
        # different lengths (9 imperial shank sizes against 18 cutting sizes),
        # and since a line offers as many SKUs as its pool allows, the longer
        # pool would put more SKUs behind every reduced-shank line. The
        # equality rate is measured per RECORD, so that alone pulled it from
        # its 0.6489 target down to 0.58 even with the line-level decision
        # drawn at exactly 0.6489.
        if metric:
            matching = [d for d in series.METRIC_CUTTING_DIAS if d in series.METRIC_SHANKS]
            full = list(series.METRIC_CUTTING_DIAS)
        else:
            shank_set = {float(sh) for sh in series.IMPERIAL_SHANKS}
            matching = [d for d in series.IMPERIAL_CUTTING_DIAS if float(d) in shank_set]
            full = list(series.IMPERIAL_CUTTING_DIAS)
        width = len(matching)
        if shanks_match:
            pool = list(matching)
        else:
            pool = list(full)
            rng.shuffle(pool)
            pool = pool[:width]
        rng.shuffle(pool)
        chosen = pool[:count] if count <= len(pool) else pool

        for dia in chosen:
            child = ChildDraft(system=system)
            if metric:
                dia_mm = float(dia)
                if shanks_match:
                    shank_mm = series.nearest_shank_metric(dia_mm)
                else:
                    ratio = float(_weighted(rng, series.OBSERVED_SHANK_RATIOS))  # type: ignore[arg-type]
                    shank_mm = series.nearest_shank_metric(dia_mm * ratio)
                    if abs(shank_mm - dia_mm) < 1e-6:
                        shank_mm = series.nearest_shank_metric(dia_mm * 2.0)
                geom = series.build_metric(dia_mm, length_class, multiple, shank_mm)
                child.price_basis = dia_mm / 4.0
            else:
                dia_fr = Fraction(dia)
                if shanks_match:
                    shank_fr = series.nearest_shank_imperial(float(dia_fr))
                else:
                    ratio = float(_weighted(rng, series.OBSERVED_SHANK_RATIOS))  # type: ignore[arg-type]
                    shank_fr = series.nearest_shank_imperial(float(dia_fr) * ratio)
                    if shank_fr == dia_fr:
                        shank_fr = series.nearest_shank_imperial(float(dia_fr) * 2.0)
                geom = series.build_imperial(dia_fr, length_class, multiple, shank_fr)
                child.price_basis = float(dia_fr) * 6.0

            style = self._style(system)
            cut_name = "Milling Dia."
            child.primary = self._length(cut_name, geom.cutting_dia_in, style)
            shank = self._length("Shank Dia.", geom.shank_dia_in, style)
            loc = self._length("Length of Cut", geom.length_of_cut_in, style)
            oal = self._length("Overall Length", geom.overall_length_in, style)
            child.attrs = [child.primary, shank, loc, oal]
            child.secondary = {
                "length_of_cut": loc,
                "other_length": oal,
            }
            if rng.random() < 0.18:
                neck_in = geom.length_of_cut_in * rng.uniform(1.05, 1.4)
                neck = self._length("Neck Length", neck_in, style)
                child.attrs.append(neck)
                child.secondary["neck"] = neck
            if rng.random() < 0.22:
                radius_in = geom.cutting_dia_in / rng.choice((8.0, 16.0, 32.0))
                child.attrs.append(self._length("Corner Radius", radius_in, style))
            # The "flute" class of misleading title token: a flute length that
            # is not the cutting diameter.
            child.secondary["flute"] = loc
            draft.children.append(child)
        return draft

    def _build_drill(self, type_key: str, category: tuple[str, ...]) -> LineDraft:
        rng = self.rng
        brand = rng.choice(BRANDS)
        material = rng.choice(("High Speed Steel", "Cobalt", "Solid Carbide"))
        point = rng.choice(("118 Degrees", "135 Degrees"))
        item = "Jobber Length Drill Bit"
        series_code = f"{rng.randint(100, 999)}-{rng.choice('ABCD')}"
        draft = LineDraft(
            item=item,
            brand=brand,
            series=series_code,
            category=category,
            provenance="generated from the conventional drill series",
        )
        draft.line_attrs = [
            keyword_attribute("Item", item),
            keyword_attribute("Drill Bit Material", material),
            keyword_attribute("Drill Point Type", rng.choice(("Split Point", "Standard Point"))),
            Attribute("Point Angle", point, float(point.split()[0])),
            keyword_attribute(
                "Drill Bit Finish", rng.choice(("Bright", "Black Oxide", "TiN", "Bronze Oxide"))
            ),
            keyword_attribute("Shank Type", rng.choice(("Straight", "Reduced"))),
            keyword_attribute("Drill Bit Direction", "Right Hand"),
            keyword_attribute("List Number", series_code),
        ]
        draft.descriptors = [("Drill Bit Material", material)]

        count = rng.randint(*self.config.skus_per_line)
        pool = list(series.DRILL_FRACTIONAL)
        rng.shuffle(pool)
        for size in pool[:count]:
            style = self._style("in")
            child = ChildDraft(system="in")
            size_in = float(size)
            # A jobber drill's flute length and overall length follow the size.
            flute_in = float(series.snap_imperial(min(size_in * 9.0, 4.0), 16))
            oal_in = float(series.snap_imperial(flute_in + max(size_in * 4.0, 0.9), 16))
            child.primary = self._length("Drill Size", size_in, style)
            flute = self._length("Flute Length", flute_in, style)
            child.attrs = [
                child.primary,
                flute,
                self._length("Overall Length", oal_in, style),
                Attribute("Decimal Equivalent", f"{size_in:.4f}", size_in),
            ]
            if rng.random() < 0.68:
                shank_in = size_in if size_in <= 0.5 else 0.5
                child.attrs.append(self._length("Shank Dia.", shank_in, style))
            child.secondary = {"other_length": child.attrs[2], "length_of_cut": flute}
            child.price_basis = size_in * 4.0
            draft.children.append(child)
        return draft

    def _build_tap(self, type_key: str, category: tuple[str, ...]) -> LineDraft:
        rng = self.rng
        brand = rng.choice(BRANDS)
        metric = rng.random() < 0.35
        item = "Spiral Point Tap"
        draft = LineDraft(
            item=item,
            brand=brand,
            series=f"SPT{rng.randint(10, 99)}",
            category=category,
            provenance="generated from the conventional tap series",
        )
        flutes = rng.choice((2, 3))
        draft.line_attrs = [
            keyword_attribute("Item", item),
            keyword_attribute("Tap Style", "Spiral Point"),
            keyword_attribute("Tap Material", rng.choice(("High Speed Steel", "Powdered Metal"))),
            keyword_attribute("Tap Finish", rng.choice(("Bright", "TiN", "Steam Oxide"))),
            keyword_attribute("Thread Direction", "Right Hand"),
            keyword_attribute("Thread Type", "Metric Coarse" if metric else "UNC"),
            keyword_attribute("Chamfer Style", rng.choice(("Plug", "Bottoming", "Taper"))),
            numeric_attribute("Number of Flutes", str(flutes), float(flutes)),
        ]
        draft.descriptors = [("Thread Type", "Metric Coarse" if metric else "UNC")]

        table = series.TAP_SIZES_METRIC if metric else series.TAP_SIZES_INCH
        pool = list(table)
        rng.shuffle(pool)
        count = min(rng.randint(*self.config.skus_per_line), len(pool))
        for designation, pitch in pool[:count]:
            system = "mm" if metric else "in"
            style = self._style(system)
            child = ChildDraft(system=system)
            if metric:
                major_mm = float(designation.split("x")[0].lstrip("M"))
                major_in = major_mm / MM_PER_INCH
            else:
                major_in = standards.INCH_MAJOR_DIA.get(designation.split("-")[0], 0.25)
            oal_in = max(major_in * 8.0, 1.8)
            child.primary = keyword_attribute("Thread Size", designation)
            child.attrs = [
                child.primary,
                keyword_attribute("Pitch", f"{pitch:g}" if metric else str(pitch)),
                self._length("Overall Length", oal_in, style),
                self._length("Thread Length", oal_in * 0.45, style),
                self._length("Shank Dia.", major_in * 0.9, style),
            ]
            child.secondary = {"other_length": child.attrs[2], "length_of_cut": child.attrs[3]}
            child.price_basis = major_in * 20.0
            draft.children.append(child)
        return draft

    def _build_socket_screw(self, type_key: str, category: tuple[str, ...]) -> LineDraft:
        """Socket head or flat countersunk head cap screws, from the standards."""
        rng = self.rng
        flat = type_key == "screw_flat_head"
        metric = rng.random() < 0.5
        if flat:
            standard = "ISO 10642" if metric else "ASME B18.3.2"
            head_style = "Flat"
            style_name = "Socket Flat Head Cap Screw"
        else:
            standard = "ISO 4762" if metric else "ASME B18.3"
            head_style = "Socket"
            style_name = "Socket Head Cap Screw"

        brand = rng.choice(BRANDS)
        material = rng.choice(("Alloy Steel", "18-8 Stainless Steel", "Grade 12.9 Alloy Steel"))
        draft = LineDraft(
            item=style_name,
            brand=brand,
            series=f"{standard.replace(' ', '')}-{rng.randint(10, 99)}",
            category=category,
            provenance=standard,
        )
        draft.line_attrs = [
            keyword_attribute("Item", style_name),
            keyword_attribute("Screw Style", style_name),
            keyword_attribute("Screw Head Type", head_style),
            keyword_attribute("Drive Type", "Hex Socket"),
            keyword_attribute("Fastener Material", material),
            keyword_attribute(
                "Fastener Finish", rng.choice(("Black Oxide", "Plain", "Zinc Plated"))
            ),
            keyword_attribute("Thread Direction", "Right Hand"),
            keyword_attribute("Thread Type", "Metric Coarse" if metric else "UNC"),
            keyword_attribute("Rockwell Hardness", rng.choice(("C38", "C39", "B80"))),
            keyword_attribute("Meets/Exceeds", standard),
        ]
        draft.descriptors = [("Fastener Material", material)]

        sizes = list(standards.available_sizes(standard))
        rng.shuffle(sizes)
        size = sizes[0]
        head = (
            standards.flat_head(standard, size) if flat else standards.socket_head(standard, size)
        )

        lengths = list(standards.offered_lengths_in(standard, size))
        if not lengths:
            lengths = [0.25, 0.375, 0.5, 0.75, 1.0, 1.25, 1.5]
        rng.shuffle(lengths)
        count = min(rng.randint(*self.config.skus_per_line), len(lengths))
        system = "mm" if head.published_unit == "mm" else "in"

        for length_in in sorted(lengths[:count]):
            style = self._style(system)
            child = ChildDraft(system=system)
            # Fully threaded below about 2x the head diameter, else a standard
            # thread length: 2D + 1/2" for inch practice.
            thread_len_in = min(length_in, 2 * head.major_dia_in + 0.5)
            child.primary = keyword_attribute("Dia./Thread Size", head.thread_designation)
            length_attr = self._length("Length", length_in, style)
            child.attrs = [
                child.primary,
                length_attr,
                self._length("Thread Length", thread_len_in, style),
                self._length("Head Dia.", head.head_dia_in, style),
                self._length("Head Height", head.head_height_in, style),
            ]
            if head.drive_size_in:
                child.attrs.append(self._length("Drive Size", head.drive_size_in, style))
            child.secondary = {"other_length": length_attr, "length_of_cut": child.attrs[2]}
            child.price_basis = length_in * 0.4 + head.major_dia_in * 2
            draft.children.append(child)
        return draft

    def _build_hex_bolt(self, type_key: str, category: tuple[str, ...]) -> LineDraft:
        rng = self.rng
        # ISO 4017 and DIN 933 describe the same product and disagree on width
        # across flats at M10 and M12. Which standard the line is built to is a
        # property of the line, so it is chosen here.
        standard = rng.choice(("ISO 4014", "ISO 4017", "DIN 933", "ASME B18.2.1"))
        brand = rng.choice(BRANDS)
        grade = rng.choice(("Grade 5", "Grade 8", "Class 8.8", "Class 10.9"))
        item = "Hex Head Bolt"
        draft = LineDraft(
            item=item,
            brand=brand,
            series=f"{standard.replace(' ', '')}-{rng.randint(10, 99)}",
            category=category,
            provenance=standard,
        )
        draft.line_attrs = [
            keyword_attribute("Item", item),
            keyword_attribute("Bolt Style", "Hex Head"),
            keyword_attribute("Screw Head Type", "Hex"),
            keyword_attribute("Fastener Material", rng.choice(("Steel", "18-8 Stainless Steel"))),
            keyword_attribute(
                "Fastener Finish", rng.choice(("Zinc Plated", "Plain", "Hot Dip Galvanized"))
            ),
            keyword_attribute("Grade", grade),
            keyword_attribute("Thread Direction", "Right Hand"),
            keyword_attribute(
                "Thread Type", "UNC" if standard.startswith("ASME") else "Metric Coarse"
            ),
        ]
        draft.descriptors = [("Grade", grade)]

        sizes = list(standards.available_sizes(standard))
        rng.shuffle(sizes)
        size = sizes[0]
        head = standards.hex_bolt(standard, size)
        lengths = list(standards.offered_lengths_in(standard, size)) or [0.5, 0.75, 1.0, 1.5, 2.0]
        rng.shuffle(lengths)
        count = min(rng.randint(*self.config.skus_per_line), len(lengths))
        system = "mm" if head.published_unit == "mm" else "in"

        for length_in in sorted(lengths[:count]):
            style = self._style(system)
            child = ChildDraft(system=system)
            thread_len_in = min(length_in, 2 * head.major_dia_in + 0.25)
            child.primary = keyword_attribute("Dia./Thread Size", head.thread_designation)
            length_attr = self._length("Length", length_in, style)
            child.attrs = [
                child.primary,
                length_attr,
                self._length("Thread Length", thread_len_in, style),
                self._length("Width Across Flats", head.width_across_flats_in, style),
                self._length("Head Height", head.head_height_in, style),
                # The renderer reads Head Dia. for a cylindrical head, and a
                # hex head's side profile really is its width across flats.
                self._length("Head Dia.", head.width_across_flats_in, style),
            ]
            child.secondary = {"other_length": length_attr, "length_of_cut": child.attrs[2]}
            child.price_basis = length_in * 0.3 + head.major_dia_in * 1.5
            draft.children.append(child)
        return draft

    def _build_washer(self, type_key: str, category: tuple[str, ...]) -> LineDraft:
        rng = self.rng
        brand = rng.choice(BRANDS)
        material = rng.choice(("18-8 Stainless Steel", "Steel", "Nylon"))
        item = "Flat Washer"
        draft = LineDraft(
            item=item,
            brand=brand,
            series=f"W{rng.randint(100, 999)}",
            category=category,
            provenance="ISO 7089",
        )
        draft.line_attrs = [
            keyword_attribute("Item", item),
            keyword_attribute("Washer Type", "Plain"),
            keyword_attribute("Fastener Material", material),
            keyword_attribute("Fastener Finish", rng.choice(("Plain", "Zinc Plated"))),
        ]
        draft.descriptors = [("Fastener Material", material)]

        sizes = list(standards.available_sizes("ISO 7089"))
        rng.shuffle(sizes)
        count = min(rng.randint(*self.config.skus_per_line), len(sizes))
        for size in sizes[:count]:
            plain = standards.washer("ISO 7089", size)
            style = self._style("mm")
            child = ChildDraft(system="mm")
            child.primary = keyword_attribute("Washer Size", size)
            outside = self._length("Outside Dia.", plain.outside_dia_in, style)
            child.attrs = [
                child.primary,
                self._length("Inside Dia.", plain.inside_dia_in, style),
                outside,
                self._length("Thickness", plain.thickness_in, style),
            ]
            child.secondary = {"other_length": outside}
            child.price_basis = plain.outside_dia_in * 0.5
            draft.children.append(child)
        return draft

    def _build_hammer(self, type_key: str, category: tuple[str, ...]) -> LineDraft:
        rng = self.rng
        brand = rng.choice(BRANDS)
        handle = rng.choice(("Hickory", "Fiberglass", "Steel"))
        item = "Ball Pein Hammer"
        draft = LineDraft(
            item=item,
            brand=brand,
            series=f"BP{rng.randint(10, 99)}",
            category=category,
            provenance="generated; no dimensional standard applies",
        )
        draft.line_attrs = [
            keyword_attribute("Item", item),
            keyword_attribute("Hammer Head Material", "Forged Steel"),
            keyword_attribute("Handle Material", handle),
            keyword_attribute("Handle Grip Material", rng.choice(("Rubber", "Vinyl", "None"))),
            keyword_attribute("Hammer Face Type", "Ball Pein"),
        ]
        draft.descriptors = [("Handle Material", handle)]

        weights = list(series.HAMMER_HEAD_OUNCES)
        rng.shuffle(weights)
        count = min(rng.randint(*self.config.skus_per_line), len(weights))
        for ounces in sorted(weights[:count]):
            style = self._style("in")
            child = ChildDraft(system="in")
            oal_in = float(series.snap_imperial(10.0 + ounces * 0.16, 16))
            child.primary = numeric_attribute("Head Weight", f"{ounces} oz", float(ounces))
            overall = self._length("Overall Length", oal_in, style)
            child.attrs = [
                child.primary,
                overall,
                self._length("Face Dia.", 0.6 + ounces * 0.02, style),
                self._length("Handle Length", oal_in - 1.5, style),
            ]
            child.secondary = {"other_length": overall}
            child.price_basis = ounces * 0.9
            draft.children.append(child)
        return draft

    def _build_flap_disc(self, type_key: str, category: tuple[str, ...]) -> LineDraft:
        rng = self.rng
        brand = rng.choice(BRANDS)
        abrasive = rng.choice(("Zirconia Alumina", "Ceramic", "Aluminum Oxide"))
        item = "Flap Disc"
        draft = LineDraft(
            item=item,
            brand=brand,
            series=f"FD{rng.randint(100, 999)}",
            category=category,
            provenance="generated; no dimensional standard applies",
        )
        draft.line_attrs = [
            keyword_attribute("Item", item),
            keyword_attribute("Abrasive Material", abrasive),
            keyword_attribute("Backing Material", rng.choice(("Fiberglass", "Plastic"))),
            keyword_attribute("Flap Disc Shape", rng.choice(("Type 27 Flat", "Type 29 Conical"))),
            keyword_attribute("Mounting Type", "Arbor Hole"),
        ]
        draft.descriptors = [("Abrasive Material", abrasive)]

        dia = rng.choice(series.FLAP_DISC_DIAS_IN)
        arbor = rng.choice(series.FLAP_DISC_ARBORS)
        grits = list(series.FLAP_DISC_GRITS)
        rng.shuffle(grits)
        count = min(rng.randint(*self.config.skus_per_line), len(grits))
        # Max safe speed falls with diameter; it is a property of the disc.
        max_rpm = int(round(48000 / float(dia) / 100.0) * 100)
        for grit in sorted(grits[:count]):
            style = self._style("in")
            child = ChildDraft(system="in")
            child.primary = numeric_attribute("Grit", str(grit), float(grit))
            disc = self._length("Disc Dia.", float(dia), style)
            child.attrs = [
                child.primary,
                disc,
                self._length("Arbor Hole Size", float(arbor), style),
                numeric_attribute("Max. RPM", f"{max_rpm:,}", float(max_rpm)),
            ]
            child.secondary = {"other_length": disc}
            child.price_basis = float(dia) * 1.1
            draft.children.append(child)
        return draft

    _BUILDERS = {
        "end_mill_square": _build_end_mill,
        "end_mill_ball": _build_end_mill,
        "drill_jobber": _build_drill,
        "tap_spiral_point": _build_tap,
        "screw_socket_head": _build_socket_screw,
        "screw_flat_head": _build_socket_screw,
        "bolt_hex": _build_hex_bolt,
        "washer_flat": _build_washer,
        "hammer_ball_pein": _build_hammer,
        "abrasive_flap_disc": _build_flap_disc,
    }

    # -- the shared post-pass --------------------------------------------

    def _apply_sparsity(self, type_key: str, attrs: list[Attribute], scope: str) -> list[Attribute]:
        """Drop optional attributes at their measured presence rate."""
        rates = {spec.name: spec for spec in VOCAB[type_key] if spec.scope == scope}
        kept: list[Attribute] = []
        for attribute in attrs:
            spec = rates.get(attribute.name)
            if spec is None:
                kept.append(attribute)
                continue
            if self.rng.random() <= self.config.scaled_presence(spec.presence):
                kept.append(attribute)
        return kept

    def _standards_attribute(self, type_key: str) -> Attribute | None:
        if self.rng.random() > STANDARDS_PRESENCE:
            return None
        pool = STANDARDS_POOL[STANDARDS_FAMILY[type_key]]
        how_many = self.rng.choices((1, 2, 3), weights=(0.45, 0.35, 0.20), k=1)[0]
        values = tuple(sorted(self.rng.sample(list(pool), k=min(how_many, len(pool)))))
        self._bump("standards_present")
        if len(values) > 1:
            self._bump("standards_multivalued")
        self._bump("standards_values", len(values))
        return multi_attribute(STANDARDS_NAME, values)

    def _measurement_system(self, system: str, name: str) -> tuple[Attribute | None, bool]:
        """The measurement-system attribute, under the spelling its LINE uses.

        The spelling is chosen once per product line, not once per record. A
        line is one supplier's feed, and a supplier is internally consistent
        about what it calls this field; the inconsistency is BETWEEN families,
        which is exactly the case a field map has to absorb. Drawing it per
        record instead put all three spellings inside every product type,
        which is both less realistic and useless as a test of scoping.

        Returns the attribute and whether its declared value contradicts the
        units actually used in the record -- a measured defect class, so the
        contradiction is produced here rather than patched in afterwards.
        """
        if self.rng.random() > MEASUREMENT_SYSTEM_PRESENCE:
            return None, False
        truthful = (
            "Metric" if system == "mm" else str(_weighted(self.rng, MEASUREMENT_SYSTEM_VALUES))
        )
        if truthful == "Metric" and system == "in":
            truthful = "Fractional Inch"
        contradicts = self.rng.random() < self.config.scaled_defect(
            self.config.defect_system_contradicts_units
        )
        if contradicts:
            value = "Fractional Inch" if system == "mm" else "Metric"
            self._bump("defect_system_contradicts")
        else:
            value = truthful
        self._bump("measurement_system_present")
        return keyword_attribute(name, value), contradicts

    def _inject_defects(self, child: ChildDraft, attrs: list[Attribute]) -> list[Attribute]:
        """Reproduce the measured internal contradictions.

        Each class is drawn against its own denominator: only a record that
        actually carries the attribute pair is eligible, which is how the
        reference statistics measure these rates.
        """
        cfg = self.config
        rng = self.rng
        by_name = {a.name: i for i, a in enumerate(attrs)}
        out = list(attrs)

        # Class 1: length of cut longer than overall length.
        loc_names = ("Length of Cut", "Flute Length", "Thread Length")
        loc_index = next((by_name[n] for n in loc_names if n in by_name), None)
        oal_index = by_name.get("Overall Length") or by_name.get("Length")
        if "Overall Length" in by_name:
            oal_index = by_name["Overall Length"]
        elif "Length" in by_name:
            oal_index = by_name["Length"]
        else:
            oal_index = None
        if loc_index is not None and oal_index is not None:
            self._bump("eligible_loc_oal")
            if rng.random() < cfg.scaled_defect(cfg.defect_loc_exceeds_oal):
                oal = out[oal_index]
                loc = out[loc_index]
                if oal.value_num and loc.value_num:
                    # Publish a cut longer than the tool, the way the corpus
                    # does: the same "3 in" against a shorter overall length.
                    inflated = oal.value_num * rng.uniform(1.2, 2.5)
                    # In the record's OWN system: publishing the inflated value
                    # in the other unit would inject a second defect class
                    # (unit mixing) as a side effect, and the two rates are
                    # measured separately.
                    style = (
                        LengthStyle("in", " in", "decimal", places=2)
                        if child.system == "in"
                        else LengthStyle("mm", "mm", "decimal", places=2)
                    )
                    out[loc_index] = length_attribute(loc.name, self._publish(inflated, style))
                    self._bump("defect_loc_exceeds_oal")

        # Class 2 (the angular attribute carrying a length unit) is NOT applied
        # here. Helix Angle and Point Angle are line-constant, so a child-scoped
        # injection would never find one -- and measured exactly 0.0000 against
        # a target of 0.0469 until that was noticed. It is applied in
        # _corrupt_angle, at line scope, where the attribute actually lives.

        # Class 3: unit mixing inside one record -- one dimension published in
        # the other system.
        dimension_indexes = [i for i, a in enumerate(out) if a.value_num is not None]
        if len(dimension_indexes) >= 2:
            self._bump("eligible_unit_mixing")
            if rng.random() < cfg.scaled_defect(cfg.unit_mixing_within_record):
                index = rng.choice(dimension_indexes)
                other = "mm" if child.system == "in" else "in"
                style = (
                    LengthStyle("mm", "mm", "decimal", places=2)
                    if other == "mm"
                    else LengthStyle("in", '"', "decimal", places=4)
                )
                attribute = out[index]
                assert attribute.value_num is not None
                out[index] = length_attribute(
                    attribute.name, self._publish(attribute.value_num, style)
                )
                self._bump("defect_unit_mixing")
        return out

    def _dimension_segment(self, child: ChildDraft) -> Segment | None:
        """The title's dimension segment, reproducing the three measured cases.

        Unlabelled (46.7%) always names the primary dimension; a token that is
        NOT the primary (17.1%) always carries a label. The corpus has no case
        that is both, so the generator produces none either.
        """
        cfg = self.config
        rng = self.rng
        primary = child.primary
        if primary is None:
            return None
        roll = rng.random()

        if roll < cfg.title_token_unlabelled:
            self._bump("title_token")
            self._bump("title_token_unlabelled")
            return Segment(value=primary.value, label=None, attribute=primary.name)

        if roll < cfg.title_token_unlabelled + cfg.title_token_not_primary:
            classes = [(k, v) for k, v in cfg.title_secondary_mix.items() if k in child.secondary]
            # If the type carries no secondary dimension there is nothing
            # misleading to name, and the token falls back to the labelled
            # primary below -- counted once, there, not twice.
            if classes:
                total = sum(w for _, w in classes)
                pick = str(
                    rng.choices([k for k, _ in classes], weights=[w / total for _, w in classes])[0]
                )
                attribute = child.secondary[pick]
                label = self._label_for(attribute.name)
                self._bump("title_token")
                self._bump("title_token_not_primary")
                return Segment(
                    value=attribute.value,
                    label=label,
                    attribute=attribute.name,
                )

        label = self._label_for(primary.name)
        self._bump("title_token")
        return Segment(value=primary.value, label=label, attribute=primary.name)

    def _label_for(self, attribute_name: str) -> str:
        forms = LABEL_FORMS.get(attribute_name)
        if not forms:
            return attribute_name
        return str(_weighted(self.rng, forms))

    def _build_line_title(self, draft: LineDraft, child: ChildDraft) -> Title:
        """A SKU title, in one of the two measured styles."""
        cfg = self.config
        rng = self.rng
        descriptive = rng.random() < cfg.title_descriptive_share
        segments: list[Segment] = []

        dimension = self._dimension_segment(child)
        if dimension is not None:
            segments.append(dimension)

        for name, value in draft.descriptors:
            text = value if descriptive else abbreviate_value(value)
            segments.append(Segment(value=text, label=None, attribute=name))

        flutes = next((a for a in draft.line_attrs if a.name == "Number of Flutes"), None)
        if flutes is not None:
            label = self._label_for("Number of Flutes")
            segments.append(Segment(value=flutes.value, label=label, attribute=flutes.name))

        if not descriptive:
            end = next(
                (a for a in draft.line_attrs if a.name == "Single End/Double End"),
                None,
            )
            if end is not None:
                segments.append(Segment(value=f"{abbreviate_value(end.value)} Sq End", label=None))

        # A label cut off where the title hits its cap.
        if segments and rng.random() < cfg.scaled_defect(cfg.title_label_truncation):
            # The cut lands on the LAST LABELLED segment. Looking only at the
            # final segment misses every title that ends in a bare descriptor,
            # which is most of them, and drove the truncation rate an order of
            # magnitude below its target.
            # The measured signature is that the label is a strict prefix of
            # the ATTRIBUTE NAME it resolved to -- "Milling Di" for
            # "Milling Dia.", "Neck L" for "Neck Length". So the cut is taken
            # from the full name, not from whatever abbreviation the segment
            # happened to be carrying: cutting a two-character "FL" leaves
            # nothing, and requiring a long enough abbreviation made most
            # titles ineligible and halved the rate.
            eligible = [
                i
                for i, seg in enumerate(segments)
                if seg.attribute and seg.label is not None and len(seg.attribute) > 4
            ]
            if not eligible:
                # The roll fired on a title carrying no label to cut. Rather
                # than drop it -- which silently conditioned the 3.23% on
                # "titles that happen to have a label", and delivered 2.2% --
                # the segment that WOULD have carried a label gets one, and
                # that is what the cap cuts through. A truncated title is by
                # definition one where a label was present and got cut.
                eligible = [
                    i for i, seg in enumerate(segments) if seg.attribute and len(seg.attribute) > 4
                ]
            if eligible:
                index = eligible[-1]
                target = segments[index]
                assert target.attribute is not None
                keep = len(target.attribute) - rng.randint(1, 3)
                segments[index] = Segment(
                    value=target.value,
                    label=truncate_label(target.attribute, keep),
                    attribute=target.attribute,
                    truncated=True,
                )
                self._bump("title_label_truncated")

        tight = rng.randrange(len(segments)) if segments and rng.random() < 0.18 else None
        return build_title(
            f"{draft.brand} {draft.item}" if rng.random() < 0.35 else draft.item,
            tuple(segments),
            cap=cfg.title_length_cap,
            tight_delimiter_at=tight,
        )

    def _image_reference(self, sku: str) -> tuple[str, ...]:
        """Which image a SKU points at.

        Measured: 54 of 496 records carry no parseable image reference at all,
        and of those that do, 325 of 442 point at an image whose SKU is not the
        product's own. Image reuse crosses brands, so the pool is global rather
        than per line -- the image reference is NOT derivable from the SKU, and
        anything downstream that assumes it is will be wrong three times in
        four.
        """
        rng = self.rng
        if rng.random() < self.config.image_missing:
            self._bump("image_missing")
            return ()
        self._bump("image_present")
        if self._image_pool and rng.random() < self.config.image_sku_diverges:
            self._bump("image_diverges")
            how_many = rng.choices((1, 2, 5), weights=(0.72, 0.18, 0.10), k=1)[0]
            how_many = min(how_many, len(self._image_pool))
            return tuple(sorted(rng.sample(self._image_pool, k=how_many)))
        self._image_pool.append(sku)
        return (sku,)

    # -- assembly ---------------------------------------------------------

    def _corrupt_angle(self, line_attrs: list[Attribute]) -> list[Attribute]:
        """An angular attribute published with a LENGTH unit: Helix Angle = 42".

        A unit-type error rather than a magnitude error, and measured at 4.7%
        of the records carrying an angle. The angle is a property of the line,
        so the bad value is too -- one wrong row in a supplier's line data
        reaches every SKU under it, which is how these arrive in a real
        catalog.
        """
        index = next(
            (i for i, a in enumerate(line_attrs) if a.name in ("Helix Angle", "Point Angle")),
            None,
        )
        if index is None:
            return line_attrs
        self._bump("eligible_angle_lines")
        if self.rng.random() >= self.config.scaled_defect(
            self.config.defect_angle_carries_length_unit
        ):
            return line_attrs
        bogus = self.rng.choice(('42"', '1"', '1-1/4"', '2"', '1-5/8"'))
        out = list(line_attrs)
        # No value_num: there is no angle here to put in one, and inventing
        # one would paper over the defect this record exists to exhibit.
        out[index] = Attribute(out[index].name, bogus)
        self._bump("defect_angle_length_unit_lines")
        return out

    def _finish_line(self, type_key: str, draft: LineDraft, index: int) -> ProductLine | None:
        rng = self.rng
        line_attrs = self._apply_sparsity(type_key, draft.line_attrs, "line")
        line_attrs = self._corrupt_angle(line_attrs)
        # One spelling of the measurement-system attribute per line.
        system_name = str(_weighted(rng, MEASUREMENT_SYSTEM_NAMES))
        standards_attr = self._standards_attribute(type_key)
        if standards_attr is not None:
            line_attrs = [*line_attrs, standards_attr]

        children: list[Sku] = []
        for child in draft.children:
            attrs = self._apply_sparsity(type_key, list(child.attrs), "sku")
            if not attrs:
                continue
            attrs = self._inject_defects(child, attrs)
            system_attr, _ = self._measurement_system(child.system, system_name)
            if system_attr is not None:
                attrs = [*attrs, system_attr]

            sku = self._new_sku()
            title = self._build_line_title(draft, child)
            price = round(max(1.25, child.price_basis * rng.uniform(2.5, 9.0)), 2)
            children.append(
                Sku(
                    sku=sku,
                    title=title.text,
                    attributes=tuple(attrs),
                    price_usd=price,
                    stock=rng.choices(
                        (0, rng.randint(1, 40), rng.randint(40, 900)), weights=(0.08, 0.42, 0.5)
                    )[0],
                    image_skus=self._image_reference(sku),
                )
            )
            self._bump("skus")

        if not children:
            return None

        product_id = f"{draft.brand.split()[0].upper()[:3]}-{draft.series}-{index:04d}"
        parent_title = f"{draft.brand} {draft.series} -- {draft.item}"
        return ProductLine(
            product_id=product_id,
            type_key=type_key,
            title=parent_title,
            brand=draft.brand,
            series=draft.series,
            category=draft.category,
            attributes=tuple(line_attrs),
            children=tuple(children),
            dimension_provenance=draft.provenance,
        )

    def generate(self) -> Catalog:
        cfg = self.config
        rng = self.rng
        weights = cfg.type_weights
        keys = list(weights)
        counts = {key: max(1, round(cfg.lines * weights[key])) for key in keys}

        lines: list[ProductLine] = []
        index = 0
        for type_key in keys:
            builder = self._BUILDERS[type_key]
            for _ in range(counts[type_key]):
                category = rng.choice(taxonomy.LEAVES[type_key])
                draft = builder(self, type_key, category)
                index += 1
                line = self._finish_line(type_key, draft, index)
                if line is not None:
                    lines.append(line)
                    self._bump("lines")
        return Catalog(lines=tuple(lines), stats=dict(self.counters))


def generate(config: GeneratorConfig | None = None) -> Catalog:
    return Generator(config).generate()
