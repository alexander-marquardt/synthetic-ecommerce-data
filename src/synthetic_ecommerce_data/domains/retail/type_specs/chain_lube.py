"""Chain Lube (gen#625): a bicycle accessory with a short title, in its own Cycling leaf.

A real product of its own type (#444): a drip bottle and a spray can of chain lube. Its short
title holds ``bicycle`` or ``bike``, so on a plain text match it outranks the bikes, whose titles
carry a model number and specs (:mod:`bicycle_model_numbers`). :mod:`kit_cycling` draws it.
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail import (
    kit_cycling,  # noqa: F401 -- registers chain_lube
)
from synthetic_ecommerce_data.domains.retail.cycling_helpers import CYCLING, _ml
from synthetic_ecommerce_data.domains.retail.sports_helpers import (
    _H,
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

PATH = (*CYCLING, "Chain Lube")

SPEC = TypeSpec(
    key="chain_lube",
    department="Sports & Outdoors",
    product_type="Chain Lube",
    rows=(
        _row("LUBDRY", "Bicycle Chain Lube", _W, PATH, "Chain Lube", 9.0, "chain_lube",
             "A dry chain lube in a squeeze bottle with a long nozzle: one drop a link keeps the chain quiet on dusty roads.",
             (GREEN, BLUE, YELLOW), (_a("lube_type", "Lube type", "Dry"), _a("application", "Application", "Drip"), _ml("volume", "Volume", 120)),
             (), "size", (("style", "drip"),)),
        _row("LUBWET", "Bike Chain Spray", _H, PATH, "Chain Lube", 11.0, "chain_lube",
             "A wet chain lube in a spray can with a straw, for rain and winter rides.",
             (RED, BLACK, WHITE), (_a("lube_type", "Lube type", "Wet"), _a("application", "Application", "Spray"), _ml("volume", "Volume", 400)),
             (), "size", (("style", "spray"),)),
    ),
)  # fmt: skip
