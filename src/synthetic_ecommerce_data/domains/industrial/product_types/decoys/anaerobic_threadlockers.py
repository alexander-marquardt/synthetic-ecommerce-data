"""Threadlocker for M6x1 Set Screws: a text-match decoy for the industrial seed queries (#462).

A threadlocker that keeps an M6x1 set screw from backing out. Its title holds the seed noun and its
category path does not, so it shows what a category policy removes (the seeds it serves are in
``domains/industrial/seed_decoys.py``).
"""

from __future__ import annotations

from synthetic_ecommerce_data.core.typespec import TypeSpec
from synthetic_ecommerce_data.domains.industrial.breadth import BreadthRow

SPEC = TypeSpec(
    "anaerobic_threadlockers",
    label="Threadlocker for M6x1 Set Screws",
    breadth=BreadthRow(
        key="anaerobic_threadlockers",
        category=("Tapes & Adhesives", "Threadlockers", "Anaerobic Threadlockers"),
        family="hand_tool",
        shape="tube",
        item="Threadlocker for M6x1 Set Screws",
        descriptor_attr=None,
        size_attr="Container Size",
        size_values=("10 ml", "50 ml"),
        attributes={"Material": ("Methacrylate Resin",)},
        price_range=(7.0, 28.0),
        skus=2,
        featured_sizes=(),
        reason=(
            "decoy for the industrial seed queries (#462): a threadlocker that keeps an M6x1 set "
            "screw from backing out"
        ),
    ),
)
