"""Seat covers (gen#970, slice 3):
neoprene, faux leather, mesh, canvas, faux sheepskin, a rear bench and a pet hammock; a color
times a set is the SKU.

Rows and decoys: ``automotive_interior_rows``. Drawing: ``kit_automotive_interior``. Every brand
is invented.
"""

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.automotive_interior_rows import (
    DECOY_ROWS,
    INTERIOR_OWNERS,
    SEAT_COVERS,
)
from synthetic_ecommerce_data.domains.retail.type_registry import Decoy, TypeSpec

SPEC = TypeSpec(
    key="seat_cover",
    department="Automotive",
    product_type="Seat Cover",
    owners=INTERIOR_OWNERS,
    rows=SEAT_COVERS,
    decoys=tuple(Decoy(c, q, p, r) for c, q, p, r in DECOY_ROWS["seat_cover"]),
)
