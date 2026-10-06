"""The price rows of ``sip-generate report``, against the price census (#52).

Each row is computed the way the census computed its figure:

* **quantiles** over the shown price of every SKU of the type;
* **larger costs more** over within-cell pairs whose key dimension differs, a
  cell being one product line (plus one length, for the fasteners whose census
  cells held length equal);
* **brand spread** over specs (key dimension and material) that two or more
  brands make: max/min of the per-brand median price;
* **endings** over every modelled SKU's cents.

Breadth lines are left out, as they are of every realism row.
"""

from __future__ import annotations

import math
import statistics
from collections import Counter, defaultdict
from typing import TYPE_CHECKING

from .price import (
    BRAND_SPREAD_MEDIAN,
    BRAND_SPREAD_TYPE,
    CENSUS,
    KEYS,
    LENGTH_HELD,
    POOLED_ENDINGS,
    ending_class,
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


def _quantile(values: list[float], q: float) -> float:
    ordered = sorted(values)
    position = q * (len(ordered) - 1)
    low = math.floor(position)
    high = min(low + 1, len(ordered) - 1)
    return ordered[low] + (ordered[high] - ordered[low]) * (position - low)


def price_comparisons(catalog: Catalog) -> list[Comparison]:
    from .measure import Comparison  # noqa: PLC0415 -- measure imports this module

    prices: dict[str, list[float]] = defaultdict(list)
    cells: dict[tuple, list[tuple[float, float]]] = defaultdict(list)
    spec_prices: dict[tuple, dict[str, list[float]]] = defaultdict(lambda: defaultdict(list))
    endings: Counter[str] = Counter()

    for line in catalog.lines:
        if line.spec_quality == "fast_and_cheap":
            continue
        key_of = KEYS.get(line.type_key)
        for child in line.children:
            price = child.price_usd
            prices[line.type_key].append(price)
            endings[ending_class(price)] += 1
            if key_of is None:
                continue
            attrs = {a.name: a for a in catalog.merged_attributes(line, child)}
            key = key_of(attrs)
            if key is None:
                continue
            length = (
                attrs["Length"].value if line.type_key in LENGTH_HELD and "Length" in attrs else ""
            )
            cells[(line.type_key, line.product_id, length)].append((key, price))
            material = attrs["Material"].value if "Material" in attrs else ""
            spec_prices[(line.type_key, round(key, 4), material)][line.brand].append(price)

    rows: list[Comparison] = []
    for type_key, census in CENSUS.items():
        values = prices.get(type_key, [])
        n = len(values)
        p50 = _quantile(values, 0.5) if values else 0.0
        spread = _quantile(values, 0.9) / _quantile(values, 0.1) if values else 0.0
        target_spread = census.p90 / census.p10
        rows.append(
            Comparison(
                f"price p50 (USD): {type_key}",
                census.p50,
                p50,
                n,
                census.n,
                "shown price; denom is the census n",
                (census.p50 * P50_BAND[0], census.p50 * P50_BAND[1]),
            )
        )
        rows.append(
            Comparison(
                f"price p90/p10: {type_key}",
                target_spread,
                spread,
                n,
                census.n,
                "shown price; denom is the census n",
                (target_spread * SPREAD_BAND[0], target_spread * SPREAD_BAND[1]),
            )
        )
        more = pairs = 0
        for (cell_type, _, _), members in cells.items():
            if cell_type != type_key:
                continue
            for i, (key_a, price_a) in enumerate(members):
                for key_b, price_b in members[i + 1 :]:
                    if abs(key_a - key_b) < 1e-9:
                        continue
                    pairs += 1
                    larger, smaller = (price_a, price_b) if key_a > key_b else (price_b, price_a)
                    more += larger > smaller
        rows.append(
            Comparison(
                f"price larger size costs more: {type_key}",
                census.larger_costs_more,
                more / pairs if pairs else 0.0,
                more,
                pairs,
                "within-cell pairs whose key dimension differs",
                (
                    census.larger_costs_more - MONOTONE_BAND,
                    census.larger_costs_more + MONOTONE_BAND,
                ),
            )
        )

    ratios = []
    for (spec_type, _, _), by_brand in spec_prices.items():
        if spec_type != BRAND_SPREAD_TYPE or len(by_brand) < 2:
            continue
        medians = [statistics.median(v) for v in by_brand.values()]
        ratios.append(max(medians) / min(medians))
    rows.append(
        Comparison(
            f"price brand spread, same spec (median max/min): {BRAND_SPREAD_TYPE}",
            BRAND_SPREAD_MEDIAN,
            statistics.median(ratios) if ratios else 0.0,
            len(ratios),
            len(ratios),
            "over specs (key dimension, material) two or more brands make",
            (
                BRAND_SPREAD_MEDIAN * BRAND_SPREAD_BAND[0],
                BRAND_SPREAD_MEDIAN * BRAND_SPREAD_BAND[1],
            ),
        )
    )

    total = sum(endings.values())
    for cls, width in ENDING_BANDS.items():
        target = POOLED_ENDINGS[cls]
        rows.append(
            Comparison(
                f"price ending {cls}",
                target,
                endings[cls] / total if total else 0.0,
                endings[cls],
                total,
                "over modelled SKUs",
                (max(0.0, target - width), target + width),
            )
        )
    return rows
