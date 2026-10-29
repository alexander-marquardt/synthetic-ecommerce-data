"""Bike Bottle (gen#625): a bicycle accessory with a short title, in its own Cycling leaf.

A real product of its own type (#444): a squeeze bottle and an insulated bottle that fit a bike's
bottle cage. Its short title holds ``bicycle`` or ``bike``, so on a plain text match it outranks
the bikes, whose titles carry a model number and specs. :mod:`kit_cycling` draws it.
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail import (
    kit_cycling,  # noqa: F401 -- registers bike_bottle
)
from synthetic_ecommerce_data.domains.retail.cycling_helpers import CYCLING, _ml
from synthetic_ecommerce_data.domains.retail.sports_helpers import (
    _L,
    _W,
    BLACK,
    BLUE,
    GREEN,
    RED,
    WHITE,
    YELLOW,
    _a,
    _row,
)
from synthetic_ecommerce_data.domains.retail.type_registry import TypeSpec

PATH = (*CYCLING, "Bike Bottles")

SPEC = TypeSpec(
    key="bike_bottle",
    department="Sports & Outdoors",
    product_type="Bike Bottle",
    rows=(
        _row("BTLSQZ", "Bicycle Water Bottle", _L, PATH, "Bike Bottle", 8.0, "bike_bottle",
             "A soft squeeze bottle with a push-pull valve and a waist that grips in the bottle cage.",
             (RED, BLUE, GREEN, YELLOW), (_a("bottle_type", "Bottle type", "Squeeze"), _a("insulated", "Insulated", "No"), _ml("capacity", "Capacity", 750)),
             (), "size", (("style", "squeeze"),)),
        _row("BTLINS", "Insulated Bike Bottle", _W, PATH, "Bike Bottle", 16.0, "bike_bottle",
             "A double-walled bike bottle that keeps water cold for two hours, with a valve that locks shut.",
             (BLACK, WHITE, BLUE, GREEN), (_a("bottle_type", "Bottle type", "Insulated"), _a("insulated", "Insulated", "Yes"), _ml("capacity", "Capacity", 600)),
             (), "size", (("style", "insulated"),)),
    ),
)  # fmt: skip
