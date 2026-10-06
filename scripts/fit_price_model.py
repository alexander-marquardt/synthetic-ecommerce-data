"""Fit each type's price anchor, noise and ladder to the price census (#52).

    python scripts/fit_price_model.py           # print the fit, every price row and the literals
    python scripts/fit_price_model.py --write   # and write them between the fit markers

The census gives each type a slope, an endings mix, a p50, a p90/p10, a
larger-costs-more share and, for some, a length slope and share and a
same-spec brand spread (:mod:`synthetic_industrial_products.catalog.price`).
The slopes, tiers and endings go into the model as they are; this script
solves the rest for the default build, holding the key, length, material,
tier and pack terms the build draws:

* ``sku_sigma``, the noise each SKU draws alone, sets how often a larger size
  costs less than a smaller one in its cell: it is the sigma whose worst miss
  over the type's order rows (larger costs more; longer costs more where the
  census measures length) is least, in band widths. Where a type's few pairs
  keep a share above the census share however loud the noise, that row aims
  a quarter of the band above its floor rather than at a share no sigma
  reaches;
* ``price_step`` (taps only, :data:`.price.EQUAL_PRICE_TYPES`), the list-price
  ladder, is the step whose equal-price share is nearest the census's, with
  ``sku_sigma`` re-solved at each step;
* ``group_sigma``, the noise one price group (a census cell) shares, is the
  sigma whose worst miss over the p90/p10 and the same-spec brand spread is
  least, with ``sku_sigma`` re-solved at each; a row
  :data:`.price.PINNED_SHORTFALLS` names is left out;
* ``anchor`` is then set so the median shown price is the census p50.

**Slope cuts need a recorded reason.** Where the slope terms ALONE (the key
term, and the length term) spread the shown price wider than the census
p90/p10, the census slope cannot be the shown-price slope. The fit then
lowers it, both slopes by one factor, until the whole model with no group
noise lands on the census p90/p10, but only for a type
:data:`.price.SLOPE_CUTS` gives a reason for: any other type that would need
a cut, or a listed type that no longer does, stops the fit.

Neither noise term nor the anchor moves any draw: the build is made once, and
every candidate is scored by recomputing prices from the recorded draws
(:class:`~synthetic_industrial_products.catalog.price.Draw`). The hammer has no
census prices and is not fitted.
"""

from __future__ import annotations

import argparse
import math
import re
import sys
from dataclasses import dataclass, replace
from pathlib import Path

import numpy as np

