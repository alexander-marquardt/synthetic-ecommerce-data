"""Hex Head Bolt Thread Chaser: a text-match decoy for the industrial seed queries (#462).

A chaser that cleans the thread of a 7/16-14 hex head bolt. Its title holds the seed noun and its
category path does not, so it shows what a category policy removes (the seeds it serves are in
``domains/industrial/seed_decoys.py``).
"""

from __future__ import annotations

from synthetic_ecommerce_data.core.typespec import TypeSpec
from synthetic_ecommerce_data.domains.industrial.breadth import BreadthRow

SPEC = TypeSpec(
    "thread_chasers",
    label="Hex Head Bolt Thread Chaser",
    breadth=BreadthRow(
        key="thread_chasers",
        category=("Threading", "Thread Repair", "Thread Chasers"),
        family="cutting_tool",
        shape="cylinder",
        item="Hex Head Bolt Thread Chaser",
        descriptor_attr=None,
        size_attr="Thread Size",
        size_values=("7/16-14", "1/2-13", "3/8-16"),
        attributes={"Material": ("High Speed Steel",), "Finish": ("Bright",)},
        price_range=(10.0, 40.0),
        skus=2,
        featured_sizes=("7/16-14",),
        reason=(
            "decoy for the industrial seed queries (#462): a chaser that cleans the thread of a "
            "7/16-14 hex head bolt"
        ),
    ),
)
