"""Bike Helmet (gen#352): road, mountain and kids helmets in a Sports & Outdoors leaf.

Sold in S, M and L. The styles are templates only (``derivable`` False). :mod:`kit_sports` draws
them. A baseball batting helmet is its own type (``batting_helmet``) in Baseball.
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from cycling_helpers import CYCLING
from sports_helpers import _H, _L, _W, BLACK, BLUE, GREEN, RED, WHITE, YELLOW, _a, _row, _words
from type_registry import TypeSpec


def _sizes(price: float) -> tuple[tuple[str, float], ...]:
    return _words(("S", price), ("M", price), ("L", price))


SPEC = TypeSpec(
    key="bike_helmet",
    department="Sports & Outdoors",
    product_type="Bike Helmet",
    rows=(
        _row("HLMRDR", "Road Bike Helmet", _W, (*CYCLING, "Bike Helmets"), "Bike Helmet", 59.0, "bike_helmet",
             "A light in-mold bike helmet with long vents and a rotational impact layer, for road rides.",
             (RED, BLACK, WHITE, BLUE),
             (_a("helmet_type", "Helmet type", "Road"), _a("impact_protection", "Impact protection", "Rotational"), _a("visor", "Visor", "No")),
             _sizes(59.0), "size", (("style", "road"),)),
        _row("HLMMTB", "Mountain Bike Helmet with Visor", _L, (*CYCLING, "Bike Helmets"), "Bike Helmet", 49.0, "bike_helmet",
             "A bike helmet with a peak that shades the eyes, extra coverage at the back of the head and a sweat pad.",
             (GREEN, YELLOW, BLACK, BLUE),
             (_a("helmet_type", "Helmet type", "Mountain"), _a("impact_protection", "Impact protection", "Standard"), _a("visor", "Visor", "Yes")),
             _sizes(49.0), "size", (("style", "mountain"),)),
        _row("HLMKID", "Kids Bike Helmet", _H, (*CYCLING, "Bike Helmets"), "Bike Helmet", 25.0, "bike_helmet",
             "A round kids bike helmet with a dial at the back to fit as they grow and a soft chin strap.",
             (RED, BLUE, YELLOW, GREEN),
             (_a("helmet_type", "Helmet type", "Kids"), _a("impact_protection", "Impact protection", "Standard"), _a("visor", "Visor", "No")),
             _sizes(25.0), "size", (("style", "kids"),)),
    ),
)  # fmt: skip
