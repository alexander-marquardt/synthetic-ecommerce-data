"""The price rows of ``sip-generate report``, against the price census (#52).

Each row is computed the way the census computed its figure:

* **quantiles** over the shown price of every SKU of the type;
* **larger costs more** over within-cell pairs whose key dimension differs. A
  census cell is one group page: one brand, every non-dimension attribute
  equal (fasteners also hold length equal). Here a cell is the type, the
  brand, and every line attribute the census would hold equal
  (:func:`.price.holds_equal`) that every line of the type publishes, with
  the length added for :data:`.price.LENGTH_HELD` -- the generator's price
  group (:func:`.price.group_draw`), less the length. It spans
  lines, because six types put the key on the line or make one SKU per line,
  so a cell of one line holds no size pair;
* **brand spread** over specs (key dimension and material) that two or more
  brands make: max/min of the per-brand median price, taken over
  :func:`brand_sample` brands of the spec (:func:`sampled_brands`), so the
  figure does not grow with how many brands a larger catalog puts on a spec;
* **economy over others** over the same specs, where an economy brand and
  another brand both make it: the economy brands' median price over the
  others';
* **longer costs more** over pairs of one brand and line cell whose key
  dimension is equal and whose length differs, for the two fastener types the
  census measures length on;
* **equal price** over the same within-cell pairs as larger-costs-more, for
  the type whose census ties the model makes (:data:`.price.EQUAL_PRICE_TYPES`);
* **smaller costs 2x or more, same product** over pairs of one product line
  whose axis differs (length at an equal key for a LENGTH_HELD type, the key
  otherwise). The census does not measure it: the target is what the
  census's slope and its larger-costs-less share imply on the catalog's own
  pairs (:func:`implied_twice_share`);
* **endings** over every modelled SKU's cents, against each type's census
  endings mix weighted by how many SKUs the catalog builds of that type
  (:func:`ending_targets`).

A new band is three census standard errors either side of the target, and a
share or brand-spread row's band is never narrower than that: a figure the
census measured on few pairs or specs gets the wide band its own sample
leaves (:func:`share_band`, :func:`brand_spread_band`). A row
:data:`.price.PINNED_SHORTFALLS` names is reported with its reason, and is
pinned by the tests to the side of its band that reason puts it, no further
out than the figure :data:`.price.PINNED_FIGURES` records for that build
(:func:`pin_holds`).

Breadth lines are left out, as they are of every realism row.

:func:`collect` reads everything but the prices once; :func:`price_rows`
scores any set of prices against it, so ``scripts/fit_price_model.py`` can
re-score a candidate model without rebuilding the catalog.
"""

from __future__ import annotations

import math
import random
import statistics
from collections import Counter, defaultdict
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass, field, replace
from statistics import NormalDist
from typing import TYPE_CHECKING

from . import brands
from .price import (
    BORROWS,
    BRAND_CENSUS,
    BRAND_SPREAD_TYPE,
    CENSUS,
    ECONOMY_OVER_OTHERS_MEDIAN,
    ENDINGS,
    EQUAL_PRICE_TYPES,
    KEYS,
    LENGTH_CENSUS,
    LENGTH_HELD,
    PIN_TOLERANCE,
    PINNED_FIGURES,
    PINNED_SHORTFALLS,
    POOLED_ENDINGS,
    POOLED_ENDINGS_N,
    BrandCensus,
    PriceCensus,
    _magnitude,
    ending_class,
    holds_equal,
)

if TYPE_CHECKING:
    from .measure import Comparison
    from .model import Catalog

