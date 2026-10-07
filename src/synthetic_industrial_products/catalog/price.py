"""Price, measured against the price census (#52).

The targets are the derived figures in ``reference-statistics/P2_price_census.json``
(5,975 priced SKUs on archived pages of a large US industrial distributor). They
are restated here because the census file does not ship in the wheel;
``tests/test_price.py`` checks every figure below against that file, so the two
cannot drift apart.

What a price row compares is the price a shopper is SHOWN (the census's
``price_quantiles_usd``), because the catalog publishes one price per SKU and
no sale unit beside it.

The model (:func:`shown_price`) is, in logs::

    log p = log anchor + slope * log(key / anchor_key) + log material + log tier
            + pack_slope * log(pack / pack_ref) + group_sigma * z_group + sku_sigma * z_sku
            + size_sigma * z_size

then rounded to an ending drawn from the type's census endings mix. The slope,
the tier factors, the pack slope and the endings are census figures. The
anchor and the sigmas are fitted by ``scripts/fit_price_model.py`` so the
default build lands on the census p50, p90/p10, larger-costs-more share and
brand spread. ``size_sigma`` is 0 but for a type :data:`SIZE_NOISE` names.
The material factors are NOT measured (:data:`MATERIAL_FACTORS`).

**A kit is priced from what it holds** (:data:`CONTENTS_PRICED`). Its key
is not one dimension but the summed price of its pieces (:func:`kit_contents`):
each size it holds, priced on its part type's own curve, times how many of
that size it holds, at the census's per-piece share of that part's shown price
(:data:`PER_PIECE`). The slope on that key is 1.0, so the kit's anchor over
its ``anchor_key`` is the kit's price over its contents' (the fitted kit factor: a small
premium fitted to the census median kit price, which moves when #76 widens
the kit kinds), and its material and tier apply once, to the kit.

``z_group`` is one draw per price group, what the census calls a cell: one
brand, every line attribute a group page holds equal (:func:`group_draw`).
The census measures how prices spread ACROSS its pages and how they order
WITHIN one, so the noise that spreads them is shared by a page.

**Where the fit lowers a slope.** The census slope is of PER-PIECE price,
within one page. A pack-sold type's pack shrinks as its size grows (a bolt
census: per-piece p90/p10 28, shown 8.2), so its shown price climbs slower;
and a type whose sizes span further than the census's (the end mills, from
11 and 18 pairs) spreads further on the census slope alone. Where the census
slope by itself spreads the shown price wider than the census p90/p10, the
fit lowers it until it does not, and the model's literal names the slope it
used (bolts and both end mills: :data:`SLOPE_CUTS`, which
:func:`slope_cut_mismatch` holds the literals to).

**Why the endings rows weigh the census by the catalog's type mix.** The
census pooled its endings over its own type mix (a quarter of its SKUs are
jobber drills, whose prices rarely end .00); the catalog builds a different
one. Each type draws from its own census mix, so the pooled census figure is
not what a correct build lands on: ``price_report.ending_targets`` weighs
each type's census mix by that type's share of the catalog's modelled SKUs,
so census and catalog are compared on the same mix.
"""

from __future__ import annotations

import math
import random
from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass, field
from statistics import NormalDist
from typing import TYPE_CHECKING, Literal

from ..dimensions import DimensionParseError, parse_length, parse_thread
from .model import Attribute
from .newtypes import KITS
from .typespec import RegistryTable

if TYPE_CHECKING:
    from .breadth import BreadthRow


@dataclass(frozen=True)
class PriceCensus:
    """One type's measured price figures, as the census states them."""

    n: int
    p10: float
    p50: float
    p90: float
    #: Pooled within-cell OLS slope of log(per-piece price) on log(key dimension).
    slope: float
    #: Share of within-cell size pairs whose larger size costs more.
    larger_costs_more: float
    #: How many within-cell pairs that share is over.
    n_pairs: int
    #: Share of those pairs whose larger size costs less.
    larger_costs_less: float
    #: Share of those pairs whose two sizes cost the same.
    equal_price: float


#: Types whose census ``n`` is 30 or more. Ball-pein hammers, button-head and
#: low-head screws have no census rows, and flat-head screws only 4.
CENSUS: dict[str, PriceCensus] = {
    "abrasive_flap_disc": PriceCensus(135, 4.7, 8.68, 16.5, 1.224, 0.949, 59, 0.051, 0.0),
    "bearing_radial_ball": PriceCensus(
        390, 12.885, 37.475, 207.375, 1.167, 0.888, 7991, 0.112, 0.0
    ),
    "bolt_hex": PriceCensus(347, 7.222, 20.91, 59.26, 1.602, 0.937, 303, 0.063, 0.0),
    "drill_jobber": PriceCensus(885, 2.208, 6.0, 21.154, 0.812, 0.878, 8382, 0.106, 0.015),
    "end_mill_ball": PriceCensus(65, 29.428, 88.23, 253.944, 1.338, 0.909, 11, 0.091, 0.0),
    "end_mill_square": PriceCensus(69, 22.21, 52.5, 167.4, 1.091, 0.833, 18, 0.111, 0.056),
    "hex_key": PriceCensus(270, 2.214, 9.68, 31.9, 1.141, 0.925, 1707, 0.066, 0.009),
    "kit_assortment": PriceCensus(46, 5.505, 80.575, 629.0, 0.849, 0.797, 79, 0.203, 0.0),
    "nut_hex": PriceCensus(473, 4.786, 15.31, 49.89, 1.192, 0.878, 1877, 0.12, 0.002),
    "screw_socket_head": PriceCensus(308, 7.0, 21.535, 48.065, 0.124, 0.575, 40, 0.35, 0.075),
    "tap_spiral_point": PriceCensus(487, 9.27, 20.02, 49.7, 0.551, 0.585, 768, 0.311, 0.104),
    "washer_flat": PriceCensus(174, 1.0, 4.89, 24.804, 1.298, 0.808, 1406, 0.188, 0.004),
    "wheel_depressed_center": PriceCensus(
        217, 2.906, 9.51, 29.05, 1.173, 0.808, 1095, 0.188, 0.004
    ),
}

