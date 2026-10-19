"""Parkas (gen#211): parkas, drawn by :mod:`kit_coats`.

The styles are written in :mod:`outerwear_rows` (the eleven outerwear types share their palette,
brands and helpers); this spec registers the type and reads its rows back. Templates only
(``derivable`` False), so the seeded derivation is what it was.
"""

from __future__ import annotations

import outerwear_rows
from type_registry import ApparelPlan, TypeSpec

PRODUCT_TYPE = "Parka"

SPEC = TypeSpec(
    key="parka",
    department="Clothing",
    product_type=PRODUCT_TYPE,
    owners=outerwear_rows.owners_of(PRODUCT_TYPE),
    rows=outerwear_rows.rows_of(PRODUCT_TYPE),
    apparel=ApparelPlan(
        compounds=(
            ("puffer", "Puffer Parka"),
            ("bomber", "Bomber Parka"),
            ("fishtail", "Fishtail Parka"),
        )
    ),
)
