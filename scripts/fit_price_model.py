"""Fit each type's price anchor and noise to the price census (#52).

    python scripts/fit_price_model.py           # print the fitted literals
    python scripts/fit_price_model.py --write   # and write them between the fit markers

The census gives each type a slope, an endings mix, a p50, a p90/p10 and a
larger-costs-more share (:mod:`synthetic_industrial_products.catalog.price`).
The slope and the endings go into the model as they are; this script solves
the other three for the default build, holding the key, material, tier and
pack terms the build draws:

* ``sku_sigma``, the noise each SKU draws alone, sets how often a larger size
  costs less than a smaller one in its cell: for a given ``group_sigma`` it is
  bisected until the larger-costs-more share is the census share;
* ``group_sigma``, the noise one price group (a census cell) shares, is bisected (with
  ``sku_sigma`` re-solved inside it) until the p90/p10 is the census figure;
* ``anchor`` is then set so the median shown price is the census p50.

Neither noise term nor the anchor moves any draw: the build is made once, and
every candidate is scored by recomputing prices from the recorded draws
(:class:`~synthetic_industrial_products.catalog.price.Draw`). Where no noise
can reach a target the fit says so in the slope or the share it lands on:
where the census slope alone already spreads the shown price wider than the
census p90/p10, the slope is lowered until it does not (``price.py`` says
why); where a type's few within-cell pairs keep a larger-costs-more share
above the census share however loud the noise, the share aims a quarter of
the band above that floor. The hammer has no census prices and is not fitted.
"""

from __future__ import annotations

import argparse
import math
import re
import sys
from dataclasses import replace
from pathlib import Path

import numpy as np

from synthetic_industrial_products.catalog import price
from synthetic_industrial_products.catalog.config import GeneratorConfig
from synthetic_industrial_products.catalog.generate import Generator, generate
from synthetic_industrial_products.catalog.model import Catalog
from synthetic_industrial_products.catalog.price_report import (
    BRAND_SPREAD_BAND,
    MONOTONE_BAND,
    SPREAD_BAND,
    collect,
    type_rows,
)

REPO = Path(__file__).resolve().parent.parent
PRICE_PY = REPO / "src" / "synthetic_industrial_products" / "catalog" / "price.py"
SOCKET_PY = (
    REPO
    / "src"
    / "synthetic_industrial_products"
    / "product_types"
    / "fasteners"
    / "screw_socket_head.py"
)
#: The largest sigma either bisection tries.
MAX_SIGMA = 3.0
STEPS = 30


def record_draws() -> tuple[Catalog, dict[str, price.Draw], dict[str, float]]:
    """The default build, every modelled SKU's draw, and each SKU's
    ``log(key / anchor_key)``: the term the slope multiplies."""
    draws: dict[str, price.Draw] = {}
    log_keys: dict[str, float] = {}
    original = Generator._price_draw  # noqa: SLF001

    def recording(self, type_key, brand, attributes, line_attributes, sku, sku_u):
        draw = original(self, type_key, brand, attributes, line_attributes, sku, sku_u)
        draws[sku] = draw
        key = price.KEYS[type_key]({a.name: a for a in attributes})
        log_keys[sku] = math.log(key / draw.model.anchor_key) if key else 0.0
        return draw

    Generator._price_draw = recording  # type: ignore[method-assign]  # noqa: SLF001
    try:
        catalog = generate(GeneratorConfig())
    finally:
        Generator._price_draw = original  # type: ignore[method-assign]  # noqa: SLF001
    return catalog, draws, log_keys


def _z(us: np.ndarray) -> np.ndarray:
    return np.array([price._z(u) for u in us])  # noqa: SLF001


def _bisect(f, target: float, low: float, high: float, increasing: bool) -> float:
    """The x in [low, high] where ``f(x)`` crosses ``target``, or the end
    nearest it when it never does."""
    f_low, f_high = f(low), f(high)
    if increasing and f_low >= target or not increasing and f_low <= target:
        return low
    if increasing and f_high <= target or not increasing and f_high >= target:
        return high
    for _ in range(STEPS):
        mid = (low + high) / 2
        if (f(mid) < target) == increasing:
            low = mid
        else:
            high = mid
    return (low + high) / 2


