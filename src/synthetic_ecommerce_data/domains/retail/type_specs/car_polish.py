"""Car polish (gen#970):
A compound, a scratch remover and a headlight restorer; the size is the SKU.

Rows and decoys: ``automotive_rows``. Drawing: ``kit_automotive`` or the kit's own bottle shapes.
Every brand is invented.
"""

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.automotive_rows import (
    AUTOMOTIVE_OWNERS,
    CAR_POLISHES,
    DECOY_ROWS,
)
from synthetic_ecommerce_data.domains.retail.type_registry import Decoy, TypeSpec

SPEC = TypeSpec(
    key="car_polish",
    department="Automotive",
    product_type="Car Polish",
    owners=AUTOMOTIVE_OWNERS,
    rows=CAR_POLISHES,
    decoys=tuple(Decoy(c, q, p, r) for c, q, p, r in DECOY_ROWS["car_polish"]),
)
