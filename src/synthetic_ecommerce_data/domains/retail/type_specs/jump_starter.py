"""Jump starters (gen#970, slice 2):
Lithium packs and jump boxes, one style per peak current; each style is one SKU.

Rows and decoys: ``automotive_fluids_rows``. Drawing: ``kit_automotive_electrics``, slice 1's
``fluid_jug`` or the electronics kit's ``charger``. Every brand is invented.
"""

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.automotive_fluids_rows import (
    DECOY_ROWS,
    ELECTRICS_OWNERS,
    JUMP_STARTERS,
)
from synthetic_ecommerce_data.domains.retail.type_registry import Decoy, TypeSpec

SPEC = TypeSpec(
    key="jump_starter",
    department="Automotive",
    product_type="Jump Starter",
    owners=ELECTRICS_OWNERS,
    rows=JUMP_STARTERS,
    decoys=tuple(Decoy(c, q, p, r) for c, q, p, r in DECOY_ROWS["jump_starter"]),
)