def fit_type(
    type_key: str, skus: list[str], pairs, draws, log_keys, specs=()
) -> tuple[float, float, float, float]:
    """``type_key``'s (anchor, slope, group_sigma, sku_sigma)."""
    census = price.CENSUS[type_key]
    index = {sku: i for i, sku in enumerate(skus)}
    log_key = np.array([log_keys[s] for s in skus])
    # The structure less its slope term, at whatever slope the build used.
    rest = np.array([draws[s].struct - draws[s].model.slope * log_keys[s] for s in skus])
    z_group = _z(np.array([draws[s].group_u for s in skus]))
    z_sku = _z(np.array([draws[s].sku_u for s in skus]))
    larger = np.array([index[a] for a, _ in pairs], dtype=int)
    smaller = np.array([index[b] for _, b in pairs], dtype=int)
    target_spread = census.p90 / census.p10

    def log_p(slope: float, group: float, sku: float) -> np.ndarray:
        return rest + slope * log_key + group * z_group + sku * z_sku

    def share(slope: float, group: float, sku: float) -> float:
        lp = log_p(slope, group, sku)
        return float(np.mean(lp[larger] > lp[smaller])) if len(larger) else 0.0

    def sku_for(slope: float, group: float) -> float:
        # A cell's pairs are a sample: however loud the noise, the share of
        # them a larger size wins cannot fall below what the draws' signs
        # give. Where that floor is above the census share, aim a quarter of
        # the band above the floor rather than at a share no sigma reaches.
        target = census.larger_costs_more
        floor = share(slope, group, MAX_SIGMA)
        if floor >= target:
            target = floor + MONOTONE_BAND / 4
        return _bisect(lambda s: share(slope, group, s), target, 0.0, MAX_SIGMA, increasing=False)

    def spread(slope: float, group: float) -> float:
        lp = log_p(slope, group, sku_for(slope, group))
        return float(np.exp(np.quantile(lp, 0.9) - np.quantile(lp, 0.1)))

    slope = census.slope
    if spread(slope, 0.0) > target_spread:
        # The census slope alone spreads the shown price wider than the
        # census does: lower it until it no longer does (see price.py).
        slope = census.slope * _bisect(
            lambda k: spread(census.slope * k, 0.0), target_spread, 0.0, 1.0, increasing=True
        )
    group = _bisect(lambda g: spread(slope, g), target_spread, 0.0, MAX_SIGMA, increasing=True)
    if specs:
        # The brand-spread type's group noise also spreads brands apart on
        # one spec: take the group sigma, up to the one the p90/p10 asks for,
        # that keeps both rows nearest their targets in band widths.
        def brand_spread(group: float) -> float:
            lp = log_p(slope, group, sku_for(slope, group))
            ratios = []
            for by_brand in specs:
                medians = [np.median(lp[[index[s] for s in members]]) for members in by_brand]
                ratios.append(np.exp(max(medians) - min(medians)))
            return float(np.median(ratios))

        def miss(group: float) -> float:
            return max(
                abs(math.log(spread(slope, group) / target_spread)) / math.log(SPREAD_BAND[1]),
                abs(math.log(brand_spread(group) / price.BRAND_SPREAD_MEDIAN))
                / math.log(BRAND_SPREAD_BAND[1]),
            )

        group = min((group * i / 40 for i in range(41)), key=miss)
    sku = sku_for(slope, group)
    anchor = census.p50 / float(np.exp(np.median(log_p(slope, group, sku))))
    return anchor, slope, group, sku


def _literal(type_key: str, model: price.PriceModel) -> str:
    args = (
        f"{model.anchor:.4g}, {model.anchor_key!r}, {model.group_sigma:.3f}, {model.sku_sigma:.3f}"
    )
    if model.slope != price.CENSUS[type_key].slope:
        args += f", slope={model.slope!r}"
    if model.pack_attribute is None:
        return f'        "{type_key}": _model("{type_key}", {args}),'
    return (
        f'        "{type_key}": _model(\n'
        f'            "{type_key}",\n'
        + "".join(f"            {a.strip()},\n" for a in args.split(","))
        + f'            pack_attribute="{model.pack_attribute}",\n'
        "            pack_slope=NUT_PACK_SLOPE,\n"
        f"            pack_ref={model.pack_ref!r},\n"
        "        ),"
    )


def _between_markers(path: Path, begin: str, body: str) -> None:
    text = path.read_text()
    pattern = re.compile(rf"(?m)^(\s*# @fit-begin{begin}\n).*?(^\s*# @fit-end)", re.S)
    if not pattern.search(text):
        sys.exit(f"no fit markers in {path}")
    path.write_text(pattern.sub(lambda m: m.group(1) + body + "\n" + m.group(2), text, count=1))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--write", action="store_true", help="write the literals into the source")
    args = parser.parse_args()

    catalog, draws, log_keys = record_draws()
    collected = collect(catalog)
    fitted: dict[str, price.PriceModel] = {}
    for type_key in price.CENSUS:
        skus = [s for s, t in collected.type_of.items() if t == type_key]
        anchor, slope, group, sku = fit_type(
            type_key,
            skus,
            collected.pairs.get(type_key, []),
            draws,
            log_keys,
            [
                list(by_brand.values())
                for (spec_type, _, _), by_brand in collected.specs.items()
                if spec_type == type_key == price.BRAND_SPREAD_TYPE and len(by_brand) >= 2
            ],
        )
        fitted[type_key] = replace(
            price.MODELS[type_key],
            anchor=float(f"{anchor:.4g}"),
            slope=round(slope, 3),
            group_sigma=round(group, 3),
            sku_sigma=round(sku, 3),
        )

    # Score the rounded literals on shown prices, endings and all.
    prices = {
        sku: price.shown_price(
            replace(
                d,
                model=fitted[collected.type_of[sku]],
                struct=d.struct
                + (fitted[collected.type_of[sku]].slope - d.model.slope) * log_keys[sku],
            )
        )
        if collected.type_of.get(sku) in fitted
        else price.shown_price(d)
        for sku, d in draws.items()
        if sku in collected.type_of
    }
    for type_key in price.CENSUS:
        for row in type_rows(type_key, collected, prices):
            flag = "ok" if row.within else "OUT"
            print(f"{row.name:<52}{row.target:>10.4f}{row.achieved:>10.4f}  {flag}")

    table = "\n".join(_literal(k, m) for k, m in fitted.items() if k != "screw_socket_head")
    socket = fitted["screw_socket_head"]
    socket_body = (
        f"    anchor={socket.anchor:.4g},\n    anchor_key={socket.anchor_key!r},\n"
        + (
            '    slope=CENSUS["screw_socket_head"].slope,\n'
            if socket.slope == price.CENSUS["screw_socket_head"].slope
            else f"    slope={socket.slope!r},\n"
        )
        + f"    group_sigma={socket.group_sigma:.3f},\n    sku_sigma={socket.sku_sigma:.3f},"
    )
    print("\n# price.py, between the fit markers:\n" + table)
    print("\n# screw_socket_head.py, between its fit markers:\n" + socket_body)
    if args.write:
        _between_markers(PRICE_PY, "", table)
        _between_markers(SOCKET_PY, " screw_socket_head", socket_body)
    return 0


if __name__ == "__main__":
    sys.exit(main())
