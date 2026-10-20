"""Tent (gen#265, moved to a spec by gen#351 and gen#455): Camping: a dome or tunnel shell, its berth the SKU axis.

The styles are templates only (``derivable`` False): the department grows by authored rows.
:mod:`kit_sports` draws them.
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from sports_helpers import (
    _H,
    _L,
    _TENTS,
    _W,
    BLACK,
    BLUE,
    GREEN,
    GREY,
    ORANGE,
    RED,
    WHITE,
    YELLOW,
    _a,
    _axis,
    _mm,
    _row,
    _season,
)
from type_registry import TypeSpec

SPEC = TypeSpec(
    key="tent",
    department="Sports & Outdoors",
    product_type="Tent",
    rows=(
        _row("TNTDOM", "Compact Dome Tent", _W, (*_TENTS, "Dome Tents"), "Tent", 49.0, "tent",
             "A two-pole dome tent with a sewn-in groundsheet and a porch door, quick to pitch for a "
             "weekend away.",
             (GREEN, BLUE, ORANGE, RED),
             (_a("tent_type", "Tent type", "Dome"), _season(3), _mm("hydrostatic_head", "Hydrostatic head", 3000),
              _a("material", "Material", "Polyester")),
             _axis((2, 49.0), (3, 59.0), (4, 72.0)), "berth", (("style", "dome"),)),
        _row("TNTBPK", "Lightweight Backpacking Dome Tent", _H, (*_TENTS, "Dome Tents"), "Tent", 89.0,
             "tent", "A light dome tent that packs small for the trail, with a taped flysheet and "
             "two guy lines.",
             (YELLOW, BLACK, GREEN, BLUE),
             (_a("tent_type", "Tent type", "Dome"), _season(4), _mm("hydrostatic_head", "Hydrostatic head", 4000),
              _a("material", "Material", "Ripstop Nylon")),
             _axis((1, 89.0), (2, 109.0), (3, 135.0)), "berth", (("style", "dome"),)),
        _row("TNTFAM", "Family Tunnel Tent", _L, (*_TENTS, "Tunnel Tents"), "Tent", 149.0, "tent",
             "A tunnel tent with a living area and separate sleeping pods, roomy enough to stand up "
             "in and stay dry on a wet weekend.",
             (WHITE, BLUE, GREEN, GREY),
             (_a("tent_type", "Tent type", "Tunnel"), _season(3), _mm("hydrostatic_head", "Hydrostatic head", 3000),
              _a("material", "Material", "Polyester")),
             _axis((4, 149.0), (6, 219.0), (8, 289.0)), "berth", (("style", "tunnel"),)),
        _row("TNTTRK", "Two Pole Tunnel Tent", _W, (*_TENTS, "Tunnel Tents"), "Tent", 119.0, "tent",
             "A low tunnel tent on two poles that pitches fast and holds up in the wind, with a "
             "vestibule for boots and bags.",
             (RED, YELLOW, BLACK, ORANGE),
             (_a("tent_type", "Tent type", "Tunnel"), _season(4), _mm("hydrostatic_head", "Hydrostatic head", 5000),
              _a("material", "Material", "Ripstop Nylon")),
             _axis((2, 119.0), (3, 149.0)), "berth", (("style", "tunnel"),)),
    ),
)  # fmt: skip
