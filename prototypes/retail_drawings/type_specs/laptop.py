"""Laptops (gen#332): clamshell, two-in-one, gaming, workstation; RAM, storage, screen per SKU.

Rows: ``electronics_rows``. Drawing: ``kit_electronics``. Only Apple is a real brand name.
"""

from __future__ import annotations

from electronics_rows import ELECTRONICS_OWNERS, LAPTOPS
from type_registry import Option, TypeSpec

SPEC = TypeSpec(
    key="laptop",
    department="Electronics",
    product_type="Laptop",
    owners=ELECTRONICS_OWNERS,
    options=(
        Option("storage_gb", "storage_capacity", "Storage (GB)"),
        Option("ram_gb", "ram", "Memory (GB)"),
        Option("screen_size_in", "screen_size", "Screen size", "INH"),
    ),
    rows=LAPTOPS,
)