#: How many census SKUs :data:`POOLED_ENDINGS` is over.
POOLED_ENDINGS_N = 5975
#: Price endings over all 5,975 census SKUs (``pooled_endings_all_types``).
POOLED_ENDINGS: dict[str, float] = {
    "other": 0.5771,
    "other .x5": 0.2243,
    ".00": 0.0648,
    "other .x9": 0.0495,
    ".50": 0.0415,
    ".95": 0.0181,
    ".49": 0.0075,
    ".98": 0.0059,
    ".99": 0.0059,
    ".97": 0.0055,
}

#: The brand spread the census measures with the most shared specs: jobber
#: drills, 101 specs offered by two or more brands. Median over those specs of
#: max/min of the per-brand median price.
BRAND_SPREAD_TYPE = "drill_jobber"
BRAND_SPREAD_MEDIAN = 2.5705
#: The distributor's own labels against the other brands on the same spec,
#: median over 83 jobber-drill specs. Those labels are its value lines, so
#: this is what an economy-tier brand is held to.
ECONOMY_OVER_OTHERS_MEDIAN = 0.5196
#: The 90th percentile of the jobber-drill brand price index (9 brands): a
#: brand's median price over the spec's geometric mean, on shared specs.
PREMIUM_BRAND_INDEX_P90 = 1.7863


@dataclass(frozen=True)
class LengthCensus:
    """Price against length at a fixed diameter (``price_vs_length_at_fixed_diameter``)."""

    slope: float
    longer_costs_more: float
    n_pairs: int
    longer_costs_less: float


#: The fastener types whose census measures length over 100 or more pairs.
LENGTH_CENSUS: dict[str, LengthCensus] = {
    "bolt_hex": LengthCensus(0.564, 0.691, 1886, 0.309),
    "screw_socket_head": LengthCensus(0.256, 0.662, 858, 0.319),
}

#: The types whose census share of same-page size pairs at one price the
#: model makes (:attr:`PriceModel.price_step`): taps, 10.4% of 768 pairs.
EQUAL_PRICE_TYPES = ("tap_spiral_point",)

#: The length a LENGTH_HELD type's model is anchored at, in inches.
ANCHOR_LENGTH = 1.0


@dataclass(frozen=True)
class BrandCensus:
    """Same-spec brand spread (``brand_spread_same_spec``)."""

    #: Median over specs two or more brands offer of max/min per-brand median.
    spread_p50: float
    n_specs: int
    low_confidence: bool
    #: The quartiles of that max/min over the same specs: how widely it
    #: varies, which sets the standard error of its median (``price_report``).
    spread_p25: float
    spread_p75: float
    #: How many brands the shared specs are spread over
    #: (``n_brands_indexed``): the most brands one census spec can hold. The
    #: census does not publish how many each spec holds.
    brands_indexed: int


#: Every type whose census measures a same-spec brand spread.
BRAND_CENSUS: dict[str, BrandCensus] = {
    "bearing_radial_ball": BrandCensus(1.3825, 49, False, 1.2108, 1.6587, 4),
    "drill_jobber": BrandCensus(2.5705, 101, False, 1.3954, 3.3944, 9),
    "end_mill_ball": BrandCensus(1.3624, 5, True, 1.2675, 1.7375, 3),
    "nut_hex": BrandCensus(5.5752, 6, True, 2.291, 9.4916, 4),
    "screw_socket_head": BrandCensus(1.3372, 7, True, 1.2829, 1.6093, 2),
    "tap_spiral_point": BrandCensus(2.2238, 31, False, 1.9292, 2.4422, 3),
    "wheel_depressed_center": BrandCensus(1.2838, 12, True, 1.1387, 1.5461, 5),
}

_NAMED_CENTS = {0: ".00", 50: ".50", 95: ".95", 99: ".99", 98: ".98", 97: ".97", 49: ".49"}


def ending_class(price: float) -> str:
    """The census's ending class of a shown price, by its cents."""
    cents = round(price * 100) % 100
    if cents in _NAMED_CENTS:
        return _NAMED_CENTS[cents]
    if cents % 10 == 5:
        return "other .x5"
    if cents % 10 == 9:
        return "other .x9"
    return "other"


def _magnitude(attribute: Attribute) -> float | None:
    """A dimension in the census's units: a thread's major diameter or a
    length in inches; otherwise the published number (ounces, a count)."""
    for parse in (lambda v: parse_thread(v).major.inches, lambda v: parse_length(v).inches):
        try:
            return parse(attribute.value)
        except DimensionParseError:
            continue
    return attribute.value_num


def key_reader(*names: str) -> Callable[[Mapping[str, Attribute]], float | None]:
    """Read a type's key dimension from the first of ``names`` it carries."""

    def read(attrs: Mapping[str, Attribute]) -> float | None:
        for name in names:
            if name in attrs:
                value = _magnitude(attrs[name])
                if value is not None and value > 0:
                    return value
        return None

    return read


#: Each type's key dimension: the catalog's names for the attribute the census
#: keyed that type on (``key_dimension_attribute``), the first one carried wins.
KEY_ATTRIBUTES: dict[str, tuple[str, ...]] = {
    "abrasive_flap_disc": ("Diameter",),
    "bearing_radial_ball": ("Bore",),
    "bolt_hex": ("Dia./Thread Size",),
    "dowel_pins": ("Diameter",),
    "drill_jobber": ("Decimal Equivalent", "Size"),
    "end_mill_ball": ("Milling Dia.",),
    "end_mill_square": ("Milling Dia.",),
    "hammer_ball_pein": ("Head Weight",),
    "hex_key": ("Size",),
    "kit_assortment": ("Number of Pieces",),
    "lock_nuts_nylon_insert": ("Thread Size",),
    "nut_hex": ("Thread Size",),
    "retaining_rings_external": ("Size",),
    # The cross-section, not the inside diameter: the borrowed washer model
    # is held to the span it was fitted over (MEASURED_SPANS), which holds
    # the larger cross-sections and almost none of the inside diameters.
    "o_rings": ("Width",),
    "screw_button_head": ("Dia./Thread Size",),
    "screw_flat_head": ("Dia./Thread Size",),
    "screw_low_head": ("Dia./Thread Size",),
    "screw_socket_head": ("Dia./Thread Size",),
    "set_screws_hex_socket": ("Dia./Thread Size",),
    "tap_spiral_point": ("Thread Size",),
    "washer_flat": ("Inside Dia.",),
    "wheel_depressed_center": ("Diameter",),
}


