"""Swim Bottoms (gen#212, plain since gen#780): sold in the Womens Bikini Bottoms leaf.

These were period swim bottoms in a ``Period Swimwear`` leaf, sold on an absorbency gusset; a
demo should not show them, so they are plain swim bottoms sold by cut (bikini or high-waisted).
:mod:`kit_swimwear` draws them (the outline and waistband they had, without the gusset layers);
the styles are templates only (``derivable`` False), so the seeded derivation is what it was. The
rows are in :mod:`swimwear_rows`.
"""

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail import details, swimwear_rows
from synthetic_ecommerce_data.domains.retail.type_registry import ApparelPlan, TypeSpec

details.register_parts("swim_bottoms", {"waistband": details.WAIST})

SPEC = TypeSpec(
    key="swim_bottoms",
    department="Clothing",
    product_type="Swim Bottoms",
    owners=swimwear_rows.OWNED,
    apparel=ApparelPlan(
        compounds=(
            ("skirt", "Skirted Swim Bottoms"),
            ("short", "Boy Short Swim Bottoms"),
            ("brief", "Brief Swim Bottoms"),
        )
    ),
    rows=swimwear_rows.SWIM_BOTTOM_ROWS,
)
