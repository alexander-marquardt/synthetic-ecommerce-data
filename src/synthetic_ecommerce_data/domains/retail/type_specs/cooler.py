"""Cooler (gen#959, slice 3): Sports & Outdoors > Camping > Coolers.

A breadth type: ``derivable`` True, so the scaled build draws more coolers by the values the titles
show (the use, the type and the ice retention). The box is the SKU's color; the type draws a hard box with latches, a soft bag with a strap or a box on wheels with a tow handle (:func:`kit_outdoor_winter.cooler`). Each SKU is a color in a capacity in litres.
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.outdoor_winter_rows import COOLERS
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


def _attrs(cooler_use: str, cooler_type: str, ice_retention: str) -> tuple[tuple, ...]:
    return (
        _a("cooler_use", "Cooler use", cooler_use),
        _a("cooler_type", "Cooler type", cooler_type),
        _a("ice_retention", "Ice retention", ice_retention),
    )


SPEC = TypeSpec(
    key="cooler",
    department="Sports & Outdoors",
    product_type="Cooler",
    derivable=True,
    rows=(
        _row("CLRCHF", "Camp Hard Cooler with 5-Day Ice Retention", _W, COOLERS, "Cooler", 149.0, "cooler",
             "Hard cooler with thick foam walls, a gasket lid and two latches that keep ice for days at a campsite.",
             (WHITE, BLUE, RED, GREEN), _attrs("Camp", "Hard", "5-Day"),
             _axis((25, 129.0), (45, 149.0), (65, 179.0)), "capacity_l", (("cooler_type", "hard"),)),
        _row("CLRBST", "Beach Soft Cooler with 2-Day Ice Retention", _H, COOLERS, "Cooler", 39.0, "cooler",
             "Soft cooler bag with a leakproof liner, a zip top and a shoulder strap, for a day at the beach.",
             (YELLOW, BLUE, RED, BLACK), _attrs("Beach", "Soft", "2-Day"),
             _axis((12, 34.0), (20, 39.0), (30, 45.0)), "capacity_l", (("cooler_type", "soft"),)),
        _row("CLRMWS", "Marine Wheeled Cooler with 7-Day Ice Retention", _L, COOLERS, "Cooler", 189.0, "cooler",
             "Wheeled cooler with a tow handle, a drain plug and a lid that seats on a gasket, for a long day on a boat.",
             (WHITE, BLACK, YELLOW, GREEN), _attrs("Marine", "Wheeled", "7-Day"),
             _axis((45, 179.0), (60, 189.0), (75, 209.0)), "capacity_l", (("cooler_type", "wheeled"),)),
        _row("CLRCST", "Camp Soft Cooler with 3-Day Ice Retention", _L, COOLERS, "Cooler", 59.0, "cooler",
             "Soft cooler with a closed-cell foam liner, a wide zip lid and a carry handle, for camping and picnics.",
             (GREEN, BLACK, RED, BLUE), _attrs("Camp", "Soft", "3-Day"),
             _axis((15, 52.0), (24, 59.0)), "capacity_l", (("cooler_type", "soft"),)),
    ),
)  # fmt: skip
