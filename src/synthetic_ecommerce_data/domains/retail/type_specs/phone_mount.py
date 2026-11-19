"""Phone mounts (gen#970, slice 2):
Vent, dashboard, windshield, cup holder and CD slot mounts; single or a 2 pack is the SKU.

Rows and decoys: ``automotive_fluids_rows``. Drawing: ``kit_automotive_electrics``, slice 1's
``fluid_jug`` or the electronics kit's ``charger``. Every brand is invented.
"""

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.automotive_fluids_rows import (
    DECOY_ROWS,
    ELECTRICS_OWNERS,
    PHONE_MOUNTS,
)
from synthetic_ecommerce_data.domains.retail.type_registry import Decoy, TypeSpec

SPEC = TypeSpec(
    key="phone_mount",
    department="Automotive",
    product_type="Phone Mount",
    owners=ELECTRICS_OWNERS,
    rows=PHONE_MOUNTS,
    decoys=tuple(Decoy(c, q, p, r) for c, q, p, r in DECOY_ROWS["phone_mount"]),
)
