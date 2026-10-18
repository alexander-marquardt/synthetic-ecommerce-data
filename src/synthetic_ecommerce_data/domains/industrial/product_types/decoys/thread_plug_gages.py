"""Hex Nut Thread Plug Gage: a text-match decoy for the industrial seed queries (#462).

A plug gage that checks the thread of a hex nut. Its title holds the seed noun and its category
path does not, so it shows what a category policy removes (the seeds it serves are in
``domains/industrial/seed_decoys.py``).
"""

from __future__ import annotations

from synthetic_ecommerce_data.core.typespec import TypeSpec
from synthetic_ecommerce_data.domains.industrial.breadth import BreadthRow

SPEC = TypeSpec(
    "thread_plug_gages",
    label="Hex Nut Thread Plug Gage",
    breadth=BreadthRow(
        key="thread_plug_gages",
        category=("Measuring & Inspecting", "Gages", "Thread Plug Gages"),
        family="hand_tool",
        shape="cylinder",
        item="Hex Nut Thread Plug Gage",
        descriptor_attr=None,
        size_attr="Thread Size",
        size_values=("M8", "M10", "M12"),
        attributes={"Material": ("Tool Steel",), "Type": ("Go/No-Go",)},
        price_range=(18.0, 95.0),
        skus=2,
        featured_sizes=(),
        reason=(
            "decoy for the industrial seed queries (#462): a plug gage that checks the thread of "
            "a hex nut"
        ),
    ),
)
