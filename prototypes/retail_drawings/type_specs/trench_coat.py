"""Trench Coats (gen#211): trench coats, drawn by :mod:`kit_coats`.

The styles are written in :mod:`outerwear_rows` (the eleven outerwear types share their palette,
brands and helpers); this spec registers the type and reads its rows back. Templates only
(``derivable`` False), so the seeded derivation is what it was.
"""

from __future__ import annotations

import outerwear_rows
from type_registry import ApparelPlan, TypeSpec

PRODUCT_TYPE = "Trench Coat"

SPEC = TypeSpec(
    key="trench_coat",
    department="Clothing",
    product_type=PRODUCT_TYPE,
    owners=outerwear_rows.owners_of(PRODUCT_TYPE),
    rows=outerwear_rows.rows_of(PRODUCT_TYPE),
    apparel=ApparelPlan(
        compounds=(
            ("blazer", "Blazer Trench Coat"),
            ("cape", "Cape Trench Coat"),
            ("shirt", "Shirt Trench Coat"),
        )
    ),
)