#: Bands a price row must land in, as (low, high) multiples of the target for
#: the ratio rows and +/- an absolute amount for the shares. Wide enough for a
#: 9,700-SKU sample and the 100K mix; narrow enough that the uniform x2.5-9
#: multiplier this replaced lands outside most of them.
P50_BAND = (0.8, 1.25)
SPREAD_BAND = (0.75, 1.33)
MONOTONE_BAND = 0.08
#: The ending classes with a row; each band is :func:`ending_band`.
ENDING_CLASSES = (".99", ".00", ".50", "other .x5")
#: How many census standard errors a new band spans either side.
CENSUS_SES = 3.0
BRAND_SPREAD_BAND = (0.75, 1.33)
#: The most brands a brand-spread row takes from one spec
#: (:func:`brand_sample`). Max/min is an order statistic: over more brands it
#: is wider, whatever the model. The default build puts 2 to 7 brands on a
#: drill spec (median 3) and the 100K build 9 to 15 (median 13), so a figure
#: over every brand of a spec reads the catalog's size, not its prices. The
#: census does not publish its brands per spec, only the most a spec can hold
#: (:attr:`.price.BrandCensus.brands_indexed`: 2 for a socket screw, 3 for a
#: tap); 3 is the median the default build's drill specs hold, so on most of
#: its specs the sample is a true sample and not every brand there is.
BRAND_SAMPLE_CAP = 3
#: The fewest census pairs a smaller-costs-2x-or-more target is implied from
#: (:func:`implied_twice_share`): below it, the census larger-costs-less
#: share the target rests on is too loose to hold a build to (the end mills'
#: 11 and 18 pairs).
TWICE_MIN_CENSUS_PAIRS = 20
#: The least half-width of a smaller-costs-2x-or-more band. The census does
#: not measure that share; where the share it implies is near 0, its band
#: from the census standard errors is near 0 wide too, and one pair in fifty
#: would put a correct build out of band. Two pairs in a hundred is the
#: resolution the catalog's 20-to-a-few-hundred pairs per type can show.
TWICE_BAND_FLOOR = 0.02
ECONOMY_BAND = (0.75, 1.33)
#: The names of the rows ``scripts/fit_price_model.py`` fits, by type.
SPREAD_ROW = "price p90/p10: {}"
ORDER_ROW = "price larger size costs more: {}"
LENGTH_ROW = "price longer costs more: {}"
BRAND_ROW = "price brand spread, same spec (median max/min): {}"
EQUAL_ROW = "price equal price, size pair: {}"


@dataclass
class Collected:
    """Everything a price row reads except the prices, by SKU."""

    #: Every modelled SKU's type.
    type_of: dict[str, str] = field(default_factory=dict)
    #: Per type, every within-cell (larger, smaller) SKU pair whose key differs.
    pairs: dict[str, list[tuple[str, str]]] = field(default_factory=lambda: defaultdict(list))
    #: Per type, every (longer, shorter) SKU pair of one brand and line cell
    #: whose key dimension is equal and whose length differs.
    length_pairs: dict[str, list[tuple[str, str]]] = field(
        default_factory=lambda: defaultdict(list)
    )
    #: Per census type (a borrower under its sibling), every (bigger,
    #: smaller, log ratio) SKU pair of one product line whose axis differs:
    #: length at an equal key for a LENGTH_HELD type, the key otherwise.
    product_pairs: dict[str, list[tuple[str, str, float]]] = field(
        default_factory=lambda: defaultdict(list)
    )
    #: Per (type, key, material) spec, the SKUs each brand makes of it.
    specs: dict[tuple, dict[str, list[str]]] = field(
        default_factory=lambda: defaultdict(lambda: defaultdict(list))
    )


def _cell_names(lines: list) -> dict[str, frozenset[str]]:
    """Per type, the line attributes a cell holds equal: those every line of
    the type publishes. An attribute sparsity drops from some lines would
    split one group page's worth of SKUs into a cell per drop pattern."""
    carried: dict[str, Counter[str]] = defaultdict(Counter)
    count: Counter[str] = Counter()
    for line in lines:
        count[line.type_key] += 1
        carried[line.type_key].update(
            a.name for a in line.attributes if holds_equal(line.type_key, a)
        )
    return {
        type_key: frozenset(name for name, n in names.items() if n == count[type_key])
        for type_key, names in carried.items()
    }


