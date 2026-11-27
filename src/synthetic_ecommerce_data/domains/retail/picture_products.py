"""The wands-inspired products: a build source of the step-2 products (gen#1093).

One product of our own for each picture of the WANDS persona's pinned manifest whose type the
book describes (:mod:`synthetic_ecommerce_data.picture_products.shipped`), 13,373 of them over
the 28 drawn types. Each type's spec names this source as a home that the scaled build does not
derive from, so the products ship as written and no derived style copies them.
"""

from __future__ import annotations

from synthetic_ecommerce_data.picture_products import shipped


def docs() -> list[dict]:
    """The step-2 product documents, fresh each call."""
    return shipped.docs()


def ids() -> frozenset[str]:
    """Their product ids."""
    return shipped.ids()
