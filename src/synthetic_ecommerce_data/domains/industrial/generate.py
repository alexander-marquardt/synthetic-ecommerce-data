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

from collections.abc import Iterable
from dataclasses import replace
from fractions import Fraction
from typing import Literal, TypeVar

from synthetic_ecommerce_data.core import brands, price, typespec
from synthetic_ecommerce_data.core.config import GeneratorConfig
from synthetic_ecommerce_data.core.formats import (
    LengthStyle,
    UnpublishableMagnitude,
    canonical_style,
    format_angle,
    format_length_best,
)
from synthetic_ecommerce_data.core.model import (
    Attribute,
    Catalog,
    ProductLine,
    keyword_attribute,
    length_attribute,
    numeric_attribute,
)
from synthetic_ecommerce_data.core.voice import Voice
from synthetic_ecommerce_data.domains.industrial import (
    breadth,
    compat,
    hammers,
    series,
    standards,
    taxonomy,
)
from synthetic_ecommerce_data.domains.industrial.defects import DefectMixin
from synthetic_ecommerce_data.domains.industrial.drafts import (  # noqa: F401 - re-exported
    END_SHAPE_WORD,
    KEY_DIMENSIONS,
    MAX_MISSES,
    UNIT_SPLIT_KEYS,
    ChildDraft,
    LineDraft,
    _weighted,
)
from synthetic_ecommerce_data.domains.industrial.finishing import FinishMixin
from synthetic_ecommerce_data.domains.industrial.muststock import (
    MAX_ATTEMPTS,
    MUST_STOCK,
    MustStockUnmetError,
)
from synthetic_ecommerce_data.domains.industrial.newtypes import NEW_TYPES
from synthetic_ecommerce_data.domains.industrial.titles import TitleMixin

MM_PER_INCH = 25.4

#: The manufacturers, their ranges, shares, house styles and voices live in
#: ONE table, :mod:`.brands`. Re-exported here, where the builders and older
#: callers have always found the name list.
BRANDS = brands.BRANDS

#: Flat washer materials, and the finishes each is sold in.
WASHER_MATERIALS: tuple[str, ...] = (
    "Steel",
    "18-8 Stainless Steel",
    "316 Stainless Steel",
    "Brass",
    "Nylon",
)
WASHER_FINISHES: dict[str, tuple[str, ...]] = {
    "Steel": ("Plain", "Zinc Plated", "Zinc Yellow", "Hot Dip Galvanized", "Black Oxide"),
    "18-8 Stainless Steel": ("Plain",),
    "316 Stainless Steel": ("Plain",),
    "Brass": ("Plain",),
    "Nylon": ("Plain",),
}

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

#: The fine-pitch standard of each hex bolt standard: the same head dimensions
#: over an ISO 262 fine thread. ASME B18.2.1 covers UNC and UNF alike.
FINE_PITCH_BOLT_STANDARD: dict[str, str] = {
    "ASME B18.2.1": "ASME B18.2.1",
    "ISO 4014": "ISO 8765",
    "ISO 4017": "ISO 8676",
    "DIN 933": "DIN 961",
}

#: The distinct standards, in the order the cycle first reaches them. A
#: standard's position here is the offset its grading and finish wheels START
#: at, and that offset is what stops three standards from replaying identical
#: wheel positions -- see :meth:`Generator._build_hex_bolt`.
HEX_BOLT_PHASE: tuple[str, ...] = tuple(dict.fromkeys(HEX_BOLT_STANDARDS))

#: Hex bolt finishes, as the sequence the finish rotates through. Zinc plated
#: first: it is the common commercial finish on a hex cap screw.
HEX_BOLT_FINISHES: tuple[str, ...] = ("Zinc Plated", "Plain", "Hot Dip Galvanized")

#: A graded hex bolt's material follows its grade: SAE J429 Grade 5 and ISO
#: 898-1 Class 8.8 are medium-carbon steel, Grade 8 and Class 10.9 alloy steel.
#: (Stainless bolts carry no SAE grade or 8.8/10.9 class, so none is made.)
BOLT_MATERIAL: dict[str, str] = {
    "Grade 5": "Steel",
    "Class 8.8": "Steel",
    "Grade 8": "Alloy Steel",
    "Class 10.9": "Alloy Steel",
}

#: A socket screw's finishes and Rockwell hardness, by material.
SOCKET_SCREW_FINISH: dict[str, tuple[tuple[str, ...], str]] = {
    "Alloy Steel": (("Black Oxide", "Zinc Plated"), "C38"),
    "Grade 12.9 Alloy Steel": (("Black Oxide", "Plain"), "C39"),
    "18-8 Stainless Steel": (("Plain",), "B80"),
}

#: Tool coatings and surface treatments, by tool material. nACo and AlTiN are
#: carbide coatings; black oxide is a steam treatment of HSS; the straw/bronze
#: oxide is cobalt's.
END_MILL_FINISH: dict[str, tuple[str, ...]] = {
    "High Speed Steel": ("Bright", "TiN", "TiCN", "TiAlN"),
    "Cobalt": ("Bright", "TiN", "TiCN", "TiAlN", "AlTiN"),
    "Solid Carbide": ("Uncoated", "TiN", "TiCN", "TiAlN", "AlTiN", "nACo"),
}
DRILL_FINISH: dict[str, tuple[str, ...]] = {
    "High Speed Steel": ("Bright", "Black Oxide", "TiN"),
    "Cobalt": ("Bright", "Bronze Oxide", "TiN"),
    "Solid Carbide": ("Bright", "TiN", "TiAlN"),
}

