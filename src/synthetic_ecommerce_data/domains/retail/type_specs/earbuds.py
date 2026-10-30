"""Earbuds and headphones (gen#332).

Rows: ``electronics_rows``. Drawing: ``kit_electronics``.
"""

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.electronics_rows import EARBUDS, ELECTRONICS_OWNERS
from synthetic_ecommerce_data.domains.retail.type_registry import TypeSpec

SPEC = TypeSpec(
    key="earbuds",
    department="Electronics",
    product_type="Earbuds",
    owners=ELECTRONICS_OWNERS,
    rows=EARBUDS,
)
