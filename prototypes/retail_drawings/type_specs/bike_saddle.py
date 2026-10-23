"""Bike Saddle (gen#625): a bicycle accessory with a short title, in its own Cycling leaf.

A real product of its own type (#444): a wide padded comfort seat and a narrow road saddle. Its
short title holds ``bicycle`` or ``bike``, so on a plain text match it outranks the bikes, whose
titles carry a model number and specs. :mod:`kit_cycling` draws it.
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

import kit_cycling  # noqa: F401 -- registers bike_saddle
from cycling_helpers import CYCLING
from sports_helpers import _H, _W, BLACK, BLUE, GREEN, RED, WHITE, YELLOW, _a, _row
from type_registry import TypeSpec

PATH = (*CYCLING, "Bike Saddles")

SPEC = TypeSpec(
    key="bike_saddle",
    department="Sports & Outdoors",
    product_type="Bike Saddle",
    rows=(
        _row("SDLCMF", "Bicycle Seat", _H, PATH, "Bike Saddle", 24.0, "bike_saddle",
             "A wide comfort saddle with gel padding and two springs under the back, for upright city riding.",
             (BLACK, BLUE, RED, GREEN), (_a("saddle_type", "Saddle type", "Comfort"), _a("padding", "Padding", "Gel")),
             (), "size", (("style", "comfort"),)),
        _row("SDLRDR", "Road Bike Saddle", _W, PATH, "Bike Saddle", 39.0, "bike_saddle",
             "A long narrow saddle with a firm foam shell and steel rails, for a bent-over road position.",
             (BLACK, WHITE, RED, YELLOW), (_a("saddle_type", "Saddle type", "Road"), _a("padding", "Padding", "Foam")),
             (), "size", (("style", "road"),)),
    ),
)  # fmt: skip
