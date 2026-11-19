"""Car chargers (gen#970, slice 2):
USB-A and USB-C chargers for the 12 V socket; single or a 2 pack is the SKU.

Rows and decoys: ``automotive_fluids_rows``. Drawing: ``kit_automotive_electrics``, slice 1's
``fluid_jug`` or the electronics kit's ``charger``. Every brand is invented.
"""

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.automotive_fluids_rows import (
    CAR_CHARGERS,
    DECOY_ROWS,
    ELECTRICS_OWNERS,
)
from synthetic_ecommerce_data.domains.retail.type_registry import Decoy, TypeSpec

SPEC = TypeSpec(
    key="car_charger",
    department="Automotive",
    product_type="Car Charger",
    owners=ELECTRICS_OWNERS,
    rows=CAR_CHARGERS,
    decoys=tuple(Decoy(c, q, p, r) for c, q, p, r in DECOY_ROWS["car_charger"]),
)
