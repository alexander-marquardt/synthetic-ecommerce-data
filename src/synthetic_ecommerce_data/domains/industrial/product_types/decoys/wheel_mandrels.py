"""Cut-Off Wheel Mandrel: a text-match decoy for the industrial seed queries (#462).

A mandrel that mounts a cut-off wheel on a rotary tool. Its title holds the seed noun and its category path does not, so it
shows what a category policy removes (the seeds it serves are in
``domains/industrial/seed_decoys.py``).
"""

from __future__ import annotations

from synthetic_ecommerce_data.core.typespec import TypeSpec
from synthetic_ecommerce_data.domains.industrial.breadth import BreadthRow

SPEC = TypeSpec(
    "wheel_mandrels",
    label="Cut-Off Wheel Mandrel",
    breadth=BreadthRow(
        key="wheel_mandrels",
        category=("Abrasives", "Grinding & Cut-Off", "Wheel Mandrels"),
        family="abrasive",
        shape="cylinder",
        item="Cut-Off Wheel Mandrel",
        descriptor_attr=None,
        size_attr="Shank Diameter",
        size_values=("1/4 in", "1/8 in"),
        attributes={"Material": ("Steel",)},
        price_range=(3.0, 12.0),
        skus=2,
        featured_sizes=("1/4 in",),
        reason="decoy for the industrial seed queries (#462): a mandrel that mounts a cut-off wheel on a rotary tool",
    ),
)
