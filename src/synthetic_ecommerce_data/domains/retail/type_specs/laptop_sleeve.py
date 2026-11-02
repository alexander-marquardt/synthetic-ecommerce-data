"""Laptop sleeves (gen#332), a screen size per SKU.

Rows: ``electronics_rows``. Drawing: ``kit_electronics``.
"""

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.electronics_rows import (
    ELECTRONICS_OWNERS,
    LAPTOP_SLEEVES,
)
from synthetic_ecommerce_data.domains.retail.type_registry import Home, Option, TypeSpec

SPEC = TypeSpec(
    key="laptop_sleeve",
    department="Electronics",
    product_type="Laptop Sleeve",
    owners=ELECTRONICS_OWNERS,
    options=(Option("screen_size_in", "screen_size", "Screen size", "INH"),),
    rows=LAPTOP_SLEEVES,
    # the class-8 sleeve with a memory card pocket (DY7961, gen#796)
    homes=(Home("decoy_product_words", False),),
)
