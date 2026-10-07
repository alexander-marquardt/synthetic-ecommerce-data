"""Fit each type's price anchor, noise and ladder to the price census (#52).

    python scripts/fit_price_model.py           # print the fit, every price row and the literals
    python scripts/fit_price_model.py --write   # and write them between the fit markers

The census gives each type a slope, an endings mix, a p50, a p90/p10, a
larger-costs-more share and, for some, a length slope and share and a
same-spec brand spread (:mod:`synthetic_industrial_products.catalog.price`).
The slopes, tiers and endings go into the model as they are; this script
solves the rest, holding the key, length, material, tier and pack terms the
builds draw.

**Every row is scored at the default build AND at 100K**
(:data:`.config.HUNDRED_K_LINES`, the size the 100K band test builds), and a
row's miss is the worse of the two: a model tuned to one build's draws holds
its realism claim only by that build's luck. The anchor sits at the
log-midpoint of the two builds' medians, so the p50 row scores how far apart
they are. The brand spread is scored as the report scores it, over
:func:`.price_report.sampled_brands`. Each fitted figure is:

* ``sku_sigma``, the noise each SKU draws alone, sets how often a larger size
  costs less than a smaller one in its cell: it is the sigma whose worst miss
  over the type's order rows (larger costs more; longer costs more where the
  census measures length) at both builds is least, in band widths. Where a
  build's few pairs keep a share above the census share however loud the
  noise, that row aims a quarter of the band above its floor rather than at a
  share no sigma reaches;
* ``price_step`` (taps only, :data:`.price.EQUAL_PRICE_TYPES`), the list-price
  ladder, is the step whose worse equal-price share is nearest the census's,
  with ``sku_sigma`` re-solved at each step;
* ``group_sigma``, the noise one price group (a census cell) shares, is the
  sigma whose worst miss over the p50, the p90/p10 and the same-spec brand
  spread is least, with ``sku_sigma`` re-solved at each; a row
  :data:`.price.PINNED_SHORTFALLS` names is left out. A group draw is one per
  page, so a type with few pages has a median that moves with the build's
  size the louder the group noise is: the p50 row holds it down. A type
  priced from its contents (:data:`.price.CONTENTS_PRICED`, kits) is fitted
  none: its spread is what its contents span;
* ``size_sigma`` (only a type :data:`.price.SIZE_NOISE` names), the noise
  one spec shares across brands, is fitted with ``group_sigma`` and
  ``sku_sigma`` together: the worst miss over p50, p90/p10, brand spread, the
  order rows and the equal-price row, each scored against its band;
* ``anchor`` is then set so the two builds' median shown prices sit either
  side of the census p50, equally far in logs.

Making both builds takes about a minute; the 100K one dominates.

Each printed row says "cannot reach" where no noise the fit scanned brings it
into band. **Every row lands in band or is pinned, at both builds.** The
fit exits non-zero, before it writes, on a row out of band at either build
that :data:`.price.PINNED_SHORTFALLS` does not name, and on a pinned row that
no longer holds (:func:`.price_report.pin_holds`) at either: back in band, on
the other side, or further out than :data:`.price.PINNED_FIGURES` records for
that build. A pinned row whose recorded figures are not the ones it built
is flagged "re-record" with the figures to write by hand, at both builds:
``tests/test_price.py`` holds each record equal to its build's figure.

**Slope cuts need a recorded reason.** Where the slope terms ALONE (the key
term, and the length term) spread the shown price wider than the census
p90/p10, the census slope cannot be the shown-price slope. The fit then
lowers it, both slopes by one factor, until the whole model with no group
noise lands on the census p90/p10, at whichever build the slopes alone spread
wider, but only for a type :data:`.price.SLOPE_CUTS` gives a reason for: any
other type that would need a cut, or a listed type that no longer does, stops
the fit.

Neither noise term nor the anchor moves any draw: each build is made once,
and every candidate is scored by recomputing prices from the recorded draws
(:class:`~synthetic_industrial_products.catalog.price.Draw`). The hammer has no
census prices and is not fitted.
"""

from __future__ import annotations

import argparse
import itertools
import math
import re
import sys
from dataclasses import dataclass, replace
from pathlib import Path

import numpy as np

