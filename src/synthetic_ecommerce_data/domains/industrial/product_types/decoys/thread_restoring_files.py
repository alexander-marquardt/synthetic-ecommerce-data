"""Hex Head Bolt Thread Restoring File: a text-match decoy for the industrial seed queries (#462).

A file that restores a damaged hex head bolt thread, 7/16-14. Its title holds the seed noun and its
category path does not, so it shows what a category policy removes (the seeds it serves are in
``domains/industrial/seed_decoys.py``).
"""

from __future__ import annotations

from synthetic_ecommerce_data.core.typespec import TypeSpec
from synthetic_ecommerce_data.domains.industrial.breadth import BreadthRow

SPEC = TypeSpec(
    "thread_restoring_files",
    label="Hex Head Bolt Thread Restoring File",
    breadth=BreadthRow(
        key="thread_restoring_files",
        category=("Hand Tools", "Files & Rasps", "Thread Restoring Files"),
        family="hand_tool",
        shape="bracket",
        item="Hex Head Bolt Thread Restoring File",
        descriptor_attr=None,
        size_attr="Thread Size",
        size_values=("7/16-14", "1/2-13", "3/8-16"),
        attributes={"Material": ("Carbon Steel",)},
        price_range=(8.0, 30.0),
        skus=2,
        featured_sizes=("7/16-14",),
        reason=(
            "decoy for the industrial seed queries (#462): a file that restores a damaged hex "
            "head bolt thread, 7/16-14"
        ),
    ),
)
