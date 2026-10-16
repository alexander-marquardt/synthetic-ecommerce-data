"""Impact drivers at 12, 18 and 20 V (gen#191, the issue's comment): a quarter-inch hex bit holder, a
torque in newton metres and the battery kit stated in the title and drawn by
:func:`kit_drills.impact_driver` (bare tool, one battery, two batteries)."""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

import diy_tools as d
from type_registry import TypeSpec

ROWS = d.styles(
    (
        (
            "IMPT12",
            "12 V Cordless Impact Driver, Bare Tool",
            d.TOR,
            49.0,
            "A compact impact driver with a quarter-inch hex bit holder. Battery and charger sold separately.",
            (*d.cordless(12), *d.impact(110, "Bare tool")),
            (("batteries", "0"),),
        ),
        (
            "IMPH18",
            "18 V Cordless Impact Driver with One Battery",
            d.HAR,
            79.0,
            "An impact driver with a quarter-inch hex bit holder, a work light and a fast charger.",
            (*d.cordless(18), *d.impact(180, "1 battery")),
            (("batteries", "1"),),
        ),
        (
            "IMPS20",
            "20 V Brushless Cordless Impact Driver with Two Batteries",
            d.STO,
            129.0,
            "A brushless impact driver with a quarter-inch hex bit holder and a spare battery.",
            (*d.cordless(20, "Brushless"), *d.impact(220, "2 batteries")),
            (("batteries", "2"),),
        ),
        (
            "IMPB18",
            "18 V Cordless Impact Driver, Bare Tool",
            d.BRI,
            59.0,
            "An impact driver with a quarter-inch hex bit holder. Battery and charger sold separately.",
            (*d.cordless(18), *d.impact(160, "Bare tool")),
            (("batteries", "0"),),
        ),
    ),
    "Impact Driver",
    "impact_driver",
    d.DRILLS + ("Impact Drivers",),
)

SPEC = TypeSpec(
    key="impact_driver",
    department=d.HOME,
    product_type="Impact Driver",
    rows=ROWS,
    decoys=d.decoys(
        ROWS[1], "impact driver", ("DCIDHM", "Impact Driver, Hammer Free", "hammer impact driver")
    ),
    owners=d.OWNERS,
)
