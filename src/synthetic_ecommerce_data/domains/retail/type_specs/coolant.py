"""Coolant (gen#970, slice 2):
Seven chemistries, each as a concentrate and a 50/50 premix; the jug size in ml is the SKU.

Rows and decoys: ``automotive_fluids_rows``. Drawing: ``kit_automotive_electrics``, slice 1's
``fluid_jug`` or the electronics kit's ``charger``. Every brand is invented.
"""

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.automotive_fluids_rows import (
    COOLANTS,
    DECOY_ROWS,
    FLUIDS_OWNERS,
)
from synthetic_ecommerce_data.domains.retail.type_registry import Decoy, TypeSpec

SPEC = TypeSpec(
    key="coolant",
    department="Automotive",
    product_type="Coolant",
    owners=FLUIDS_OWNERS,
    rows=COOLANTS,
    decoys=tuple(Decoy(c, q, p, r) for c, q, p, r in DECOY_ROWS["coolant"]),
)
