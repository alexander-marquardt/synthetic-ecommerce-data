"""Kick Scooter (gen#352): folding, stunt and commuter scooters in Sports & Outdoors.

The kids' ride-on scooters of Toys are another type (``ride_on``); these are the sports and
commuting scooters. The styles are templates only (``derivable`` False). :mod:`kit_sports` draws
them.
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from cycling_helpers import WHEELED, _inch
from sports_helpers import _H, _L, _W, BLACK, BLUE, GREEN, RED, WHITE, YELLOW, _a, _kg, _row
from type_registry import TypeSpec

SPEC = TypeSpec(
    key="kick_scooter",
    department="Sports & Outdoors",
    product_type="Kick Scooter",
    rows=(
        _row("SCTFLD", "Folding Kick Scooter", _H, (*WHEELED, "Kick Scooters"), "Kick Scooter", 59.0, "kick_scooter",
             "A folding kick scooter with a height-adjustable bar, a rear brake and a hinge that drops it flat for the bus.",
             (RED, BLUE, BLACK, GREEN),
             (_a("scooter_type", "Scooter type", "Folding"), _inch("wheel_size", "Wheel size", 8), _kg("max_load_kg", "Maximum load", 100), _a("folds", "Folds", "Yes")),
             (), "size", (("style", "folding"),)),
        _row("SCTSTN", "Stunt Kick Scooter", _L, (*WHEELED, "Kick Scooters"), "Kick Scooter", 79.0, "kick_scooter",
             "A kick scooter for the skate park, with small hard wheels, a wide bar and a reinforced deck.",
             (BLACK, YELLOW, WHITE, RED),
             (_a("scooter_type", "Scooter type", "Stunt"), _inch("wheel_size", "Wheel size", 4.7), _kg("max_load_kg", "Maximum load", 110), _a("folds", "Folds", "No")),
             (), "size", (("style", "stunt"),)),
        _row("SCTCMT", "Large Wheel Commuter Kick Scooter", _W, (*WHEELED, "Kick Scooters"), "Kick Scooter", 129.0, "kick_scooter",
             "A kick scooter with large air-filled wheels that roll over cracks and curbs, with a front and rear brake, for the daily trip.",
             (BLUE, GREEN, BLACK, WHITE),
             (_a("scooter_type", "Scooter type", "Commuter"), _inch("wheel_size", "Wheel size", 10), _kg("max_load_kg", "Maximum load", 120), _a("folds", "Folds", "Yes")),
             (), "size", (("style", "commuter"),)),
    ),
)  # fmt: skip
