"""Spiral Flute Tap Extractor: a text-match decoy for the industrial seed queries (#462).

An extractor that removes a broken spiral flute tap. Its title holds the seed noun and its category
path does not, so it shows what a category policy removes (the seeds it serves are in
``domains/industrial/seed_decoys.py``).
"""

from __future__ import annotations

from synthetic_ecommerce_data.core.typespec import TypeSpec
from synthetic_ecommerce_data.domains.industrial.breadth import BreadthRow

SPEC = TypeSpec(
    "tap_extractors",
    label="Spiral Flute Tap Extractor",
    breadth=BreadthRow(
        key="tap_extractors",
        category=("Threading", "Tap Accessories", "Tap Extractors"),
        family="cutting_tool",
        shape="cylinder",
        item="Spiral Flute Tap Extractor",
        descriptor_attr=None,
        size_attr="Size",
        size_values=("1/4 in", "3/8 in"),
        attributes={"Material": ("Alloy Steel",), "Type": ("4 Flute",)},
        price_range=(14.0, 55.0),
        skus=2,
        featured_sizes=(),
        reason=(
            "decoy for the industrial seed queries (#462): an extractor that removes a broken "
            "spiral flute tap"
        ),
    ),
)