def collect(catalog: Catalog) -> Collected:
    out = Collected()
    cells: dict[tuple, list[tuple[float, str]]] = defaultdict(list)
    by_length: dict[tuple, list[tuple[float, str]]] = defaultdict(list)
    lines = [line for line in catalog.lines if line.spec_quality != "fast_and_cheap"]
    cell_names = _cell_names(lines)
    for line in lines:
        key_of = KEYS.get(line.type_key)
        held = cell_names.get(line.type_key, frozenset())
        line_cell = tuple((a.name, a.value) for a in line.attributes if a.name in held)
        in_line: list[tuple[float, float, str]] = []
        for child in line.children:
            out.type_of[child.sku] = line.type_key
            if key_of is None:
                continue
            attrs = {a.name: a for a in catalog.merged_attributes(line, child)}
            key = key_of(attrs)
            if key is None:
                continue
            length = (
                attrs["Length"].value if line.type_key in LENGTH_HELD and "Length" in attrs else ""
            )
            cells[(line.type_key, line.brand, line_cell, length)].append((key, child.sku))
            if length:
                by_length[(line.type_key, line.brand, line_cell, round(key, 4))].append(
                    (_magnitude(attrs["Length"]) or 0.0, child.sku)
                )
            material = attrs["Material"].value if "Material" in attrs else ""
            out.specs[(line.type_key, round(key, 4), material)][line.brand].append(child.sku)
            in_line.append(
                (key, (_magnitude(attrs["Length"]) or 0.0) if length else 0.0, child.sku)
            )
        _product_pairs(out, line.type_key, in_line)
    for target, groups in ((out.pairs, cells), (out.length_pairs, by_length)):
        for (type_key, *_), members in groups.items():
            for i, (key_a, sku_a) in enumerate(members):
                for key_b, sku_b in members[i + 1 :]:
                    if abs(key_a - key_b) < 1e-9:
                        continue
                    target[type_key].append((sku_a, sku_b) if key_a > key_b else (sku_b, sku_a))
    return out


def _product_pairs(out: Collected, type_key: str, in_line: list[tuple[float, float, str]]) -> None:
    """One line's (bigger, smaller, log ratio) pairs along its axis."""
    by_length = type_key in LENGTH_HELD
    family = BORROWS.get(type_key, type_key)
    for i, (key_a, length_a, sku_a) in enumerate(in_line):
        for key_b, length_b, sku_b in in_line[i + 1 :]:
            if by_length:
                if abs(key_a - key_b) > 1e-9 or length_a <= 0 or length_b <= 0:
                    continue
                a, b = length_a, length_b
            else:
                a, b = key_a, key_b
            if abs(a - b) < 1e-9:
                continue
            bigger, smaller = (sku_a, sku_b) if a > b else (sku_b, sku_a)
            out.product_pairs[family].append((bigger, smaller, abs(math.log(a / b))))


def _quantile(values: list[float], q: float) -> float:
    ordered = sorted(values)
    position = q * (len(ordered) - 1)
    low = math.floor(position)
    high = min(low + 1, len(ordered) - 1)
    return ordered[low] + (ordered[high] - ordered[low]) * (position - low)


def ending_targets(type_counts: Mapping[str, int]) -> dict[str, float]:
    """Each ending class's share of the census, on the catalog's type mix.

    The census pooled its endings over its own type mix (a quarter of its
    SKUs are jobber drills); the catalog builds a different one. Each type's
    census mix (a borrower's sibling's; the pooled mix for a type with none)
    is weighted by the type's share of the catalog's modelled SKUs, so the
    two are compared on the same mix.
    """
    total = sum(type_counts.values())
    targets: dict[str, float] = defaultdict(float)
    for type_key, count in type_counts.items():
        mix = ENDINGS.get(BORROWS.get(type_key, type_key), POOLED_ENDINGS)
        mix_total = sum(mix.values())
        for cls, share in mix.items():
            targets[cls] += share / mix_total * count / total
    return dict(targets)


