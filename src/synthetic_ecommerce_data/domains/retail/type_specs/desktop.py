"""Desktop computers (gen#332): towers, all-in-ones and minis; RAM and storage ride on each SKU.

Rows: ``electronics_rows``. Drawing: ``kit_electronics``. Only Apple is a real brand name.
"""

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.electronics_rows import DESKTOPS, ELECTRONICS_OWNERS
from synthetic_ecommerce_data.domains.retail.type_registry import Option, TypeSpec

SPEC = TypeSpec(
    key="desktop",
    department="Electronics",
    product_type="Desktop Computer",
    owners=ELECTRONICS_OWNERS,
    options=(
        Option("storage_gb", "storage_capacity", "Storage (GB)"),
        Option("ram_gb", "ram", "Memory (GB)"),
    ),
    rows=DESKTOPS,
)
