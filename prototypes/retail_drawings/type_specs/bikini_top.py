"""Bikini Top (gen#212): sold in the Swimwear node of its audience. :mod:`kit_swimwear` draws it
(its own shape, the variant axes as params); the styles are templates only (``derivable`` False),
so the seeded derivation is what it was. The rows are in :mod:`swimwear_rows`.
"""

from __future__ import annotations

import swimwear_rows
from type_registry import ApparelPlan, TypeSpec

SPEC = TypeSpec(
    key="bikini_top",
    department="Clothing",
    product_type="Bikini Top",
    owners=swimwear_rows.OWNED,
    apparel=ApparelPlan(
        compounds=(
            ("bralette", "Bralette Bikini Top"),
            ("crop", "Crop Bikini Top"),
            ("sports bra", "Sports Bra Bikini Top"),
        )
    ),
    rows=swimwear_rows.TOP_ROWS,
)
