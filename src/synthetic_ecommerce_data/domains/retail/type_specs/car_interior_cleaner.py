"""Car interior cleaner (gen#970): a trigger spray per surface; the size is the SKU.

Rows and decoys: ``automotive_rows``. Drawing: ``kit_automotive`` or the kit's own bottle shapes.
Every brand is invented.
"""

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.automotive_rows import (
    AUTOMOTIVE_OWNERS,
    DECOY_ROWS,
    INTERIOR_CLEANERS,
)
from synthetic_ecommerce_data.domains.retail.type_registry import Decoy, TypeSpec

SPEC = TypeSpec(
    key="car_interior_cleaner",
    department="Automotive",
    product_type="Car Interior Cleaner",
    owners=AUTOMOTIVE_OWNERS,
    rows=INTERIOR_CLEANERS,
    decoys=tuple(Decoy(c, q, p, r) for c, q, p, r in DECOY_ROWS["car_interior_cleaner"]),
)
