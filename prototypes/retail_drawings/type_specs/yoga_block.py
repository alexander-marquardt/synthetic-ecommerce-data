"""Yoga Block (gen#368, moved to a spec by gen#351): the second Sports & Outdoors increment.

The styles are templates only (``derivable`` False): the department grows by authored rows.
:mod:`kit_sports` draws them.
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from sports_helpers import _H, _L, _NEUTRAL, _PRIMARY, _YOGA, _a, _axis, _row
from type_registry import TypeSpec

SPEC = TypeSpec(
    key="yoga_block",
    department="Sports & Outdoors",
    product_type="Yoga Block",
    rows=(
        _row("YGBFOM", "Foam Yoga Block", _L, (*_YOGA, "Yoga Blocks"), "Yoga Block", 7.0, "yoga_block",
             "A firm EVA foam block to lift the floor closer in seated poses and deepen a stretch, sold singly.",
             _PRIMARY, (_a("material", "Material", "EVA Foam"), _a("sold_as", "Sold as", "Single")),
             _axis((7.5, 7.0), (10, 9.0)), "height_cm", (("material", "foam"),)),
        _row("YGBCRK", "Cork Yoga Block", _H, (*_YOGA, "Yoga Blocks"), "Yoga Block", 14.0, "yoga_block",
             "A dense natural cork block with a grippy surface that does not slip under damp hands, sold as a pair.",
             _NEUTRAL, (_a("material", "Material", "Cork"), _a("sold_as", "Sold as", "Pair")),
             _axis((7.5, 14.0), (10, 17.0)), "height_cm", (("material", "cork"),)),
    ),
)  # fmt: skip
