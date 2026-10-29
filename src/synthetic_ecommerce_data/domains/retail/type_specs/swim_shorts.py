"""Swim Shorts (gen#212): sold in the Swimwear node of its audience. :mod:`kit_swimwear` draws it
(its own shape, the variant axes as params); the styles are templates only (``derivable`` False),
so the seeded derivation is what it was. The rows are in :mod:`swimwear_rows`.
"""

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail import swimwear_rows
from synthetic_ecommerce_data.domains.retail.type_registry import ApparelPlan, Home, TypeSpec

SPEC = TypeSpec(
    key="swim_shorts",
    homes=(Home("decoy_product_words", False),),
    department="Clothing",
    product_type="Swim Shorts",
    owners=swimwear_rows.OWNED,
    apparel=ApparelPlan(
        compounds=(
            ("cargo", "Cargo Swim Shorts"),
            ("chino", "Chino Swim Shorts"),
            ("tailored", "Tailored Swim Shorts"),
        )
    ),
    rows=swimwear_rows.SHORTS_ROWS,
)
