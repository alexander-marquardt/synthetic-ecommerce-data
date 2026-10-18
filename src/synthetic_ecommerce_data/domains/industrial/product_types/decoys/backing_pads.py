"""Flap Disc Backing Pad: a text-match decoy for the industrial seed queries (#462).

A backing pad that carries a flap disc on an angle grinder. Its title holds the seed noun and its
category path does not, so it shows what a category policy removes (the seeds it serves are in
``domains/industrial/seed_decoys.py``).
"""

from __future__ import annotations

from synthetic_ecommerce_data.core.typespec import TypeSpec
from synthetic_ecommerce_data.domains.industrial.breadth import BreadthRow

SPEC = TypeSpec(
    "backing_pads",
    label="Flap Disc Backing Pad",
    breadth=BreadthRow(
        key="backing_pads",
        category=("Abrasives", "Sanding & Grinding Accessories", "Backing Pads"),
        family="abrasive",
        shape="disc",
        item="Flap Disc Backing Pad",
        descriptor_attr=None,
        size_attr="Diameter",
        size_values=("4-1/2 in", "5 in"),
        attributes={"Material": ("Fiberglass",)},
        price_range=(6.0, 22.0),
        skus=2,
        featured_sizes=(),
        reason=(
            "decoy for the industrial seed queries (#462): a backing pad that carries a flap disc "
            "on an angle grinder"
        ),
    ),
)
