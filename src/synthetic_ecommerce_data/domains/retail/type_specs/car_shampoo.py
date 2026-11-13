"""Car shampoo (gen#970): a brand's formula is the product, the bottle size in ml is the SKU.

Rows and decoys: ``automotive_rows``. Drawing: ``kit_automotive`` or the kit's own bottle shapes.
Every brand is invented.
"""

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.automotive_rows import (
    AUTOMOTIVE_OWNERS,
    CAR_SHAMPOOS,
    DECOY_ROWS,
)
from synthetic_ecommerce_data.domains.retail.type_registry import Decoy, TypeSpec

SPEC = TypeSpec(
    key="car_shampoo",
    department="Automotive",
    product_type="Car Shampoo",
    owners=AUTOMOTIVE_OWNERS,
    rows=CAR_SHAMPOOS,
    decoys=tuple(Decoy(c, q, p, r) for c, q, p, r in DECOY_ROWS["car_shampoo"]),
)
