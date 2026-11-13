"""Car air fresheners (gen#970):
A hanging card, a vent clip or a gel can in seven scents; the pack is the SKU.

Rows and decoys: ``automotive_rows``. Drawing: ``kit_automotive`` or the kit's own bottle shapes.
Every brand is invented.
"""

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.automotive_rows import (
    AIR_FRESHENERS,
    AUTOMOTIVE_OWNERS,
    DECOY_ROWS,
)
from synthetic_ecommerce_data.domains.retail.type_registry import Decoy, TypeSpec

SPEC = TypeSpec(
    key="car_air_freshener",
    department="Automotive",
    product_type="Car Air Freshener",
    owners=AUTOMOTIVE_OWNERS,
    rows=AIR_FRESHENERS,
    decoys=tuple(Decoy(c, q, p, r) for c, q, p, r in DECOY_ROWS["car_air_freshener"]),
)
