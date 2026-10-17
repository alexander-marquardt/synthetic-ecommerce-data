"""Sleeping Bag (gen#265, moved to a spec by gen#351 and gen#455): Camping: a bag's length in centimetres is the SKU axis.

The styles are templates only (``derivable`` False): the department grows by authored rows.
:mod:`kit_sports` draws them.
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from sports_helpers import (
    _CAMP,
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
    _season,
)
from type_registry import TypeSpec


def _lengths(base: float) -> tuple[tuple[str, float], ...]:
    """A sleeping bag's SKU lengths in centimetres (a measured axis, no garment size), and the
    price at each."""
    return _axis((190, base), (210, base + 6.0))


SPEC = TypeSpec(
    key="sleeping_bag",
    department="Sports & Outdoors",
    product_type="Sleeping Bag",
    rows=(
        _row("SLPMUM", "Three Season Mummy Sleeping Bag", _W, (*_CAMP, "Sleeping Bags"), "Sleeping Bag",
             39.0, "sleeping_bag", "A tapered mummy bag with a hood and a two-way zip, warm enough for "
             "spring to autumn camping and light to carry.",
             (BLUE, GREEN, YELLOW, RED),
             (_a("bag_shape", "Bag shape", "Mummy"), _season(3), _a("fill", "Fill", "Hollow Fibre"),
              _a("material", "Material", "Polyester")),
             _lengths(39.0), "length_cm", (("style", "mummy"),)),
        _row("SLPWIN", "Four Season Mummy Sleeping Bag", _H, (*_CAMP, "Sleeping Bags"), "Sleeping Bag",
             79.0, "sleeping_bag", "A snug mummy bag with a draught collar and a deep hood for cold "
             "nights, packing into its own stuff sack.",
             (BLACK, WHITE, BLUE, GREEN),
             (_a("bag_shape", "Bag shape", "Mummy"), _season(4), _a("fill", "Fill", "Hollow Fibre"),
              _a("material", "Material", "Ripstop Nylon")),
             _lengths(79.0), "length_cm", (("style", "mummy"),)),
        _row("SLPRCT", "Two Season Rectangular Sleeping Bag", _L, (*_CAMP, "Sleeping Bags"),
             "Sleeping Bag", 24.0, "sleeping_bag", "A roomy rectangular bag that unzips flat to use as "
             "a quilt, for summer nights and sleepovers.",
             (RED, BLUE, GREEN, YELLOW),
             (_a("bag_shape", "Bag shape", "Rectangular"), _season(2), _a("fill", "Fill", "Hollow Fibre"),
              _a("material", "Material", "Polyester")),
             _lengths(24.0), "length_cm", (("style", "rectangular"),)),
    ),
)  # fmt: skip
