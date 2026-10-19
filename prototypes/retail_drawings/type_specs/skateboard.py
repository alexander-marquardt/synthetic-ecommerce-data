"""Skateboard (gen#352): a complete street board, a cruiser and a longboard in Sports & Outdoors.

Sold by deck width in inches. The styles are templates only (``derivable`` False).
:mod:`kit_sports` draws them.
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from cycling_helpers import WHEELED
from sports_helpers import _H, _L, _W, BLACK, BLUE, GREEN, RED, WHITE, YELLOW, _a, _axis, _row
from type_registry import Option, TypeSpec

SPEC = TypeSpec(
    key="skateboard",
    department="Sports & Outdoors",
    product_type="Skateboard",
    options=(Option("deck_width_in", "deck_width", "Deck width", "INH"),),
    rows=(
        _row("SKBCMP", "Complete Street Skateboard", _W, (*WHEELED, "Skateboards"), "Skateboard", 79.0, "skateboard",
             "A ready-to-ride skateboard with a seven-ply maple deck, grip tape, trucks, bearings and hard wheels for the street.",
             (RED, BLACK, WHITE, BLUE),
             (_a("board_type", "Board type", "Street"), _a("material", "Material", "Maple")),
             _axis((7.75, 79.0), (8, 79.0), (8.25, 84.0)), "deck_width_in", (("style", "street"),)),
        _row("SKBCRS", "Retro Cruiser Skateboard", _H, (*WHEELED, "Skateboards"), "Skateboard", 89.0, "skateboard",
             "A wide cruiser skateboard with a single kicktail and large soft wheels that roll over rough pavement.",
             (YELLOW, GREEN, BLUE, BLACK),
             (_a("board_type", "Board type", "Cruiser"), _a("material", "Material", "Maple")),
             _axis((8.5, 89.0), (9, 94.0)), "deck_width_in", (("style", "cruiser"),)),
        _row("SKBLNG", "Drop-Through Longboard Skateboard", _L, (*WHEELED, "Skateboards"), "Skateboard", 129.0, "skateboard",
             "A long, flat skateboard with a bamboo deck, a drop-through mount and big wheels for carving and commuting.",
             (WHITE, GREEN, RED, BLACK),
             (_a("board_type", "Board type", "Longboard"), _a("material", "Material", "Bamboo")),
             _axis((9, 129.0), (9.5, 139.0)), "deck_width_in", (("style", "longboard"),)),
    ),
)  # fmt: skip
