"""Monitors (gen#332): standard, ultrawide and curved, a screen size per SKU.

Rows: ``electronics_rows``. Drawing: ``kit_electronics``. Only Apple is a real brand name.
"""

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.electronics_rows import ELECTRONICS_OWNERS, MONITORS
from synthetic_ecommerce_data.domains.retail.type_registry import Option, TypeSpec

SPEC = TypeSpec(
    key="monitor",
    department="Electronics",
    product_type="Monitor",
    owners=ELECTRONICS_OWNERS,
    options=(Option("screen_size_in", "screen_size", "Screen size", "INH"),),
    rows=MONITORS,
)
