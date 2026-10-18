"""Counterbore for M12x1.75 Socket Cap Screws: a text-match decoy for the industrial seed queries (#462).

A counterbore that sinks the head of an M12x1.75 socket cap screw. Its title holds the seed noun and its category path does not, so it
shows what a category policy removes (the seeds it serves are in
``domains/industrial/seed_decoys.py``).
"""

from __future__ import annotations

from synthetic_ecommerce_data.core.typespec import TypeSpec
from synthetic_ecommerce_data.domains.industrial.breadth import BreadthRow

SPEC = TypeSpec(
    "piloted_counterbores",
    label="Counterbore for M12x1.75 Socket Cap Screws",
    breadth=BreadthRow(
        key="piloted_counterbores",
        category=("Holemaking", "Counterbores & Countersinks", "Piloted Counterbores"),
        family="cutting_tool",
        shape="cylinder",
        item="Counterbore for M12x1.75 Socket Cap Screws",
        descriptor_attr=None,
        size_attr="Diameter",
        size_values=("20 mm", "22 mm"),
        attributes={"Material": ("High-Speed Steel",), "Finish": ("Bright",)},
        price_range=(22.0, 85.0),
        skus=2,
        featured_sizes=(),
        reason="decoy for the industrial seed queries (#462): a counterbore that sinks the head of an M12x1.75 socket cap screw",
    ),
)
