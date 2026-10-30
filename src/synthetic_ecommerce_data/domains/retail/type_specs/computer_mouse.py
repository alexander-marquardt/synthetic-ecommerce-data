"""Computer mice (gen#332): wireless, gaming and ergonomic.

Rows: ``electronics_rows``. Drawing: ``kit_electronics``.
"""

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.electronics_rows import ELECTRONICS_OWNERS, MICE
from synthetic_ecommerce_data.domains.retail.type_registry import TypeSpec

SPEC = TypeSpec(
    key="computer_mouse",
    department="Electronics",
    product_type="Computer Mouse",
    owners=ELECTRONICS_OWNERS,
    rows=MICE,
)
