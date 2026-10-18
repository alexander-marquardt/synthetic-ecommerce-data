"""Boleros (gen#211): boleros, shrugs and capes, drawn by :mod:`kit_outerwear`.

The styles are written in :mod:`outerwear_rows` (the eleven outerwear types share their palette,
brands and helpers); this spec registers the type and reads its rows back. Templates only
(``derivable`` False), so the seeded derivation is what it was.
"""

from __future__ import annotations

import outerwear_rows
from type_registry import ApparelPlan, TypeSpec

PRODUCT_TYPE = "Bolero"

SPEC = TypeSpec(
    key="bolero",
    department="Clothing",
    product_type=PRODUCT_TYPE,
    owners=outerwear_rows.owners_of(PRODUCT_TYPE),
    rows=outerwear_rows.rows_of(PRODUCT_TYPE),
    apparel=ApparelPlan(
        compounds=(
            ("cardigan", "Cardigan Bolero"),
            ("blazer", "Blazer Bolero"),
            ("denim", "Denim Bolero"),
        )
    ),
)
