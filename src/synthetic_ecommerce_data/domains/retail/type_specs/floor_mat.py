"""Floor mats (gen#970, slice 3):
all-weather and trim-to-fit rubber, deep dish liners, carpet and premium carpet; a color times a
front pair or a 4-piece set is the SKU.

Rows and decoys: ``automotive_interior_rows``. Drawing: ``kit_automotive_interior``. Every brand
is invented.
"""

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.automotive_interior_rows import (
    DECOY_ROWS,
    FLOOR_MATS,
    INTERIOR_OWNERS,
)
from synthetic_ecommerce_data.domains.retail.type_registry import Decoy, TypeSpec

SPEC = TypeSpec(
    key="floor_mat",
    department="Automotive",
    product_type="Floor Mat",
    owners=INTERIOR_OWNERS,
    rows=FLOOR_MATS,
    decoys=tuple(Decoy(c, q, p, r) for c, q, p, r in DECOY_ROWS["floor_mat"]),
)