def _ending_variance(cls: str, type_counts: Mapping[str, int]) -> float:
    """The census sampling variance of ``cls``'s share on the catalog's mix:
    sum over types of w^2 p (1 - p) / n, w the type's catalog share, p and n
    the census share and the census SKUs it is over."""
    total = sum(type_counts.values())
    variance = 0.0
    for type_key, count in type_counts.items():
        census_type = BORROWS.get(type_key, type_key)
        mix = ENDINGS.get(census_type, POOLED_ENDINGS)
        n = CENSUS[census_type].n if census_type in ENDINGS else POOLED_ENDINGS_N
        p = mix.get(cls, 0.0) / sum(mix.values())
        variance += (count / total) ** 2 * p * (1 - p) / n
    return variance


def ending_band(cls: str, type_counts: Mapping[str, int]) -> tuple[float, float]:
    """``cls``'s band: its target (:func:`ending_targets`) plus or minus
    :data:`CENSUS_SES` census standard errors on the catalog's type mix."""
    target = ending_targets(type_counts).get(cls, 0.0)
    width = CENSUS_SES * math.sqrt(_ending_variance(cls, type_counts))
    return (max(0.0, target - width), target + width)


def share_band(target: float, n_pairs: int) -> tuple[float, float]:
    """A larger- or longer-costs-more row's band: :data:`MONOTONE_BAND`
    either side of the census share, or :data:`CENSUS_SES` census standard
    errors where its pairs are so few that is wider (a socket screw's 40)."""
    width = max(MONOTONE_BAND, CENSUS_SES * math.sqrt(target * (1 - target) / n_pairs))
    return (target - width, target + width)


def equal_band(census: PriceCensus) -> tuple[float, float]:
    """An equal-price row's band: :data:`CENSUS_SES` census standard errors
    either side of the census share."""
    share = census.equal_price
    width = CENSUS_SES * math.sqrt(share * (1 - share) / census.n_pairs)
    return (share - width, share + width)


def brand_spread_band(figure: BrandCensus) -> tuple[float, float]:
    """A brand-spread row's band: :data:`BRAND_SPREAD_BAND` about the census
    median, or :data:`CENSUS_SES` standard errors of that median where its
    specs are so few that is wider (a ball end mill's 5).

    The error is of a median in logs: sqrt(pi / 2) * sigma / sqrt(n), with
    sigma read off the census quartiles (the interquartile range of a normal
    is 1.349 sigma)."""
    sigma = math.log(figure.spread_p75 / figure.spread_p25) / 1.349
    width = CENSUS_SES * math.sqrt(math.pi / 2) * sigma / math.sqrt(figure.n_specs)
    low, high = math.exp(-width), math.exp(width)
    return (
        figure.spread_p50 * min(BRAND_SPREAD_BAND[0], low),
        figure.spread_p50 * max(BRAND_SPREAD_BAND[1], high),
    )


def brand_sample(figure: BrandCensus) -> int:
    """How many brands of one spec a brand-spread row takes: the census's
    most per spec, at most :data:`BRAND_SAMPLE_CAP`."""
    return min(figure.brands_indexed, BRAND_SAMPLE_CAP)


def sampled_brands(spec: tuple, names: Iterable[str], k: int) -> list[str]:
    """The ``k`` brands of one spec a brand-spread row reads, drawn once per
    spec on its own stream: as a census page shows the few brands it shows,
    whichever the catalog makes. A spec with ``k`` or fewer gives them all."""
    ordered = sorted(names)
    if len(ordered) <= k:
        return ordered
    return sorted(random.Random(f"brand-sample:{spec}").sample(ordered, k))


