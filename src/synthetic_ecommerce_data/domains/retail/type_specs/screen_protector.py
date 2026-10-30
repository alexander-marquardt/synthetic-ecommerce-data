"""Screen protectors (gen#332): glass, matte and privacy sheets for a named phone or tablet.

Rows: ``electronics_rows``. Drawing: ``kit_electronics``.
"""

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.electronics_rows import (
    ELECTRONICS_OWNERS,
    SCREEN_PROTECTORS,
)
from synthetic_ecommerce_data.domains.retail.type_registry import TypeSpec

SPEC = TypeSpec(
    key="screen_protector",
    department="Electronics",
    product_type="Screen Protector",
    owners=ELECTRONICS_OWNERS,
    rows=SCREEN_PROTECTORS,
)