#: Bolt gradings, by the system the standard publishes in. SAE J429 grades
#: describe inch fasteners and ISO property classes describe metric ones; the
#: two are not interchangeable spellings of one idea and a line carries the
#: one its standard uses.
INCH_GRADES: tuple[str, ...] = ("Grade 5", "Grade 8")
METRIC_GRADES: tuple[str, ...] = ("Class 8.8", "Class 10.9")


#: A fastener head of either kind, rebuilt by :meth:`Generator._near_miss_thread`.
_Head = TypeVar("_Head", standards.FastenerHead, standards.HexBoltHead)


def _retype(draft: LineDraft, thread_type: str) -> None:
    """Restate a line's ``Thread Type`` (and its descriptor, if it names one)."""
    draft.line_attrs = [
        keyword_attribute("Thread Type", thread_type) if a.name == "Thread Type" else a
        for a in draft.line_attrs
    ]
    draft.descriptors = [
        (n, thread_type if n == "Thread Type" else v) for n, v in draft.descriptors
    ]


#: The letters an end mill's series code starts with, per type. Both types
#: publish the bare item "End Mill" half the time, and series are kept unique
#: within one type only (a type shares no state with another), so disjoint
#: letters are what keep a square and a ball end mill from sharing a name.
END_MILL_SERIES_LETTERS: dict[str, str] = {"end_mill_square": "GHK", "end_mill_ball": "MPR"}


