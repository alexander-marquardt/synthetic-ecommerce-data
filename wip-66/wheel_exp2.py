"""Kind noise (brand-free, keyed on line attributes) beside the per-brand group
noise, fitted on the size axis; spec holds extra attributes.

argv: kind attribute names (comma list) ; spec-extra attribute names (comma list)
"""

import random
import sys
from collections import defaultdict
from dataclasses import replace

sys.path.insert(0, "/tmp/wt-gen66/scripts")
import fit_price_model as f  # noqa: E402

from synthetic_industrial_products.catalog import price  # noqa: E402
from synthetic_industrial_products.catalog.generate import Generator  # noqa: E402
from synthetic_industrial_products.catalog.price_report import brand_spread_band  # noqa: E402

T = "wheel_depressed_center"
kind = [n for n in sys.argv[1].split(",") if n]
extra = [n for n in sys.argv[2].split(",") if n]

base = Generator._price_draw


def patched(self, type_key, brand, attributes, line_attributes, sku, sku_u):
    draw = base(self, type_key, brand, attributes, line_attributes, sku, sku_u)
    if type_key != T or not kind:
        return draw
    facts = {a.name: a.value for a in attributes}
    if kind == ["factor"]:
        lf = FACTORS["abr"][facts["Abrasive Material"]]
        lf += FACTORS["app"][facts["Application"]]
        lf += FACTORS["hub"][facts["Connector Type"]]
        lf += FACTORS["type"][facts["Type"]]
        # size_u is read through the normal quantile: store the quantile
        # whose z is the log factor.
        from statistics import NormalDist

        return replace(draw, size_u=NormalDist().cdf(lf))
    k = tuple(facts.get(n, "") for n in kind)
    u = random.Random(f"{self.config.seed}:price-kind:{type_key}:{k}").random()
    return replace(draw, size_u=u)


import math  # noqa: E402

FACTORS = {
    "abr": {
        "Aluminum Oxide": 0.0,
        "Silicon Carbide": math.log(1.1),
        "Zirconia Alumina": math.log(1.6),
        "Ceramic": math.log(2.5),
    },
    "app": {"Cutting & Grinding": 0.0, "Grinding": math.log(1.3)},
    "hub": {"Arbor": 0.0, "5/8-11 Hub": math.log(1.5)},
    "type": {"Type 27": 0.0, "Type 28": math.log(1.1)},
}


Generator._price_draw = patched
price.PINNED_SHORTFALLS.pop("price brand spread, same spec (median max/min): wheel_depressed_center", None)
if kind:
    price.SIZE_NOISE[T] = "experiment"
builds = []
for name, config in f.BUILDS.items():
    catalog, rec = f.record_draws(config)
    col = f.collect(catalog)
    if extra:
        specs = defaultdict(lambda: defaultdict(list))
        for line in catalog.lines:
            if line.type_key != T or line.spec_quality == "fast_and_cheap":
                continue
            for child in line.children:
                attrs = {a.name: a for a in catalog.merged_attributes(line, child)}
                key = price.KEYS[T](attrs)
                spec = (T, round(key, 4), "", *(attrs[n].value if n in attrs else "" for n in extra))
                specs[spec][line.brand].append(child.sku)
        col.specs = specs
    builds.append(f.type_build(T, col, rec))
    print(name, "specs", len(builds[-1].spec_starts))
for b in builds:
    tiers = b.rest + 0 * b.z_group
    eco = 0
    for i, s in enumerate(b.spec_starts):
        end = b.spec_starts[i + 1] if i + 1 < len(b.spec_starts) else len(b.starts)
        firsts = b.members[b.starts[s:end]]
        eco += bool((b.tier[firsts] < -0.3).any())
    print(f"  tiers-only spread={f._brand_spread(tiers, b):.3f} specs with economy sampled={eco}/{len(b.spec_starts)}")
if "--tiers" in sys.argv:
    sys.exit()
fit = f.fit_type(T, builds)
print(
    "group", round(fit.group, 3), "kind", round(fit.size, 3), "sku", round(fit.sku, 3),
    "unreachable", fit.unreachable,
)
census = price.CENSUS[T]
for b in builds:
    x = b.rest + fit.slope * b.log_key + fit.group * b.z_group + fit.sku * b.z_sku + fit.size * b.z_size
    import numpy as np

    print(
        f"  spread={f._brand_spread(x, b):.3f} band={tuple(round(v, 2) for v in brand_spread_band(price.BRAND_CENSUS[T]))}"
        f" p9010={f._p90_p10(x):.2f} (census {census.p90 / census.p10:.2f})"
        f" order={f._share(x, b.order_rows[0][1]):.3f} (census {census.larger_costs_more})"
        f" p50={np.exp(np.median(x)) * fit.anchor:.2f}"
    )
