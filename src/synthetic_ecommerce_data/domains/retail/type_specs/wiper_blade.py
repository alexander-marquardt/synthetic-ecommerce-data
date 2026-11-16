"""Wiper blades (gen#970):
Conventional, beam, hybrid, rear and winter blades; the blade length in inches is the SKU.

Rows and decoys: ``automotive_rows``. Drawing: ``kit_automotive`` or the kit's own bottle shapes.
Every brand is invented.
"""

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.automotive_rows import (
    AUTOMOTIVE_OWNERS,
    DECOY_ROWS,
    WIPER_BLADES,
)
from synthetic_ecommerce_data.domains.retail.type_registry import Decoy, Option, TypeSpec

SPEC = TypeSpec(
    key="wiper_blade",
    department="Automotive",
    product_type="Wiper Blade",
    owners=AUTOMOTIVE_OWNERS,
    options=(Option("blade_length_in", "blade_length", "Blade length", "INH"),),
    rows=WIPER_BLADES,
    decoys=tuple(Decoy(c, q, p, r) for c, q, p, r in DECOY_ROWS["wiper_blade"]),
)