def _bounded(
    type_key: str, read: Callable[[Mapping[str, Attribute]], float | None]
) -> Callable[[Mapping[str, Attribute]], float | None]:
    """``read``, held to the span of the model ``type_key`` borrows, when that
    model's span is recorded (:data:`MEASURED_SPANS`). Looked up at each read:
    a type module's borrow is registered after this table is built."""

    def bounded(attrs: Mapping[str, Attribute]) -> float | None:
        key = read(attrs)
        span = MEASURED_SPANS.get(BORROWS.get(type_key, ""))
        if key is None or span is None:
            return key
        return min(max(key, span[0]), span[1])

    return bounded


#: Each type's key-dimension reader (:func:`key_reader`); a borrower's is
#: held to its model's span (:func:`_bounded`).
KEYS: dict[str, Callable[[Mapping[str, Attribute]], float | None]] = {
    type_key: _bounded(type_key, key_reader(*names)) for type_key, names in KEY_ATTRIBUTES.items()
}

#: Types priced from what they hold (:func:`kit_contents`) rather than from
#: one key dimension. Their census key (a kit's ``Number of Pieces``) still
#: keys the report's size pairs and its order row, which the price meets as an
#: outcome: more of the same pieces sum to more. ``scripts/fit_price_model.py``
#: fits such a type no group noise: the census kit spread comes from kinds of
#: kit the catalog does not build, and noise loud enough to stand in for them
#: would spread a kit's price further than its contents do (the kit p90/p10
#: pin, :data:`PINNED_SHORTFALLS`).
CONTENTS_PRICED = frozenset({"kit_assortment"})
#: The slope of a contents-priced type's price on its contents' price: a kit
#: is its contents at one fitted factor, whatever it holds.
CONTENTS_SLOPE = 1.0

#: Each kit part type's census per-piece p50 and shown-price p50 (USD). A
#: shown price may be a pack (every census socket screw is, most of them 100
#: to a pack; a third of hex keys are), and a kit holds pieces, so a part's
#: shown price is scaled by the first over the second to price one piece.
PER_PIECE: dict[str, tuple[float, float]] = {
    "drill_jobber": (5.6, 6.0),
    "hex_key": (6.25, 9.68),
    "screw_socket_head": (0.2545, 21.535),
    "tap_spiral_point": (20.02, 20.02),
}

#: What each kit kind (its ``Type``) holds, from the kit table itself.
KIT_PARTS: dict[str, str] = {kit.item: kit.part_type for kit in KITS}


def kit_contents(attributes: Mapping[str, Attribute]) -> float | None:
    """The summed price (USD) of the pieces a kit holds, or None where its
    kind, sizes or piece count cannot be read.

    Each size in ``Sizes Included`` is priced on its part type's curve at
    that size (standard tier, a material of 1.0, no noise: the price the
    catalog's single parts are drawn about), times the census per-piece
    share (:data:`PER_PIECE`), times how many of that size the kit holds
    (``Number of Pieces`` over its sizes: a kit holds as many of each).
    """
    kind = attributes.get("Type")
    sizes = attributes.get("Sizes Included")
    pieces = attributes.get("Number of Pieces")
    if kind is None or sizes is None or pieces is None or pieces.value_num is None:
        return None
    part = KIT_PARTS.get(kind.value)
    if part is None:
        return None
    model = model_for(part)
    values = sizes.values or (sizes.value,)
    each, shown = PER_PIECE[part]
    total = 0.0
    for value in values:
        key = _magnitude(Attribute(name=sizes.name, value=value))
        if key is None or key <= 0:
            return None
        total += model.anchor * math.exp(structure(model, key, None, "standard"))
    return total * pieces.value_num / len(values) * each / shown


def price_key(type_key: str, attributes: Mapping[str, Attribute]) -> float | None:
    """What a SKU's price slope multiplies: its contents' price for a type
    :data:`CONTENTS_PRICED` names, its key dimension otherwise."""
    if type_key in CONTENTS_PRICED:
        return kit_contents(attributes)
    return KEYS[type_key](attributes)


def model_slope(type_key: str) -> float:
    """A census type's slope before any cut: :data:`CONTENTS_SLOPE` for a
    contents-priced type, the census slope on its key dimension otherwise."""
    return CONTENTS_SLOPE if type_key in CONTENTS_PRICED else CENSUS[type_key].slope

#: Types whose census cells also hold length equal (``method.slope``).
LENGTH_HELD = frozenset(
    {
        "bolt_hex",
        "screw_socket_head",
        "screw_flat_head",
        "screw_button_head",
        "screw_low_head",
        "dowel_pins",
    }
)


