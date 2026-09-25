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
    LengthStyle,
    UnpublishableMagnitude,
    canonical_style,
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
    states_value,
)
from .taxonomy import drawing_for, image_id_for
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

#: The cycle a hex bolt line's standard rotates through. ISO 4017 and DIN 933
#: describe the same product and disagree on width across flats at M10 and
#: M12, which is why both are here.
#:
#: The inch standard takes TWO of the five places. Three of the four standards
#: are metric ones for very nearly the same product, so drawing uniformly made
#: three hex-bolt lines in four metric, in a catalog modelled on a US
#: industrial distributor whose hex cap screws are overwhelmingly inch. Two
#: places rather than three, because the arithmetic is tight in the other
#: direction: each metric standard offers NINE sizes and the type's 45 lines
#: leave exactly nine per metric standard, which is what the size rotation
#: needs to reach all of them.
HEX_BOLT_STANDARDS: tuple[str, ...] = (
    "ASME B18.2.1",
    "ISO 4014",
    "ASME B18.2.1",
    "ISO 4017",
    "DIN 933",
)

#: The distinct standards, in the order the cycle first reaches them. A
#: standard's position here is the offset its grading and finish wheels START
#: at, and that offset is what stops three standards from replaying identical
#: wheel positions -- see :meth:`Generator._build_hex_bolt`.
HEX_BOLT_PHASE: tuple[str, ...] = tuple(dict.fromkeys(HEX_BOLT_STANDARDS))

#: Hex bolt finishes, as the sequence the finish rotates through. Zinc plated
#: first: it is the common commercial finish on a hex cap screw.
HEX_BOLT_FINISHES: tuple[str, ...] = ("Zinc Plated", "Plain", "Hot Dip Galvanized")

