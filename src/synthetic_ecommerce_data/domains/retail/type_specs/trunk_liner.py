"""Trunk liners (gen#970, slice 3):
a rubber tray, a waterproof fabric liner and one with a bumper flap; a color times a vehicle
size is the SKU.

Rows and decoys: ``automotive_interior_rows``. Drawing: ``kit_automotive_interior``. Every brand
is invented.
"""

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.automotive_interior_rows import (
    DECOY_ROWS,
    INTERIOR_OWNERS,
    TRUNK_LINERS,
)
from synthetic_ecommerce_data.domains.retail.type_registry import Decoy, TypeSpec

SPEC = TypeSpec(
    key="trunk_liner",
    department="Automotive",
    product_type="Trunk Liner",
    owners=INTERIOR_OWNERS,
    rows=TRUNK_LINERS,
    decoys=tuple(Decoy(c, q, p, r) for c, q, p, r in DECOY_ROWS["trunk_liner"]),
)
