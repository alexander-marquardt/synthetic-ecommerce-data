"""Sun shades (gen#970, slice 3):
accordion, reflective bubble, twist-fold, umbrella and side window shades; colorless, a size or
a pack is the SKU.

Rows and decoys: ``automotive_interior_rows``. Drawing: ``kit_automotive_interior``. Every brand
is invented.
"""

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.automotive_interior_rows import (
    DECOY_ROWS,
    INTERIOR_OWNERS,
    SUN_SHADES,
)
from synthetic_ecommerce_data.domains.retail.type_registry import Decoy, Option, TypeSpec

SPEC = TypeSpec(
    key="sun_shade",
    department="Automotive",
    product_type="Sun Shade",
    owners=INTERIOR_OWNERS,
    rows=SUN_SHADES,
    decoys=tuple(Decoy(c, q, p, r) for c, q, p, r in DECOY_ROWS["sun_shade"]),
    options=(Option("vehicle_fit", "vehicle_fit", "Vehicle fit", None),),
)
