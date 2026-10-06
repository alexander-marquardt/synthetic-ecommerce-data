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

import functools
import hashlib
import random
from collections.abc import Iterable
from dataclasses import dataclass, field, replace
from fractions import Fraction
from typing import Literal, TypeVar

from . import (
    brands,
    breadth,
    compat,
    conformance,
    noise,
    price,
    series,
    standards,
    taxonomy,
    typespec,
)
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
from .muststock import MAX_ATTEMPTS, MUST_STOCK, MustStockUnmetError
from .naming import (
    LABEL_FORMS,
    Segment,
    Title,
    abbreviate_value,
    build_title,
    states_value,
)
from .newtypes import NEW_TYPES
from .taxonomy import drawing_for, image_id_for
from .vocab import (
    MEASUREMENT_SYSTEM_NAMES,
    MEASUREMENT_SYSTEM_PRESENCE,
    MEASUREMENT_SYSTEM_VALUES,
    STANDARDS_FAMILY,
    STANDARDS_NAME,
    STANDARDS_PRESENCE,
    VOCAB,
)
from .voice import Voice, description_tail, product_name, voice_for

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

#: Ball pein hammer handles, and the grips each is sold with: a wood handle
#: is sold bare, a fiberglass or steel one with a grip or without.
HAMMER_HANDLES: tuple[str, ...] = ("Hickory", "Ash", "Fiberglass", "Steel")
HAMMER_GRIPS: dict[str, tuple[str, ...]] = {
    "Hickory": ("None",),
    "Ash": ("None",),
    "Fiberglass": ("Rubber", "Vinyl", "None"),
    "Steel": ("Rubber", "Vinyl", "None"),
}

#: The attribute a type's titles must name when its variant axis is not its
#: size: the census title core is "<Item>, <key dim>, ...". Measured on the
#: first 100K build, bearing titles were 0.01 distinct and carried no size at
#: all ("Radial Ball Bearing, Double Seal Closure Type, Chrome Steel", 452
#: times); wheels 0.06 and flap discs 0.22 named only their grit.
KEY_DIMENSIONS: dict[str, tuple[str, ...]] = {
    # A bearing is named by its number AND its bore: the bore is what a
    # shopper fits it to (the review of the 100K catalog, 2026-09-29).
    "bearing_radial_ball": ("Bearing Number", "Bore"),
    "wheel_depressed_center": ("Diameter",),
    "abrasive_flap_disc": ("Diameter",),
    # Not a dimension, but it names what the screw IS, so it leads. Last in
    # the title, the value's trailing "Point" reads as a cut "Point Type".
    "set_screws_hex_socket": ("Point Type",),
}

#: Lines in a row a (type, brand) may draft without making a SKU before its
#: spec space counts as spent. See ``Generator._finish_line``.
MAX_MISSES = 20

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
    #: A deliberately awkward single variant that carries NO variant-scope
    #: attribute: everything it publishes is on its product. A grouped view
    #: must render a selector with zero axes (elastic/prism-industrial-products#103).
    zero_axis: bool = False


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
    #: Set by ``_finish_line``; the builders need not.
    type_key: str = ""
    #: The dimensional standard EVERY child's dimensions were read from, when
    #: the line's dimensions are not already a standard's by provenance (the
    #: hex nut: :func:`.newtypes.nut_row`). Empty when no one standard fits.
    standard: str = ""


#: The letters an end mill's series code starts with, per type. Both types
#: publish the bare item "End Mill" half the time, and series are kept unique
#: within one type only (a type shares no state with another), so disjoint
#: letters are what keep a square and a ball end mill from sharing a name.
END_MILL_SERIES_LETTERS: dict[str, str] = {"end_mill_square": "GHK", "end_mill_ball": "MPR"}

#: The word a terse title uses for an end mill's end shape, by its
#: ``End Mill Style``: ``SGL Sq End`` / ``SGL Ball End``.
END_SHAPE_WORD: dict[str, str] = {"Square": "Sq", "Ball Nose": "Ball"}


