"""Swim Cap (gen#368, moved to a spec by gen#351): the second Sports & Outdoors increment.

The styles are templates only (``derivable`` False): the department grows by authored rows.
:mod:`kit_sports` draws them.
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from sports_helpers import _L, _NEUTRAL, _PRIMARY, _SWIM, _W, _a, _row
from type_registry import TypeSpec

SPEC = TypeSpec(
    key="swim_cap",
    department="Sports & Outdoors",
    product_type="Swim Cap",
    rows=(
        _row("SCPSIL", "Silicone Swim Cap", _W, (*_SWIM, "Swim Caps"), "Swim Cap", 6.0, "swim_cap",
             "A smooth, stretchy swim cap that keeps hair dry and cuts drag, free of latex.",
             _PRIMARY, (_a("material", "Material", "Silicone"), _a("latex_free", "Latex free", "Yes")),
             (), "size", (("material", "silicone"),)),
        _row("SCPLYC", "Lycra Swim Cap", _L, (*_SWIM, "Swim Caps"), "Swim Cap", 5.0, "swim_cap",
             "A soft panelled fabric cap for easy pulling on and long wear, a gentler fit for the pool.",
             _NEUTRAL, (_a("material", "Material", "Lycra"), _a("latex_free", "Latex free", "Yes")),
             (), "size", (("material", "lycra"),)),
    ),
)  # fmt: skip
