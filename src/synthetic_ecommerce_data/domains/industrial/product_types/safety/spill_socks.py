"""Absorbent Spill Socks: a text-match decoy for the query "socks" (gen#774).

A long tube of absorbent filler laid around a machine to hold an oil or coolant leak. Its title
holds the plural and its category path does not, so a category policy drops it from a search for
socks. That query is the retail demo's, so this is no industrial seed decoy (``decoys/``).
"""

from __future__ import annotations

from synthetic_ecommerce_data.core.typespec import TypeSpec
from synthetic_ecommerce_data.domains.industrial.breadth import BreadthRow

SPEC = TypeSpec(
    "spill_socks",
    label="Absorbent Spill Socks",
    breadth=BreadthRow(
        key="spill_socks",
        category=("Safety", "Spill Control", "Spill Absorbents"),
        family="hand_tool",
        shape="tube",
        item="Absorbent Spill Socks",
        descriptor_attr=None,
        size_attr="Length",
        size_values=("48 in", "96 in"),
        attributes={"Material": ("Plastic",)},
        price_range=(9.0, 40.0),
        skus=2,
        featured_sizes=(),
        reason=(
            "decoy for the query socks (gen#774): a tube of absorbent filler laid around a leak"
        ),
    ),
)