#: Bolt gradings, by the system the standard publishes in. SAE J429 grades
#: describe inch fasteners and ISO property classes describe metric ones; the
#: two are not interchangeable spellings of one idea and a line carries the
#: one its standard uses.
INCH_GRADES: tuple[str, ...] = ("Grade 5", "Grade 8")
METRIC_GRADES: tuple[str, ...] = ("Class 8.8", "Class 10.9")


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
        self.counters: dict[str, int] = {}
        self._rotations: dict[str, int] = {}

    # -- bookkeeping ----------------------------------------------------

    def _bump(self, key: str, amount: int = 1) -> None:
        self.counters[key] = self.counters.get(key, 0) + amount

    def _rotate(self, key: str, count: int) -> int:
        """The next index of a deterministic rotation over ``count`` choices.

        Used wherever a LINE makes ONE choice from a list the catalog claims
        to offer -- a thread size out of a standard's sizes, a window over the
        cutting-diameter series. Sampling those leaves coverage to luck, and
        luck has already cost this catalog real products: 500 lines spread
        over twelve product types draw a list of sixteen values so few times
        that several values land on no line at all, and the miss is silent --
        the catalog simply has no 15 mm end mill and nothing says so. Measured
        before this: 11 mm, 15 mm and 25 mm cutting diameters each held ZERO
        documents while their neighbours held eighty.

        A rotation visits every value before it revisits any, so the offered
        list and the catalog's contents cannot drift apart, and a test can
        assert that every offered value reached a line.

        Keys are nested where combinations matter: the grade rotation is keyed
        per (standard, size), so the second line at one size gets the second
        grade rather than a fresh draw that may repeat the first.
        """
        return self._rotation_step(key) % count if count else 0

    def _rotation_step(self, key: str) -> int:
        """How many times ``key``'s rotation has advanced, uncapped.

        Exposed because some rotations run several wheels off ONE step -- see
        :meth:`_build_hex_bolt`, where the size, the grade and the finish all
        turn on the line counter and have to stay out of phase with each other.
        """
        index = self._rotations.get(key, 0)
        self._rotations[key] = index + 1
        return index

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
        """The spelling for *system* -- the SAME one every time.

        This used to draw from a weighted table, which is what put ``18mm``,
        ``18.00mm``, ``18 mm`` and ``18.00 mm`` in one column of one catalog
        and fragmented every dimensional facet roughly threefold. The draw is
        gone rather than narrowed: a distribution with one member is still a
        distribution, and the next person to widen it would not be breaking a
        rule that was written down. See :mod:`.formats`.
        """
        return canonical_style(system)

    def _publish(self, inches: float, style: LengthStyle) -> str:
        try:
            return format_length_best(inches, style)
        except UnpublishableMagnitude:
            fallback = LengthStyle(style.system, style.suffix, "decimal", places=4)
            return format_length_best(inches, fallback)

    def _length(self, name: str, inches: float, style: LengthStyle) -> Attribute:
        return length_attribute(name, self._publish(inches, style))

    def _offered_run(self, key: str, lengths: list[float], count: int) -> list[float]:
        """A CONTIGUOUS run of a size's offered lengths, at a rotating offset.

        A real line stocks a run -- 1", 1-1/4", 1-3/8", 1-1/2", 1-5/8", 1-3/4"
        -- not a scatter. Shuffling the standard's 29 offered lengths and
        keeping twelve produced lines reading 1", 1-3/8", 2-1/4", 3-1/4", 12",
        which is not what a distributor offers and, worse, left the COMMON
        lengths missing at random: the reference distributor's own query names
        ``1-3/4" length under head`` and whether any record carried it was a
        coin toss.

        The offset rotates per (standard, size), so the first line at a size
        offers the shortest run -- where the common lengths are -- and later
        lines walk up the list until the long end is covered too.
        """
        if count >= len(lengths):
            return sorted(lengths)
        ordered = sorted(lengths)
        start = self._rotate(key, len(ordered) - count + 1)
        return ordered[start : start + count]

    # -- type builders ---------------------------------------------------

    def _build_end_mill(self, type_key: str, category: tuple[str, ...]) -> LineDraft:
        cfg = self.config
        rng = self.rng
        ball = type_key == "end_mill_ball"
        # The line's tool material: an ATTRIBUTE, never a path level
        # (elastic/prism-industrial-products#77).
        # Drawn first, where the earlier generator drew the per-material path,
        # so the rest of the random stream is exactly where it was.
        material = rng.choice(taxonomy.END_MILL_MATERIALS[type_key])
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
        # A ROTATING WINDOW over the series rather than a random subset of it.
        # The cap has to stay (see above), but WHICH of the sixteen offered
        # diameters a line gets must not be a lottery: the metric series is
        # drawn only by the ~22% of end-mill lines that are metric, and a
        # random subset left three ordinary sizes -- 11, 15 and 25 mm -- on no
        # line at all. The window advances one place per line and is shared
        # between the square and the ball-nose builder, so a size reaches BOTH
        # styles rather than whichever type happened to draw it.
        #
        # The window is cut to the SKU count here rather than by truncating a
        # shuffled pool afterwards. Truncating after the shuffle throws away a
        # random part of the window, which is the lottery again by another
        # route: measured that way, 15 mm came back to zero square end mills.
        window = min(len(matching), count)
        pool_of = matching if shanks_match else full
        start = self._rotate(
            f"cutting_dia:{system}:{'match' if shanks_match else 'any'}", len(pool_of)
        )
        chosen = [pool_of[(start + offset) % len(pool_of)] for offset in range(window)]
        rng.shuffle(chosen)

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

    #: The four hex-socket screw lines, each with the standard its dimensions
    #: come from in each system, the head style the drawing reads, and the
    #: accessor that knows which columns of that standard's table are the head.
    #:
    #: Four rows rather than an ``if flat`` and a default: a button head and a
    #: low head are different products with different published dimensions, and
    #: a table says so where a boolean would have had to grow a second and a
    #: third meaning.
    _SOCKET_SCREW_LINES: dict[str, tuple[str, str, str, str]] = {
        "screw_socket_head": ("ISO 4762", "ASME B18.3", "Socket", "Socket Head Cap Screw"),
        "screw_flat_head": ("ISO 10642", "ASME B18.3.2", "Flat", "Socket Flat Head Cap Screw"),
        "screw_button_head": (
            "ISO 7380-1",
            "ASME B18.3.3A",
            "Button",
            "Button Head Socket Cap Screw",
        ),
        "screw_low_head": (
            "DIN 7984",
            "ASME B18.3.1G",
            "Low Socket",
            "Low Head Socket Cap Screw",
        ),
    }

    def _build_socket_screw(self, type_key: str, category: tuple[str, ...]) -> LineDraft:
        """Hexagon socket cap screws -- socket, countersunk, button or low head.

        All four come from extracted standards, and which one a line is built
        to decides its head dimensions entirely: a button head's dome and a low
        head's squat cylinder are that standard's own head diameter and head
        height, not a socket head's scaled.
        """
        rng = self.rng
        flat = type_key == "screw_flat_head"
        # Alternated rather than tossed. Both systems get half the lines
        # either way in expectation, but a coin flip over the twenty lines of
        # the low-head type gave eight metric and twelve inch, and the metric
        # standard offers NINE sizes -- so M20 low head cap screws did not
        # exist. Which sizes a catalog carries must not be decided by a coin.
        metric = self._rotate(f"system:{type_key}", 2) == 0
        metric_standard, inch_standard, head_style, style_name = self._SOCKET_SCREW_LINES[type_key]
        standard = metric_standard if metric else inch_standard
        head_of = {
            "screw_socket_head": standards.socket_head,
            "screw_flat_head": standards.flat_head,
            "screw_button_head": standards.button_head,
            "screw_low_head": standards.low_head,
        }[type_key]

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

        sizes = standards.available_sizes(standard)
        size = sizes[self._rotate(f"size:{type_key}:{standard}", len(sizes))]
        head = head_of(standard, size)

        lengths = list(standards.offered_lengths_in(standard, size))
        if not lengths:
            lengths = [0.25, 0.375, 0.5, 0.75, 1.0, 1.25, 1.5]
        count = min(rng.randint(*self.config.skus_per_line), len(lengths))
        offered = self._offered_run(f"lengths:{standard}:{size}", lengths, count)
        system = "mm" if head.published_unit == "mm" else "in"

        for length_in in offered:
            style = self._style(system)
            child = ChildDraft(system=system)
            # Fully threaded below about 2x the head diameter, else a standard
            # thread length: 2D + 1/2" for inch practice.
            thread_len_in = min(length_in, 2 * head.major_dia_in + 0.5)
            # A countersunk screw's nominal length is measured OVER its head,
            # because the head sinks into the work; every other style's is
            # measured under it. So the length under the head is the nominal
            # length less a head height for the flat head line, and the nominal
            # length itself for the other three -- which is why the attribute
            # is worth publishing rather than inferring from Length.
            under_head_in = length_in - head.head_height_in if flat else length_in
            child.primary = keyword_attribute("Dia./Thread Size", head.thread_designation)
            length_attr = self._length("Length", length_in, style)
            thread_attr = self._length("Thread Length", thread_len_in, style)
            child.attrs = [
                child.primary,
                length_attr,
                self._length("Length Under Head", under_head_in, style),
                thread_attr,
                self._length("Head Dia.", head.head_dia_in, style),
                self._length("Head Height", head.head_height_in, style),
            ]
            if head.drive_size_in:
                child.attrs.append(self._length("Drive Size", head.drive_size_in, style))
            # Named rather than indexed: the misleading-title-token classes
            # have to keep naming the same two attributes when the list they
            # are drawn from grows a third length.
            child.secondary = {"other_length": length_attr, "length_of_cut": thread_attr}
            child.price_basis = length_in * 0.4 + head.major_dia_in * 2
            draft.children.append(child)
        return draft

    def _build_hex_bolt(self, type_key: str, category: tuple[str, ...]) -> LineDraft:
        rng = self.rng
        # ISO 4017 and DIN 933 describe the same product and disagree on width
        # across flats at M10 and M12. Which standard the line is built to is a
        # property of the line, so it is chosen here.
        standard = HEX_BOLT_STANDARDS[self._rotate("bolt_standard", len(HEX_BOLT_STANDARDS))]
        brand = rng.choice(BRANDS)
        # Three wheels off ONE line counter: the size, the grading and the
        # finish. Those are three of the four attribute-value pairs the
        # reference distributor's parametric query names, and eleven lines per standard
        # cannot cover thirty-six combinations -- so which combinations exist
        # must not be luck. Sampling them left the catalog with no Grade 8,
        # Zinc Plated 7/16-14 hex bolt at all, which is the reference distributor's own
        # example.
        #
        # The grade and finish wheels take ONE EXTRA STEP each time the size
        # wheel wraps. Without it their periods (2 and 3) divide the size
        # wheel's (6) and the triple ALIASES: every 7/16 line is the same
        # grading and the same finish, so a shopper filtering to one size finds
        # a single value in each of those two facets. Measured both ways --
        # aliased, Class 10.9 and Hot Dip Galvanized fell to zero documents
        # each; out of phase, consecutive lines at one size walk through the
        # gradings and the finishes and every value keeps its documents.
        #
        # The size is also read before the line's attributes because the GRADE
        # depends on it: an SAE J429 grade is an inch fastener's grading and an
        # ISO property class is a metric one. Drawing from one pool of four
        # published a "Class 10.9" 7/16-14 bolt, a designation that does not
        # exist.
        sizes = standards.available_sizes(standard)
        step = self._rotation_step(f"line:{type_key}:{standard}")
        size = sizes[step % len(sizes)]
        # The extra step on a wrap is not enough on its own: each of the three
        # METRIC standards gets nine lines and offers nine sizes, so the size
        # wheel never wraps, the extra step never fires, and all three replay
        # the SAME wheel positions. A shopper filtering to M8x1.25 -- the
        # natural action, and the one this is about -- then meets one grading
        # and one finish whichever standard's line they land on. Measured that
        # way: 9 of the 15 published sizes locked, every metric one.
        #
        # So each standard also STARTS its grading and finish wheels at its own
        # offset. The inch standard's offset is zero, which leaves that half of
        # the catalog exactly as it was.
        phase = step + step // len(sizes) + HEX_BOLT_PHASE.index(standard)
        head = standards.hex_bolt(standard, size)
        grades = INCH_GRADES if head.published_unit == "in" else METRIC_GRADES
        grade = grades[phase % len(grades)]
        finish = HEX_BOLT_FINISHES[phase % len(HEX_BOLT_FINISHES)]
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
            keyword_attribute("Fastener Finish", finish),
            keyword_attribute("Grade", grade),
            keyword_attribute("Thread Direction", "Right Hand"),
            keyword_attribute(
                "Thread Type", "UNC" if standard.startswith("ASME") else "Metric Coarse"
            ),
        ]
        draft.descriptors = [("Grade", grade)]

        lengths = list(standards.offered_lengths_in(standard, size)) or [0.5, 0.75, 1.0, 1.5, 2.0]
        count = min(rng.randint(*self.config.skus_per_line), len(lengths))
        offered = self._offered_run(f"lengths:{standard}:{size}", lengths, count)
        system = "mm" if head.published_unit == "mm" else "in"

        for length_in in offered:
            style = self._style(system)
            child = ChildDraft(system=system)
            thread_len_in = min(length_in, 2 * head.major_dia_in + 0.25)
            child.primary = keyword_attribute("Dia./Thread Size", head.thread_designation)
            length_attr = self._length("Length", length_in, style)
            thread_attr = self._length("Thread Length", thread_len_in, style)
            child.attrs = [
                child.primary,
                length_attr,
                # A hex head does not sink into the work, so the bolt's length
                # is already measured under the head and the two attributes
                # state the same span. They are still two attributes: the
                # shopper's "1-3/4 length under head" has to bind to one, and
                # binding it to Thread Length would be silently wrong.
                self._length("Length Under Head", length_in, style),
                thread_attr,
                self._length("Width Across Flats", head.width_across_flats_in, style),
                self._length("Head Height", head.head_height_in, style),
                # The renderer reads Head Dia. for a cylindrical head, and a
                # hex head's side profile really is its width across flats.
                self._length("Head Dia.", head.width_across_flats_in, style),
            ]
            child.secondary = {"other_length": length_attr, "length_of_cut": thread_attr}
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
        "screw_button_head": _build_socket_screw,
        "screw_low_head": _build_socket_screw,
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
                    # The record's OWN system, in the catalog's ONE spelling
                    # for it. This used to pick its own style -- " in" at two
                    # decimals -- which published "2.25 in" beside the
                    # "2-1/4"" every other row of the same column carried, and
                    # split that size across two facet buckets. The DEFECT
                    # here is the value (a cut longer than the tool); its
                    # spelling was never part of it. Keep the bad value, drop
                    # the bad spelling (elastic/prism#9284).
                    style = canonical_style(child.system)
                    out[loc_index] = length_attribute(loc.name, self._publish(inflated, style))
                    self._bump("defect_loc_exceeds_oal")

        # Class 2 (the angular attribute carrying a length unit) is NOT applied
        # here. Helix Angle and Point Angle are line-constant, so a child-scoped
        # injection would never find one -- and measured exactly 0.0000 against
        # a target of 0.0469 until that was noticed. It is applied in
        # _corrupt_angle, at line scope, where the attribute actually lives.

        # Class 3: unit mixing inside one record -- one dimension published in
        # the other system.
        # LENGTHS only. "Unit mixing" is a record describing itself in two
        # measurement systems; a grit number, a flute count or an ounce weight
        # is in neither, and moving one produced "Grit: 1524mm" -- not a
        # modelled defect class, just a wrong value in a column that has no
        # measurement system to mix. Measured before this: 2 of the 6 Grit
        # values and 1 of the 8 Head Weight values were millimetre strings.
        length_names = {
            spec.name for specs in VOCAB.values() for spec in specs if spec.kind == "length"
        }
        dimension_indexes = [
            i for i, a in enumerate(out) if a.value_num is not None and a.name in length_names
        ]
        if len(dimension_indexes) >= 2:
            self._bump("eligible_unit_mixing")
            if rng.random() < cfg.scaled_defect(cfg.unit_mixing_within_record):
                index = rng.choice(dimension_indexes)
                other = "mm" if child.system == "in" else "in"
                # The OTHER system, in that system's one canonical spelling.
                # The defect is that this row is in the wrong unit for its
                # record -- not that it is spelled unusually within that unit.
                style = canonical_style(other)
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

        # NO label is cut off here any more. This block used to fire at the
        # measured 3.23% and publish titles ending "Dia./Thread Siz" or
        # "Number of Flut". The reference distributor's real titles carry none of it --
        # measured 24/24 clean on the scraped sample -- so it was a defect
        # class we invented, and it reads to a viewer as our rendering bug
        # rather than as a fact about catalog data. Removed by the ruling on
        # elastic/prism#9284, which is the same call already made for missing
        # product images: reproduce the defects the demo is meant to EXPOSE,
        # not the ones that merely make it look unfinished.
        #
        # ``truncate_label`` and ``Segment.truncated`` stay in naming.py: the
        # honest-rendering property they exist for is now proven by a test
        # fixture (elastic/prism#9288) rather than by shipped catalog data.

        tight = rng.randrange(len(segments)) if segments and rng.random() < 0.18 else None
        return build_title(
            f"{draft.brand} {draft.item}" if rng.random() < 0.35 else draft.item,
            tuple(segments),
            cap=cfg.title_length_cap,
            tight_delimiter_at=tight,
        )

    def _identifying_attribute(self, published: list[list[Attribute]]) -> str | None:
        """The ONE attribute that tells every SKU of a line apart, or None.

        Derived from the line's own records, never listed per product type: a
        hand-maintained per-type enumeration has gone stale in this repository
        twice already, and the data answers the question exactly. An attribute
        whose value is the same on every SKU distinguishes nothing -- a shopper
        choosing between six alloy-steel screws is not choosing the material,
        and ``Fastener Material: Alloy Steel`` belongs in the attribute block.

        Two conditions, and both are needed for the answer to be USABLE in a
        title. The attribute has to be on EVERY record (one carried by a fifth
        of them cannot name the other four fifths), and its published values
        have to be pairwise DISTINCT (a thread length that saturates at
        2D + 1/2" varies across the line and is still the same string on ten
        of twelve SKUs). An attribute failing either is not an identifier,
        whatever its spread.

        Among the ones that qualify, the widest RELATIVE variation wins, max
        over min of the parsed magnitudes: a line's SKUs are one product in
        several sizes, and the size that spreads furthest is the one being
        chosen between. Ties keep the attribute the type builder published
        first, so the answer never depends on dictionary ordering.

        Measured against what the records PUBLISH -- after sparsity has
        dropped what it drops and after the defect injection has rewritten
        what it rewrites -- rather than against the drafts. An attribute
        chosen off the drafts can be absent from the record by the time it is
        emitted, and a title naming a value its own attribute block does not
        carry is the defect this is here to remove, not a fix for it.
        Measured: 52 titles named a draft value the record had since lost.
        """
        if len(published) < 2:
            return None
        values: dict[str, list[str]] = {}
        numbers: dict[str, list[float]] = {}
        order: list[str] = []
        for attributes in published:
            for attribute in attributes:
                if attribute.name not in values:
                    values[attribute.name] = []
                    numbers[attribute.name] = []
                    order.append(attribute.name)
                values[attribute.name].append(attribute.value)
                if attribute.value_num is not None:
                    numbers[attribute.name].append(attribute.value_num)

        best: str | None = None
        best_spread = -1.0
        for name in order:
            seen = values[name]
            if len(seen) != len(published) or len(set(seen)) != len(published):
                continue
            magnitudes = [value for value in numbers[name] if value > 0]
            spread = max(magnitudes) / min(magnitudes) if len(magnitudes) > 1 else 0.0
            if spread > best_spread + 1e-9:
                best, best_spread = name, spread
        return best

    def _disambiguate_titles(
        self,
        titles: list[Title],
        published: list[list[Attribute]],
        identifying: str | None,
    ) -> list[Title]:
        """Give two SKUs of one line that share a title the thing that differs.

        This is the defect a shopper meets on the first screen: six cards
        reading ``Socket Head Cap Screw, M6x1, Alloy Steel`` at $2.10, $2.48,
        $4.85, $8.00, $8.34 and $10.42, identical in every visible respect.
        They are not duplicates -- they are 12, 16, 30 and 45 mm long -- and a
        thread size is LINE-constant, so a title built around it says the same
        thing on every SKU under the line. Measured before this: 176 of 500
        lines published a title two of their SKUs shared, over 1,214 SKUs.

        Repair rather than prevention, and deliberately so. The measured title
        grammar contains two hazards worth more than tidiness -- a dimension
        token with no label (46.7%) and a token that is NOT the primary
        dimension (17.1%) -- and composing every title around the identifying
        attribute would erase both. So the titles are composed as measured,
        and only the ones that actually collide are given one more segment.
        An end mill's title is untouched by this: its cutting diameter varies
        down the line, so its titles were already distinct.

        The segment goes in SECOND, right after the dimension token, so the
        100-character cap can never be what removes it -- and the title is
        reassembled from the segments it already had rather than rebuilt, so
        no measured choice is re-rolled.

        The trigger is NOT "two titles are the same string". That was the
        first formulation and it is too weak by a factor of five: a title
        carries the brand about a third of the time and a label in one of
        several abbreviations, so ``Hex Head Bolt, 7/16-14, Grade 8`` and
        ``Redmoor Hex Head Bolt, 7/16-14, Grade 8`` are different strings that
        tell a shopper apart by the brand name of the line they are both in.
        Measured, 705 SKUs passed a string-equality check while naming nothing
        that was theirs. The trigger is the PROPERTY instead: a title has to
        name a value this SKU publishes and its siblings do not.
        """
        if identifying is None or len(published) < 2:
            return titles
        by_name = [{a.name: a.value for a in attributes} for attributes in published]
        for index, title in enumerate(titles):
            mine = by_name[index]
            # Per ATTRIBUTE, not per value: the same string legitimately
            # appears on two SKUs of one line in two different roles -- a 3/8"
            # that is one tool's cutting diameter and another's shank -- and
            # that collision is what this catalog exists to exhibit.
            alone = [
                value
                for name, value in mine.items()
                if not any(
                    other.get(name) == value
                    for position, other in enumerate(by_name)
                    if position != index
                )
            ]
            if any(states_value(title.text, value) for value in alone):
                continue
            # No exemption for a title that already NAMES the identifying
            # attribute. It can name it and still be carrying a value the
            # record no longer publishes: a title is composed before the
            # defect injection, so a unit-mixing defect leaves a title reading
            # ``3/8"`` on a record publishing ``9.52mm``, and a shopper
            # scanning the card cannot tell that apart from a third size.
            # Measured at 8 rows on the 4,688-document generation that
            # preceded this catalog, and NOT re-derived here -- the
            # denominator names the catalog the figure belongs to rather
            # than being renumbered to this one's 4,689 on the assumption
            # that the numerator held. The published value goes in regardless,
            # and the stale token stays where it was -- mixed units inside one
            # record are a defect class this catalog carries on purpose, not
            # one to quietly repair.
            attribute = next((a for a in published[index] if a.name == identifying), None)
            if attribute is not None:
                segment = Segment(
                    value=attribute.value,
                    label=self._label_for(attribute.name),
                    attribute=attribute.name,
                )
                at = min(1, len(title.segments))
                segments = (*title.segments[:at], segment, *title.segments[at:])
                tight = title.tight_delimiter_at
                if tight is not None and tight >= at:
                    tight += 1
                titles[index] = build_title(
                    title.item,
                    segments,
                    cap=self.config.title_length_cap,
                    tight_delimiter_at=tight,
                )
                self._bump("title_disambiguated")
        return titles

    def _build_description(
        self, draft: LineDraft, title: Title, attributes: list[Attribute]
    ) -> str:
        """The description, in the grammar the real rows use.

            <title clause> - <the dimensions the title had no room for>,
            <line descriptors>, <brand line>

        Measured over the 24 real rows this catalog is modelled against, 24 of
        24 compose exactly that way::

            TITLE        Square End Mill: 3/4" Dia, 1-1/2" LOC
            DESCRIPTION  Square End Mill: 3/4" Dia, 1-1/2" LOC - 4" OAL,
                         3/4" Shank Dia, 40 deg Helix, AlTiN Finish, ...

        Three properties are load-bearing, and none of them is an accident:

        * **The title is the description's opening clause, verbatim.** The
          overlap is the SOURCE's own convention rather than duplication to be
          tidied away -- a marketplace listing repeats its size in the title,
          in the variant selector and twice in the specification table,
          because each tier is read at a different moment. Removing the
          overlap would be improving away the thing being reproduced.
        * **After the dash is what the title had no room for**: the attributes
          this SKU actually publishes, with their units, so that a shopper
          scanning six neighbouring cards can see what separates them without
          opening any of them.
        * **The brand line stays, at the end.** It is what the description
          used to be in its entirety -- ``Marrow & Sons ISO4762-64 -- Socket
          Head Cap Screw`` -- which restated the title, the brand and the
          product type and said nothing at all about this SKU. It earns a
          place; it does not earn the whole field.

        Composed from the attributes the record PUBLISHES, after sparsity and
        after defect injection, so the description and the attribute block
        cannot disagree about a value.
        """
        named = title.attribute_names()
        details: list[str] = []
        for attribute in attributes:
            if attribute.name in named:
                continue
            if attribute.values is not None:
                details.append(", ".join(attribute.values))
            else:
                details.append(f"{attribute.value} {attribute.name}")
        details.extend(
            value for _, value in draft.descriptors if not states_value(title.text, value)
        )
        details.append(f"{draft.brand} {draft.series}")
        return f"{title.text} - {', '.join(details)}"

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

        # The product id is built before the SKUs, because a SKU's image id is
        # its LINE's: one drawing stands behind the line, and every SKU under
        # it points at that one rather than at a drawing of its own.
        product_id = f"{draft.brand.split()[0].upper()[:3]}-{draft.series}-{index:04d}"
        image_id = image_id_for(type_key, product_id)

        # Composed first, for every SKU, because whether a title needs the
        # thing that differs is a question about the LINE and cannot be
        # answered one SKU at a time.
        built: list[tuple[str, list[Attribute], float, int]] = []
        titles: list[Title] = []
        for child in draft.children:
            attrs = self._apply_sparsity(type_key, list(child.attrs), "sku")
            if not attrs:
                continue
            attrs = self._inject_defects(child, attrs)
            system_attr, _ = self._measurement_system(child.system, system_name)
            if system_attr is not None:
                attrs = [*attrs, system_attr]

            sku = self._new_sku()
            titles.append(self._build_line_title(draft, child))
            price = round(max(1.25, child.price_basis * rng.uniform(2.5, 9.0)), 2)
            stock = rng.choices(
                (0, rng.randint(1, 40), rng.randint(40, 900)), weights=(0.08, 0.42, 0.5)
            )[0]
            built.append((sku, attrs, price, stock))

        if not built:
            return None

        published = [attrs for _, attrs, _, _ in built]
        titles = self._disambiguate_titles(
            titles, published, self._identifying_attribute(published)
        )

        children: list[Sku] = []
        for (sku, attrs, price, stock), title in zip(built, titles, strict=True):
            children.append(
                Sku(
                    sku=sku,
                    title=title.text,
                    description=self._build_description(draft, title, attrs),
                    attributes=tuple(attrs),
                    price_usd=price,
                    stock=stock,
                    image_id=image_id,
                )
            )
            self._bump("skus")

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
            image_id=image_id,
            drawing=drawing_for(type_key),
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
                (category,) = taxonomy.LEAVES[type_key]
                if type_key not in taxonomy.END_MILL_MATERIALS:
                    # A draw over a one-path tuple decides nothing. It is kept
                    # because the stream position it consumes is where an end
                    # mill's builder now draws its material: removing it would
                    # move every later id, dimension and price in the catalog.
                    rng.choice(taxonomy.LEAVES[type_key])
                draft = builder(self, type_key, category)
                index += 1
                line = self._finish_line(type_key, draft, index)
                if line is not None:
                    lines.append(line)
                    self._bump("lines")
        return Catalog(lines=tuple(lines), stats=dict(self.counters))


def generate(config: GeneratorConfig | None = None) -> Catalog:
    return Generator(config).generate()
