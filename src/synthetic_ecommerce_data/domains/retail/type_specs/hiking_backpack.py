"""Hiking Backpack (gen#959, slice 3): Sports & Outdoors > Hiking > Hiking Backpacks.

A breadth type: ``derivable`` True, so the scaled build draws more hiking backpacks by the values the titles
show (the fabric, the frame and the opening). The pack's body is the SKU's color; the frame draws a hip belt, bare frame rails or a cord grid (:func:`kit_outdoor_winter.hiking_backpack`). Each SKU is a color in a capacity in litres.
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.outdoor_winter_rows import HIKING_BACKPACKS
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


def _attrs(pack_fabric: str, pack_frame: str, pack_opening: str) -> tuple[tuple, ...]:
    return (
        _a("pack_fabric", "Pack fabric", pack_fabric),
        _a("pack_frame", "Pack frame", pack_frame),
        _a("pack_opening", "Pack opening", pack_opening),
    )


SPEC = TypeSpec(
    key="hiking_backpack",
    department="Sports & Outdoors",
    product_type="Hiking Backpack",
    derivable=True,
    rows=(
        _row("HBPRIT", "Ripstop Nylon Internal Frame Hiking Backpack with Top Lid", _W, HIKING_BACKPACKS, "Hiking Backpack", 119.0, "hiking_backpack",
             "Ripstop nylon hiking backpack on an internal frame, with a padded hip belt, a top lid pocket and a rain cover.",
             (RED, BLUE, GREEN, BLACK), _attrs("Ripstop Nylon", "Internal Frame", "Top Lid"),
             _axis((45, 109.0), (55, 119.0), (65, 135.0)), "capacity_l", (("pack_frame", "internal frame"),)),
        _row("HBPPET", "Polyester External Frame Hiking Backpack with Top Lid", _H, HIKING_BACKPACKS, "Hiking Backpack", 99.0, "hiking_backpack",
             "Polyester hiking backpack on an aluminium external frame that carries a heavy load off the back on long treks.",
             (YELLOW, GREEN, BLACK, BLUE), _attrs("Polyester", "External Frame", "Top Lid"),
             _axis((55, 95.0), (65, 99.0), (75, 109.0)), "capacity_l", (("pack_frame", "external frame"),)),
        _row("HBPRFR", "Ripstop Nylon Frameless Hiking Backpack with Roll Top", _L, HIKING_BACKPACKS, "Hiking Backpack", 79.0, "hiking_backpack",
             "Light frameless hiking backpack in ripstop nylon with a roll-top closure and a stretch cord on the front.",
             (WHITE, RED, YELLOW, BLACK), _attrs("Ripstop Nylon", "Frameless", "Roll Top"),
             _axis((30, 69.0), (35, 75.0), (40, 79.0)), "capacity_l", (("pack_frame", "frameless"),)),
        _row("HBPWIP", "Waxed Canvas Internal Frame Hiking Backpack with Panel Zip", _L, HIKING_BACKPACKS, "Hiking Backpack", 139.0, "hiking_backpack",
             "Waxed canvas hiking backpack on an internal frame, opened by a full panel zip, with a padded hip belt.",
             (GREEN, BLACK, WHITE, RED), _attrs("Waxed Canvas", "Internal Frame", "Panel Zip"),
             _axis((40, 129.0), (50, 139.0)), "capacity_l", (("pack_frame", "internal frame"),)),
    ),
)  # fmt: skip
