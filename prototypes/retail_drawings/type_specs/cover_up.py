"""Cover-Up (gen#212): sold in the Swimwear node of its audience. :mod:`kit_swimwear` draws it
(its own shape, the variant axes as params); the styles are templates only (``derivable`` False),
so the seeded derivation is what it was. The rows are in :mod:`swimwear_rows`.
"""

from __future__ import annotations

import swimwear_rows
from type_registry import ApparelPlan, TypeSpec

SPEC = TypeSpec(
    key="cover_up",
    department="Clothing",
    product_type="Cover-Up",
    owners=swimwear_rows.OWNED,
    apparel=ApparelPlan(
        compounds=(
            ("kimono", "Kimono Cover-Up"),
            ("shirt", "Shirt Cover-Up"),
            ("tunic", "Tunic Cover-Up"),
            ("dress", "Dress Cover-Up"),
        )
    ),
    rows=swimwear_rows.COVER_ROWS,
)
