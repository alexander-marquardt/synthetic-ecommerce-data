"""Tire inflators (gen#970, slice 2):
Plug-in, cordless, dual power and battery clamp inflators; each style is one SKU.

Rows and decoys: ``automotive_fluids_rows``. Drawing: ``kit_automotive_electrics``, slice 1's
``fluid_jug`` or the electronics kit's ``charger``. Every brand is invented.
"""

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.automotive_fluids_rows import (
    DECOY_ROWS,
    ELECTRICS_OWNERS,
    TIRE_INFLATORS,
)
from synthetic_ecommerce_data.domains.retail.type_registry import Decoy, TypeSpec

SPEC = TypeSpec(
    key="tire_inflator",
    department="Automotive",
    product_type="Tire Inflator",
    owners=ELECTRICS_OWNERS,
    rows=TIRE_INFLATORS,
    decoys=tuple(Decoy(c, q, p, r) for c, q, p, r in DECOY_ROWS["tire_inflator"]),
)