class Generator(TitleMixin, DefectMixin, FinishMixin):
    """One product type's builder, deterministic from the seed and the type key.

    Every piece of state here -- the random stream, the SKU sequence, the
    product index, the specs and series already used -- belongs to ONE type
    (:mod:`.typespec`), so a type's output cannot depend on which other types
    were built or in what order. Only ``counters`` (the build statistics) is
    shared, and it is a sum.
    """

    def __init__(
        self,
        config: GeneratorConfig | None,
        type_key: str,
        counters: dict[str, int] | None = None,
    ) -> None:
        # A builder with no type would draw from a stream and a block no
        # collision check has seen, so only a known type, after that check.
        if type_key not in _check_blocks():
            raise ValueError(f"no product type {type_key!r}")
        self.config = config or GeneratorConfig()
        self.type_key = type_key
        self.rng = typespec.type_rng(self.config.seed, type_key)
        #: The type's part-number block, which leads every SKU and product id.
        self._block = typespec.block_of(type_key)
        #: How many SKUs and how many product drafts this type has issued.
        self._sequence = 0
        self._index = 0
        self._used_skus: set[str] = set()
        #: Every spec drawn so far, per (type, brand) -- see :meth:`_spec_key`.
        self._drawn_specs: set[tuple] = set()
        self._title_styles: dict[tuple[str, str], str] = {}
        #: The PUBLISHED specs, per (type, brand, always-published values):
        #: a SKU whose published spec is a subset or superset of one already
        #: made differs from it only by an attribute sparsity dropped.
        self._published_specs: dict[tuple, list[frozenset]] = {}
        #: (type, brand) pairs whose spec space is spent, and how many lines
        #: in a row each has drafted without making a SKU.
        self._exhausted: set[tuple[str, str]] = set()
        self._misses: dict[tuple[str, str], int] = {}
        #: Every (brand, series) a product of this type already carries, so no
        #: two products share a product name.
        self._used_series: set[tuple[str, str]] = set()
        #: The current line's brand voice (:mod:`.voice`) and its published
        #: line-level facts, set per line by :meth:`_finish_line`.
        self._voice: Voice | None = None
        self._line_facts: dict[str, str] = {}
        #: The attribute names the SKU being titled publishes.
        self._published: set[str] = set()
        self.counters: dict[str, int] = {} if counters is None else counters
        self._rotations: dict[str, int] = {}
        #: Builder choices a must-stock entry fixes (:mod:`.muststock`); empty
        #: for the main generation.
        self._pins: dict[str, float] = {}

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

    def _pack(
        self, type_key: str, line: str, diameter_in: float, diameters: Iterable[float]
    ) -> Attribute:
        """A pack-sold line's ``Package Quantity`` (:func:`.price.pack_quantity`):
        ranked by its diameter among every diameter its type offers, so the
        pack falls as the size grows, and placed by its own draw, so no other
        draw moves."""
        offered = sorted({round(d, 4) for d in diameters})
        quantity = price.pack_quantity(
            price.BORROWS.get(type_key, type_key),
            offered.index(round(diameter_in, 4)),
            len(offered),
            price.pack_draw(self.config.seed, type_key, line),
        )
        return numeric_attribute("Package Quantity", str(quantity), float(quantity))

    def _page_pack(self, type_key: str, brand: str, line_attributes: list[Attribute]) -> Attribute:
        """A line's ``Package Quantity`` when the pack belongs to its group
        page (:func:`.price.page_pack`): drawn from the brand and the line
        attributes every line of the type publishes and a census cell holds
        equal, as :func:`.price.group_draw` reads them, so every size of a
        page shares one pack and no size ranks it."""
        always = self._always_published(type_key)
        held = [
            (a.name, a.value)
            for a in line_attributes
            if a.name in always and price.holds_equal(type_key, a)
        ]
        quantity = price.page_pack(
            type_key, price.page_pack_draw(self.config.seed, type_key, brand, held)
        )
        return numeric_attribute("Package Quantity", str(quantity), float(quantity))

    def _new_sku(self) -> str:
        """The type's next part number: its block, then a scrambled sequence.

        Unique by construction rather than by retrying a random draw: a draw
        checked against every SKU issued so far couples each type to all the
        others. All digits, so it can never wear a reference SKU's code, every
        one of which carries letters (``tests/test_catalog_noncopy.py``).
        """
        self._sequence += 1
        sku = typespec.part_number(self._block, self._sequence)
        if sku in self._used_skus:  # pragma: no cover - the stride is coprime to 10**6
            raise RuntimeError(f"{self.type_key} issued part number {sku} twice")
        self._used_skus.add(sku)
        return sku

    def _next_index(self) -> int:
        """The type's next product index; every draft takes one, made or not."""
        self._index += 1
        return self._index

    def _product_id(self, brand: str, series: str, index: int) -> str:
        """``<brand code>-<series>-<block>-<index>``: unique because the block is."""
        return f"{brands.BY_NAME[brand].code}-{series}-{self._block:04d}-{index:04d}"

    def _variant_count(self) -> int:
        """How many variants the next product offers, from the ONE distribution knob."""
        return int(_weighted(self.rng, self.config.variants_per_product))  # type: ignore[arg-type]

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
        material = rng.choice(taxonomy.END_MILL_MATERIALS[type_key])
        metric = rng.random() < 0.22
        system = "mm" if metric else "in"

        brand = brands.pick_brand(rng, type_key, self._exhausted)
        flutes = int(_weighted(rng, series.FLUTE_WEIGHTS))  # type: ignore[arg-type]
        helix = rng.choice(series.HELIX_ANGLES)
        coating = rng.choice(END_MILL_FINISH[material])
        style_name = "Ball Nose" if ball else "Square"
        item = f"{material} {style_name} End Mill" if rng.random() < 0.5 else "End Mill"
        series_code = f"{rng.choice(END_MILL_SERIES_LETTERS[type_key])}{rng.randint(100, 999)}"

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
            keyword_attribute("Material", material),
            keyword_attribute("Finish", coating),
            numeric_attribute("Number of Flutes", str(flutes), float(flutes)),
            Attribute("Helix Angle", format_angle(helix), helix),
            keyword_attribute(
                "Cutting Direction", "Right Hand" if rng.random() < 0.93 else "Left Hand"
            ),
            keyword_attribute(
                "Single End/Double End", "Single End" if rng.random() < 0.85 else "Double End"
            ),
            keyword_attribute(
                "Cutting Type",
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
            ("Material", material),
            ("Finish", coating),
        ]

        # One shank policy per line: a line is either built on matching shanks
        # or on a reduced/oversize shank, and the measured 64.9% equal rate is
        # a property of the catalog, so it is decided here.
        shanks_match = rng.random() < cfg.shank_equals_cutting_dia
        length_class, multiple = rng.choice(series.LENGTH_CLASSES)
        # Drawn first either way, so a pinned multiple moves no later draw.
        multiple = self._pins.get("length_multiple", multiple)

        count = self._variant_count()
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
                    # Never smaller than the cutting diameter: a ratio below 1
                    # (the census carries 0.833 and 0.75) is read as "the next
                    # shank up", and a snap that lands below it goes up too.
                    shank_mm = series.larger_shank_metric(dia_mm, dia_mm * max(ratio, 1.0))
                geom = series.build_metric(dia_mm, length_class, multiple, shank_mm)
            else:
                dia_fr = Fraction(dia)
                if shanks_match:
                    shank_fr = series.nearest_shank_imperial(float(dia_fr))
                else:
                    ratio = float(_weighted(rng, series.OBSERVED_SHANK_RATIOS))  # type: ignore[arg-type]
                    shank_fr = series.larger_shank_imperial(
                        float(dia_fr), float(dia_fr) * max(ratio, 1.0)
                    )
                geom = series.build_imperial(dia_fr, length_class, multiple, shank_fr)

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
            # Unconditionally computed and appended, like Milling Dia./Shank
            # Dia./Length of Cut/Overall Length above: WHETHER either publishes
            # is decided once, centrally, by ``_apply_sparsity`` reading the
            # census presence rate off VOCAB. A second probabilistic gate here
            # used to duplicate that decision at the SAME rate VOCAB declares,
            # squaring the presence instead of reproducing it -- 0.22 and 0.18
            # made Corner Radius and Neck Length land at ~5%/~3% of end mills
            # instead of the measured 40%/27%
            # (alexander-marquardt/synthetic-ecommerce-data#39).
            neck_in = geom.length_of_cut_in * rng.uniform(1.05, 1.4)
            neck = self._length("Neck Length", neck_in, style)
            child.attrs.append(neck)
            child.secondary["neck"] = neck
            radius_in = geom.cutting_dia_in / rng.choice((8.0, 16.0, 32.0))
            child.attrs.append(self._length("Corner Radius", radius_in, style))
            # The "flute" class of misleading title token: a flute length that
            # is not the cutting diameter.
            child.secondary["flute"] = loc
            draft.children.append(child)
        return draft

    def _build_drill(self, type_key: str, category: tuple[str, ...]) -> LineDraft:
        rng = self.rng
        brand = brands.pick_brand(rng, type_key, self._exhausted)
        material = rng.choice(("High Speed Steel", "Cobalt", "Solid Carbide"))
        point = rng.choice(series.POINT_ANGLES)
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
            keyword_attribute("Material", material),
            keyword_attribute("Point Type", rng.choice(("Split Point", "Standard Point"))),
            Attribute("Point Angle", format_angle(point), point),
            keyword_attribute("Finish", rng.choice(DRILL_FINISH[material])),
            keyword_attribute("Shank Type", rng.choice(("Straight", "Reduced"))),
            keyword_attribute("Cutting Direction", "Right Hand"),
            keyword_attribute("List Number", series_code),
        ]
        draft.descriptors = [("Material", material)]

        count = self._variant_count()
        # A third of the drill lines are metric (DIN 338 sizes), which is where
        # a metric tap's drill lives: a tap-drill chart names 10.2mm for
        # M12x1.75, and a catalog of fractional drills alone has no such part.
        metric = rng.random() < 0.35
        system = "mm" if metric else "in"
        pool: list[float] = (
            [mm / MM_PER_INCH for mm in series.DRILL_METRIC_MM]
            if metric
            else [float(f) for f in series.DRILL_FRACTIONAL]
        )
        rng.shuffle(pool)
        for size_in in pool[:count]:
            style = self._style(system)
            child = ChildDraft(system=system)
            # A jobber drill's flute length and overall length follow the size,
            # in whole millimetres or sixteenths as each system states them.
            if metric:
                flute_in = round(min(size_in * 9.0, 4.0) * MM_PER_INCH) / MM_PER_INCH
                oal_in = round((flute_in + max(size_in * 4.0, 0.9)) * MM_PER_INCH) / MM_PER_INCH
            else:
                flute_in = float(series.snap_imperial(min(size_in * 9.0, 4.0), 16))
                oal_in = float(series.snap_imperial(flute_in + max(size_in * 4.0, 0.9), 16))
            child.primary = self._length("Size", size_in, style)
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
            draft.children.append(child)
        return draft

    def _build_tap(self, type_key: str, category: tuple[str, ...]) -> LineDraft:
        rng = self.rng
        brand = brands.pick_brand(rng, type_key, self._exhausted)
        metric = rng.random() < 0.35
        # One line in four is the series' fine-pitch sibling.
        fine = rng.random() < 0.25
        thread_type = (
            ("Metric Fine" if fine else "Metric Coarse") if metric else ("UNF" if fine else "UNC")
        )
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
            keyword_attribute("Material", rng.choice(("High Speed Steel", "Powdered Metal"))),
            keyword_attribute("Finish", rng.choice(("Bright", "TiN", "Steam Oxide"))),
            keyword_attribute("Thread Direction", "Right Hand"),
            keyword_attribute("Thread Type", thread_type),
            keyword_attribute("Tap Chamfer", rng.choice(("Plug", "Bottoming", "Taper"))),
            numeric_attribute("Number of Flutes", str(flutes), float(flutes)),
        ]
        draft.descriptors = [("Thread Type", thread_type)]

        table = {
            "Metric Coarse": series.TAP_SIZES_METRIC,
            "Metric Fine": series.TAP_SIZES_METRIC_FINE,
            "UNC": series.TAP_SIZES_UNC,
            "UNF": series.TAP_SIZES_UNF,
        }[thread_type]
        pool = list(table)
        rng.shuffle(pool)
        count = min(self._variant_count(), len(pool))
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
                # Two quantities, two headings, as real catalogs publish them: a
                # metric tap's Pitch is the millimetres between threads, an inch
                # tap's Threads per Inch is how many an inch holds. One heading
                # over both put a bare 32 beside 0.5 mm.
                (
                    Attribute("Thread Pitch", f"{pitch:g}", bare_unit="MMT")
                    if metric
                    else Attribute("Threads per Inch", str(pitch), bare_unit="TPI")
                ),
                self._length("Overall Length", oal_in, style),
                self._length("Thread Length", oal_in * 0.45, style),
                self._length("Shank Dia.", major_in * 0.9, style),
            ]
            child.secondary = {"other_length": child.attrs[2], "length_of_cut": child.attrs[3]}
            draft.children.append(child)
        return draft

    #: The hex-socket screw lines still declared here, each with the standard
    #: its dimensions come from in each system, the head style the drawing
    #: reads, and the accessor that knows which columns of that standard's
    #: table are the head. A type declared in its own module
    #: (``screw_socket_head``) passes its own row to the builder instead.
    #:
    #: One row per line rather than an ``if flat`` and a default: a button head
    #: and a low head are different products with different published
    #: dimensions, and a row says so where a boolean would have had to grow a
    #: second and a third meaning.
    _SOCKET_SCREW_LINES: dict[str, standards.SocketScrewLine] = {
        "screw_flat_head": standards.SocketScrewLine(
            "ISO 10642",
            "ASME B18.3.2",
            "Flat",
            "Socket Flat Head Cap Screw",
            standards.flat_head,
            length_over_head=True,
        ),
        "screw_button_head": standards.SocketScrewLine(
            "ISO 7380-1",
            "ASME B18.3.3A",
            "Button",
            "Button Head Socket Cap Screw",
            standards.button_head,
        ),
        "screw_low_head": standards.SocketScrewLine(
            "DIN 7984",
            "ASME B18.3.1G",
            "Low Socket",
            "Low Head Socket Cap Screw",
            standards.low_head,
        ),
    }

    def _build_socket_screw(
        self,
        type_key: str,
        category: tuple[str, ...],
        line: standards.SocketScrewLine | None = None,
    ) -> LineDraft:
        """Hexagon socket cap screws -- socket, countersunk, button or low head.

        All four come from extracted standards, and which one a line is built
        to decides its head dimensions entirely: a button head's dome and a low
        head's squat cylinder are that standard's own head diameter and head
        height, not a socket head's scaled.

        ``line`` is the type's own row, passed by its type module; a type
        still declared here reads its row from :attr:`_SOCKET_SCREW_LINES`.
        """
        line = line or self._SOCKET_SCREW_LINES[type_key]
        rng = self.rng
        flat = line.length_over_head
        # Alternated rather than tossed. Both systems get half the lines
        # either way in expectation, but a coin flip over the twenty lines of
        # the low-head type gave eight metric and twelve inch, and the metric
        # standard offers NINE sizes -- so M20 low head cap screws did not
        # exist. Which sizes a catalog carries must not be decided by a coin.
        metric = self._rotate(f"system:{type_key}", 2) == 0
        head_style, style_name = line.head_style, line.style_name
        standard = line.metric_standard if metric else line.inch_standard
        head_of = line.head

        brand = brands.pick_brand(rng, type_key, self._exhausted)
        material = rng.choice(("Alloy Steel", "18-8 Stainless Steel", "Grade 12.9 Alloy Steel"))
        # Finish and hardness follow the material, as a distributor lists them
        # (SOCKET_SCREW_FINISH): alloy steel through-hardened to Rockwell C,
        # black oxide or zinc; 18-8 stainless, cold-worked to Rockwell B and
        # left plain. A zinc-plated stainless screw is not sold.
        finishes, hardness = SOCKET_SCREW_FINISH[material]
        finish = rng.choice(finishes)
        draft = LineDraft(
            item=style_name,
            brand=brand,
            series=f"{standard.replace(' ', '')}-{rng.randint(10, 99)}",
            category=category,
            provenance=standard,
        )
        draft.line_attrs = [
            keyword_attribute("Item", style_name),
            keyword_attribute("Type", style_name),
            keyword_attribute("Head Type", head_style),
            keyword_attribute("Drive Type", "Hex Socket"),
            keyword_attribute("Material", material),
            keyword_attribute("Finish", finish),
            keyword_attribute("Thread Direction", "Right Hand"),
            keyword_attribute("Thread Type", "Metric Coarse" if metric else "UNC"),
            keyword_attribute("Rockwell Hardness", hardness),
            keyword_attribute("Meets/Exceeds", standard),
        ]
        draft.descriptors = [("Material", material)]

        sizes = standards.available_sizes(standard)
        size = sizes[self._rotate(f"size:{type_key}:{standard}", len(sizes))]
        head = head_of(standard, size)
        draft.line_attrs.append(
            self._pack(
                type_key,
                f"{standard}:{size}:{brand}:{draft.series}",
                head.major_dia_in,
                (
                    head_of(system_standard, offered_size).major_dia_in
                    for system_standard in (line.metric_standard, line.inch_standard)
                    for offered_size in standards.available_sizes(system_standard)
                ),
            )
        )
        # Near-miss threads: every FINE_PERIOD-th line of a diameter that has a
        # fine pitch is built to it, so ``m12 socket cap screws`` finds M12x1.5
        # and M12x1.25 beside M12x1.75 and the pitch facet has a real choice.
        # Rotated, not tossed, for the reason the system alternates above.
        head, fine = self._near_miss_thread(head, f"{type_key}:{standard}:{size}", metric)
        if fine:
            if metric:
                # ISO 4762 and its three siblings are COARSE-thread standards;
                # a fine-pitch screw keeps their head dimensions but does not
                # meet them, so it claims none.
                draft.line_attrs = [a for a in draft.line_attrs if a.name != "Meets/Exceeds"]
                draft.provenance = f"{standard} head dimensions; ISO 262 fine-pitch thread"
            _retype(draft, "Metric Fine" if metric else "UNF")

        lengths = list(standards.offered_lengths_in(standard, size))
        if not lengths:
            lengths = [0.25, 0.375, 0.5, 0.75, 1.0, 1.25, 1.5]
        count = min(self._variant_count(), len(lengths))
        offered = self._offered_run(f"lengths:{standard}:{size}", lengths, count)
        system = "mm" if head.published_unit == "mm" else "in"

        for length_in in offered:
            style = self._style(system)
            child = ChildDraft(system=system)
            # Fully threaded below about 2x the head diameter, else a standard
            # thread length: 2D + 1/2" for inch practice.
            thread_len_in = min(length_in, 2 * head.major_dia_in + 0.5)
            child.primary = keyword_attribute("Dia./Thread Size", head.thread_designation)
            length_attr = self._length("Length", length_in, style)
            thread_attr = self._length("Thread Length", thread_len_in, style)
            child.attrs = [
                child.primary,
                length_attr,
                # Not on the countersunk line. Its nominal length is measured
                # OVER the head (ISO 10642, ASME B18.3), so its catalog length
                # is ``Length``; what lies under the head is that length less a
                # toleranced cone height, and publishing it put 12.56mm and
                # 1.3910" beside the stocked lengths -- values no distributor
                # lists and no shopper types.
                *([] if flat else [self._length("Length under Head", length_in, style)]),
                thread_attr,
                self._length("Head Dia.", head.head_dia_in, style),
                self._length("Head Height", head.head_height_in, style),
            ]
            if head.drive_size_in:
                # The nominal key, not the extracted socket's toleranced
                # across-flats: a distributor prints "10mm", never 10.07mm.
                key_in = compat.nominal_key_in(head.drive_size_in, metric)
                child.attrs.append(self._length("Drive Size", key_in, style))
            # Named rather than indexed: the misleading-title-token classes
            # have to keep naming the same two attributes when the list they
            # are drawn from grows a third length.
            child.secondary = {"other_length": length_attr, "length_of_cut": thread_attr}
            draft.children.append(child)
        return draft

    #: Every FINE_PERIOD-th line of a diameter with a fine pitch is built to
    #: it -- one in three. Coarse stays the common case, as it is in any
    #: distributor's fastener aisle, and each fine pitch still exists.
    FINE_PERIOD = 3
    #: The hex bolt's period is FIVE, not three, because its finish wheel is
    #: three long and turns with the line counter: every third line of a size
    #: landed on the same finish, so each UNF size offered one finish
    #: (measured: 6 of 26 sizes locked). Five is prime to both wheels.
    BOLT_FINE_PERIOD = 5

    def _near_miss_thread(
        self, head: _Head, key: str, metric: bool, period: int = FINE_PERIOD
    ) -> tuple[_Head, bool]:
        """``head`` rebuilt to a fine pitch of its diameter on every third line, else as is.

        The fine pitches are ISO 262's (metric) and the Unified fine series
        (inch) -- :func:`.compat.fine_threads`. The head dimensions do not
        change: they are a function of the diameter, not the pitch.
        """
        fine = compat.fine_threads(head.size, metric)
        if not fine or self._rotate(f"fine:{key}", period) != period - 1:
            return head, False
        designation = fine[self._rotate(f"fine-pitch:{key}", len(fine))]
        if metric:
            return replace(head, pitch_mm=float(designation.split("x")[1])), True
        return replace(head, threads_per_inch=float(designation.split("-")[1])), True

    def _build_hex_bolt(self, type_key: str, category: tuple[str, ...]) -> LineDraft:
        rng = self.rng
        # ISO 4017 and DIN 933 describe the same product and disagree on width
        # across flats at M10 and M12. Which standard the line is built to is a
        # property of the line, so it is chosen here.
        standard = HEX_BOLT_STANDARDS[self._rotate("bolt_standard", len(HEX_BOLT_STANDARDS))]
        brand = brands.pick_brand(rng, type_key, self._exhausted)
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
        # Hot-dip galvanizing is for Grade 5 / Class 8.8: ASTM F2329 keeps it
        # off fasteners as hard as Grade 8 / Class 10.9, which are sold zinc
        # yellow instead. Same wheel position, so no size locks to a finish.
        if finish == "Hot Dip Galvanized" and grade in ("Grade 8", "Class 10.9"):
            finish = "Zinc Yellow"
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
            keyword_attribute("Type", "Hex Head"),
            keyword_attribute("Head Type", "Hex"),
            keyword_attribute("Material", BOLT_MATERIAL[grade]),
            keyword_attribute("Finish", finish),
            keyword_attribute("Grade", grade),
            keyword_attribute("Thread Direction", "Right Hand"),
            keyword_attribute(
                "Thread Type", "UNC" if standard.startswith("ASME") else "Metric Coarse"
            ),
        ]
        draft.descriptors = [("Grade", grade)]
        # Near-miss threads, as on the socket screws. A fine-pitch hex bolt
        # has the coarse one's head and is its own standard: ISO 8765 beside
        # ISO 4014, ISO 8676 beside ISO 4017, DIN 961 beside DIN 933. ASME
        # B18.2.1 covers the Unified fine series itself.
        metric = head.published_unit == "mm"
        head, fine = self._near_miss_thread(
            head, f"{type_key}:{standard}:{size}", metric, self.BOLT_FINE_PERIOD
        )
        if fine:
            _retype(draft, "Metric Fine" if metric else "UNF")
            draft.provenance = FINE_PITCH_BOLT_STANDARD[standard]
        # After the thread's retyping, so the page is read as the cell holds it.
        draft.line_attrs.append(self._page_pack(type_key, brand, draft.line_attrs))

        lengths = list(standards.offered_lengths_in(standard, size)) or [0.5, 0.75, 1.0, 1.5, 2.0]
        count = min(self._variant_count(), len(lengths))
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
                self._length("Length under Head", length_in, style),
                thread_attr,
                self._length("Width Across Flats", head.width_across_flats_in, style),
                self._length("Head Height", head.head_height_in, style),
                # The renderer reads Head Dia. for a cylindrical head, and a
                # hex head's side profile really is its width across flats.
                self._length("Head Dia.", head.width_across_flats_in, style),
            ]
            child.secondary = {"other_length": length_attr, "length_of_cut": thread_attr}
            draft.children.append(child)
        return draft

    def _build_washer(self, type_key: str, category: tuple[str, ...]) -> LineDraft:
        rng = self.rng
        brand = brands.pick_brand(rng, type_key, self._exhausted)
        # Headroom for the 100K catalog: five materials, each with the finishes
        # it is actually sold in. A plated or oxided stainless, brass or nylon
        # washer is not a product, so only steel carries a coating; the others
        # are sold plain. (The draw used to pair any material with "Zinc
        # Plated", nylon included.) ISO 7089 fixes the dimensions whatever
        # the material, so no dimension is invented here.
        material = rng.choice(WASHER_MATERIALS)
        finish = rng.choice(WASHER_FINISHES[material])
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
            keyword_attribute("Type", "Plain"),
            keyword_attribute("Material", material),
            keyword_attribute("Finish", finish),
        ]
        draft.descriptors = [("Material", material)]

        sizes = list(standards.available_sizes("ISO 7089"))
        rng.shuffle(sizes)
        count = min(self._variant_count(), len(sizes))
        for size in sizes[:count]:
            plain = standards.washer("ISO 7089", size)
            style = self._style("mm")
            child = ChildDraft(system="mm")
            child.primary = keyword_attribute("Size", size)
            outside = self._length("Outside Dia.", plain.outside_dia_in, style)
            child.attrs = [
                child.primary,
                self._length("Inside Dia.", plain.inside_dia_in, style),
                outside,
                self._length("Thickness", plain.thickness_in, style),
            ]
            child.secondary = {"other_length": outside}
            draft.children.append(child)
        return draft

    def _build_hammer(self, type_key: str, category: tuple[str, ...]) -> LineDraft:
        """The ball pein hammer; every other hammer kind is a type module (hammers.py)."""
        return hammers.build(hammers.BALL_PEIN)(self, type_key, category)

    def _build_flap_disc(self, type_key: str, category: tuple[str, ...]) -> LineDraft:
        rng = self.rng
        brand = brands.pick_brand(rng, type_key, self._exhausted)
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
            keyword_attribute("Shape", rng.choice(("Type 27 Flat", "Type 29 Conical"))),
            keyword_attribute("Mounting Type", "Arbor Hole"),
        ]
        draft.descriptors = [("Abrasive Material", abrasive)]

        dia = rng.choice(series.FLAP_DISC_DIAS_IN)
        arbor = rng.choice(series.FLAP_DISC_ARBORS)
        grits = list(series.FLAP_DISC_GRITS)
        rng.shuffle(grits)
        count = min(self._variant_count(), len(grits))
        # Max safe speed falls with diameter; it is a property of the disc.
        max_rpm = int(round(48000 / float(dia) / 100.0) * 100)
        for grit in sorted(grits[:count]):
            style = self._style("in")
            child = ChildDraft(system="in")
            child.primary = numeric_attribute("Grit", str(grit), float(grit))
            disc = self._length("Diameter", float(dia), style)
            child.attrs = [
                child.primary,
                disc,
                self._length("Arbor Hole", float(arbor), style),
                numeric_attribute("Max. RPM", f"{max_rpm:,}", float(max_rpm)),
            ]
            child.secondary = {"other_length": disc}
            draft.children.append(child)
        return draft

    _BUILDERS = {
        "end_mill_square": _build_end_mill,
        "end_mill_ball": _build_end_mill,
        "drill_jobber": _build_drill,
        "tap_spiral_point": _build_tap,
        "screw_flat_head": _build_socket_screw,
        "screw_button_head": _build_socket_screw,
        "screw_low_head": _build_socket_screw,
        "bolt_hex": _build_hex_bolt,
        "washer_flat": _build_washer,
        "hammer_ball_pein": _build_hammer,
        "abrasive_flap_disc": _build_flap_disc,
    }

    def build(self) -> list[ProductLine]:
        """This type's lines: its own products, then its must-stock lines."""
        key = self.type_key
        cfg = self.config
        lines: list[ProductLine] = []
        kind = _type_kinds()[key]
        if kind == "modelled":
            builder = self._builder()
            (category,) = taxonomy.LEAVES[key]
            own = typespec.modelled().get(key)
            weight = cfg.type_weights.get(key, own.share if own else None)
            count = 0 if weight is None else max(1, round(cfg.lines * weight))
            for _ in range(count):
                self._keep(
                    lines, self._finish_line(key, builder(self, key, category), self._next_index())
                )
        elif kind == "new":
            for _ in range(cfg.new_type_products.get(key, 0)):
                self._keep(lines, self._new_type_line(key))
        else:
            lines.append(breadth.build_line(self, breadth.row_for(key), self._next_index()))
        if cfg.must_stock:
            lines.extend(self._must_stock(lines))
        return lines

    def _builder(self):
        """This modelled type's builder: its type module's ``make``, else the shared table's."""
        own = typespec.modelled().get(self.type_key)
        if own is not None:
            return lambda gen, key, category: own.make(gen, key, category)
        return self._BUILDERS[self.type_key]

    def _keep(self, lines: list[ProductLine], line: ProductLine | None) -> None:
        if line is not None:
            lines.append(line)
            self._bump("lines")

    def _new_type_line(self, type_key: str) -> ProductLine | None:
        """One newer-type product, a few of them deliberately with zero axes."""
        spec = NEW_TYPES[type_key]
        draft = spec.build(self, type_key, spec.category)
        if len(draft.children) == 1 and self.rng.random() < self.config.zero_axis_share:
            (only,) = draft.children
            draft.line_attrs = [*draft.line_attrs, *only.attrs]
            only.attrs = []
            only.zero_axis = True
            self._bump("zero_axis_products")
        return self._finish_line(type_key, draft, self._next_index())

    def _must_stock(self, lines: list[ProductLine]) -> list[ProductLine]:
        """A line for every must-stock entry this type owns and does not yet carry.

        See :mod:`.muststock`. An entry belongs to its FIRST type, and only
        that type's lines are checked, so whether a line is added never
        depends on what another type happened to draw. Each entry builds from
        its own stream, so adding an entry moves none of the type's products.
        """

        def stocked(entry, candidates) -> bool:
            return any(
                entry.matches(
                    line.type_key, {a.name: a.value for a in (*line.attributes, *child.attributes)}
                )
                for line in candidates
                for child in line.children
            )

        key = self.type_key
        added: list[ProductLine] = []
        for entry in MUST_STOCK:
            if entry.types[0] != key or stocked(entry, [*lines, *added]):
                continue
            own_rng, own_pins = self.rng, self._pins
            self.rng = typespec.type_rng(self.config.seed, f"{key}:must-stock:{entry.example}")
            self._pins = dict(entry.pins)
            try:
                builder = self._builder()
                (category,) = taxonomy.LEAVES[key]
                for _ in range(MAX_ATTEMPTS):
                    line = self._finish_line(key, builder(self, key, category), self._next_index())
                    if line is not None and stocked(entry, [line]):
                        added.append(line)
                        self._bump("must_stock_lines")
                        break
                else:
                    raise MustStockUnmetError(
                        f"no {key} line built in {MAX_ATTEMPTS} tries carries "
                        f"{dict(entry.values)} ({entry.example!r})"
                    )
            finally:
                self.rng, self._pins = own_rng, own_pins
        return added


