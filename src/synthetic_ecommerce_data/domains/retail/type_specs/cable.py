"""Cables (gen#332): USB-C, micro and multi-tip cables, a length per SKU.

Rows: ``electronics_rows`` and ``phone_range_rows`` (gen#1117). Drawing: ``kit_electronics``.
"""

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail import phone_range_rows
from synthetic_ecommerce_data.domains.retail.electronics_rows import CABLES, ELECTRONICS_OWNERS
from synthetic_ecommerce_data.domains.retail.type_registry import Home, Option, TypeSpec

SPEC = TypeSpec(
    key="cable",
    department="Electronics",
    product_type="Cable",
    owners=ELECTRONICS_OWNERS,
    options=(Option("length_m", "item_length", "Item length", "MTR"),),
    rows=CABLES + phone_range_rows.CABLES_NEW,
    homes=(Home("decoy_product_words", False),),
)