#: Price endings per type (``deep_types.<type>.endings.class_share``), for the
#: 13 types :data:`CENSUS` restates.
ENDINGS: dict[str, dict[str, float]] = {
    "abrasive_flap_disc": {
        "other": 0.6741,
        "other .x5": 0.1481,
        "other .x9": 0.0519,
        ".49": 0.0444,
        ".99": 0.037,
        ".50": 0.0222,
        ".95": 0.0148,
        ".00": 0.0074,
    },
    "bearing_radial_ball": {
        "other": 0.4462,
        "other .x5": 0.3769,
        ".50": 0.0513,
        ".00": 0.0462,
        "other .x9": 0.0436,
        ".95": 0.0256,
        ".49": 0.0051,
        ".98": 0.0026,
        ".97": 0.0026,
    },
    "bolt_hex": {
        "other": 0.634,
        "other .x5": 0.1988,
        ".50": 0.0432,
        ".00": 0.0432,
        "other .x9": 0.0317,
        ".95": 0.0231,
        ".97": 0.0086,
        ".49": 0.0058,
        ".98": 0.0058,
        ".99": 0.0058,
    },
    "drill_jobber": {
        "other": 0.7559,
        "other .x5": 0.1028,
        "other .x9": 0.0723,
        ".49": 0.0136,
        ".50": 0.0124,
        ".00": 0.0113,
        ".95": 0.0102,
        ".98": 0.009,
        ".99": 0.0068,
        ".97": 0.0056,
    },
    "end_mill_ball": {
        "other": 0.6923,
        ".50": 0.1077,
        ".00": 0.0923,
        "other .x5": 0.0769,
        "other .x9": 0.0308,
    },
    "end_mill_square": {
        ".00": 0.3478,
        ".50": 0.2899,
        "other .x5": 0.2464,
        "other": 0.1014,
        ".98": 0.0145,
    },
    "hex_key": {
        "other": 0.5741,
        "other .x5": 0.2111,
        "other .x9": 0.0704,
        ".00": 0.0667,
        ".50": 0.0407,
        ".95": 0.0185,
        ".97": 0.0111,
        ".98": 0.0074,
    },
    "kit_assortment": {
        "other .x5": 0.4783,
        "other": 0.1957,
        ".50": 0.1304,
        "other .x9": 0.087,
        ".00": 0.0435,
        ".98": 0.0435,
        ".49": 0.0217,
    },
    "nut_hex": {
        "other": 0.6385,
        "other .x5": 0.1882,
        "other .x9": 0.0592,
        ".00": 0.0444,
        ".95": 0.0169,
        ".50": 0.0169,
        ".49": 0.0148,
        ".97": 0.0127,
        ".98": 0.0063,
        ".99": 0.0021,
    },
    "screw_socket_head": {
        "other": 0.487,
        "other .x5": 0.2468,
        ".00": 0.1688,
        ".50": 0.039,
        "other .x9": 0.0325,
        ".95": 0.0195,
        ".97": 0.0032,
        ".99": 0.0032,
    },
    "tap_spiral_point": {
        "other": 0.6489,
        "other .x5": 0.2197,
        "other .x9": 0.0452,
        ".50": 0.0287,
        ".00": 0.0185,
        ".95": 0.0103,
        ".98": 0.0103,
        ".97": 0.0082,
        ".99": 0.0062,
        ".49": 0.0041,
    },
    "washer_flat": {
        "other": 0.6207,
        "other .x5": 0.1264,
        ".00": 0.092,
        "other .x9": 0.0862,
        ".95": 0.023,
        ".49": 0.0172,
        ".97": 0.0172,
        ".50": 0.0115,
        ".99": 0.0057,
    },
    "wheel_depressed_center": {
        "other": 0.6452,
        "other .x5": 0.1705,
        "other .x9": 0.0737,
        ".95": 0.0276,
        ".50": 0.0276,
        ".99": 0.0276,
        ".00": 0.0138,
        ".49": 0.0092,
        ".98": 0.0046,
    },
}

#: The pooled log-log slope of a nut's shown pack price on its pack quantity
#: (``deep_types.nut_hex.pack_vs_each.pooled_loglog_slope_price_on_pack_qty``):
#: a pack of 100 costs more than a pack of 25, but far less than four times.
NUT_PACK_SLOPE = 0.234

#: Each measured breadth category's shown-price (p10, p50, p90)
#: (``breadth_categories.<key>.price_quantiles_usd``). A row listed here is
#: priced from these (:func:`breadth_price`); every other row from its own
#: ``price_range``.
BREADTH_CENSUS: dict[str, tuple[float, float, float]] = {
    "ball_valves": (3.674, 13.145, 182.59),
    "blind_rivets": (12.308, 21.1, 27.415),
    "c_clamps": (10.526, 52.0, 342.25),
    "carriage_bolts": (10.841, 26.1, 67.205),
    "cold_chisels": (7.13, 15.68, 38.2),
    "combination_wrenches": (4.011, 15.38, 39.145),
    "cut_resistant_gloves": (9.45, 21.45, 67.675),
    "eye_bolts": (3.469, 14.735, 62.405),
    "foam_ear_plugs": (3.152, 95.675, 175.9),
    "hand_files": (4.409, 21.43, 24.9),
    "hex_pipe_nipples": (3.33, 5.2, 16.24),
    "hose_clamps": (13.492, 34.95, 43.43),
    "rigid_casters": (20.744, 76.2, 351.85),
    "roller_chain": (74.1, 358.0, 773.0),
    "safety_glasses": (5.0, 8.605, 24.26),
    "threaded_rod": (6.511, 33.52, 140.855),
    "u_bolts": (3.454, 10.68, 23.918),
    "v_belts": (7.707, 23.465, 103.945),
    "wedge_anchors": (41.05, 117.775, 251.625),
}

Tier = Literal["economy", "standard", "premium"]

#: A brand tier's price multiplier, against a standard brand on the same spec.
#: Economy is the distributor's own value labels against the other brands on
#: shared specs (``house_label_over_other_brands``, p50); premium is the 90th
#: percentile of the brand price index (``brand_price_index_quantiles``).
#: These are the jobber-drill figures (101 shared specs), which every type
#: without figures of its own uses (:data:`TYPE_TIERS`).
TIER_FACTORS: dict[str, float] = {
    "economy": ECONOMY_OVER_OTHERS_MEDIAN,
    "standard": 1.0,
    "premium": PREMIUM_BRAND_INDEX_P90,
}

