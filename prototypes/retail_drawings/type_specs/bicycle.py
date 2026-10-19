"""Bicycle (gen#352): road, mountain, kids and electric bikes in a Sports & Outdoors group.

Each style is a template (``derivable`` False): the range is authored, four styles. An adult bike
is sold by frame size (centimeters); a kids' bike by wheel size (inches), as the toy bikes are
(gen#271). The wheel size of an adult bike is a fixed attribute. A balance bike stays in Toys.
:mod:`kit_sports` draws them.
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from cycling_helpers import BIKES, _count, _inch
from sports_helpers import (
    _H,
    _L,
    _W,
    BLACK,
    BLUE,
    GREEN,
    ORANGE,
    RED,
    WHITE,
    YELLOW,
    _a,
    _axis,
    _row,
)
from type_registry import Option, TypeSpec

SPEC = TypeSpec(
    key="bicycle",
    department="Sports & Outdoors",
    product_type="Bicycle",
    options=(Option("frame_cm", "frame_size", "Frame size", "CMT"),),
    rows=(
        _row("BIKRDR", "Aluminum Road Bike", _W, (*BIKES, "Road Bikes"), "Bicycle", 449.0, "bicycle",
             "A light aluminum road bicycle with drop bars, a carbon fork and eighteen gears for fast rides on tarmac.",
             (RED, BLACK, WHITE, BLUE),
             (_a("bike_type", "Bike type", "Road"), _a("frame_material", "Frame material", "Aluminum"),
              _count("gears", "Gears", 18), _inch("wheel_size", "Wheel size", 28), _a("brake_type", "Brake type", "Rim")),
             _axis((50, 449.0), (54, 449.0), (58, 459.0)), "frame_cm", (("style", "road"),)),
        _row("BIKMTB", "Hardtail Mountain Bike", _H, (*BIKES, "Mountain Bikes"), "Bicycle", 399.0, "bicycle",
             "A hardtail mountain bicycle with front suspension, wide tires and twenty-one gears for trails and fire roads.",
             (GREEN, ORANGE, BLACK, YELLOW),
             (_a("bike_type", "Bike type", "Mountain"), _a("frame_material", "Frame material", "Aluminum"),
              _count("gears", "Gears", 21), _inch("wheel_size", "Wheel size", 29), _a("brake_type", "Brake type", "Disc")),
             _axis((41, 399.0), (46, 399.0), (51, 409.0)), "frame_cm", (("style", "mountain"),)),
        _row("BIKEBK", "City Electric Bike", _L, (*BIKES, "Electric Bikes"), "Bicycle", 1199.0, "bicycle",
             "An electric bicycle with a hub motor, a removable battery on the down tube and seven gears for the commute.",
             (BLACK, WHITE, BLUE, GREEN),
             (_a("bike_type", "Bike type", "Electric"), _a("frame_material", "Frame material", "Aluminum"),
              _count("gears", "Gears", 7), _inch("wheel_size", "Wheel size", 28), _a("brake_type", "Brake type", "Disc")),
             _axis((48, 1199.0), (52, 1199.0), (56, 1229.0)), "frame_cm", (("style", "electric"),)),
        _row("BIKKID", "Kids Bike with Stabilizers", _W, (*BIKES, "Kids Bikes"), "Bicycle", 119.0, "bicycle",
             "A steel kids bicycle with a single gear, a front basket and removable stabilizers. In three wheel sizes: 16, 20 and 24 inches.",
             (RED, BLUE, YELLOW, GREEN),
             (_a("bike_type", "Bike type", "Kids"), _a("frame_material", "Frame material", "Steel"),
              _count("gears", "Gears", 1), _a("brake_type", "Brake type", "Coaster")),
             _axis((16, 119.0), (20, 139.0), (24, 159.0)), "wheel_size_in", (("style", "kids"),)),
    ),
)  # fmt: skip
