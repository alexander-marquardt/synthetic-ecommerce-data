"""Ball Bearing Swivel Caster: a text-match decoy for the industrial seed queries (#462).

A swivel caster on ball bearings, 100 mm. Its title holds the seed noun and its category path does
not, so it shows what a category policy removes (the seeds it serves are in
``domains/industrial/seed_decoys.py``).
"""

from __future__ import annotations

from synthetic_ecommerce_data.core.typespec import TypeSpec
from synthetic_ecommerce_data.domains.industrial.breadth import BreadthRow

SPEC = TypeSpec(
    "swivel_casters",
    label="Ball Bearing Swivel Caster",
    breadth=BreadthRow(
        key="swivel_casters",
        category=("Material Handling & Storage", "Casters & Wheels", "Swivel Casters"),
        family="hand_tool",
        shape="disc",
        item="Ball Bearing Swivel Caster",
        descriptor_attr=None,
        size_attr="Diameter",
        size_values=("75 mm", "100 mm", "125 mm"),
        attributes={"Material": ("Steel",), "Finish": ("Zinc Plated",)},
        price_range=(10.0, 40.0),
        skus=2,
        featured_sizes=("100 mm",),
        reason=(
            "decoy for the industrial seed queries (#462): a swivel caster on ball bearings, 100 mm"
        ),
    ),
)
