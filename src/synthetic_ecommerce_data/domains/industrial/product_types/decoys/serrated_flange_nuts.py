"""Washer-Faced Flange Nut: a text-match decoy for the industrial seed queries (#462).

A flange nut with a washer face, M10. Its title holds the seed noun and its category path does not, so it
shows what a category policy removes (the seeds it serves are in
``domains/industrial/seed_decoys.py``).
"""

from __future__ import annotations

from synthetic_ecommerce_data.core.typespec import TypeSpec
from synthetic_ecommerce_data.domains.industrial.breadth import BreadthRow

SPEC = TypeSpec(
    "serrated_flange_nuts",
    label="Washer-Faced Flange Nut",
    breadth=BreadthRow(
        key="serrated_flange_nuts",
        category=("Fasteners", "Nuts", "Serrated Flange Nuts"),
        family="fastener",
        shape="block",
        item="Washer-Faced Flange Nut",
        descriptor_attr=None,
        size_attr="Thread Size",
        size_values=("M8", "M10", "M12"),
        attributes={"Material": ("Steel",), "Finish": ("Zinc Plated",), "Grade": ("Class 8",)},
        price_range=(4.0, 14.0),
        skus=2,
        featured_sizes=("M10",),
        reason="decoy for the industrial seed queries (#462): a flange nut with a washer face, M10",
    ),
)
