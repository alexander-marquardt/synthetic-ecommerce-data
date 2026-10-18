"""Thread Repair Insert Kit for 1/4-20 Screws: text-match decoy for the industrial seeds (#462).

A threaded insert kit that repairs a stripped 1/4-20 screw hole. Its title holds the seed noun and
its category path does not, so it shows what a category policy removes (the seeds it serves are in
``domains/industrial/seed_decoys.py``).
"""

from __future__ import annotations

from synthetic_ecommerce_data.core.typespec import TypeSpec
from synthetic_ecommerce_data.domains.industrial.breadth import BreadthRow

SPEC = TypeSpec(
    "thread_repair_kits",
    label="Thread Repair Insert Kit for 1/4-20 Screws",
    breadth=BreadthRow(
        key="thread_repair_kits",
        category=("Threading", "Thread Repair", "Thread Repair Kits"),
        family="cutting_tool",
        shape="block",
        item="Thread Repair Insert Kit for 1/4-20 Screws",
        descriptor_attr=None,
        size_attr="Thread Size",
        size_values=("1/4-20",),
        attributes={"Material": ("Stainless Steel",)},
        price_range=(24.0, 75.0),
        skus=1,
        featured_sizes=(),
        reason=(
            "decoy for the industrial seed queries (#462): a threaded insert kit that repairs a "
            "stripped 1/4-20 screw hole"
        ),
    ),
)
