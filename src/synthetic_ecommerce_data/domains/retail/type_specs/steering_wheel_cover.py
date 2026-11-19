"""Steering wheel covers (gen#970, slice 3):
faux leather, microfiber suede, silicone and sport grip; a color times a rim size is the SKU.

Rows and decoys: ``automotive_interior_rows``. Drawing: ``kit_automotive_interior``. Every brand
is invented.
"""

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.automotive_interior_rows import (
    DECOY_ROWS,
    INTERIOR_OWNERS,
    STEERING_WHEEL_COVERS,
)
from synthetic_ecommerce_data.domains.retail.type_registry import Decoy, TypeSpec

SPEC = TypeSpec(
    key="steering_wheel_cover",
    department="Automotive",
    product_type="Steering Wheel Cover",
    owners=INTERIOR_OWNERS,
    rows=STEERING_WHEEL_COVERS,
    decoys=tuple(Decoy(c, q, p, r) for c, q, p, r in DECOY_ROWS["steering_wheel_cover"]),
)