#: The six types priced with their own (economy, premium) census figures, as
#: above; every other type, the hex nut included, takes the drill's
#: (:data:`TIER_FACTORS`). The census measures the hex nut's same-spec brand
#: spread too, but on its 6 shared specs the house label is the DEARER brand
#: (5.58x the others, p50), so it gives no economy figure. A bearing's premium maker is
#: barely dearer than the rest (1.056), and its house label far cheaper
#: (0.577, 10 specs); a drill's figures are :data:`TIER_FACTORS`.
#:
#: The wheel, the socket screw and the ball end mill are low-confidence (12, 7
#: and 5 shared specs; a wheel's house label over 4, a socket's over 7). Their
#: own figures still describe their own brands better than a drill's do: a
#: drill's premium maker is 1.79x the index, theirs 1.04 to 1.13x. The ball
#: end mill has no house-label figure, so its economy is its brand price
#: index p10 (0.886), as its premium is the p90. Their brand-spread rows get
#: a band as wide as their few specs leave the census median
#: (``price_report.brand_spread_band``).
TYPE_TIER_CENSUS: dict[str, tuple[float, float]] = {
    "bearing_radial_ball": (0.5769, 1.0564),
    "drill_jobber": (ECONOMY_OVER_OTHERS_MEDIAN, PREMIUM_BRAND_INDEX_P90),
    "end_mill_ball": (0.886, 1.045),
    "screw_socket_head": (0.7479, 1.1272),
    "tap_spiral_point": (0.5039, 1.3157),
    "wheel_depressed_center": (0.5387, 1.1326),
}

#: Each type's tier multipliers: its own census figures, else the drills'.
TYPE_TIERS: dict[str, dict[str, float]] = {
    type_key: {"economy": economy, "standard": 1.0, "premium": premium}
    for type_key, (economy, premium) in TYPE_TIER_CENSUS.items()
}

#: What a material costs against plain steel (or high speed steel, for a
#: cutting tool). NOT MEASURED: the census holds material equal inside a cell
#: and does not report a material ratio, so these are general-knowledge
#: ratios. Each type's fitted anchor absorbs the level, so only the ratios
#: between one type's materials matter. A material missing here counts 1.0.
MATERIAL_FACTORS: dict[str, float] = {
    "Steel": 1.0,
    "Alloy Steel": 1.0,
    "Forged Steel": 1.0,
    "Chrome Steel": 1.0,
    "Chrome Vanadium Steel": 1.0,
    "Grade 12.9 Alloy Steel": 1.15,
    "S2 Tool Steel": 1.2,
    "18-8 Stainless Steel": 1.6,
    "440C Stainless Steel": 1.8,
    # The retaining rings' generic stainless, at 18-8's ratio, and their
    # spring steel at plain steel's.
    "Stainless Steel": 1.6,
    "Spring Steel": 1.0,
    "316 Stainless Steel": 2.2,
    "Brass": 1.9,
    "Nylon": 0.6,
    "High Speed Steel": 1.0,
    "Cobalt": 1.5,
    "Powdered Metal": 1.6,
    "Solid Carbide": 2.8,
}

#: A noise quantile is clamped to this, so one draw is never more than about
#: three sigmas out.
_Q_CLAMP = 0.001


@dataclass(frozen=True)
class PriceModel:
    """One type's price model: what :func:`shown_price` reads.

    ``slope``, ``length_slope``, ``tiers``, ``pack_slope`` and ``endings``
    come from the census (a slope only the fit may lower, for a reason
    :data:`SLOPE_CUTS` records); ``anchor``, ``group_sigma``, ``sku_sigma``
    and ``price_step`` from ``scripts/fit_price_model.py``. ``measured`` is
    False for a type the census has no prices for, whose model keeps the
    level the catalog had.
    """

    #: Shown price (USD) at ``anchor_key``, standard tier, a material of 1.0.
    anchor: float
    #: The key dimension the anchor is at, in the census's units.
    anchor_key: float
    #: Log-log slope of price on the key dimension.
    slope: float
    #: Sigma of the log-normal noise one group (:func:`group_draw`) shares.
    group_sigma: float
    #: Sigma of the log-normal noise each SKU draws on its own.
    sku_sigma: float
    #: The ending-class mix a price is rounded to.
    endings: Mapping[str, float] = field(default_factory=lambda: POOLED_ENDINGS)
    #: The attribute a pack price scales with, and the log-log slope and the
    #: reference quantity it scales from.
    pack_attribute: str | None = None
    pack_slope: float = 0.0
    pack_ref: float = 1.0
    measured: bool = True
    #: Log-log slope of price on length, for a LENGTH_HELD type, and the
    #: length (inches) the anchor is at.
    length_slope: float = 0.0
    anchor_length: float = ANCHOR_LENGTH
    #: The tier multipliers (:data:`TYPE_TIERS`, else :data:`TIER_FACTORS`).
    tiers: Mapping[str, float] = field(default_factory=lambda: TIER_FACTORS)
    #: The step, in log price, of a list-price ladder the price snaps to
    #: (:func:`shown_price`); 0.0 for none.
    price_step: float = 0.0
    #: Sigma of the log-normal noise one size shares across every brand
    #: (:func:`size_draw`); 0.0 but for a type :data:`SIZE_NOISE` names.
    size_sigma: float = 0.0


def _model(
    type_key: str,
    anchor: float,
    anchor_key: float,
    group: float,
    sku: float,
    slope: float | None = None,
    length_slope: float | None = None,
    **kw,
) -> PriceModel:
    """A census type's model: its census slopes (:func:`model_slope`) unless
    the fit lowered them (:data:`SLOPE_CUTS`), and its census tiers
    (:data:`TYPE_TIERS`)."""
    length = LENGTH_CENSUS.get(type_key)
    return PriceModel(
        anchor,
        anchor_key,
        model_slope(type_key) if slope is None else slope,
        group,
        sku,
        ENDINGS[type_key],
        length_slope=(length.slope if length else 0.0) if length_slope is None else length_slope,
        tiers=TYPE_TIERS.get(type_key, TIER_FACTORS),
        **kw,
    )


