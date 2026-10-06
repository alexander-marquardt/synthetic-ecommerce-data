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
  brands make: max/min of the per-brand median price;
* **economy over others** over the same specs, where an economy brand and
  another brand both make it: the economy brands' median price over the
  others';
* **endings** over every modelled SKU's cents, against each type's census
  endings mix weighted by how many SKUs the catalog builds of that type
  (:func:`ending_targets`).

Breadth lines are left out, as they are of every realism row.

:func:`collect` reads everything but the prices once; :func:`price_rows`
scores any set of prices against it, so ``scripts/fit_price_model.py`` can
re-score a candidate model without rebuilding the catalog.
"""

from __future__ import annotations

import math
import statistics
from collections import Counter, defaultdict
from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from . import brands
from .price import (
    BORROWS,
    BRAND_SPREAD_MEDIAN,
    BRAND_SPREAD_TYPE,
    CENSUS,
    ECONOMY_OVER_OTHERS_MEDIAN,
    ENDINGS,
    KEYS,
    LENGTH_HELD,
    POOLED_ENDINGS,
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
ENDING_BANDS = {".99": 0.006, ".00": 0.025, ".50": 0.02, "other .x5": 0.04}
BRAND_SPREAD_BAND = (0.75, 1.33)
ECONOMY_BAND = (0.75, 1.33)


@dataclass
class Collected:
    """Everything a price row reads except the prices, by SKU."""

    #: Every modelled SKU's type.
    type_of: dict[str, str] = field(default_factory=dict)
    #: Per type, every within-cell (larger, smaller) SKU pair whose key differs.
    pairs: dict[str, list[tuple[str, str]]] = field(default_factory=lambda: defaultdict(list))
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
    lines = [line for line in catalog.lines if line.spec_quality != "fast_and_cheap"]
    cell_names = _cell_names(lines)
    for line in lines:
        key_of = KEYS.get(line.type_key)
        held = cell_names.get(line.type_key, frozenset())
        line_cell = tuple((a.name, a.value) for a in line.attributes if a.name in held)
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
            material = attrs["Material"].value if "Material" in attrs else ""
            out.specs[(line.type_key, round(key, 4), material)][line.brand].append(child.sku)
    for (type_key, *_), members in cells.items():
        for i, (key_a, sku_a) in enumerate(members):
            for key_b, sku_b in members[i + 1 :]:
                if abs(key_a - key_b) < 1e-9:
                    continue
                out.pairs[type_key].append((sku_a, sku_b) if key_a > key_b else (sku_b, sku_a))
    return out


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
            f"price p90/p10: {type_key}",
            target_spread,
            spread,
            n,
            census.n,
            "shown price; denom is the census n",
            (target_spread * SPREAD_BAND[0], target_spread * SPREAD_BAND[1]),
        ),
        Comparison(
            f"price larger size costs more: {type_key}",
            census.larger_costs_more,
            more / len(pairs) if pairs else 0.0,
            more,
            len(pairs),
            "within-cell pairs whose key dimension differs",
            (
                census.larger_costs_more - MONOTONE_BAND,
                census.larger_costs_more + MONOTONE_BAND,
            ),
        ),
    ]


def price_rows(collected: Collected, prices: Mapping[str, float]) -> list[Comparison]:
    """Every price row, scoring ``prices`` (by SKU) against the census."""
    from .measure import Comparison  # noqa: PLC0415 -- measure imports this module

    rows: list[Comparison] = []
    for type_key in CENSUS:
        rows.extend(type_rows(type_key, collected, prices))

    spreads = []
    economy = []
    for (spec_type, _, _), by_brand in collected.specs.items():
        if spec_type != BRAND_SPREAD_TYPE or len(by_brand) < 2:
            continue
        medians = {b: statistics.median(prices[s] for s in skus) for b, skus in by_brand.items()}
        spreads.append(max(medians.values()) / min(medians.values()))
        cheap = [
            s for b, skus in by_brand.items() if brands.BY_NAME[b].tier == "economy" for s in skus
        ]
        rest = [
            s for b, skus in by_brand.items() if brands.BY_NAME[b].tier != "economy" for s in skus
        ]
        if cheap and rest:
            economy.append(
                statistics.median(prices[s] for s in cheap)
                / statistics.median(prices[s] for s in rest)
            )
    rows.append(
        Comparison(
            f"price brand spread, same spec (median max/min): {BRAND_SPREAD_TYPE}",
            BRAND_SPREAD_MEDIAN,
            statistics.median(spreads) if spreads else 0.0,
            len(spreads),
            len(spreads),
            "over specs (key dimension, material) two or more brands make",
            (
                BRAND_SPREAD_MEDIAN * BRAND_SPREAD_BAND[0],
                BRAND_SPREAD_MEDIAN * BRAND_SPREAD_BAND[1],
            ),
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
    targets = ending_targets(Counter(collected.type_of.values()))
    for cls, width in ENDING_BANDS.items():
        target = targets.get(cls, 0.0)
        rows.append(
            Comparison(
                f"price ending {cls}",
                target,
                endings[cls] / total if total else 0.0,
                endings[cls],
                total,
                "over modelled SKUs; target is each type's census mix on the catalog's type mix",
                (max(0.0, target - width), target + width),
            )
        )
    return rows


def price_comparisons(catalog: Catalog) -> list[Comparison]:
    prices = {child.sku: child.price_usd for _, child in catalog.all_skus()}
    return price_rows(collect(catalog), prices)
