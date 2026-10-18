"""Ball Bearing Drawer Slides: a text-match decoy for the industrial seed queries (#462).

Ball bearing drawer slides for a tool cabinet. Its title holds the seed noun and its category path
does not, so it shows what a category policy removes (the seeds it serves are in
``domains/industrial/seed_decoys.py``).
"""

from __future__ import annotations

from synthetic_ecommerce_data.core.typespec import TypeSpec
from synthetic_ecommerce_data.domains.industrial.breadth import BreadthRow

SPEC = TypeSpec(
    "drawer_slides",
    label="Ball Bearing Drawer Slides",
    breadth=BreadthRow(
        key="drawer_slides",
        category=("Material Handling & Storage", "Cabinet Hardware", "Drawer Slides"),
        family="hand_tool",
        shape="bracket",
        item="Ball Bearing Drawer Slides",
        descriptor_attr=None,
        size_attr="Length",
        size_values=("450 mm", "600 mm"),
        attributes={"Material": ("Steel",), "Finish": ("Zinc Plated",)},
        price_range=(14.0, 48.0),
        skus=2,
        featured_sizes=("450 mm",),
        reason=(
            "decoy for the industrial seed queries (#462): ball bearing drawer slides for a tool "
            "cabinet"
        ),
    ),
)