class Generator:
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
            # (alexander-marquardt/synthetic-industrial-products#39).
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
            keyword_attribute("Material", material),
            keyword_attribute("Point Type", rng.choice(("Split Point", "Standard Point"))),
            Attribute("Point Angle", point, float(point.split()[0])),
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
                    Attribute("Pitch", f"{pitch:g}", bare_unit="MMT")
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
        rng = self.rng
        brand = brands.pick_brand(rng, type_key, self._exhausted)
        handle = rng.choice(HAMMER_HANDLES)
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
            keyword_attribute("Material", "Forged Steel"),
            keyword_attribute("Handle Material", handle),
            keyword_attribute("Handle Grip Material", rng.choice(HAMMER_GRIPS[handle])),
            keyword_attribute("Face Type", "Ball Pein"),
        ]
        draft.descriptors = [("Handle Material", handle)]

        weights = list(series.HAMMER_HEAD_OUNCES)
        rng.shuffle(weights)
        count = min(self._variant_count(), len(weights))
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
            draft.children.append(child)
        return draft

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

    def _standards_attribute(self, type_key: str, draft: LineDraft) -> Attribute | None:
        """The standards this LINE conforms to, from :mod:`.conformance`'s
        truth table -- never a draw from a pool of standards for other parts."""
        if self.rng.random() > STANDARDS_PRESENCE:
            return None
        pool = conformance.applicable(
            type_key,
            {a.name: a.value for a in draft.line_attrs},
            metric=bool(draft.children) and draft.children[0].system == "mm",
            provenance=draft.provenance,
            standard=draft.standard,
        )
        if not pool:
            return None
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

    #: A (brand, type)'s title style, drawn ONCE per pair: "unlabelled" names
    #: the key dimension bare, "labelled" with its label, "secondary" labels it
    #: and adds a labelled secondary dimension. One maker lists one type one
    #: way; the census mix is reproduced ACROSS brands, not per SKU.
    TITLE_STYLES = ("unlabelled", "secondary", "labelled")

    def _title_style(self, brand: str, type_key: str) -> str:
        """The (brand, type)'s style: fixed per pair, and the census mix is hit
        ACROSS the type's makers by their market weight.

        The makers of a type are put in a seeded order and each takes the style
        its slice of the type's market weight falls in: the first 46.7% of
        weight unlabelled, the next 17.1% secondary, the rest labelled. A
        brand's share of a type's SKUs follows its weight, so the per-title
        mix approximates the census while every brand keeps one style. (A
        per-pair coin flip did not: 250 pairs weighted by SKU count drifted to
        0.35 / 0.26 against 0.47 / 0.17.)
        """
        cfg = self.config
        key = (brand, type_key)
        style = self._title_styles.get(key)
        if style is None:
            makers = sorted(
                brands.brands_for(type_key),
                key=lambda b: hashlib.sha256(
                    f"{cfg.seed}:title:{b.name}:{type_key}".encode()
                ).hexdigest(),
            )
            total = sum(b.weight for b in makers)
            cumulative = 0.0
            for maker in makers:
                middle = (cumulative + maker.weight / 2) / total
                cumulative += maker.weight
                if middle < cfg.title_token_unlabelled:
                    choice = "unlabelled"
                elif middle < cfg.title_token_unlabelled + cfg.title_token_not_primary:
                    choice = "secondary"
                else:
                    choice = "labelled"
                self._title_styles[(maker.name, type_key)] = choice
            style = self._title_styles.get(key, "labelled")
        return style

    def _dimension_segments(self, draft: LineDraft, child: ChildDraft) -> list[Segment]:
        """The title's dimension segments, in the (brand, type)'s ONE style.

        The key dimension (the child's primary, the axis the line varies on)
        is ALWAYS named; the style decides only whether it carries a label and
        whether a labelled secondary dimension follows it. A secondary is named
        only when the record PUBLISHES it -- a title naming a length the
        attribute block does not carry states a spec the record cannot back.
        """
        primary = child.primary
        if primary is None:
            return []
        style = self._title_style(draft.brand, draft.type_key)
        self._bump("title_token")
        if style == "unlabelled":
            self._bump("title_token_unlabelled")
            return [Segment(value=primary.value, label=None, attribute=primary.name)]
        segments = [
            Segment(
                value=primary.value, label=self._label_for(primary.name), attribute=primary.name
            )
        ]
        if style == "secondary":
            # The pair's secondary dimension, fixed like its style: the pair
            # ranks the secondary classes once, and each title names the
            # first one THIS record publishes. It used to pick by
            # ``digest % len(classes this child has)``, so an end mill with a
            # neck and one without picked different classes -- and a pick the
            # record did not publish left that title with no secondary, while
            # its siblings had one. A title names a secondary whenever the
            # record publishes one, or never (a "labelled" pair).
            attribute = next(
                (
                    child.secondary[k]
                    for k in self._secondary_order(draft.brand, draft.type_key)
                    if k in child.secondary
                    and child.secondary[k].name in self._published
                    and child.secondary[k].name != primary.name
                ),
                None,
            )
            if attribute is not None:
                self._bump("title_token_not_primary")
                segments.append(
                    Segment(
                        value=attribute.value,
                        label=self._label_for(attribute.name),
                        attribute=attribute.name,
                    )
                )
        return segments

    def _secondary_order(self, brand: str, type_key: str) -> list[str]:
        """The (brand, type)'s ranking of the secondary classes: the census mix,
        rotated by a seeded digest of the pair so makers lead with different
        ones."""
        classes = list(self.config.title_secondary_mix)
        digest = hashlib.sha256(f"{self.config.seed}:secondary:{brand}:{type_key}".encode())
        start = int(digest.hexdigest()[:8], 16) % len(classes)
        return classes[start:] + classes[:start]

    def _label_for(self, attribute_name: str) -> str:
        forms = LABEL_FORMS.get(attribute_name)
        if not forms:
            return attribute_name
        if self._voice is None:
            return str(_weighted(self.rng, forms))
        # The BRAND's spelling: every title one maker lists spells a label
        # the same way (:mod:`.voice`).
        return self._voice.labels[attribute_name]

    def _build_line_title(self, draft: LineDraft, child: ChildDraft) -> Title:
        """A SKU title, in one of the two measured styles: the brand's."""
        voice = self._voice
        assert voice is not None, "a title is composed inside _finish_line"
        descriptive = voice.descriptive
        segments: list[Segment] = []

        # The type's KEY dimension, when the variant axis is something else
        # (a bearing's closure, a wheel's grit): the census core of a title
        # names what the part IS, so a bearing title carries its number and a
        # wheel its diameter. Only a value the record publishes.
        key_values = {a.name: a.value for a in (*draft.line_attrs, *child.attrs)}
        for name in KEY_DIMENSIONS.get(draft.type_key, ()):
            if name in self._published and name in key_values:
                segments.append(Segment(value=key_values[name], label=None, attribute=name))

        segments.extend(self._dimension_segments(draft, child))

        for name, value in draft.descriptors:
            # A descriptor the record does not publish (sparsity dropped it)
            # is not stated: measured, 27 bearing titles named a ring
            # material their attribute block did not carry.
            if name not in self._published:
                continue
            text = value if descriptive else abbreviate_value(value)
            segments.append(Segment(value=text, label=None, attribute=name))

        flutes = next(
            (
                a
                for a in draft.line_attrs
                if a.name == "Number of Flutes" and a.name in self._published
            ),
            None,
        )
        if flutes is not None:
            label = self._label_for("Number of Flutes")
            segments.append(Segment(value=flutes.value, label=label, attribute=flutes.name))

        if not descriptive:
            end = next(
                (a for a in draft.line_attrs if a.name == "Single End/Double End"),
                None,
            )
            # The end SHAPE is the mill's own style: "SGL Sq End" on a square
            # end mill, "SGL Ball End" on a ball nose one. It used to say
            # "Sq End" on every end mill, ball nose included.
            shape = next(
                (a.value for a in draft.line_attrs if a.name == "End Mill Style"),
                None,
            )
            if end is not None and shape is not None:
                segments.append(
                    Segment(
                        value=f"{abbreviate_value(end.value)} {END_SHAPE_WORD[shape]} End",
                        label=None,
                    )
                )

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

        # The pack segment, last so the cap sheds it first -- and ONLY with the
        # record's own Package Quantity; no quantity is ever stated unbacked.
        quantity = self._line_facts.get("Package Quantity")
        if quantity is not None and voice.pack_label is not None:
            segments.append(
                Segment(value=quantity, label=voice.pack_label, attribute="Package Quantity")
            )

        tight = (
            min(int(voice.tight_at * len(segments)), len(segments) - 1)
            if segments and voice.tight_at is not None
            else None
        )
        qualifier = voice.qualifier[STANDARDS_FAMILY[draft.type_key]]
        item = f"{qualifier} {draft.item}" if qualifier else draft.item
        return build_title(
            f"{draft.brand} {item}" if voice.brand_first else item,
            tuple(segments),
            cap=self.config.title_length_cap,
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
        ``Vellinhorst Hex Head Bolt, 7/16-14, Grade 8`` are different strings that
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
        self,
        draft: LineDraft,
        title: Title,
        attributes: list[Attribute],
        compatibility: str = "",
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
          used to be in its entirety -- ``Ingleward ISO4762-64 -- Socket
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
            # Skipped only when the title states THIS value. A title composed
            # before the unit-mixing defect can name the attribute with its
            # pre-defect token (``5-5/16"`` beside a published ``134.94mm``);
            # the description then has to carry the value the record publishes.
            if attribute.name in named and (
                attribute.values is not None or states_value(title.text, attribute.value)
            ):
                continue
            if attribute.values is not None:
                details.append(", ".join(attribute.values))
            else:
                details.append(f"{attribute.value} {attribute.name}")
        published = {*self._line_facts, *(a.name for a in attributes)}
        details.extend(
            value
            for name, value in draft.descriptors
            if name in published and not states_value(title.text, value)
        )
        details.append(f"{draft.brand} {draft.series}")
        facts = {**self._line_facts, **{a.name: a.value for a in attributes}}
        tail = description_tail(draft.brand, draft.series, draft.type_key, facts)
        # The cross-reference sentence (:mod:`.compat`) sits between the spec
        # clause and the brand's template, where a distributor prints "for M12
        # socket head cap screws".
        middle = f"{compatibility} " if compatibility else ""
        return f"{title.text} - {', '.join(details)}. {middle}{tail}"

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

    #: Attributes that identify a SKU rather than describe it, left out of the
    #: spec a SKU must not share with another of its brand and type.
    IDENTIFIER_ATTRIBUTES = frozenset({"List Number"})
    #: What makes a SKU different is SUBSTANCE, never metadata: the
    #: measurement-system attribute (three spellings of one fact about the
    #: record's units) and the standards claimed are not what a shopper tells
    #: two parts apart by. Left out of both uniqueness checks, with the
    #: identifiers (the review of the 100K catalog: washers differing only by
    #: "Dimension Type" vs "System of Measurement").
    METADATA_ATTRIBUTES = frozenset(
        {STANDARDS_NAME, *(name for name, _ in MEASUREMENT_SYSTEM_NAMES)}
    )
    NOT_SUBSTANCE = IDENTIFIER_ATTRIBUTES | METADATA_ATTRIBUTES

    @classmethod
    def _spec_key(cls, type_key: str, brand: str, attributes: list[Attribute]) -> tuple:
        """What makes two SKUs the same product: type, brand, every attribute.

        Identifiers (``List Number``) are left out, and so is everything that
        is not an attribute -- the SKU, the product id, the image, the price
        and the stock. Brand is IN: the same standard part from two makers is
        two products, as on any marketplace.
        """
        spec = tuple(
            sorted(
                (a.name, a.value if a.values is None else "|".join(a.values))
                for a in attributes
                if a.name not in cls.NOT_SUBSTANCE
            )
        )
        return (type_key, brand, spec)

    def _unique_series(self, draft: LineDraft, line_attrs: list[Attribute]) -> None:
        """Give the product a series no other product of its brand has in this type.

        The set walked here is the type's own (:mod:`.typespec`), so it never
        sees another type's series. Names stay unique across types only
        because each type's series shape is disjoint from every other's
        (``BR###``, ``FD###``, ``ISO4017-``, ...). Nothing here enforces that;
        ``test_no_two_products_share_a_product_name_catalog_wide`` catches a
        clash after the fact.

        A drawn series already taken walks its trailing number up, one step at
        a time, to the first free one -- deterministic, and never a re-draw.
        The walk touches the series and the IDENTIFIER attributes that publish
        it (``List Number``) and NOTHING else: a value that carries meaning --
        a bearing number, a size -- is never rewritten, even when it equals the
        series (the first version walked 11,784 bearing numbers to numbers that
        are not bearings; tests/test_catalog_brands_voice.py now holds every
        bearing to its table entry).
        """
        taken = self._used_series
        series = draft.series
        while (draft.brand, series) in taken:
            head = series.rstrip("0123456789")
            tail = series[len(head) :]
            series = f"{head}{int(tail) + 1}" if tail else f"{series}1"
        taken.add((draft.brand, series))
        if series != draft.series:
            self._bump("series_walked")
            old = draft.series
            draft.series = series

            def walked(attribute: Attribute) -> Attribute:
                if attribute.name in self.IDENTIFIER_ATTRIBUTES and attribute.value == old:
                    return Attribute(attribute.name, series)
                return attribute

            line_attrs[:] = [walked(a) for a in line_attrs]
            draft.line_attrs = [walked(a) for a in draft.line_attrs]

    @functools.cache  # noqa: B019 - a pure function of the config and the type
    def _always_published(self, type_key: str) -> frozenset[str]:
        """The attributes sparsity never drops for this type (presence 1.0)."""
        return frozenset(
            spec.name
            for spec in VOCAB[type_key]
            if self.config.scaled_presence(spec.presence) >= 1.0
        )

    def _differs_only_by_a_drop(
        self, type_key: str, brand: str, published: list[Attribute]
    ) -> bool:
        """Whether a published spec is a subset or superset of one already made.

        Two SKUs whose published attributes differ only in that one lacks an
        attribute the other carries are NOT different to a shopper, whatever
        the dropped value was (measured on the first 100K build: 3,212 such
        SKUs). Compared within the bucket of SKUs that agree on every
        always-published attribute -- the only place a subset can live -- so
        the check stays cheap at 100K. Records the spec when it is new.
        """
        spec = frozenset(
            (a.name, a.value if a.values is None else "|".join(a.values))
            for a in published
            if a.name not in self.NOT_SUBSTANCE
        )
        always = self._always_published(type_key)
        bucket = (type_key, brand, tuple(sorted(x for x in spec if x[0] in always)))
        made = self._published_specs.setdefault(bucket, [])
        if any(spec <= other or other <= spec for other in made):
            return True
        made.append(spec)
        return False

    def _finish_line(self, type_key: str, draft: LineDraft, index: int) -> ProductLine | None:
        rng = self.rng
        line_attrs = self._apply_sparsity(type_key, draft.line_attrs, "line")
        line_attrs = self._corrupt_angle(line_attrs)
        # One spelling of the measurement-system attribute per line.
        system_name = str(_weighted(rng, MEASUREMENT_SYSTEM_NAMES))
        standards_attr = self._standards_attribute(type_key, draft)
        if standards_attr is not None:
            line_attrs = [*line_attrs, standards_attr]

        draft.type_key = type_key
        self._unique_series(draft, line_attrs)
        self._voice = voice_for(draft.brand)
        self._line_facts = {a.name: a.value for a in line_attrs}

        # The product id is built before the SKUs, because every SKU's image
        # id names it: one drawing per SKU, filed under its product.
        product_id = self._product_id(draft.brand, draft.series, index)

        # Composed first, for every SKU, because whether a title needs the
        # thing that differs is a question about the LINE and cannot be
        # answered one SKU at a time.
        built: list[tuple[str, list[Attribute], float, int]] = []
        titles: list[Title] = []
        for child in draft.children:
            attrs = self._apply_sparsity(type_key, list(child.attrs), "sku")
            if not attrs and not child.zero_axis:
                continue
            attrs = self._inject_defects(child, attrs)
            system_attr, _ = self._measurement_system(child.system, system_name)
            if system_attr is not None and not child.zero_axis:
                attrs = [*attrs, system_attr]
            # Each SKU is different from every other SKU of its brand and type.
            # A membership check, i.e. rejection: a draft whose UNSPARSIFIED
            # spec this brand has already made, or whose published spec differs
            # from one already made only by a dropped attribute, is not made.
            unsparsified = [
                *draft.line_attrs,
                *([standards_attr] if standards_attr is not None else []),
                *child.attrs,
                *([system_attr] if system_attr is not None else []),
            ]
            key = self._spec_key(type_key, draft.brand, unsparsified)
            if key in self._drawn_specs or self._differs_only_by_a_drop(
                type_key, draft.brand, [*line_attrs, *attrs]
            ):
                self._bump("spec_already_drawn")
                continue
            self._drawn_specs.add(key)

            sku = self._new_sku()
            self._published = {a.name for a in (*line_attrs, *attrs)}
            titles.append(self._build_line_title(draft, child))
            # One draw, where the uniform multiplier this replaced drew one, so
            # every later draw (stock and on) is the draw it always was.
            sku_u = rng.random()
            shown = price.shown_price(
                self._price_draw(type_key, draft.brand, unsparsified, draft.line_attrs, sku, sku_u)
            )
            stock = rng.choices(
                (0, rng.randint(1, 40), rng.randint(40, 900)), weights=(0.08, 0.42, 0.5)
            )[0]
            built.append((sku, attrs, shown, stock))

        # A (type, brand) that drafts line after line and makes nothing has
        # spent its spec space: after MAX_MISSES in a row it stops getting
        # products of that type (``brands.pick_brand`` excludes it).
        pair = (type_key, draft.brand)
        if not built:
            self._misses[pair] = self._misses.get(pair, 0) + 1
            if self._misses[pair] >= MAX_MISSES:
                self._exhausted.add(pair)
                self._bump("brand_type_exhausted")
            return None
        self._misses[pair] = 0

        published = [attrs for _, attrs, _, _ in built]
        titles = self._disambiguate_titles(
            titles, published, self._identifying_attribute(published)
        )

        # The variant axis: what "also available in" names the siblings by.
        axis = draft.children[0].primary.name if draft.children else None
        siblings = [
            next((a.value for a in attrs if a.name == axis), "") for _, attrs, _, _ in built
        ]
        children: list[Sku] = []
        for (sku, attrs, shown, stock), title in zip(built, titles, strict=True):
            # From the PUBLISHED values, after sparsity and defects, so the
            # sentence can never disagree with the record it sits on.
            values = {a.name: a.value for a in (*line_attrs, *attrs)}
            compatibility = compat.sentence_for(type_key, values) or ""
            noise_text = " ".join(
                noise.sentences(
                    type_key,
                    values,
                    sku=sku,
                    seed=self.config.seed,
                    noise=self.config.noise,
                    provenance=draft.provenance,
                    primary=values.get(axis) if axis else None,
                    siblings=siblings,
                )
            )
            extra = " ".join(part for part in (compatibility, noise_text) if part)
            children.append(
                Sku(
                    sku=sku,
                    title=title.text,
                    description=self._build_description(draft, title, attrs, extra),
                    attributes=tuple(attrs),
                    price_usd=shown,
                    stock=stock,
                    image_id=image_id_for(type_key, product_id, sku),
                    compatibility=compatibility,
                    noise=noise_text,
                )
            )
            self._bump("skus")

        parent_title = product_name(
            draft.brand, draft.series, draft.item, STANDARDS_FAMILY[type_key]
        )
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
            # A grouped card shows its first variant's drawing until one is
            # selected; the product has no drawing of its own to disagree.
            image_id=children[0].image_id,
            drawing=drawing_for(type_key),
        )

    def _price_draw(
        self,
        type_key: str,
        brand: str,
        attributes: list[Attribute],
        line_attributes: list[Attribute],
        sku: str,
        sku_u: float,
    ) -> price.Draw:
        """What a SKU's shown price is computed from (:mod:`.price`), read off
        its unsparsified attributes, so a dropped or defective published value
        never moves its price. Its group (:func:`.price.group_draw`) is read
        off the line attributes sparsity never drops."""
        model = price.model_for(type_key)
        facts = {a.name: a for a in attributes}
        material = facts["Material"].value if "Material" in facts else None
        pack = None
        if model.pack_attribute is not None and model.pack_attribute in facts:
            pack = facts[model.pack_attribute].value_num
        key = price.KEYS[type_key](facts)
        struct = price.structure(
            model,
            key,
            material,
            brands.tier_of(brand, type_key),
            pack,
            price.length_of(facts) if type_key in price.LENGTH_HELD else None,
        )
        seed = self.config.seed
        always = self._always_published(type_key)
        group_u = price.group_draw(
            seed, type_key, brand, (a for a in line_attributes if a.name in always)
        )
        size_u = price.size_draw(seed, type_key, key, material)
        return price.Draw(model, struct, group_u, sku_u, price.ending_draw(seed, sku), size_u)

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
