"""O-Ring Pick Set: a text-match decoy for the industrial seed queries (#462).

A pick set that lifts an O-ring from its groove. Its title holds the seed noun and its category path does not, so it
shows what a category policy removes (the seeds it serves are in
``domains/industrial/seed_decoys.py``).
"""

from __future__ import annotations

from synthetic_ecommerce_data.core.typespec import TypeSpec
from synthetic_ecommerce_data.domains.industrial.breadth import BreadthRow

SPEC = TypeSpec(
    "seal_pick_sets",
    label="O-Ring Pick Set",
    breadth=BreadthRow(
        key="seal_pick_sets",
        category=("Hand Tools", "Picks & Hooks", "Seal Pick Sets"),
        family="hand_tool",
        shape="cylinder",
        item="O-Ring Pick Set",
        descriptor_attr=None,
        size_attr="Number of Pieces",
        size_values=("4", "5"),
        attributes={"Material": ("Nylon",)},
        price_range=(5.0, 20.0),
        skus=2,
        featured_sizes=(),
        reason="decoy for the industrial seed queries (#462): a pick set that lifts an O-ring from its groove",
    ),
)
