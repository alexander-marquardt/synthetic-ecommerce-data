"""Tablets (gen#332): twelve tablets of invented brands, with storage tiers.

Rows: ``electronics_rows``. Drawing: ``kit_electronics``.
"""

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.electronics_rows import ELECTRONICS_OWNERS, TABLETS
from synthetic_ecommerce_data.domains.retail.type_registry import Option, TypeSpec

SPEC = TypeSpec(
    key="tablet",
    department="Electronics",
    product_type="Tablet",
    owners=ELECTRONICS_OWNERS,
    options=(Option("storage_gb", "storage_capacity", "Storage (GB)"),),
    rows=TABLETS,
)