from synthetic_industrial_products.catalog import brands, price
from synthetic_industrial_products.catalog.config import HUNDRED_K_LINES, GeneratorConfig
from synthetic_industrial_products.catalog.generate import Generator, generate
from synthetic_industrial_products.catalog.model import Catalog
from synthetic_industrial_products.catalog.price_report import (
    BRAND_ROW,
    EQUAL_ROW,
    LENGTH_ROW,
    ORDER_ROW,
    P50_BAND,
    SPREAD_BAND,
    SPREAD_ROW,
    Collected,
    brand_sample,
    brand_spread_band,
    collect,
    equal_band,
    pin_holds,
    price_rows,
    recorded_digits,
    sampled_brands,
    share_band,
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
#: The grid a minimax search scans before it refines, on one axis and a side
#: of several.
GRID = 61
GRID_ND = 13
#: The builds every row is scored at: the default, and the 100K band test's.
BUILDS = {"default": GeneratorConfig(), "100K": GeneratorConfig(lines=HUNDRED_K_LINES)}
P50_ROW = "price p50 (USD): {}"


@dataclass
class Recorded:
    """One modelled SKU's draw and the terms its structure is made of."""

    draw: price.Draw
    #: log(key / anchor_key) and log(length / anchor_length): what the slopes multiply.
    log_key: float
    log_length: float
    tier: float
    material: float


def record_draws(config: GeneratorConfig) -> tuple[Catalog, dict[str, Recorded]]:
    """The build ``config`` makes and every modelled SKU's draw and terms."""
    recorded: dict[str, Recorded] = {}
    original = Generator._price_draw  # noqa: SLF001

    def recording(self, type_key, brand, attributes, line_attributes, sku, sku_u):
        draw = original(self, type_key, brand, attributes, line_attributes, sku, sku_u)
        facts = {a.name: a for a in attributes}
        model = draw.model
        key = price.price_key(type_key, facts)
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
        catalog = generate(config)
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


def _miss(achieved: float, target: float, band: tuple[float, float], ratio: bool) -> float:
    """How far a row is from its target, in half-bands on the side it falls
    (in logs for a ratio row): 1.0 or less is in band."""
    values = (achieved, target, *band)
    a, t, low, high = (math.log(max(v, 1e-12)) for v in values) if ratio else values
    side = high - t if a >= t else t - low
    return abs(a - t) / side if side > 0 else math.inf


def _argmin_grid(f, high: float, axes: int) -> tuple[float, ...]:
    """The point in [0, high]^axes where ``f`` is least: a grid of
    :data:`GRID_ND` a side, then finer grids around the best point."""
    lows, highs = [0.0] * axes, [high] * axes
    for _ in range(3):
        ticks = [np.linspace(lo, hi, GRID_ND) for lo, hi in zip(lows, highs, strict=True)]
        points = list(itertools.product(*ticks))
        best = points[int(np.argmin([f(*point) for point in points]))]
        steps = [(hi - lo) / (GRID_ND - 1) for lo, hi in zip(lows, highs, strict=True)]
        lows = [max(b - st, 0.0) for b, st in zip(best, steps, strict=True)]
        highs = [b + st for b, st in zip(best, steps, strict=True)]
    return tuple(float((lo + hi) / 2) for lo, hi in zip(lows, highs, strict=True))


@dataclass
class TypeFit:
    """One type's fitted figures, the spread each term gives alone, and the
    rows no noise the fit scanned brings into band."""

    anchor: float
    slope: float
    length_slope: float
    group: float
    sku: float
    step: float
    size: float
    spreads: dict[str, float]
    unreachable: set[str]


#: (row name, (larger, smaller) SKU indexes, band, census share) of one order row.
OrderRow = tuple[str, tuple[np.ndarray, np.ndarray], tuple[float, float], float]


@dataclass
class TypeBuild:
    """One type's SKUs in one build, as the arrays a candidate is scored on."""

    rest: np.ndarray
    log_key: np.ndarray
    log_length: np.ndarray
    tier: np.ndarray
    material: np.ndarray
    z_group: np.ndarray
    z_sku: np.ndarray
    z_size: np.ndarray
    order_rows: list[OrderRow]
    #: The sampled (spec, brand) groups the brand-spread row reads: every
    #: member's SKU index, laid out group after group and spec after spec,
    #: each group's start and size, and each spec's first group.
    members: np.ndarray
    group_of: np.ndarray
    starts: np.ndarray
    sizes: np.ndarray
    spec_starts: np.ndarray


def type_build(type_key: str, collected: Collected, recorded: dict[str, Recorded]) -> TypeBuild:
    """``type_key``'s arrays in the build ``collected`` and ``recorded`` read."""
    census = price.CENSUS[type_key]
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

    def pair_index(pairs) -> tuple[np.ndarray, np.ndarray]:
        return (
            np.array([index[a] for a, _ in pairs], dtype=int),
            np.array([index[b] for _, b in pairs], dtype=int),
        )

    order_rows: list[OrderRow] = [
        (
            ORDER_ROW.format(type_key),
            pair_index(collected.pairs.get(type_key, [])),
            share_band(census.larger_costs_more, census.n_pairs),
            census.larger_costs_more,
        )
    ]
    length = price.LENGTH_CENSUS.get(type_key)
    if length is not None:
        order_rows.append(
            (
                LENGTH_ROW.format(type_key),
                pair_index(collected.length_pairs.get(type_key, [])),
                share_band(length.longer_costs_more, length.n_pairs),
                length.longer_costs_more,
            )
        )

    members: list[int] = []
    group_of: list[int] = []
    starts: list[int] = []
    sizes: list[int] = []
    spec_starts: list[int] = []
    figure = price.BRAND_CENSUS.get(type_key)
    if figure is not None:
        for spec, by_brand in collected.specs.items():
            if spec[0] != type_key or len(by_brand) < 2:
                continue
            spec_starts.append(len(starts))
            for name in sampled_brands(spec, by_brand, brand_sample(figure)):
                starts.append(len(members))
                sizes.append(len(by_brand[name]))
                group_of += [len(starts) - 1] * len(by_brand[name])
                members += [index[s] for s in by_brand[name]]
    return TypeBuild(
        rest,
        log_key,
        log_length,
        np.array([r.tier for r in rec]),
        np.array([r.material for r in rec]),
        _z(np.array([r.draw.group_u for r in rec])),
        _z(np.array([r.draw.sku_u for r in rec])),
        _z(np.array([r.draw.size_u for r in rec])),
        order_rows,
        np.array(members, dtype=int),
        np.array(group_of, dtype=int),
        np.array(starts, dtype=int),
        np.array(sizes, dtype=int),
        np.array(spec_starts, dtype=int),
    )


def _share(lp: np.ndarray, pairs) -> float:
    larger, smaller = pairs
    return float(np.mean(lp[larger] > lp[smaller])) if len(larger) else 0.0


def _share_in_sku(base: np.ndarray, z_sku: np.ndarray, pairs):
    """The share of ``pairs`` a larger size wins as a function of the SKU
    sigma, where the log price is ``base + sigma * z_sku`` (no ladder): each
    pair's difference is linear in the sigma, so the share at any sigma is two
    binary searches over the pairs' crossing points rather than a pass over
    every pair. The 100K build's pairs number in the hundreds of thousands,
    and the SKU sigma is solved at every candidate group sigma."""
    larger, smaller = pairs
    a = base[larger] - base[smaller]
    b = z_sku[larger] - z_sku[smaller]
    n = len(a)
    with np.errstate(divide="ignore", invalid="ignore"):
        cross = -a / b
    rising = np.sort(cross[b > 0])
    falling = np.sort(cross[b < 0])
    flat = int(np.sum((b == 0) & (a > 0)))

    def share(sigma: float) -> float:
        wins = np.searchsorted(rising, sigma, side="left")
        wins += len(falling) - np.searchsorted(falling, sigma, side="right")
        return float(wins + flat) / n if n else 0.0

    return share


def _p90_p10(values: np.ndarray) -> float:
    return float(np.exp(np.quantile(values, 0.9) - np.quantile(values, 0.1)))


def _brand_spread(lp: np.ndarray, b: TypeBuild) -> float:
    """The median over specs of the sampled brands' max/min median price."""
    values = lp[b.members]
    ordered = values[np.lexsort((values, b.group_of))]
    medians = np.exp(
        (ordered[b.starts + (b.sizes - 1) // 2] + ordered[b.starts + b.sizes // 2]) / 2
    )
    high = np.maximum.reduceat(medians, b.spec_starts)
    low = np.minimum.reduceat(medians, b.spec_starts)
    return float(np.median(high / low))


def fit_type(type_key: str, builds: list[TypeBuild]) -> TypeFit:
    """``type_key``'s fitted model figures (see the module docstring)."""
    census = price.CENSUS[type_key]
    length = price.LENGTH_CENSUS.get(type_key)
    brand = price.BRAND_CENSUS.get(type_key)
    target_spread = census.p90 / census.p10
    spread_row = SPREAD_ROW.format(type_key)
    p50_row = P50_ROW.format(type_key)
    spread_band = (target_spread * SPREAD_BAND[0], target_spread * SPREAD_BAND[1])
    # The anchor sits midway between the builds' medians, so each is half
    # their distance from the census p50, in logs.
    p50_half = min(math.log(P50_BAND[1]), -math.log(P50_BAND[0]))
    laddered = type_key in price.EQUAL_PRICE_TYPES
    contents = type_key in price.CONTENTS_PRICED
    sized = type_key in price.SIZE_NOISE

    def log_p(
        b: TypeBuild, slope: float, ls: float, group: float, sku: float, step: float, size: float
    ) -> np.ndarray:
        lp = b.rest + slope * b.log_key + ls * b.log_length + group * b.z_group + sku * b.z_sku
        lp = lp + size * b.z_size
        return np.round(lp / step) * step if step else lp

    def sku_for(slope: float, ls: float, group: float, step: float, size: float) -> float:
        # A row's pairs are a sample: however loud the noise, the share of
        # them a larger size wins cannot fall below what the draws' signs
        # give. Where that floor is above the census share, the row aims a
        # quarter of its half-band above the floor.
        aims = []
        for b in builds:
            base = log_p(b, slope, ls, group, 0.0, 0.0, size)
            for _, pairs, band, target in b.order_rows:
                if not len(pairs[0]):
                    continue
                if step:

                    def at(s: float, b=b, pairs=pairs) -> float:
                        return _share(log_p(b, slope, ls, group, s, step, size), pairs)

                else:
                    at = _share_in_sku(base, b.z_sku, pairs)
                half = (band[1] - band[0]) / 2
                floor = at(MAX_SIGMA)
                aims.append((at, half, floor + half / 4 if floor >= target else target))
        if not aims:
            return 0.0

        def miss(sku: float) -> float:
            return max(abs(at(sku) - aim) / half for at, half, aim in aims)

        return _argmin(miss, 0.0, MAX_SIGMA)

    def alone(b: TypeBuild, slope: float, ls: float) -> float:
        return _p90_p10(slope * b.log_key + ls * b.log_length)

    slope, ls = price.model_slope(type_key), length.slope if length else 0.0
    wide = max(builds, key=lambda b: alone(b, slope, ls))
    widest = alone(wide, slope, ls)
    if widest > target_spread and type_key not in price.SLOPE_CUTS:
        sys.exit(
            f"{type_key}: the census slopes alone spread the shown price {widest:.2f}x, wider "
            f"than the census p90/p10 {target_spread:.2f}x, and price.SLOPE_CUTS records no "
            "reason to lower them"
        )
    if type_key in price.SLOPE_CUTS:
        if widest <= target_spread:
            sys.exit(
                f"{type_key}: price.SLOPE_CUTS lowers its slope, but the census slopes alone "
                f"spread only {widest:.2f}x, inside the census p90/p10 {target_spread:.2f}x"
            )

        def spread(s: float, lsk: float) -> float:
            return _p90_p10(log_p(wide, s, lsk, 0.0, sku_for(s, lsk, 0.0, 0.0, 0.0), 0.0, 0.0))

        factor = _bisect(
            lambda k: spread(slope * k, ls * k), target_spread, 0.0, 1.0, increasing=True
        )
        slope, ls = slope * factor, ls * factor

    # Each row's least miss over every noise the fit scores: above 1.0, no
    # noise the fit scanned brings that row into band.
    least: dict[str, float] = {}

    def objective(group: float, size: float, step: float, sku: float | None = None) -> float:
        """The worst miss, in half-bands, over both builds and the rows the
        noise is fitted to: p50, p90/p10 and brand spread, and, where the
        SKU noise is fitted beside it (``sku`` given), the order rows. A
        pinned row is scored, for the "cannot reach" flag, but not fitted to."""
        joint = sku is not None
        if sku is None:
            sku = sku_for(slope, ls, group, step, size)
        lps = [log_p(b, slope, ls, group, sku, step, size) for b in builds]
        medians = [float(np.median(lp)) for lp in lps]
        misses = {p50_row: (max(medians) - min(medians)) / 2 / p50_half}

        def worst(name: str, m: float) -> None:
            misses[name] = max(misses.get(name, 0.0), m)

        for b, lp in zip(builds, lps, strict=True):
            worst(spread_row, _miss(_p90_p10(lp), target_spread, spread_band, ratio=True))
            if brand is not None and len(b.spec_starts):
                worst(
                    BRAND_ROW.format(type_key),
                    _miss(
                        _brand_spread(lp, b),
                        brand.spread_p50,
                        brand_spread_band(brand),
                        ratio=True,
                    ),
                )
            if joint:
                for name, pairs, band, target in b.order_rows:
                    worst(name, _miss(_share(lp, pairs), target, band, ratio=False))
                if laddered:
                    pairs = b.order_rows[0][1]
                    worst(
                        EQUAL_ROW.format(type_key),
                        _miss(
                            float(np.mean(lp[pairs[0]] == lp[pairs[1]])),
                            census.equal_price,
                            equal_band(census),
                            ratio=False,
                        ),
                    )
        for name, m in misses.items():
            least[name] = min(least.get(name, math.inf), m)
        fitted = [m for name, m in misses.items() if name not in price.PINNED_SHORTFALLS]
        return max(fitted) if fitted else 0.0

    def equal_miss(step: float, group: float, size: float, sku: float | None) -> float:
        if sku is None:
            sku = sku_for(slope, ls, group, step, size)
        misses = []
        for b in builds:
            lp = log_p(b, slope, ls, group, sku, step, size)
            pairs = b.order_rows[0][1]
            misses.append(abs(float(np.mean(lp[pairs[0]] == lp[pairs[1]])) - census.equal_price))
        return max(misses)

    # Where a size noise is fitted, it and the SKU noise both invert size
    # pairs, but only the SKU noise spreads one spec's brands: the three
    # sigmas are fitted together, the order rows scored in band rather than
    # solved for exactly. A ladder's step and the noise move each other's
    # figures, so a laddered type fits the step at the noise it has, then the
    # noise at that step, twice over.
    group = size = step = 0.0
    fixed_sku: float | None = 0.0 if sized else None
    for _ in range(2 if laddered else 1):
        if laddered:
            step = _argmin(
                lambda st, g=group, z=size, k=fixed_sku: equal_miss(st, g, z, k), 0.01, 0.6
            )
        if sized:
            group, size, fixed_sku = _argmin_grid(
                lambda g, z, k, st=step: objective(g, z, st, k), MAX_SIGMA / 3, 3
            )
        elif not contents:
            group = _argmin(lambda g, st=step: objective(g, 0.0, st), 0.0, MAX_SIGMA)
    sku = sku_for(slope, ls, group, step, size) if fixed_sku is None else fixed_sku
    lps = [log_p(b, slope, ls, group, sku, step, size) for b in builds]
    anchor = census.p50 / float(np.exp(np.mean([np.median(lp) for lp in lps])))

    unreachable = {name for name, m in least.items() if m > 1.0}
    for b in builds:
        for name, pairs, band, _ in b.order_rows:
            # The share a row's pairs give runs from no SKU noise to MAX_SIGMA.
            loud = _share(log_p(b, slope, ls, group, MAX_SIGMA, step, size), pairs)
            quiet = _share(log_p(b, slope, ls, group, 0.0, step, size), pairs)
            outside = min(loud, quiet) > band[1] or max(loud, quiet) < band[0]
            if len(pairs[0]) and outside and least.get(name, math.inf) > 1.0:
                unreachable.add(name)

    # Each term's spread alone, at the default build; "all" at each build.
    b = builds[0]
    pack = b.rest - b.tier - b.material
    spreads = {
        "key": _p90_p10(slope * b.log_key),
        "length": _p90_p10(ls * b.log_length),
        "tier": _p90_p10(b.tier),
        "material": _p90_p10(b.material),
        "pack": _p90_p10(pack),
        "group": _p90_p10(group * b.z_group),
        "sku": _p90_p10(sku * b.z_sku),
        "size": _p90_p10(size * b.z_size),
        **{f"all {name}": _p90_p10(lp) for name, lp in zip(BUILDS, lps, strict=True)},
        "census": target_spread,
    }
    return TypeFit(anchor, slope, ls, group, sku, step, size, spreads, unreachable)


def _literal(type_key: str, model: price.PriceModel) -> str:
    args = [
        f"{model.anchor:.4g}",
        repr(model.anchor_key),
        f"{model.group_sigma:.3f}",
        f"{model.sku_sigma:.3f}",
    ]
    if model.slope != price.model_slope(type_key):
        args.append(f"slope={model.slope!r}")
    length = price.LENGTH_CENSUS.get(type_key)
    if length is not None and model.length_slope != length.slope:
        args.append(f"length_slope={model.length_slope!r}")
    if model.price_step:
        args.append(f"price_step={model.price_step!r}")
    if model.size_sigma:
        args.append(f"size_sigma={model.size_sigma!r}")
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


def _shown_prices(
    collected: Collected, recorded: dict[str, Recorded], fitted: dict[str, price.PriceModel]
) -> dict[str, float]:
    """Every scored SKU's shown price under the ``fitted`` literals, endings and all."""
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
    return prices


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--write", action="store_true", help="write the literals into the source")
    args = parser.parse_args()

    made = {}
    for name, config in BUILDS.items():
        catalog, recorded = record_draws(config)
        made[name] = (collect(catalog), recorded)
    fitted: dict[str, price.PriceModel] = {}
    columns = ("key", "length", "tier", "material", "pack", "group", "sku", "size")
    columns += tuple(f"all {name}" for name in BUILDS) + ("census",)
    print(f"{'p90/p10 of each term alone':<26}" + "".join(f"{k:>12}" for k in columns))
    unreachable: set[str] = set()
    for type_key in price.CENSUS:
        fit = fit_type(
            type_key,
            [type_build(type_key, collected, recorded) for collected, recorded in made.values()],
        )
        unreachable |= fit.unreachable
        print(f"{type_key:<26}" + "".join(f"{v:>12.2f}" for v in fit.spreads.values()))
        fitted[type_key] = replace(
            price.MODELS[type_key],
            anchor=float(f"{fit.anchor:.4g}"),
            slope=round(fit.slope, 3),
            length_slope=round(fit.length_slope, 3),
            group_sigma=round(fit.group, 3),
            sku_sigma=round(fit.sku, 3),
            price_step=round(fit.step, 3),
            size_sigma=round(fit.size, 3),
        )
    for type_key, reason in price.SLOPE_CUTS.items():
        print(f"slope cut, {type_key}: {fitted[type_key].slope} ({reason})")

    # Score the rounded literals on shown prices at each build. A row out of
    # band needs a recorded cause, and a recorded cause a row still out on
    # its side and no further out than recorded: the fit stops on either, at
    # either build, before it writes.
    by_build = {}
    for name, (collected, rec) in made.items():
        rows = price_rows(collected, _shown_prices(collected, rec, fitted))
        by_build[name] = {row.name: row for row in rows}
    unpinned: set[str] = set()
    stale: set[str] = set()
    print(f"{'':<62}{'target':>10}" + "".join(f"{name:>10}" for name in BUILDS))
    for row_name in next(iter(by_build.values())):
        rows = [by_build[name][row_name] for name in BUILDS]
        flags = []
        for build, (name, row) in enumerate(zip(BUILDS, rows, strict=True)):
            if row.name in price.PINNED_SHORTFALLS:
                if not pin_holds(row, build):
                    stale.add(row.name)
                    flags.append(f"pin does not hold at {name}")
            elif not row.within:
                unpinned.add(row.name)
                flags.append(f"OUT at {name}")
        recorded = price.PINNED_FIGURES.get(row_name)
        if recorded is not None:
            built = tuple(round(row.achieved, recorded_digits(row_name)) for row in rows)
            if built != recorded:
                flags.append(f"re-record {built}")
        if row_name in unreachable:
            flags.append("cannot reach")
        if row_name in price.PINNED_SHORTFALLS:
            flags.append("pinned shortfall")
        print(
            f"{row_name:<62}{rows[0].target:>10.4f}"
            + "".join(f"{row.achieved:>10.4f}" for row in rows)
            + f"  {', '.join(flags) or 'ok'}"
        )

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
        + (f"\n    size_sigma={socket.size_sigma!r}," if socket.size_sigma else "")
    )
    print("\n# price.py, between the fit markers:\n" + table)
    print("\n# screw_socket_head.py, between its fit markers:\n" + socket_body)
    if unpinned or stale:
        for name in sorted(unpinned):
            print(f"OUT of band and not pinned: {name}", file=sys.stderr)
        for name in sorted(stale):
            print(
                f"pinned in price.PINNED_SHORTFALLS but does not hold (in band, on the other "
                f"side, or further out than price.PINNED_FIGURES): {name}",
                file=sys.stderr,
            )
        return 1
    if args.write:
        _between_markers(PRICE_PY, "", table)
        _between_markers(SOCKET_PY, " screw_socket_head", socket_body)
    return 0


if __name__ == "__main__":
    sys.exit(main())
