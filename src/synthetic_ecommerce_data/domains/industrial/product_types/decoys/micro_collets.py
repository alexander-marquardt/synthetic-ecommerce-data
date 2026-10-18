"""ER11 Collet for End Mill: a text-match decoy for the industrial seed queries (#462).

An ER11 collet that grips a 2.5 mm end mill. Its title holds the seed noun and its category path
does not, so it shows what a category policy removes (the seeds it serves are in
``domains/industrial/seed_decoys.py``).
"""

from __future__ import annotations

from synthetic_ecommerce_data.core.typespec import TypeSpec
from synthetic_ecommerce_data.domains.industrial.breadth import BreadthRow

SPEC = TypeSpec(
    "micro_collets",
    label="ER11 Collet for End Mill",
    breadth=BreadthRow(
        key="micro_collets",
        category=("Tool Holding", "Collets", "Micro Collets"),
        family="cutting_tool",
        shape="cylinder",
        item="ER11 Collet for End Mill",
        descriptor_attr=None,
        size_attr="Size",
        size_values=("2.5 mm", "3 mm"),
        attributes={"Material": ("Alloy Steel",)},
        price_range=(7.0, 28.0),
        skus=2,
        featured_sizes=("2.5 mm",),
        reason=(
            "decoy for the industrial seed queries (#462): an ER11 collet that grips a 2.5 mm end "
            "mill"
        ),
    ),
)
