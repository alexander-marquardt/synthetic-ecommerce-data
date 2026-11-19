"""Bike Light (gen#959, slice 3): Sports & Outdoors > Cycling > Bike Lights.

A breadth type: ``derivable`` True, so the scaled build draws more bike lights by the values the titles
show (the power, the position and the modes). The housing is the SKU's color; the position draws a front light with a round lens, a rear light with a ribbed red lens or a twin pack of both (:func:`kit_outdoor_winter.bike_light`). Each SKU is a color in a light output, a rating and not a size.
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.outdoor_winter_rows import BIKE_LIGHTS
from synthetic_ecommerce_data.domains.retail.sports_helpers import (
    _H,
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
    _words,
)
from synthetic_ecommerce_data.domains.retail.type_registry import Option, TypeSpec


def _attrs(light_power: str, light_position: str, light_modes: str) -> tuple[tuple, ...]:
    return (
        _a("light_power", "Light power", light_power),
        _a("light_position", "Light position", light_position),
        _a("light_modes", "Light modes", light_modes),
    )


SPEC = TypeSpec(
    key="bike_light",
    department="Sports & Outdoors",
    product_type="Bike Light",
    derivable=True,
    options=(Option("light_output", "light_output", "Light output"),),
    rows=(
        _row("BLTUFF", "USB Rechargeable Front Bike Light with 5 Modes", _W, BIKE_LIGHTS, "Bike Light", 29.0, "bike_light",
             "USB rechargeable front light with a strap mount that fits any handlebar and a low-battery warning.",
             (BLACK, RED, BLUE, GREEN), _attrs("USB Rechargeable", "Front", "5 Modes"),
             _words(("400 Lumen", 24.0), ("800 Lumen", 29.0), ("1200 Lumen", 39.0)), "light_output", (("light_position", "front"),)),
        _row("BLTBRT", "Battery-Powered Rear Bike Light with 3 Modes", _H, BIKE_LIGHTS, "Bike Light", 12.0, "bike_light",
             "Battery-powered rear light with a steady and two flashing modes, on a clip or a seatpost strap.",
             (RED, BLACK, YELLOW, WHITE), _attrs("Battery-Powered", "Rear", "3 Modes"),
             _words(("30 Lumen", 10.0), ("60 Lumen", 12.0)), "light_output", (("light_position", "rear"),)),
        _row("BLTUTS", "USB Rechargeable Twin-Pack Bike Light with 7 Modes", _L, BIKE_LIGHTS, "Bike Light", 45.0, "bike_light",
             "USB rechargeable front and rear light set with strap mounts, so a bike is seen from both ends.",
             (YELLOW, WHITE, BLACK, GREEN), _attrs("USB Rechargeable", "Twin-Pack", "7 Modes"),
             _words(("400 Lumen", 39.0), ("800 Lumen", 45.0)), "light_output", (("light_position", "twin-pack"),)),
        _row("BLTURF", "USB Rechargeable Rear Bike Light with 5 Modes", _L, BIKE_LIGHTS, "Bike Light", 19.0, "bike_light",
             "USB rechargeable rear light with a wide-angle lens seen from the side, on a seatpost strap.",
             (BLUE, GREEN, WHITE, RED), _attrs("USB Rechargeable", "Rear", "5 Modes"),
             _words(("60 Lumen", 17.0), ("100 Lumen", 19.0), ("150 Lumen", 22.0)), "light_output", (("light_position", "rear"),)),
    ),
)  # fmt: skip
