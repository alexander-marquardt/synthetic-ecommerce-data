"""Screw Anchor: a text-match decoy for the industrial seed queries (#462).

A plastic anchor that holds a screw in a wall. Its title holds the seed noun and its category path
does not, so it shows what a category policy removes (the seeds it serves are in
``domains/industrial/seed_decoys.py``).
"""

from __future__ import annotations

from synthetic_ecommerce_data.core.typespec import TypeSpec
from synthetic_ecommerce_data.domains.industrial.breadth import BreadthRow

SPEC = TypeSpec(
    "nylon_wall_anchors",
    label="Screw Anchor",
    use_lines=(
        (
            "Expands in the drilled hole as the screw is driven, so the screw holds in masonry or "
            "drywall."
        ),
        (
            "Push the anchor into a drilled hole and drive a screw into it; the anchor spreads "
            "and grips the wall around the screw."
        ),
    ),
    breadth=BreadthRow(
        key="nylon_wall_anchors",
        category=("Fasteners", "Anchors", "Plastic Wall Anchors"),
        family="fastener",
        shape="cylinder",
        item="Screw Anchor",
        descriptor_attr="Material",
        size_attr="Diameter",
        size_values=("6 mm", "8 mm", "10 mm"),
        attributes={"Material": ("Nylon",), "Units per Pack": ("50", "100")},
        price_range=(3.0, 10.0),
        skus=2,
        featured_sizes=(),
        reason=(
            "decoy for the industrial seed queries (#462): a plastic anchor that holds a screw in "
            "a wall"
        ),
    ),
)
