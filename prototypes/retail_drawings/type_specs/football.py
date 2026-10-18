"""Football (gen#368, moved to a spec by gen#351): the second Sports & Outdoors increment.

The styles are templates only (``derivable`` False): the department grows by authored rows.
:mod:`kit_sports` draws them.
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from sports_helpers import _L, _NEUTRAL, _PRIMARY, _TEAM, _W, _a, _axis, _row
from type_registry import Option, TypeSpec

SPEC = TypeSpec(
    options=(
        Option("ball_size", "ball_size", "Ball size", "C62"),
    ),
    key="football",
    department="Sports & Outdoors",
    product_type="Football",
    rows=(
        _row("FBLCLS", "Classic Panel Football", _W, (*_TEAM, "Footballs"), "Football", 12.0, "football",
             "A machine-stitched football with the classic pentagon panels, for training and park games.",
             _NEUTRAL, (_a("cover", "Cover", "Synthetic Leather"), _a("construction", "Construction", "Machine Stitched")),
             _axis((3, 10.0), (4, 11.0), (5, 12.0)), "ball_size", (("panels", "classic"),)),
        _row("FBLMOD", "Thermal Bonded Match Football", _L, (*_TEAM, "Footballs"), "Football", 26.0, "football",
             "A seamless match football with bonded panels that keep their shape and take on no water.",
             _PRIMARY, (_a("cover", "Cover", "Polyurethane"), _a("construction", "Construction", "Thermal Bonded")),
             _axis((4, 24.0), (5, 26.0)), "ball_size", (("panels", "modern"),)),
    ),
)  # fmt: skip
