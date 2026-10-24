"""E-readers (gen#332): paper-like screens, two storage sizes.

Rows: ``electronics_rows``. Drawing: ``kit_electronics``. Only Apple is a real brand name.
"""

from __future__ import annotations

from electronics_rows import E_READERS, ELECTRONICS_OWNERS
from type_registry import Option, TypeSpec

SPEC = TypeSpec(
    key="e_reader",
    department="Electronics",
    product_type="E-reader",
    owners=ELECTRONICS_OWNERS,
    options=(Option("storage_gb", "storage_capacity", "Storage (GB)"),),
    rows=E_READERS,
)
