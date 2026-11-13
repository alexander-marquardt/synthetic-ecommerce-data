"""Microfiber towels (gen#970):
Drying towels, all-purpose and glass cloths; the color and the size or pack are the SKU.

Rows and decoys: ``automotive_rows``. Drawing: ``kit_automotive`` or the kit's own bottle shapes.
Every brand is invented.
"""

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.automotive_rows import (
    AUTOMOTIVE_OWNERS,
    DECOY_ROWS,
    MICROFIBER_TOWELS,
)
from synthetic_ecommerce_data.domains.retail.type_registry import Decoy, TypeSpec

SPEC = TypeSpec(
    key="microfiber_towel",
    department="Automotive",
    product_type="Microfiber Towel",
    owners=AUTOMOTIVE_OWNERS,
    rows=MICROFIBER_TOWELS,
    decoys=tuple(Decoy(c, q, p, r) for c, q, p, r in DECOY_ROWS["microfiber_towel"]),
)
