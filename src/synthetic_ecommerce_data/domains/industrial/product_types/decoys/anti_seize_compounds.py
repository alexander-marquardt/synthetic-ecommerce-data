"""Anti-Seize Compound for Stainless Steel Hex Bolts: text-match decoy (#462).

A nickel anti-seize paste for stainless bolts. Its title holds the seed noun and its category path
does not, so it shows what a category policy removes (the seeds it serves are in
``domains/industrial/seed_decoys.py``).
"""

from __future__ import annotations

from synthetic_ecommerce_data.core.typespec import TypeSpec
from synthetic_ecommerce_data.domains.industrial.breadth import BreadthRow

SPEC = TypeSpec(
    "anti_seize_compounds",
    label="Anti-Seize Compound for Stainless Steel Hex Bolts",
    breadth=BreadthRow(
        key="anti_seize_compounds",
        category=(
            "Lubricants, Coolants & Fluids",
            "Anti-Seize & Thread Compounds",
            "Anti-Seize Compounds",
        ),
        family="hand_tool",
        shape="tube",
        item="Anti-Seize Compound for Stainless Steel Hex Bolts",
        descriptor_attr=None,
        size_attr="Container Size",
        size_values=("4 oz", "8 oz", "16 oz"),
        attributes={"Material": ("Nickel",)},
        price_range=(8.0, 36.0),
        skus=2,
        featured_sizes=(),
        reason=(
            "decoy for the industrial seed queries (#462): a nickel anti-seize paste for "
            "stainless bolts"
        ),
    ),
)
