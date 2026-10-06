"""Price, measured against the price census (#52).

The targets are the derived figures in ``reference-statistics/P2_price_census.json``
(5,975 priced SKUs on archived pages of a large US industrial distributor). They
are restated here because the census file does not ship in the wheel;
``tests/test_price.py`` checks every figure below against that file, so the two
cannot drift apart.

What a price row compares is the price a shopper is SHOWN (the census's
``price_quantiles_usd``), because the catalog publishes one price per SKU and
no sale unit beside it.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass

from ..dimensions import DimensionParseError, parse_length, parse_thread
from .model import Attribute


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


#: Types whose census ``n`` is 30 or more. Ball-pein hammers, button-head and
#: low-head screws have no census rows, and flat-head screws only 4.
CENSUS: dict[str, PriceCensus] = {
    "abrasive_flap_disc": PriceCensus(135, 4.7, 8.68, 16.5, 1.224, 0.949, 59),
    "bearing_radial_ball": PriceCensus(390, 12.885, 37.475, 207.375, 1.167, 0.888, 7991),
    "bolt_hex": PriceCensus(347, 7.222, 20.91, 59.26, 1.602, 0.937, 303),
    "drill_jobber": PriceCensus(885, 2.208, 6.0, 21.154, 0.812, 0.878, 8382),
    "end_mill_ball": PriceCensus(65, 29.428, 88.23, 253.944, 1.338, 0.909, 11),
    "end_mill_square": PriceCensus(69, 22.21, 52.5, 167.4, 1.091, 0.833, 18),
    "hex_key": PriceCensus(270, 2.214, 9.68, 31.9, 1.141, 0.925, 1707),
    "kit_assortment": PriceCensus(46, 5.505, 80.575, 629.0, 0.849, 0.797, 79),
    "nut_hex": PriceCensus(473, 4.786, 15.31, 49.89, 1.192, 0.878, 1877),
    "screw_socket_head": PriceCensus(308, 7.0, 21.535, 48.065, 0.124, 0.575, 40),
    "tap_spiral_point": PriceCensus(487, 9.27, 20.02, 49.7, 0.551, 0.585, 768),
    "washer_flat": PriceCensus(174, 1.0, 4.89, 24.804, 1.298, 0.808, 1406),
    "wheel_depressed_center": PriceCensus(217, 2.906, 9.51, 29.05, 1.173, 0.808, 1095),
}

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


#: Each type's key dimension: the catalog's name for the attribute the census
#: keyed that type on (``key_dimension_attribute``).
KEYS: dict[str, Callable[[Mapping[str, Attribute]], float | None]] = {
    "abrasive_flap_disc": key_reader("Diameter"),
    "bearing_radial_ball": key_reader("Bore"),
    "bolt_hex": key_reader("Dia./Thread Size"),
    "drill_jobber": key_reader("Decimal Equivalent", "Size"),
    "end_mill_ball": key_reader("Milling Dia."),
    "end_mill_square": key_reader("Milling Dia."),
    "hammer_ball_pein": key_reader("Head Weight"),
    "hex_key": key_reader("Size"),
    "kit_assortment": key_reader("Number of Pieces"),
    "nut_hex": key_reader("Thread Size"),
    "screw_button_head": key_reader("Dia./Thread Size"),
    "screw_flat_head": key_reader("Dia./Thread Size"),
    "screw_low_head": key_reader("Dia./Thread Size"),
    "screw_socket_head": key_reader("Dia./Thread Size"),
    "tap_spiral_point": key_reader("Thread Size"),
    "washer_flat": key_reader("Inside Dia."),
    "wheel_depressed_center": key_reader("Diameter"),
}

#: Types whose census cells also hold length equal (``method.slope``).
LENGTH_HELD = frozenset(
    {"bolt_hex", "screw_socket_head", "screw_flat_head", "screw_button_head", "screw_low_head"}
)
