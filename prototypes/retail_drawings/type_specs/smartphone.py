"""Smartphones (gen#332): 26 styles, Apple and seven invented brands, with storage tiers.

Rows: ``electronics_rows``. Drawing: ``kit_electronics``. Only Apple is a real brand name.
"""

from __future__ import annotations

from electronics_rows import ELECTRONICS_OWNERS, SMARTPHONES
from type_registry import Option, TypeSpec

SPEC = TypeSpec(
    key="smartphone",
    department="Electronics",
    product_type="Smartphone",
    owners=ELECTRONICS_OWNERS,
    options=(Option("storage_gb", "storage_capacity", "Storage (GB)"),),
    rows=SMARTPHONES,
)
