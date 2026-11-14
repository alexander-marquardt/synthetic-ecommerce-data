"""Windshield washer fluid (gen#970): four blends in a jug; the jug size is the SKU.

Rows and decoys: ``automotive_rows``. Drawing: ``kit_automotive`` or the kit's own bottle shapes.
Every brand is invented.
"""

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.automotive_rows import (
    AUTOMOTIVE_OWNERS,
    DECOY_ROWS,
    WASHER_FLUIDS,
)
from synthetic_ecommerce_data.domains.retail.type_registry import Decoy, TypeSpec

SPEC = TypeSpec(
    key="washer_fluid",
    department="Automotive",
    product_type="Windshield Washer Fluid",
    owners=AUTOMOTIVE_OWNERS,
    rows=WASHER_FLUIDS,
    decoys=tuple(Decoy(c, q, p, r) for c, q, p, r in DECOY_ROWS["washer_fluid"]),
)
