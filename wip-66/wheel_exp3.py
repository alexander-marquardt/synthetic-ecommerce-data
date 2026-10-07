"""How often a brand-shared kind noise lands every wheel row in band, over
many draws of the kind stream. argv: kind attribute names (comma list), n."""

import random
import sys
from statistics import NormalDist

import numpy as np

sys.path.insert(0, "/tmp/wt-gen66/scripts")
import fit_price_model as f  # noqa: E402

from synthetic_industrial_products.catalog import price  # noqa: E402
from synthetic_industrial_products.catalog.generate import Generator  # noqa: E402
from synthetic_industrial_products.catalog.price_report import (  # noqa: E402
    P50_BAND,
    SPREAD_BAND,
    brand_spread_band,
    share_band,
)

T = "wheel_depressed_center"
kind = [n for n in sys.argv[1].split(",") if n]
n = int(sys.argv[2])
price.PINNED_SHORTFALLS.pop(f"price brand spread, same spec (median max/min): {T}", None)
price.SIZE_NOISE[T] = "experiment"
kinds: dict[str, tuple] = {}
base = Generator._price_draw


def patched(self, type_key, brand, attributes, line_attributes, sku, sku_u):
    draw = base(self, type_key, brand, attributes, line_attributes, sku, sku_u)
    if type_key == T:
        facts = {a.name: a.value for a in attributes}
        kinds[sku] = tuple(facts.get(k, "") for k in kind)
    return draw


Generator._price_draw = patched
builds, skus = [], []
for name, config in f.BUILDS.items():
    catalog, rec = f.record_draws(config)
    col = f.collect(catalog)
    builds.append(f.type_build(T, col, rec))
    skus.append([s for s, t in col.type_of.items() if t == T])
census = price.CENSUS[T]
target = census.p90 / census.p10
bband = brand_spread_band(price.BRAND_CENSUS[T])
oband = share_band(census.larger_costs_more, census.n_pairs)
levels = sorted({kinds[s] for s in skus[0]})
ok = 0
for salt in range(n):
    rng = random.Random(f"salt{salt}")
    z = {k: NormalDist().inv_cdf(rng.random()) for k in levels}
    for b, ss in zip(builds, skus, strict=True):
        b.z_size = np.array([z[kinds[s]] for s in ss])
    fit = f.fit_type(T, builds)
    good = True
    rows = []
    for b in builds:
        x = b.rest + fit.slope * b.log_key + fit.group * b.z_group + fit.sku * b.z_sku
        x = x + fit.size * b.z_size
        sp, p9, od = f._brand_spread(x, b), f._p90_p10(x), f._share(x, b.order_rows[0][1])
        p50 = float(np.exp(np.median(x))) * fit.anchor
        good &= bband[0] <= sp <= bband[1]
        good &= target * SPREAD_BAND[0] <= p9 <= target * SPREAD_BAND[1]
        good &= oband[0] <= od <= oband[1]
        good &= census.p50 * P50_BAND[0] <= p50 <= census.p50 * P50_BAND[1]
        rows.append(f"{sp:.2f}/{p9:.1f}/{od:.3f}/{p50:.1f}")
    ok += good
    print(salt, "IN " if good else "out", f"g={fit.group:.2f} k={fit.size:.2f} s={fit.sku:.2f}", *rows)
print(f"kind={kind}: {ok} of {n} kind streams land every wheel row in band at both builds")