#: The types whose fit may lower the census slope, and why. The census
#: slopes are within one group page; where they alone spread the shown price
#: across the catalog wider than the census p90/p10, the fit lowers them
#: until they do not. ``scripts/fit_price_model.py`` refuses to lower any
#: other type's slope: a cut needs a reason recorded here.
SLOPE_CUTS: dict[str, str] = {
    "bolt_hex": (
        "a stand-in for the pack the catalog does not model: 98.8% of census bolts are "
        "pack-sold and the pack shrinks as the size grows (per-piece p90/p10 28, shown 8.2), "
        "so the shown price climbs slower across pages than within one; the key and the "
        "length slope are scaled by one factor (follow-up #65: model the pack)"
    ),
    "end_mill_ball": (
        "a size-span stand-in on a low-confidence slope (11 census pairs): the catalog's "
        "1 mm to 1-1/2 in span spreads further than the census's, which it reports no span for"
    ),
    "end_mill_square": (
        "a size-span stand-in on a low-confidence slope (18 census pairs): the catalog's "
        "1 mm to 1-1/2 in span spreads further than the census's, which it reports no span for"
    ),
}

#: The types whose sizes draw a noise every brand shares (:func:`size_draw`),
#: and why. ``scripts/fit_price_model.py`` fits ``size_sigma`` only for these.
SIZE_NOISE: dict[str, str] = {
    "tap_spiral_point": (
        "the census tap pages invert a size pair often (31.1% of 768 pairs) yet two brands "
        "of one size sit close (brand spread 2.22, of which the census tiers alone give 1.98 "
        "to 2.61): noise drawn per SKU loud enough for the inversions spreads one size's "
        "brands 4.1x apart, while noise one size shares across brands inverts the order and "
        "leaves the brand spread to the tiers (a popular size costs less than its neighbours)"
    ),
    "screw_socket_head": (
        "the catalog's socket sizes and lengths spread its price about 2x where the census "
        "spreads 6.9x (308 SKUs), yet two brands of one spec sit close (brand spread 1.34 over "
        "7 specs): group noise loud enough to make up the p90/p10 is drawn per brand and spreads "
        "one spec's brands 3.5x apart, while noise one spec shares across brands carries the "
        "p90/p10 and leaves the brand spread to the tiers, as on taps"
    ),
}

#: The types whose SKUs of one line share one per-SKU noise draw, and why:
#: price then follows size within a line, as one maker's product line does,
#: while the draw still spreads lines and brands. The model itself is not
#: changed.
LINE_NOISE: dict[str, str] = {
    "retaining_rings_external": (
        "GENERATED, NOT MEASURED: the ring borrows washer_flat's model, whose per-SKU "
        "sigma (0.701) is loud next to a ring line's key term, since adjacent DIN 471 "
        "sizes are 1 mm apart; drawn per SKU, 11 of 44 ring pairs priced the smaller "
        "size 2x or more over the larger (washer_flat: 6 of 131), far above the "
        "ring's own 2x band"
    ),
}

#: Each pinned row's figure on the default and on the 100K build, as the
#: fit last measured them. A pin discloses a shortfall; it does not license
#: a worse one: ``price_report.pin_holds`` fails a row that lands further
#: from its band than its build's figure by more than :data:`PIN_TOLERANCE`.
#: ``tests/test_price.py`` holds each figure equal to what its build produces
#: (``price_report.recorded_digits``), so a record cannot be loosened by hand.
_WHEEL_SPREAD_ROW = "price brand spread, same spec (median max/min): wheel_depressed_center"
_KIT_SPREAD_ROW = "price p90/p10: kit_assortment"
PINNED_FIGURES: dict[str, tuple[float, float]] = {
    "price p90/p10: bearing_radial_ball": (4.493, 4.783),
    _WHEEL_SPREAD_ROW: (3.241, 2.776),
    _KIT_SPREAD_ROW: (4.015, 3.901),
}

#: How far past its recorded figure a pinned row may move, as a ratio. The
#: build is one seed, so the figure is exact on it; the tolerance is room for
#: the fit rounding its literals, well under the 5% the mildest worsening a
#: review planted moved a pin (bearing noise off: 4.55 to 4.31).
PIN_TOLERANCE = 0.02

#: Rows that land outside their band, and why: disclosed, and pinned by
#: ``tests/test_price.py`` to the side of the band the cause puts them. A
#: figure a reason quotes is read from :data:`PINNED_FIGURES`, so a refit that
#: re-records the figure cannot leave the reason quoting the old one.
PINNED_SHORTFALLS: dict[str, str] = {
    "price p90/p10: bearing_radial_ball": (
        "below band: catalog bores span a p90/p10 of about 3x against the census's 16.1x, "
        "and the census's own brand spread (1.38) leaves no group noise to make up the rest "
        "(widen the bore range: #64)"
    ),
    _WHEEL_SPREAD_ROW: (
        "above band: catalog diameters span 2.25x, which the key term spreads to 2.6x of the "
        "census's 10x, and the group noise that makes up the rest is drawn independently per "
        "brand for each of the 12 brands that make every shared wheel spec, so the brands "
        "the row samples from one spec land "
        f"{PINNED_FIGURES[_WHEEL_SPREAD_ROW][0]:.2f}x apart on the default build and "
        f"{PINNED_FIGURES[_WHEEL_SPREAD_ROW][1]:.2f}x apart at 100K. "
        "Offered a noise one spec shares "
        "across brands (SIZE_NOISE, as on taps), the fit gives it no weight and moves the "
        "spread to SKU noise, which inverts the few diameters (larger costs more falls below "
        "band) and still leaves the p90/p10 below band (#66)"
    ),
    _KIT_SPREAD_ROW: (
        "below band: a kit is priced from its contents, and the catalog's kit kinds hold "
        "between about $36 and $130 of parts, so with material and tier its prices span "
        f"{PINNED_FIGURES[_KIT_SPREAD_ROW][0]:.1f}x on the default build and "
        f"{PINNED_FIGURES[_KIT_SPREAD_ROW][1]:.1f}x at 100K against the census's 114x, whose "
        "kits run from packs of 12 and 15 at about $4.50 to a p90 of $629. Group noise loud "
        "enough to make up the rest (about 2.2) spreads a kit's price about 79x on its own, "
        "so the price would follow the noise, not the contents, and a kit draws none "
        "(widen the kit range: #76)"
    ),
}