#: How a type is built: by a modelled builder (a type module's ``make``, or
#: :attr:`Generator._BUILDERS` until it has one), from :data:`.newtypes.NEW_TYPES`,
#: or from one breadth row (a YAML row, or a type module's ``breadth``).
TypeKind = Literal["modelled", "new", "breadth"]


def _type_kinds() -> dict[str, TypeKind]:
    """Every type's kind, from every place a type can be declared, refusing a key
    declared twice."""
    declared: list[tuple[str, TypeKind]] = [
        *((key, "modelled") for key in Generator._BUILDERS),
        *((key, "modelled") for key in typespec.modelled()),
        *((key, "new") for key in NEW_TYPES),
        *((row.key, "breadth") for row in breadth.rows()),
    ]
    keys = [key for key, _ in declared]
    twice = sorted({key for key in keys if keys.count(key) > 1})
    if twice:
        raise typespec.TypeCollisionError(f"type keys defined twice: {twice}")
    return dict(declared)


def all_type_keys(kind: TypeKind | None = None) -> list[str]:
    """Every type the build makes (or every one of ``kind``), in build order:
    sorted by key, so a new type lands in a fixed place without being listed
    anywhere.

    The one place a reader gets the type list: a type moves from a shared
    table to its own module without any reader noticing (#48).
    """
    return sorted(key for key, found in _type_kinds().items() if kind in (None, found))


