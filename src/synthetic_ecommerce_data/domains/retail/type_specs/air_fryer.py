"""Air Fryer (gen#963, slice 1): the type of fryer and its controls vary.

**Home > Small Appliances > Air Fryers** holds single-basket, dual-basket, viewing-window and
rotisserie fryers, one style per brand that sells them. Each style is sold in the six main colors
and by its capacity in liters. A derivable breadth type: the scaled build draws more styles from
these rows, and :mod:`kit_kitchen_appliances` draws the fryer its type states.
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.kitchen_appliance_rows import (
    DEPARTMENT,
    OWNERS,
    decoy,
    litres,
    table,
)
from synthetic_ecommerce_data.domains.retail.type_registry import Decoy, TypeSpec

#: Each type: its price, its description and its capacities, each at its price.
KINDS = {
    "Single Basket": (59.0, "Crisps chips, wings and vegetables with little or no oil, with eight presets, a shake reminder and a non-stick basket that goes in the dishwasher.",
                      litres((4.2, 59.0), (5.5, 79.0))),
    "Dual Basket": (119.0, "Two drawers that cook two foods at once and finish together, each with a separate timer and temperature.",
                    litres((7.6, 119.0), (9.5, 149.0))),
    "Viewing Window": (69.0, "Watch the food crisp through the front of the drawer, with a light inside and a timer up to sixty minutes.",
                       litres((4.5, 69.0), (6.2, 89.0))),
    "Rotisserie": (129.0, "An oven-style fryer with a turning spit for a whole chicken and three racks for drying fruit.",
                   litres((10.0, 129.0), (12.0, 159.0))),
}
CONTROLS = ("Digital", "Dial", "Smart", "Touchscreen")

ROWS = table("AFR", "Air Fryers", "Air Fryer", "air_fryer", "air_fryer_type", "Air fryer type",
             KINDS, "controls", "Controls", CONTROLS, "capacity_l")

SPEC = TypeSpec(
    key="air_fryer",
    department=DEPARTMENT,
    product_type="Air Fryer",
    derivable=True,
    owners=OWNERS,
    rows=ROWS,
    decoys=(
        Decoy(2, "air fryer cookbook", "category", decoy(ROWS[0], "AFRBOK", f"{ROWS[0].title} with Recipe Cookbook Booklet",
              "An air fryer that comes with a printed recipe booklet; the cookbook is not sold apart.")),
        Decoy(6, "toaster", "generic", decoy(ROWS[4], "AFRTST", f"Toaster Hill {ROWS[4].title}",
              "From the Toaster Hill range: an air fryer with a timer and a cool-touch handle.")),
    ),
)  # fmt: skip
