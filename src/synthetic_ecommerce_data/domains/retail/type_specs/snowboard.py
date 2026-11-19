"""Snowboard (gen#959, slice 3): Sports & Outdoors > Winter Sports > Snowboards.

A breadth type: ``derivable`` True, so the scaled build draws more snowboards by the values the titles
show (the riding style, the shape and the profile). The top sheet is the SKU's color; the profile draws the board's edge arched, bowed or straight beside it (:func:`kit_outdoor_winter.snowboard`). Each SKU is a color in a length.
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.outdoor_winter_rows import SNOWBOARDS
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


def _attrs(riding_style: str, board_shape: str, board_profile: str) -> tuple[tuple, ...]:
    return (
        _a("riding_style", "Riding style", riding_style),
        _a("board_shape", "Board shape", board_shape),
        _a("board_profile", "Board profile", board_profile),
    )


SPEC = TypeSpec(
    key="snowboard",
    department="Sports & Outdoors",
    product_type="Snowboard",
    derivable=True,
    rows=(
        _row("SNBADC", "All-Mountain Directional Snowboard with Camber Profile", _W, SNOWBOARDS, "Snowboard", 349.0, "snowboard",
             "All-mountain snowboard with a directional shape and a cambered base that holds an edge on hard snow.",
             (BLACK, BLUE, RED, WHITE), _attrs("All-Mountain", "Directional", "Camber"),
             _axis((150, 339.0), (154, 349.0), (158, 359.0), (162, 369.0)), "length_cm", (("board_profile", "camber"),)),
        _row("SNBFTR", "Freestyle True Twin Snowboard with Rocker Profile", _H, SNOWBOARDS, "Snowboard", 279.0, "snowboard",
             "Freestyle snowboard, a true twin rides the same both ways, with a soft rockered base for the park.",
             (YELLOW, GREEN, BLACK, RED), _attrs("Freestyle", "True Twin", "Rocker"),
             _axis((142, 269.0), (146, 279.0), (150, 289.0)), "length_cm", (("board_profile", "rocker"),)),
        _row("SNBFTC", "Freeride Tapered Snowboard with Camber Profile", _L, SNOWBOARDS, "Snowboard", 429.0, "snowboard",
             "Freeride snowboard with a tapered tail that floats in deep snow and a stiff cambered base.",
             (WHITE, BLUE, GREEN, BLACK), _attrs("Freeride", "Tapered", "Camber"),
             _axis((156, 419.0), (160, 429.0), (164, 439.0)), "length_cm", (("board_profile", "camber"),)),
        _row("SNBATF", "All-Mountain True Twin Snowboard with Flat Profile", _L, SNOWBOARDS, "Snowboard", 299.0, "snowboard",
             "All-mountain true twin snowboard with a flat base that stays stable and catches no edge.",
             (RED, YELLOW, WHITE, GREEN), _attrs("All-Mountain", "True Twin", "Flat"),
             _axis((148, 289.0), (152, 299.0), (156, 309.0)), "length_cm", (("board_profile", "flat"),)),
    ),
)  # fmt: skip
