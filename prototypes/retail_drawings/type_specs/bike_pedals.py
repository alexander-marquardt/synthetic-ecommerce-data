"""Bike Pedals (gen#625): a bicycle accessory with a short title, in its own Cycling leaf.

A real product of its own type (#444), sold as a pair: flat platform pedals and clipless pedals.
Its short title holds ``bike``, so on a plain text match it outranks the bikes, whose titles carry
a model number and specs. :mod:`kit_cycling` draws it.
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

import kit_cycling  # noqa: F401 -- registers bike_pedals
from cycling_helpers import CYCLING
from sports_helpers import _L, _W, BLACK, BLUE, GREEN, RED, WHITE, YELLOW, _a, _row
from type_registry import TypeSpec

PATH = (*CYCLING, "Bike Pedals")

SPEC = TypeSpec(
    key="bike_pedals",
    department="Sports & Outdoors",
    product_type="Bike Pedals",
    rows=(
        _row("PDLFLT", "Bike Pedals", _L, PATH, "Bike Pedals", 19.0, "bike_pedals",
             "A pair of flat aluminum platform pedals with grip pins, to ride in any shoes.",
             (BLACK, RED, BLUE, GREEN), (_a("pedal_type", "Pedal type", "Flat"), _a("material", "Material", "Aluminum")),
             (), "size", (("style", "flat"),)),
        _row("PDLCLP", "Clipless Bike Pedals", _W, PATH, "Bike Pedals", 49.0, "bike_pedals",
             "A pair of light clipless pedals that lock to a cleat on a cycling shoe.",
             (BLACK, WHITE, RED, YELLOW), (_a("pedal_type", "Pedal type", "Clipless"), _a("material", "Material", "Composite")),
             (), "size", (("style", "clipless"),)),
    ),
)  # fmt: skip
