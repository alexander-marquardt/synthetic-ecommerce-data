"""ER32 Collet for End Mill: a text-match decoy for the industrial seed queries (#462).

An ER32 collet that grips a 1/2 in end mill. Its title holds the seed noun and its category path
does not, so it shows what a category policy removes (the seeds it serves are in
``domains/industrial/seed_decoys.py``).
"""

from __future__ import annotations

from synthetic_ecommerce_data.core.typespec import TypeSpec
from synthetic_ecommerce_data.domains.industrial.breadth import BreadthRow

SPEC = TypeSpec(
    "milling_collets",
    label="ER32 Collet for End Mill",
    breadth=BreadthRow(
        key="milling_collets",
        category=("Tool Holding", "Collets", "Milling Collets"),
        family="cutting_tool",
        shape="cylinder",
        item="ER32 Collet for End Mill",
        descriptor_attr=None,
        size_attr="Size",
        size_values=("1/2 in", "3/8 in"),
        attributes={"Material": ("Alloy Steel",)},
        price_range=(9.0, 36.0),
        skus=2,
        featured_sizes=("1/2 in",),
        reason=(
            "decoy for the industrial seed queries (#462): an ER32 collet that grips a 1/2 in end "
            "mill"
        ),
    ),
)