def implied_twice_share(slope: float, less: float, log_ratios: Sequence[float]) -> float:
    """The share of pairs whose smaller member costs 2x or more that the
    census implies, on the catalog's own pairs.

    The census measures a slope ``b`` and the share ``less`` of pairs whose
    larger member costs less, not how much less. With log price normal about
    the slope, a pair ``d`` apart in log size inverts with probability
    Phi(-b d / s): ``s`` is solved so the mean over the catalog's ``d`` is
    ``less``, and the 2x share is then the mean of Phi((-ln 2 - b d) / s).
    """
    if not log_ratios or not 0.0 < less < 0.5:
        return 0.0
    cdf = NormalDist().cdf

    def mean(shift: float, sigma: float) -> float:
        return sum(cdf((shift - slope * d) / sigma) for d in log_ratios) / len(log_ratios)

    low, high = 1e-6, 50.0
    for _ in range(60):
        mid = (low + high) / 2
        if mean(0.0, mid) < less:
            low = mid
        else:
            high = mid
    return mean(-math.log(2), (low + high) / 2)


def _axis_census(type_key: str) -> tuple[float, float, int]:
    """(slope, larger-costs-less share, pairs) on a type's within-product axis."""
    if type_key in LENGTH_CENSUS:
        length = LENGTH_CENSUS[type_key]
        return length.slope, length.longer_costs_less, length.n_pairs
    census = CENSUS[type_key]
    return census.slope, census.larger_costs_less, census.n_pairs


#: The census types with a smaller-costs-2x-or-more row: those whose census
#: measures the within-product axis over :data:`TWICE_MIN_CENSUS_PAIRS` or
#: more pairs. :func:`price_rows` scores one only where the catalog builds
#: pairs of one product along that axis; a type that makes one SKU per line
#: along it has none, and a share over no pairs is 0.0 whatever the prices.
TWICE_TYPES: tuple[str, ...] = tuple(
    type_key for type_key in CENSUS if _axis_census(type_key)[2] >= TWICE_MIN_CENSUS_PAIRS
)


def twice_row(type_key: str, collected: Collected, prices: Mapping[str, float]) -> Comparison:
    """The smaller-costs-2x-or-more row of one census type (its borrowers'
    pairs pooled in)."""
    from .measure import Comparison  # noqa: PLC0415 -- measure imports this module

    slope, less, n = _axis_census(type_key)
    pairs = collected.product_pairs.get(type_key, [])
    ratios = [d for _, _, d in pairs]
    twice = sum(prices[small] >= 2 * prices[big] for big, small, _ in pairs)
    se = math.sqrt(less * (1 - less) / n)
    target = implied_twice_share(slope, less, ratios)
    low = implied_twice_share(slope, max(less - CENSUS_SES * se, 1e-6), ratios)
    high = implied_twice_share(slope, min(less + CENSUS_SES * se, 0.4999), ratios)
    low = max(0.0, min(low, target - TWICE_BAND_FLOOR))
    high = max(high, target + TWICE_BAND_FLOOR)
    axis = "length at an equal key" if type_key in LENGTH_HELD else "key dimension"
    return Comparison(
        f"price smaller costs 2x+, same product: {type_key}",
        target,
        twice / len(pairs) if pairs else 0.0,
        twice,
        len(pairs),
        f"pairs of one product, {axis} differs; target IMPLIED by the census slope "
        "and larger-costs-less share, not measured",
        (low, high),
    )


