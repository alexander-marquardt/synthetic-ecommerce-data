"""Bar Stock Cutting Blade: a text-match decoy for the industrial seed queries (#462).

A bi-metal band saw blade that cuts bar stock. Its title holds the seed noun and its category path
does not, so it shows what a category policy removes (the seeds it serves are in
``domains/industrial/seed_decoys.py``).
"""

from __future__ import annotations

from synthetic_ecommerce_data.core.typespec import TypeSpec
from synthetic_ecommerce_data.domains.industrial.breadth import BreadthRow

SPEC = TypeSpec(
    "band_saw_blades",
    label="Bar Stock Cutting Blade",
    breadth=BreadthRow(
        key="band_saw_blades",
        category=("Saw Blades", "Band Saw Blades", "Bi-Metal Band Saw Blades"),
        family="cutting_tool",
        shape="disc",
        item="Bar Stock Cutting Blade",
        descriptor_attr=None,
        size_attr="Length",
        size_values=("64-1/2 in", "93 in"),
        attributes={"Material": ("Bi-Metal",)},
        price_range=(14.0, 60.0),
        skus=2,
        featured_sizes=(),
        reason=(
            "decoy for the industrial seed queries (#462): a bi-metal band saw blade that cuts "
            "bar stock"
        ),
    ),
)