def _check_blocks() -> list[str]:
    """Every type key, after refusing any two that share a part-number block."""
    keys = all_type_keys()
    yaml_rows = {row.key for row in breadth.rows()} - set(typespec.registered())
    typespec.check_collisions(
        {key: typespec.block_of(key) for key in keys},
        {key: breadth.fix_site(key) for key in keys if key in yaml_rows},
    )
    return keys


def generate_type(
    config: GeneratorConfig, type_key: str, counters: dict[str, int] | None = None
) -> list[ProductLine]:
    """One type's lines, built alone: the same lines the whole build makes for it."""
    return Generator(config, type_key, counters).build()


def generate(config: GeneratorConfig | None = None, types: Iterable[str] | None = None) -> Catalog:
    """The catalog: each type built on its own, in key order, and concatenated.

    ``types`` builds only those types; every other type's output is unchanged
    by leaving one out, which is what lets types be built in parallel.
    """
    cfg = config or GeneratorConfig()
    known = _check_blocks()
    unknown = sorted({*cfg.type_weights, *cfg.new_type_share, *(types or ())} - set(known))
    if unknown:
        raise ValueError(f"no such product type(s): {unknown}")
    chosen = known if types is None else sorted(set(types))
    counters: dict[str, int] = {}
    lines = [line for key in chosen for line in Generator(cfg, key, counters).build()]
    return Catalog(lines=tuple(lines), stats=dict(counters))