def tier_order(collected: Collected, prices: Mapping[str, float]) -> dict[str, tuple[float, float]]:
    """Per brand family, the median over shared specs of economy over
    standard and of premium over standard (each tier's median price on the
    spec). A family whose tiers price in order has the first below 1 and the
    second above it."""
    ratios: dict[str, tuple[list[float], list[float]]] = defaultdict(lambda: ([], []))
    for (type_key, _, _), by_brand in collected.specs.items():
        if len(by_brand) < 2:
            continue
        by_tier: dict[str, list[float]] = defaultdict(list)
        for brand, skus in by_brand.items():
            by_tier[brands.tier_of(brand, type_key)].extend(prices[s] for s in skus)
        if "standard" not in by_tier:
            continue
        standard = statistics.median(by_tier["standard"])
        economy, premium = ratios[brands.STANDARDS_FAMILY[type_key]]
        if "economy" in by_tier:
            economy.append(statistics.median(by_tier["economy"]) / standard)
        if "premium" in by_tier:
            premium.append(statistics.median(by_tier["premium"]) / standard)
    return {
        family: (
            statistics.median(economy) if economy else math.nan,
            statistics.median(premium) if premium else math.nan,
        )
        for family, (economy, premium) in ratios.items()
    }


def type_rows(type_key: str, collected: Collected, prices: Mapping[str, float]) -> list[Comparison]:
    """The p50, p90/p10 and larger-costs-more rows of one census type."""
    from .measure import Comparison  # noqa: PLC0415 -- measure imports this module

    census = CENSUS[type_key]
    values = [prices[sku] for sku, t in collected.type_of.items() if t == type_key]
    n = len(values)
    p50 = _quantile(values, 0.5) if values else 0.0
    spread = _quantile(values, 0.9) / _quantile(values, 0.1) if values else 0.0
    target_spread = census.p90 / census.p10
    pairs = collected.pairs.get(type_key, [])
    more = sum(prices[larger] > prices[smaller] for larger, smaller in pairs)
    return [
        Comparison(
            f"price p50 (USD): {type_key}",
            census.p50,
            p50,
            n,
            census.n,
            "shown price; denom is the census n",
            (census.p50 * P50_BAND[0], census.p50 * P50_BAND[1]),
        ),
        Comparison(
            SPREAD_ROW.format(type_key),
            target_spread,
            spread,
            n,
            census.n,
            "shown price; denom is the census n",
            (target_spread * SPREAD_BAND[0], target_spread * SPREAD_BAND[1]),
        ),
        Comparison(
            ORDER_ROW.format(type_key),
            census.larger_costs_more,
            more / len(pairs) if pairs else 0.0,
            more,
            len(pairs),
            "within-cell pairs whose key dimension differs",
            share_band(census.larger_costs_more, census.n_pairs),
        ),
    ]


