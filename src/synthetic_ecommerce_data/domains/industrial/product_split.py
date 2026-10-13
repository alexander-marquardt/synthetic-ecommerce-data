"""What a product is held to (gen#63): its SKUs agree on every product-constant attribute,
and the SKU count per product follows ``variants_per_product``.

The declaration is :func:`.vocab.product_constant_names` (a type's ``line``-scope vocabulary
and the measurement system). This module reads it back from a built catalog."""

from __future__ import annotations

from collections import Counter
from statistics import median
from typing import Any

from synthetic_ecommerce_data.core.config import GeneratorConfig
from synthetic_ecommerce_data.core.model import Catalog, ProductLine
from synthetic_ecommerce_data.domains.industrial.vocab import product_constant_names


def disagreements(line: ProductLine, catalog: Catalog) -> list[str]:
    """The product-constant attribute names this product's SKUs do not all agree on.

    A SKU that lacks the attribute while a sibling states it disagrees too."""
    constant = product_constant_names(line.type_key)
    seen: dict[str, set[tuple[str, ...]]] = {}
    for child in line.children:
        merged: dict[str, set[str]] = {}
        for a in catalog.merged_attributes(line, child):
            if a.name in constant:
                merged.setdefault(a.name, set()).update(a.values or (a.value,))
        for name in constant:
            seen.setdefault(name, set()).add(tuple(sorted(merged.get(name, ()))))
    return sorted(name for name, versions in seen.items() if len(versions) > 1)


def split_products(catalog: Catalog) -> dict[str, list[str]]:
    """Product id -> the product-constant names its SKUs disagree on (disagreeing only)."""
    out = {}
    for line in catalog.lines:
        names = disagreements(line, catalog)
        if names:
            out[line.product_id] = names
    return out


def skus_per_product(catalog: Catalog) -> dict[str, dict[str, Any]]:
    """Per type: its product count, the median and maximum SKUs per product, and the
    histogram (SKU count -> products)."""
    counts: dict[str, list[int]] = {}
    for line in catalog.lines:
        counts.setdefault(line.type_key, []).append(len(line.children))
    return {
        key: {
            "products": len(sizes),
            "median": median(sizes),
            "max": max(sizes),
            "histogram": dict(sorted(Counter(sizes).items())),
        }
        for key, sizes in sorted(counts.items())
    }


#: A median over fewer products than this says nothing about a distribution: the breadth
#: types hold one fixed product each, sized by their own row, not drawn from the knob.
MEDIAN_MIN_PRODUCTS = 20


def distribution_problems(
    distribution: dict[str, dict[str, Any]], config: GeneratorConfig
) -> list[str]:
    """Types whose SKUs per product leave what ``variants_per_product`` allows.

    The knob caps a product at its largest count. A type's median may sit at most at the
    count where the knob's cumulative weight reaches 75%: a product never offers more
    variants than its pool has, which only lowers a count, so the median of a type
    that draws the knob cannot pass it. The median is checked for types of at least
    :data:`MEDIAN_MIN_PRODUCTS` products; the maximum for all."""
    table = sorted(config.variants_per_product)
    ceiling = table[-1][0]
    total = sum(weight for _, weight in table)
    running = 0.0
    median_ceiling = ceiling
    for count, weight in table:
        running += weight / total
        if running >= 0.75:
            median_ceiling = count
            break
    problems = []
    for key, row in distribution.items():
        if row["max"] > ceiling:
            problems.append(
                f"{key}: a product has {row['max']} SKUs, the knob's maximum is {ceiling}"
            )
        if row["products"] >= MEDIAN_MIN_PRODUCTS and row["median"] > median_ceiling:
            problems.append(
                f"{key}: median {row['median']} SKUs per product, the knob allows {median_ceiling}"
            )
    return problems