def slope_cut_mismatch(models: Mapping[str, PriceModel], cuts: Mapping[str, str]) -> set[str]:
    """The census types whose slope in ``models`` is cut without a reason in
    ``cuts``, or has a reason but no cut. A slope is cut where its key slope
    is not :func:`model_slope`'s, or its length slope not the census figure
    (0.0 for a type the census measures no length slope on)."""
    cut = {
        type_key
        for type_key in CENSUS
        if models[type_key].slope != model_slope(type_key)
        or models[type_key].length_slope
        != (LENGTH_CENSUS[type_key].slope if type_key in LENGTH_CENSUS else 0.0)
    }
    return cut ^ {type_key for type_key, reason in cuts.items() if reason.strip()}


#: Every modelled type's price model, by key. A type declared in its own module
#: declares its model as ``TypeSpec.price`` and :func:`.typespec.register`
#: writes it here; the types still built from the shared tables are listed
#: below. Fitted by ``scripts/fit_price_model.py``.
MODELS: RegistryTable[str, PriceModel] = RegistryTable(
    {
        # @fit-begin
        "abrasive_flap_disc": _model("abrasive_flap_disc", 8.542, 5.0, 0.172, 0.086),
        "bearing_radial_ball": _model("bearing_radial_ball", 24.62, 0.5, 0.194, 0.049),
        "bolt_hex": _model("bolt_hex", 18.33, 0.375, 0.284, 0.194, slope=0.987, length_slope=0.347),
        "drill_jobber": _model("drill_jobber", 4.435, 0.25, 0.634, 0.182),
        "end_mill_ball": _model("end_mill_ball", 45.33, 0.375, 0.108, 0.246, slope=0.952),
        "end_mill_square": _model("end_mill_square", 32.86, 0.375, 0.230, 0.308, slope=0.653),
        "hex_key": _model("hex_key", 17.71, 0.25, 0.658, 0.216),
        "kit_assortment": _model("kit_assortment", 100.9, 100.0, 0.000, 0.022),
        "nut_hex": _model(
            "nut_hex",
            16.7,
            0.375,
            0.454,
            0.313,
            pack_attribute="Package Quantity",
            pack_slope=NUT_PACK_SLOPE,
            pack_ref=100.0,
        ),
        "tap_spiral_point": _model(
            "tap_spiral_point",
            16.56,
            0.25,
            0.308,
            0.400,
            price_step=0.19,
            size_sigma=0.215,
        ),
        "washer_flat": _model("washer_flat", 5.243, 0.375, 0.500, 0.701),
        "wheel_depressed_center": _model("wheel_depressed_center", 7.451, 4.5, 0.713, 0.306),
        # @fit-end
        # No census prices: the ball-pein hammer's archived pages are script
        # shells. Its curve is hand-set near the level the uniform multiplier
        # gave (0.9 USD/oz x 5.75), linear in head weight; NOT MEASURED. The
        # built median sits above it (72.62 USD on the golden catalog); no
        # band holds it until #69.
        "hammer_ball_pein": PriceModel(82.8, 16.0, 1.0, 0.0, 0.37, measured=False),
    }
)

#: Types with no census prices of their own that price as a sibling does: the
#: census has no button-head or low-head socket screws, and 4 flat-head ones.
#: Nor has it any dowel pins: they price as the socket head screw, the closest
#: measured hardened fastener sold by diameter and length, so a dowel pin's
#: price is generated from a borrowed model, not measured.
#: A type module adds its own with ``TypeSpec.borrows`` (the O-rings and the
#: external retaining rings borrow the flat washer's model).
BORROWS: dict[str, str] = {
    "dowel_pins": "screw_socket_head",
    "screw_button_head": "screw_socket_head",
    "screw_flat_head": "screw_socket_head",
    "screw_low_head": "screw_socket_head",
}

#: ISO 7089's M3 and M20 inside diameters (3.2 mm and 21 mm), the smallest and
#: largest the flat washer builder stocks.
_WASHER_SPAN = (3.2 / 25.4, 21.0 / 25.4)

#: The key span (census units) a borrowable model was fitted over, so a
#: borrower's key is held inside it (:func:`_bounded`) and the model is never
#: read beyond what it was fitted on: the washer's 1.3 slope run out to a
#: 25.94" O-ring priced it near 1,000 USD. The census records no key span, so
#: the span is that of the catalog's own rows the anchor was fitted to.
MEASURED_SPANS: dict[str, tuple[float, float]] = {"washer_flat": _WASHER_SPAN}


def model_for(type_key: str) -> PriceModel:
    """``type_key``'s price model: its own, or the sibling's it borrows."""
    return MODELS[BORROWS.get(type_key, type_key)]


def _z(quantile: float) -> float:
    return NormalDist().inv_cdf(min(max(quantile, _Q_CLAMP), 1.0 - _Q_CLAMP))


#: Line attributes that are not numbers but still name a size, so a group
#: holding them equal would hold the key dimension equal too.
SIZE_NAMES = frozenset({"Bearing Number"})
#: A number a census cell held equal: one pack size per group page.
HELD_NUMBERS = frozenset({"Package Quantity"})


def holds_equal(type_key: str, attribute: Attribute) -> bool:
    """Whether a census cell (one group page) holds this line attribute equal:
    any that is not a number, but the pack quantity, and nothing that names
    the size."""
    return (
        (attribute.value_num is None or attribute.name in HELD_NUMBERS)
        and attribute.name not in SIZE_NAMES
        and attribute.name not in KEY_ATTRIBUTES.get(type_key, ())
    )


def group_draw(seed: int, type_key: str, brand: str, line_attributes: Iterable[Attribute]) -> float:
    """The quantile a group's noise is drawn at: its own stream, so no other
    draw moves.

    A group is what the census calls a cell, one group page: one brand, every
    line attribute it holds equal (:func:`holds_equal`). ``line_attributes``
    are the ones every line of the type publishes, so a sparse attribute
    dropped from one line does not split the group. Every line of a group
    shares the draw, as the rows of one group page share a price level: the
    census measures how prices spread ACROSS pages (p90/p10) and how they
    order WITHIN one (larger costs more), and noise drawn per line would
    break the order between two lines of one page.
    """
    held = sorted((a.name, a.value) for a in line_attributes if holds_equal(type_key, a))
    return random.Random(f"{seed}:price-group:{type_key}:{brand}:{held}").random()