def price_rows(collected: Collected, prices: Mapping[str, float]) -> list[Comparison]:
    """Every price row, scoring ``prices`` (by SKU) against the census."""
    from .measure import Comparison  # noqa: PLC0415 -- measure imports this module

    rows: list[Comparison] = []
    for type_key in CENSUS:
        rows.extend(type_rows(type_key, collected, prices))

    for type_key, figure in LENGTH_CENSUS.items():
        pairs = collected.length_pairs.get(type_key, [])
        more = sum(prices[longer] > prices[shorter] for longer, shorter in pairs)
        rows.append(
            Comparison(
                LENGTH_ROW.format(type_key),
                figure.longer_costs_more,
                more / len(pairs) if pairs else 0.0,
                more,
                len(pairs),
                "pairs of one brand and line cell, key dimension equal, length differs",
                share_band(figure.longer_costs_more, figure.n_pairs),
            )
        )

    for type_key in EQUAL_PRICE_TYPES:
        census = CENSUS[type_key]
        pairs = collected.pairs.get(type_key, [])
        equal = sum(prices[larger] == prices[smaller] for larger, smaller in pairs)
        rows.append(
            Comparison(
                EQUAL_ROW.format(type_key),
                census.equal_price,
                equal / len(pairs) if pairs else 0.0,
                equal,
                len(pairs),
                "within-cell pairs whose key dimension differs",
                equal_band(census),
            )
        )

    rows.extend(
        twice_row(type_key, collected, prices)
        for type_key in TWICE_TYPES
        if collected.product_pairs.get(type_key)
    )

    economy = []
    for type_key, figure in BRAND_CENSUS.items():
        spreads = []
        for spec, by_brand in collected.specs.items():
            if spec[0] != type_key or len(by_brand) < 2:
                continue
            medians = [
                statistics.median(prices[s] for s in by_brand[b])
                for b in sampled_brands(spec, by_brand, brand_sample(figure))
            ]
            spreads.append(max(medians) / min(medians))
            if type_key != BRAND_SPREAD_TYPE:
                continue
            cheap = [
                s
                for b, skus in by_brand.items()
                if brands.tier_of(b, type_key) == "economy"
                for s in skus
            ]
            rest = [
                s
                for b, skus in by_brand.items()
                if brands.tier_of(b, type_key) != "economy"
                for s in skus
            ]
            if cheap and rest:
                economy.append(
                    statistics.median(prices[s] for s in cheap)
                    / statistics.median(prices[s] for s in rest)
                )
        rows.append(
            Comparison(
                BRAND_ROW.format(type_key),
                figure.spread_p50,
                statistics.median(spreads) if spreads else 0.0,
                len(spreads),
                figure.n_specs,
                f"over specs (key dimension, material) two or more brands make; "
                f"{brand_sample(figure)} brands sampled per spec",
                brand_spread_band(figure),
            )
        )
    rows.append(
        Comparison(
            f"price economy brands over others, same spec (median): {BRAND_SPREAD_TYPE}",
            ECONOMY_OVER_OTHERS_MEDIAN,
            statistics.median(economy) if economy else 0.0,
            len(economy),
            len(economy),
            "over specs an economy brand and another brand both make",
            (
                ECONOMY_OVER_OTHERS_MEDIAN * ECONOMY_BAND[0],
                ECONOMY_OVER_OTHERS_MEDIAN * ECONOMY_BAND[1],
            ),
        )
    )

    endings = Counter(ending_class(prices[sku]) for sku in collected.type_of)
    total = sum(endings.values())
    type_counts = Counter(collected.type_of.values())
    targets = ending_targets(type_counts)
    for cls in ENDING_CLASSES:
        rows.append(
            Comparison(
                f"price ending {cls}",
                targets.get(cls, 0.0),
                endings[cls] / total if total else 0.0,
                endings[cls],
                total,
                "over modelled SKUs; target is each type's census mix on the catalog's type mix",
                ending_band(cls, type_counts),
            )
        )
    return [
        replace(row, note=f"{row.note}; PINNED SHORTFALL, {PINNED_SHORTFALLS[row.name]}")
        if row.name in PINNED_SHORTFALLS
        else row
        for row in rows
    ]


def pin_holds(row: Comparison, build: int) -> bool:
    """Whether a row :data:`.price.PINNED_SHORTFALLS` names is still out of
    band on the side its reason names, and no further out than the figure
    :data:`.price.PINNED_FIGURES` records for ``build`` (0 the default
    build, 1 the 100K one), past :data:`.price.PIN_TOLERANCE`."""
    assert row.band is not None
    recorded = PINNED_FIGURES[row.name][build]
    if PINNED_SHORTFALLS[row.name].startswith("below band"):
        return recorded / (1 + PIN_TOLERANCE) <= row.achieved < row.band[0]
    return row.band[1] < row.achieved <= recorded * (1 + PIN_TOLERANCE)


def recorded_digits(name: str) -> int:
    """The decimal places a pinned row's figure is recorded to
    (:data:`.price.PINNED_FIGURES`): a dollar p50 to the cent, a ratio to
    three places."""
    return 2 if name.startswith("price p50 (USD)") else 3


def price_comparisons(catalog: Catalog) -> list[Comparison]:
    prices = {child.sku: child.price_usd for _, child in catalog.all_skus()}
    return price_rows(collect(catalog), prices)
