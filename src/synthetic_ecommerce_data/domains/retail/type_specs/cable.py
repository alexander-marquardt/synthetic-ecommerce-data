"""Cables (gen#332): USB-C, micro and multi-tip cables, a length per SKU.

Rows: ``electronics_rows``. Drawing: ``kit_electronics``. Only Apple is a real brand name.
"""

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.electronics_rows import CABLES, ELECTRONICS_OWNERS
from synthetic_ecommerce_data.domains.retail.type_registry import Option, TypeSpec

SPEC = TypeSpec(
    key="cable",
    department="Electronics",
    product_type="Cable",
    owners=ELECTRONICS_OWNERS,
    options=(Option("length_m", "item_length", "Item length", "MTR"),),
    rows=CABLES,
)
