"""Baseball Bat (gen#368, moved to a spec by gen#351): the second Sports & Outdoors increment.

The styles are templates only (``derivable`` False): the department grows by authored rows.
:mod:`kit_sports` draws them.
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from sports_helpers import _BASEBALL, _L, _NEUTRAL, _PRIMARY, _W, _a, _axis, _mm, _row
from type_registry import TypeSpec

SPEC = TypeSpec(
    key="baseball_bat",
    department="Sports & Outdoors",
    product_type="Baseball Bat",
    rows=(
        _row("BBTWOD", "Maple Baseball Bat", _W, (*_BASEBALL, "Baseball Bats"), "Baseball Bat", 38.0, "baseball_bat",
             "A turned maple bat with a balanced swing weight and a flared knob, for batting practice.",
             _NEUTRAL, (_a("material", "Material", "Maple"), _mm("barrel_diameter", "Barrel diameter", 64)),
             _axis((76, 38.0), (81, 40.0), (86, 42.0)), "length_cm", (("material", "wood"),)),
        _row("BBTALY", "Alloy Youth Baseball Bat", _L, (*_BASEBALL, "Baseball Bats"), "Baseball Bat", 44.0, "baseball_bat",
             "A lightweight alloy bat with a cushioned grip and a large barrel, for young hitters learning the swing.",
             _PRIMARY, (_a("material", "Material", "Aluminum Alloy"), _mm("barrel_diameter", "Barrel diameter", 69)),
             _axis((71, 44.0), (76, 47.0), (81, 50.0)), "length_cm", (("material", "alloy"),)),
    ),
)  # fmt: skip
