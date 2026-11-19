"""Motor oil (gen#970, slice 2):
Full synthetic, synthetic blend, high mileage and conventional oils in nine viscosity grades;
the jug size in ml is the SKU.

Rows and decoys: ``automotive_fluids_rows``. Drawing: ``kit_automotive_electrics``, slice 1's
``fluid_jug`` or the electronics kit's ``charger``. Every brand is invented.
"""

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.automotive_fluids_rows import (
    DECOY_ROWS,
    FLUIDS_OWNERS,
    MOTOR_OILS,
)
from synthetic_ecommerce_data.domains.retail.type_registry import Decoy, TypeSpec

SPEC = TypeSpec(
    key="motor_oil",
    department="Automotive",
    product_type="Motor Oil",
    owners=FLUIDS_OWNERS,
    rows=MOTOR_OILS,
    decoys=tuple(Decoy(c, q, p, r) for c, q, p, r in DECOY_ROWS["motor_oil"]),
)
