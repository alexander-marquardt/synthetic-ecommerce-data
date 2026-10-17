"""Baseball Glove (gen#368, moved to a spec by gen#351): the second Sports & Outdoors increment.

The styles are templates only (``derivable`` False): the department grows by authored rows.
:mod:`kit_sports` draws them.
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from sports_helpers import _BASEBALL, _H, _L, _NEUTRAL, _PRIMARY, _a, _axis, _row
from type_registry import TypeSpec

SPEC = TypeSpec(
    key="baseball_glove",
    department="Sports & Outdoors",
    product_type="Baseball Glove",
    rows=(
        _row("BGLINF", "Infield Baseball Glove", _H, (*_BASEBALL, "Baseball Gloves"), "Baseball Glove", 36.0,
             "baseball_glove", "A short-webbed leather glove with a shallow pocket for a quick transfer from glove to hand.",
             _NEUTRAL, (_a("material", "Material", "Leather"), _a("position", "Position", "Infield")),
             _axis((10.5, 36.0), (11.5, 42.0)), "glove_size_in", (("position", "infield"),)),
        _row("BGLOUT", "Outfield Baseball Glove", _L, (*_BASEBALL, "Baseball Gloves"), "Baseball Glove", 32.0,
             "baseball_glove", "A long glove with a deep web and a padded palm, built to reach and hold fly balls.",
             _PRIMARY, (_a("material", "Material", "Synthetic Leather"), _a("position", "Position", "Outfield")),
             _axis((11.5, 32.0), (12.5, 38.0)), "glove_size_in", (("position", "outfield"),)),
    ),
)  # fmt: skip