from synthetic_industrial_products.catalog import brands, price
from synthetic_industrial_products.catalog.config import GeneratorConfig
from synthetic_industrial_products.catalog.generate import Generator, generate
from synthetic_industrial_products.catalog.model import Catalog
from synthetic_industrial_products.catalog.price_report import (
    BRAND_SPREAD_BAND,
    CENSUS_SES,
    MONOTONE_BAND,
    SPREAD_BAND,
    Collected,
    collect,
    price_rows,
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
#: The largest sigma the fit tries.
MAX_SIGMA = 3.0
STEPS = 30
#: The grid a minimax search scans before it refines.
GRID = 61


@dataclass
class Recorded:
    """One modelled SKU's draw and the terms its structure is made of."""

    draw: price.Draw
    #: log(key / anchor_key) and log(length / anchor_length): what the slopes multiply.
    log_key: float
    log_length: float
    tier: float
    material: float


def record_draws() -> tuple[Catalog, dict[str, Recorded]]:
    """The default build and every modelled SKU's draw and terms."""
    recorded: dict[str, Recorded] = {}
    original = Generator._price_draw  # noqa: SLF001

    def recording(self, type_key, brand, attributes, line_attributes, sku, sku_u):
        draw = original(self, type_key, brand, attributes, line_attributes, sku, sku_u)
        facts = {a.name: a for a in attributes}
        model = draw.model
        key = price.KEYS[type_key](facts)
        length = price.length_of(facts) if type_key in price.LENGTH_HELD else None
        material = facts["Material"].value if "Material" in facts else ""
        recorded[sku] = Recorded(
            draw,
            math.log(key / model.anchor_key) if key else 0.0,
            math.log(length / model.anchor_length) if length else 0.0,
            math.log(model.tiers[brands.tier_of(brand, type_key)]),
            math.log(price.MATERIAL_FACTORS.get(material, 1.0)),
        )
        return draw

    Generator._price_draw = recording  # type: ignore[method-assign]  # noqa: SLF001
    try:
        catalog = generate(GeneratorConfig())
    finally:
        Generator._price_draw = original  # type: ignore[method-assign]  # noqa: SLF001
    return catalog, recorded


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


def _argmin(f, low: float, high: float) -> float:
    """The x in [low, high] where ``f`` is least: a grid, then a finer grid
    around the best point."""
    for _ in range(3):
        xs = np.linspace(low, high, GRID)
        best = int(np.argmin([f(x) for x in xs]))
        step = (high - low) / (GRID - 1)
        low, high = max(xs[best] - step, 0.0), xs[best] + step
    return float((low + high) / 2)


def _ratio_miss(achieved: float, target: float, band: tuple[float, float]) -> float:
    """How far a ratio row is from its target, in band widths."""
    return abs(math.log(achieved / target)) / math.log(band[1])


@dataclass
class TypeFit:
    """One type's fitted figures and the spread each term gives alone."""

    anchor: float
    slope: float
    length_slope: float
    group: float
    sku: float
    step: float
    spreads: dict[str, float]


def fit_type(type_key: str, collected: Collected, recorded: dict[str, Recorded]) -> TypeFit:
    """``type_key``'s fitted model figures (see the module docstring)."""
    census = price.CENSUS[type_key]
    model = price.MODELS[type_key]
    skus = [s for s, t in collected.type_of.items() if t == type_key]
    index = {sku: i for i, sku in enumerate(skus)}
    rec = [recorded[s] for s in skus]
    log_key = np.array([r.log_key for r in rec])
    log_length = np.array([r.log_length for r in rec])
    # The structure less its slope terms, at whatever slopes the build used.
    rest = np.array(
        [
            r.draw.struct
            - r.draw.model.slope * r.log_key
            - r.draw.model.length_slope * r.log_length
            for r in rec
        ]
    )
    tier = np.array([r.tier for r in rec])
    material = np.array([r.material for r in rec])
    z_group = _z(np.array([r.draw.group_u for r in rec]))
    z_sku = _z(np.array([r.draw.sku_u for r in rec]))

    def pair_index(pairs) -> tuple[np.ndarray, np.ndarray]:
        return (
            np.array([index[a] for a, _ in pairs], dtype=int),
            np.array([index[b] for _, b in pairs], dtype=int),
        )

    order_rows = [(pair_index(collected.pairs.get(type_key, [])), census.larger_costs_more)]
    length = price.LENGTH_CENSUS.get(type_key)
    if length is not None:
        order_rows.append(
            (pair_index(collected.length_pairs.get(type_key, [])), length.longer_costs_more)
        )
    specs = [
        [np.array([index[s] for s in members]) for members in by_brand.values()]
        for (spec_type, _, _), by_brand in collected.specs.items()
        if spec_type == type_key and len(by_brand) >= 2
    ]
    brand = price.BRAND_CENSUS.get(type_key)
    target_spread = census.p90 / census.p10
    spread_pinned = f"price p90/p10: {type_key}" in price.PINNED_SHORTFALLS
    laddered = type_key in price.EQUAL_PRICE_TYPES

    def log_p(slope: float, ls: float, group: float, sku: float, step: float) -> np.ndarray:
        lp = rest + slope * log_key + ls * log_length + group * z_group + sku * z_sku
        return np.round(lp / step) * step if step else lp

    def share(lp: np.ndarray, pairs) -> float:
        larger, smaller = pairs
        return float(np.mean(lp[larger] > lp[smaller])) if len(larger) else 0.0

    def p90_p10(values: np.ndarray) -> float:
        return float(np.exp(np.quantile(values, 0.9) - np.quantile(values, 0.1)))

    def brand_spread(lp: np.ndarray) -> float:
        ratios = [
            np.exp(max(medians) - min(medians))
            for medians in ([np.median(lp[m]) for m in by_brand] for by_brand in specs)
        ]
        return float(np.median(ratios))

    def sku_for(slope: float, ls: float, group: float, step: float) -> float:
        # A row's pairs are a sample: however loud the noise, the share of
        # them a larger size wins cannot fall below what the draws' signs
        # give. Where that floor is above the census share, the row aims a
        # quarter of the band above the floor.
        aims = []
        for pairs, target in order_rows:
            if not len(pairs[0]):
                continue
            floor = share(log_p(slope, ls, group, MAX_SIGMA, step), pairs)
            aims.append((pairs, floor + MONOTONE_BAND / 4 if floor >= target else target))
        if not aims:
            return 0.0

        def miss(sku: float) -> float:
            lp = log_p(slope, ls, group, sku, step)
            return max(abs(share(lp, pairs) - aim) / MONOTONE_BAND for pairs, aim in aims)

        if len(aims) == 1:
            pairs, aim = aims[0]
            return _bisect(
                lambda s: share(log_p(slope, ls, group, s, step), pairs),
                aim,
                0.0,
                MAX_SIGMA,
                increasing=False,
            )
        return _argmin(miss, 0.0, MAX_SIGMA)

    def spread(slope: float, ls: float, group: float, step: float) -> float:
        return p90_p10(log_p(slope, ls, group, sku_for(slope, ls, group, step), step))

    slope, ls = census.slope, length.slope if length else 0.0
    alone = p90_p10(slope * log_key + ls * log_length)
    if alone > target_spread and type_key not in price.SLOPE_CUTS:
        sys.exit(
            f"{type_key}: the census slopes alone spread the shown price {alone:.2f}x, wider "
            f"than the census p90/p10 {target_spread:.2f}x, and price.SLOPE_CUTS records no "
            "reason to lower them"
        )
    if type_key in price.SLOPE_CUTS:
        if alone <= target_spread:
            sys.exit(
                f"{type_key}: price.SLOPE_CUTS lowers its slope, but the census slopes alone "
                f"spread only {alone:.2f}x, inside the census p90/p10 {target_spread:.2f}x"
            )
        factor = _bisect(
            lambda k: spread(slope * k, ls * k, 0.0, 0.0), target_spread, 0.0, 1.0, increasing=True
        )
        slope, ls = slope * factor, ls * factor

    step = 0.0
    if laddered:
        pairs = order_rows[0][0]

        def equal_miss(step: float) -> float:
            lp = log_p(slope, ls, 0.0, sku_for(slope, ls, 0.0, step), step)
            return abs(float(np.mean(lp[pairs[0]] == lp[pairs[1]])) - census.equal_price)

        step = _argmin(equal_miss, 0.01, 0.6)

    def group_miss(group: float) -> float:
        lp = log_p(slope, ls, group, sku_for(slope, ls, group, step), step)
        misses = [] if spread_pinned else [_ratio_miss(p90_p10(lp), target_spread, SPREAD_BAND)]
        if brand is not None and specs:
            misses.append(_ratio_miss(brand_spread(lp), brand.spread_p50, BRAND_SPREAD_BAND))
        return max(misses) if misses else 0.0

    group = _argmin(group_miss, 0.0, MAX_SIGMA)
    sku = sku_for(slope, ls, group, step)
    anchor = census.p50 / float(np.exp(np.median(log_p(slope, ls, group, sku, step))))
    pack = rest - tier - material
    spreads = {
        "key": p90_p10(slope * log_key),
        "length": p90_p10(ls * log_length),
        "tier": p90_p10(tier),
        "material": p90_p10(material),
        "pack": p90_p10(pack),
        "group": p90_p10(group * z_group),
        "sku": p90_p10(sku * z_sku),
        "all": p90_p10(log_p(slope, ls, group, sku, step)),
        "census": target_spread,
    }
    del model
    return TypeFit(anchor, slope, ls, group, sku, step, spreads)


def _literal(type_key: str, model: price.PriceModel) -> str:
    args = [
        f"{model.anchor:.4g}",
        repr(model.anchor_key),
        f"{model.group_sigma:.3f}",
        f"{model.sku_sigma:.3f}",
    ]
    if model.slope != price.CENSUS[type_key].slope:
        args.append(f"slope={model.slope!r}")
    length = price.LENGTH_CENSUS.get(type_key)
    if length is not None and model.length_slope != length.slope:
        args.append(f"length_slope={model.length_slope!r}")
    if model.price_step:
        args.append(f"price_step={model.price_step!r}")
    if model.pack_attribute is not None:
        args += [
            f'pack_attribute="{model.pack_attribute}"',
            "pack_slope=NUT_PACK_SLOPE",
            f"pack_ref={model.pack_ref!r}",
        ]
    one_line = f'        "{type_key}": _model("{type_key}", {", ".join(args)}),'
    if len(one_line) <= 100:
        return one_line
    return (
        f'        "{type_key}": _model(\n            "{type_key}",\n'
        + "".join(f"            {a},\n" for a in args)
        + "        ),"
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

    catalog, recorded = record_draws()
    collected = collect(catalog)
    fitted: dict[str, price.PriceModel] = {}
    print(
        f"{'p90/p10 of each term alone':<26}"
        + "".join(
            f"{k:>9}"
            for k in ("key", "length", "tier", "material", "pack", "group", "sku", "all", "census")
        )
    )
    for type_key in price.CENSUS:
        fit = fit_type(type_key, collected, recorded)
        print(f"{type_key:<26}" + "".join(f"{v:>9.2f}" for v in fit.spreads.values()))
        fitted[type_key] = replace(
            price.MODELS[type_key],
            anchor=float(f"{fit.anchor:.4g}"),
            slope=round(fit.slope, 3),
            length_slope=round(fit.length_slope, 3),
            group_sigma=round(fit.group, 3),
            sku_sigma=round(fit.sku, 3),
            price_step=round(fit.step, 3),
        )
    for type_key, reason in price.SLOPE_CUTS.items():
        print(f"slope cut, {type_key}: {fitted[type_key].slope} ({reason})")

    # Score the rounded literals on shown prices, endings and all.
    prices: dict[str, float] = {}
    for sku, rec in recorded.items():
        if sku not in collected.type_of:
            continue
        old = rec.draw.model
        new = fitted.get(price.BORROWS.get(collected.type_of[sku], collected.type_of[sku]))
        if new is None:
            prices[sku] = price.shown_price(rec.draw)
            continue
        struct = (
            rec.draw.struct
            + (new.slope - old.slope) * rec.log_key
            + (new.length_slope - old.length_slope) * rec.log_length
        )
        prices[sku] = price.shown_price(replace(rec.draw, model=new, struct=struct))
    for row in price_rows(collected, prices):
        flag = "ok" if row.within else "OUT"
        if row.name in price.PINNED_SHORTFALLS:
            flag += " (pinned shortfall)"
        print(f"{row.name:<62}{row.target:>10.4f}{row.achieved:>10.4f}  {flag}")

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
