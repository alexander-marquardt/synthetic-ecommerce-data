"""Print every price row of the default build, the per-family tier order,
the within-product order per type and each brand-spread type's fixed-order
share (#52, #58). Read-only: it builds the catalog and scores it.

    uv run python scripts/measure_price_rows.py
"""

import itertools
import statistics
from collections import defaultdict

from synthetic_ecommerce_data.core import brands, price
from synthetic_ecommerce_data.core.config import GeneratorConfig
from synthetic_ecommerce_data.domains.industrial.generate import generate
from synthetic_ecommerce_data.domains.industrial.price_report import collect, price_rows, tier_order

cat = generate(GeneratorConfig())
col = collect(cat)
prices = {c.sku: c.price_usd for _, c in cat.all_skus()}
for r in price_rows(col, prices):
    flag = "ok" if r.within else "OUT"
    print(
        f"{r.name:<62}{r.target:>9.4f}{r.achieved:>9.4f}{r.denominator:>7} "
        f"{r.band[0]:.4f}-{r.band[1]:.4f} {flag}"
    )
print("tier order (economy/standard, premium/standard):", tier_order(col, prices))

print("within-product: type, pairs, inverted %, >=2x %")
for t, pairs in sorted(col.product_pairs.items()):
    n = len(pairs)
    inv = sum(prices[s] > prices[b] for b, s, _ in pairs)
    twice = sum(prices[s] >= 2 * prices[b] for b, s, _ in pairs)
    print(f"  {t:<24}{n:>6}{100 * inv / n:>7.1f}{100 * twice / n:>7.1f}")

print("brand pairs whose order is fixed on every shared spec")
for t in sorted(price.BRAND_CENSUS):
    per_brand: dict[str, dict] = defaultdict(dict)
    for (st, k, m), by in col.specs.items():
        if st == t:
            for b, sk in by.items():
                per_brand[b][(k, m)] = statistics.median(prices[s] for s in sk)
    fixed = tot = 0
    for a, b in itertools.combinations(per_brand, 2):
        shared = set(per_brand[a]) & set(per_brand[b])
        if len(shared) >= 2:
            tot += 1
            fixed += len({per_brand[a][s] > per_brand[b][s] for s in shared}) == 1
    tiers = sorted({brands.tier_of(b, t) for b in per_brand})
    print(f"  {t:<24} fixed {fixed}/{tot}  tiers {tiers}")
