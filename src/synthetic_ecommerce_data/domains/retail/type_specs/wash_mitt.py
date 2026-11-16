"""Wash mitts (gen#970):
Chenille microfiber in the six main colors, and natural lambswool; the color is the SKU.

Rows and decoys: ``automotive_rows``. Drawing: ``kit_automotive`` or the kit's own bottle shapes.
Every brand is invented.
"""

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.automotive_rows import (
    AUTOMOTIVE_OWNERS,
    DECOY_ROWS,
    WASH_MITTS,
)
from synthetic_ecommerce_data.domains.retail.type_registry import Decoy, TypeSpec

SPEC = TypeSpec(
    key="wash_mitt",
    department="Automotive",
    product_type="Wash Mitt",
    owners=AUTOMOTIVE_OWNERS,
    rows=WASH_MITTS,
    decoys=tuple(Decoy(c, q, p, r) for c, q, p, r in DECOY_ROWS["wash_mitt"]),
)
