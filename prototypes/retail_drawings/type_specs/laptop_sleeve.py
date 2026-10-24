"""Laptop sleeves (gen#332), a screen size per SKU.

Rows: ``electronics_rows``. Drawing: ``kit_electronics``. Only Apple is a real brand name.
"""

from __future__ import annotations

from electronics_rows import ELECTRONICS_OWNERS, LAPTOP_SLEEVES
from type_registry import Option, TypeSpec

SPEC = TypeSpec(
    key="laptop_sleeve",
    department="Electronics",
    product_type="Laptop Sleeve",
    owners=ELECTRONICS_OWNERS,
    options=(Option("screen_size_in", "screen_size", "Screen size", "INH"),),
    rows=LAPTOP_SLEEVES,
)
