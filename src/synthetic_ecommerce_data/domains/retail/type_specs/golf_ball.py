"""Golf Ball (gen#959, slice 1): Sports & Outdoors > Golf > Golf Balls.

A breadth type: ``derivable`` True, so the scaled build draws more balls by the values the titles
show (the cover and the construction). The cover is the SKU's color; the construction draws the
layers in a cut-away quarter (:func:`kit_fishing_golf.golf_ball`). Each SKU is a color in a pack.
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.fishing_golf_rows import BALLS, LARCHMERE, OWNERS
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
from synthetic_ecommerce_data.domains.retail.type_registry import TypeSpec


def _ball(cover: str, construction: str) -> tuple[tuple, ...]:
    return (_a("cover", "Cover", cover), _a("construction", "Construction", construction))


SPEC = TypeSpec(
    key="golf_ball",
    department="Sports & Outdoors",
    product_type="Golf Ball",
    derivable=True,
    owners=OWNERS,
    rows=(
        _row("GBLTWO", "Ionomer 2-Piece Golf Balls", _W, BALLS, "Golf Ball", 9.0, "golf_ball",
             "Durable 2-piece golf balls with an ionomer cover and a large core, for distance and a straight flight.",
             (WHITE, YELLOW, RED, BLUE), _ball("Ionomer", "2-Piece"),
             _words(("3 pack", 9.0), ("12 pack", 24.0), ("24 pack", 42.0)), "pack_size", (("construction", "2-piece"),)),
        _row("GBLTHR", "Urethane 3-Piece Golf Balls", LARCHMERE, BALLS, "Golf Ball", 14.0, "golf_ball",
             "Soft 3-piece golf balls with a urethane cover over a firm mantle, for spin and feel around the green.",
             (WHITE, GREEN, YELLOW, BLACK), _ball("Urethane", "3-Piece"),
             _words(("3 pack", 14.0), ("12 pack", 39.0), ("24 pack", 69.0)), "pack_size", (("construction", "3-piece"),)),
        _row("GBLFOR", "Urethane 4-Piece Golf Balls", _H, BALLS, "Golf Ball", 17.0, "golf_ball",
             "Tour 4-piece golf balls with a urethane cover and two mantles, for fast swings and a soft feel.",
             (WHITE, RED, BLUE, GREEN), _ball("Urethane", "4-Piece"),
             _words(("3 pack", 17.0), ("12 pack", 46.0), ("24 pack", 82.0)), "pack_size", (("construction", "4-piece"),)),
        _row("GBLIO3", "Ionomer 3-Piece Golf Balls", _L, BALLS, "Golf Ball", 12.0, "golf_ball",
             "Mid-price 3-piece golf balls with an ionomer cover and a soft mantle, for distance off the tee and control on the green.",
             (YELLOW, WHITE, BLACK, GREEN), _ball("Ionomer", "3-Piece"),
             _words(("3 pack", 12.0), ("12 pack", 32.0), ("24 pack", 56.0)), "pack_size", (("construction", "3-piece"),)),
    ),
)  # fmt: skip
