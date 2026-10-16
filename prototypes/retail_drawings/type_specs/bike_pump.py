"""Bike Pump (gen#368, moved to a spec by gen#351): the second Sports & Outdoors increment.

The styles are templates only (``derivable`` False): the department grows by authored rows.
:mod:`kit_sports` draws them.
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from sports_helpers import _CYCLING, _H, _NEUTRAL, _PRIMARY, _a, _row
from type_registry import TypeSpec

SPEC = TypeSpec(
    key="bike_pump",
    department="Sports & Outdoors",
    product_type="Bike Pump",
    rows=(
        _row("PMPFLR", "Floor Pump with Pressure Gauge", "Stridewell", (*_CYCLING,), "Bike Pump", 24.0, "bike_pump",
             "A steel-based floor pump with a wide gauge and a locking head that fits both valve types.",
             _PRIMARY, (_a("pump_type", "Pump type", "Floor"), _a("valve_type", "Valve type", "Presta and Schrader"),
                        _a("max_pressure", "Maximum pressure (psi)", "160")),
             (), "size", (("style", "floor"),)),
        _row("PMPHND", "Mini Hand Pump", _H, (*_CYCLING,), "Bike Pump", 12.0, "bike_pump",
             "A pocket hand pump with a fold-out foot peg and a short hose, for a puncture on the road.",
             _NEUTRAL, (_a("pump_type", "Pump type", "Hand"), _a("valve_type", "Valve type", "Presta and Schrader"),
                        _a("max_pressure", "Maximum pressure (psi)", "100")),
             (), "size", (("style", "hand"),)),
    ),
)  # fmt: skip