def size_draw(seed: int, type_key: str, key: float | None, material: str | None) -> float:
    """The quantile a size's shared noise is drawn at: its own stream, so no
    other draw moves. A size is a key dimension in one material, the spec the
    census measures its brand spread over, so every brand and line of one
    spec share the draw and it spreads no spec's brands (:data:`SIZE_NOISE`)."""
    size = round(key, 4) if key else None
    return random.Random(f"{seed}:price-size:{type_key}:{size}:{material or ''}").random()


def ending_draw(seed: int, sku: str) -> float:
    """The quantile a SKU's ending class is drawn at: its own stream."""
    return random.Random(f"{seed}:price-ending:{sku}").random()


def structure(
    model: PriceModel,
    key: float | None,
    material: str | None,
    tier: str,
    pack: float | None = None,
    length: float | None = None,
) -> float:
    """The log-price terms that are not noise and not the anchor."""
    log_p = 0.0
    if key is not None and key > 0:
        log_p += model.slope * math.log(key / model.anchor_key)
    if model.length_slope and length is not None and length > 0:
        log_p += model.length_slope * math.log(length / model.anchor_length)
    log_p += math.log(MATERIAL_FACTORS.get(material or "", 1.0))
    log_p += math.log(model.tiers[tier])
    if model.pack_slope and pack is not None and pack > 0:
        log_p += model.pack_slope * math.log(pack / model.pack_ref)
    return log_p


def length_of(attributes: Mapping[str, Attribute]) -> float | None:
    """A SKU's length in inches, or None."""
    return _magnitude(attributes["Length"]) if "Length" in attributes else None


def log_offset(draw: Draw) -> float:
    """The log price over the anchor: structure and the noise terms."""
    model = draw.model
    offset = draw.struct + model.group_sigma * _z(draw.group_u) + model.sku_sigma * _z(draw.sku_u)
    if model.size_sigma:
        offset += model.size_sigma * _z(draw.size_u)
    return offset


def ladder_point(model: PriceModel, offset: float) -> int:
    """The list-price ladder point a log offset snaps to."""
    return round(offset / model.price_step)


def noisy(draw: Draw) -> float:
    """The unrounded price: anchor, structure and the noise terms, snapped
    to the type's list-price ladder when it has one."""
    model = draw.model
    offset = log_offset(draw)
    if model.price_step:
        offset = ladder_point(model, offset) * model.price_step
    return math.exp(math.log(model.anchor) + offset)


def ending_for(mix: Mapping[str, float], ending_u: float) -> str:
    """The ending class at quantile ``ending_u`` of ``mix``."""
    total = sum(mix.values())
    running = 0.0
    for cls, share in mix.items():
        running += share / total
        if ending_u < running:
            return cls
    return next(reversed(mix))


#: How far the nearest price in a drawn ending class may move a price before
#: the class gives way to "other": a $1.40 part is not rounded to $1.00.
MAX_ENDING_MOVE = 0.25


def with_ending(price: float, cls: str) -> float:
    """The price nearest ``price`` whose cents are in ``cls``, falling back to
    the nearest "other" price when that would move it more than
    :data:`MAX_ENDING_MOVE`. Never below one cent."""
    target = round(price * 100)
    for wanted in (cls, "other"):
        best: int | None = None
        for step in range(0, 101):
            for cents in (target - step, target + step):
                if cents >= 1 and ending_class(cents / 100) == wanted:
                    best = cents
                    break
            if best is not None:
                break
        moved = abs(best / 100 - price) if best is not None else math.inf
        if best is not None and (wanted == "other" or moved <= MAX_ENDING_MOVE * price):
            return best / 100
    raise AssertionError(f"no price near {price} ends in {cls} or other")


@dataclass(frozen=True)
class Draw:
    """Everything a SKU's price is computed from: its model, its structure
    (:func:`structure`) and its draws."""

    model: PriceModel
    struct: float
    group_u: float
    sku_u: float
    ending_u: float
    #: The size's shared draw (:func:`size_draw`); read only where the
    #: model's ``size_sigma`` is not 0.
    size_u: float = 0.5


def shown_price(draw: Draw) -> float:
    """A SKU's shown price.

    On a type with a list-price ladder (taps: 10.4% of census size pairs on
    one page cost the same), two SKUs of one group that snap to one ladder
    point draw one ending, so they print one price: the ending is drawn per
    (group, ladder point), not per SKU.
    """
    model = draw.model
    ending_u = draw.ending_u
    if model.price_step:
        point = ladder_point(model, log_offset(draw))
        ending_u = random.Random(f"price-ending:{draw.group_u!r}:{point}").random()
    return with_ending(noisy(draw), ending_for(model.endings, ending_u))


def breadth_price(row: BreadthRow, size_value: str, tier: str, u: float, ending_u: float) -> float:
    """A breadth SKU's shown price.

    A measured category goes from its census p10 to its p90, through p50, in
    logs. Each of its n sizes draws its position from its own n-th of that
    range, smallest size lowest, at ``u`` within it: over every size and
    ``u`` the positions are uniform, so the draws centre on the census p50
    whatever n is. (A fixed share of the range per size leaves its middle
    undrawn at two sizes: foam ear plugs drew none near their p50.) Then the
    brand's tier and the pooled endings mix. Any other row draws uniformly
    from its own ``price_range``, as it always has.
    """
    measured = BREADTH_CENSUS.get(row.key)
    if measured is None:
        assert row.price_range is not None, row.key
        low, high = row.price_range
        return round(max(1.25, low + (high - low) * u), 2)
    sizes = row.size_values
    position = (sizes.index(size_value) + u) / len(sizes)
    p10, p50, p90 = (math.log(v) for v in measured)
    if position < 0.5:
        log_p = p10 + (p50 - p10) * position * 2
    else:
        log_p = p50 + (p90 - p50) * (position - 0.5) * 2
    return with_ending(math.exp(log_p) * TIER_FACTORS[tier], ending_for(POOLED_ENDINGS, ending_u))
