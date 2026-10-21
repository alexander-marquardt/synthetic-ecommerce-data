"""Tablets (gen#332): four iPads and eight invented tablets, with storage tiers.

Rows: ``electronics_rows``. Drawing: ``kit_electronics``. Only Apple is a real brand name.
"""

from __future__ import annotations

from electronics_rows import ELECTRONICS_OWNERS, TABLETS
from type_registry import Option, TypeSpec

SPEC = TypeSpec(
    key="tablet",
    department="Electronics",
    product_type="Tablet",
    owners=ELECTRONICS_OWNERS,
    options=(Option("storage_gb", "storage_capacity", "Storage (GB)"),),
    rows=TABLETS,
)
