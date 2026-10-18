"""Shackets (gen#211): shackets and overshirts, drawn by :mod:`kit_outerwear`.

The styles are written in :mod:`outerwear_rows` (the eleven outerwear types share their palette,
brands and helpers); this spec registers the type and reads its rows back. Templates only
(``derivable`` False), so the seeded derivation is what it was.
"""

from __future__ import annotations

import outerwear_rows
from type_registry import ApparelPlan, TypeSpec

PRODUCT_TYPE = "Shacket"

SPEC = TypeSpec(
    key="shacket",
    department="Clothing",
    product_type=PRODUCT_TYPE,
    owners=outerwear_rows.owners_of(PRODUCT_TYPE),
    rows=outerwear_rows.rows_of(PRODUCT_TYPE),
    apparel=ApparelPlan(
        compounds=(
            ("cardigan", "Cardigan Shacket"),
            ("bomber", "Bomber Shacket"),
            ("blazer", "Blazer Shacket"),
        )
    ),
)
