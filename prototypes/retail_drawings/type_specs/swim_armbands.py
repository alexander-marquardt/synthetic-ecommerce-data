"""Swim Armbands (gen#368, moved to a spec by gen#351): the second Sports & Outdoors increment.

The styles are templates only (``derivable`` False): the department grows by authored rows.
:mod:`kit_sports` draws them.
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from sports_helpers import _H, _L, _NEUTRAL, _PRIMARY, _SWIM, _a, _axis, _row
from type_registry import TypeSpec

SPEC = TypeSpec(
    key="swim_armbands",
    department="Sports & Outdoors",
    product_type="Swim Armbands",
    rows=(
        _row("ARMTWO", "Two Chamber Swimming Armbands", _L, (*_SWIM, "Swim Armbands"), "Swim Armbands", 4.0,
             "swim_armbands", "Inflatable armbands with two air chambers each, for children learning to float.",
             _PRIMARY, (_a("material", "Material", "PVC"), _a("chambers", "Chambers", "Two")),
             _axis((15, 4.0), (30, 5.0)), "max_load_kg", (("chambers", "two"),)),
        _row("ARMTHR", "Three Chamber Swimming Armbands", _H, (*_SWIM, "Swim Armbands"), "Swim Armbands", 6.0,
             "swim_armbands", "Armbands with three separate air chambers, so one leak never takes away all the lift.",
             _NEUTRAL, (_a("material", "Material", "PVC"), _a("chambers", "Chambers", "Three")),
             _axis((15, 6.0), (30, 7.0)), "max_load_kg", (("chambers", "three"),)),
    ),
)  # fmt: skip
