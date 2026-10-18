"""Roller Chain Tensioner: a text-match decoy for the industrial seed queries (#462).

A spring tensioner that takes up slack in roller chain. Its title holds the seed noun and its category path does not, so it
shows what a category policy removes (the seeds it serves are in
``domains/industrial/seed_decoys.py``).
"""

from __future__ import annotations

from synthetic_ecommerce_data.core.typespec import TypeSpec
from synthetic_ecommerce_data.domains.industrial.breadth import BreadthRow

SPEC = TypeSpec(
    "chain_tensioners",
    label="Roller Chain Tensioner",
    breadth=BreadthRow(
        key="chain_tensioners",
        category=("Motion Control & Fluid Power", "Chain & Sprockets", "Chain Tensioners"),
        family="motion",
        shape="bracket",
        item="Roller Chain Tensioner",
        descriptor_attr=None,
        size_attr="Size",
        size_values=("#40", "#50"),
        attributes={"Material": ("Steel",), "Finish": ("Zinc Plated",)},
        price_range=(14.0, 52.0),
        skus=2,
        featured_sizes=(),
        reason="decoy for the industrial seed queries (#462): a spring tensioner that takes up slack in roller chain",
    ),
)
