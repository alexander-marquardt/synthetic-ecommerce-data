"""Insulated Water Bottle (gen#959, slice 3): Sports & Outdoors > Camping > Insulated Water Bottles.

A breadth type: ``derivable`` True, so the scaled build draws more insulated water bottles by the values the titles
show (the coating, the mouth and the lid). The wall is the SKU's color; the lid draws a flip straw, a chug spout or a screw cap with a loop (:func:`kit_outdoor_winter.bottle_insul`). Each SKU is a color in a capacity in millilitres.
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.outdoor_winter_rows import INSULATED_BOTTLES
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
    _axis,
    _row,
)
from synthetic_ecommerce_data.domains.retail.type_registry import TypeSpec


def _attrs(bottle_coating: str, bottle_mouth: str, bottle_lid: str) -> tuple[tuple, ...]:
    return (
        _a("bottle_coating", "Bottle coating", bottle_coating),
        _a("bottle_mouth", "Bottle mouth", bottle_mouth),
        _a("bottle_lid", "Bottle lid", bottle_lid),
    )


SPEC = TypeSpec(
    key="insulated_water_bottle",
    department="Sports & Outdoors",
    product_type="Insulated Water Bottle",
    derivable=True,
    rows=(
        _row("IWBPWS", "Powder-Coated Wide Mouth Insulated Water Bottle with Straw Lid", _W, INSULATED_BOTTLES, "Insulated Water Bottle", 29.0, "bottle_insul",
             "Double-wall stainless steel bottle with a grippy coat, keeping drinks cold for a day, with a flip straw lid.",
             (RED, BLUE, GREEN, YELLOW), _attrs("Powder-Coated", "Wide Mouth", "Straw Lid"),
             _axis((530, 26.0), (710, 29.0), (950, 34.0)), "capacity_ml", (("bottle_lid", "straw lid"),)),
        _row("IWBMNS", "Matte Enamel Narrow Mouth Insulated Water Bottle with Screw Cap", _H, INSULATED_BOTTLES, "Insulated Water Bottle", 22.0, "bottle_insul",
             "Double-wall stainless steel bottle with a matte finish and a screw cap with a carry loop, for hikes and the gym.",
             (BLACK, WHITE, BLUE, RED), _attrs("Matte Enamel", "Narrow Mouth", "Screw Cap"),
             _axis((500, 20.0), (750, 22.0), (1000, 26.0)), "capacity_ml", (("bottle_lid", "screw cap"),)),
        _row("IWBGWC", "Gloss Enamel Wide Mouth Insulated Water Bottle with Chug Lid", _L, INSULATED_BOTTLES, "Insulated Water Bottle", 27.0, "bottle_insul",
             "Double-wall stainless steel bottle with a gloss finish, a wide mouth for ice and a chug spout under a flip cap.",
             (YELLOW, GREEN, WHITE, BLACK), _attrs("Gloss Enamel", "Wide Mouth", "Chug Lid"),
             _axis((650, 25.0), (950, 27.0), (1200, 32.0)), "capacity_ml", (("bottle_lid", "chug lid"),)),
        _row("IWBPNC", "Powder-Coated Narrow Mouth Insulated Water Bottle with Chug Lid", _L, INSULATED_BOTTLES, "Insulated Water Bottle", 24.0, "bottle_insul",
             "Double-wall stainless steel bottle with a grippy coat and a chug spout, slim enough for a cup holder.",
             (WHITE, RED, GREEN, BLUE), _attrs("Powder-Coated", "Narrow Mouth", "Chug Lid"),
             _axis((500, 22.0), (750, 24.0)), "capacity_ml", (("bottle_lid", "chug lid"),)),
    ),
)  # fmt: skip
