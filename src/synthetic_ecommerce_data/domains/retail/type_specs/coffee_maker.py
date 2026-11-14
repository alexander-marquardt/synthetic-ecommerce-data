"""Coffee Maker (gen#963, slice 1): the type of machine and its design vary.

**Home > Small Appliances > Coffee Makers** holds drip machines, espresso machines, pod machines,
bean-to-cup machines and cold-brew towers, one style per brand that sells them. Each style is
sold in the six main colors, one SKU per color. A derivable breadth type: the scaled build draws
more styles from these rows, and :mod:`kit_kitchen_appliances` draws the machine its type states.
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.kitchen_appliance_rows import (
    DEPARTMENT,
    OWNERS,
    decoy,
    table,
)
from synthetic_ecommerce_data.domains.retail.type_registry import Decoy, TypeSpec

#: Each type: its price, its description and its sizes (none: one SKU per color).
KINDS = {
    "Drip": (39.0, "Brews up to ten cups into a glass carafe that sits on a warming plate, with a reusable filter and a one-hour keep-warm.", ()),
    "Espresso": (149.0, "A 15-bar pump and a steam wand for frothed milk, with a cup warmer on top and a removable water tank.", ()),
    "Pod": (69.0, "Makes one cup at a time from a capsule in under a minute, with a side water tank and a fold-away cup stand.", ()),
    "Bean to Cup": (349.0, "Grinds fresh for every cup with a built-in conical grinder, a touch display and a milk system for lattes.", ()),
    "Cold Brew": (59.0, "Steeps ground coffee slowly in cold water through a glass tower, for a smooth concentrate that keeps in the fridge.", ()),
}
DESIGNS = ("Classic", "Retro", "Compact", "Digital", "Slimline")

ROWS = table("CFM", "Coffee Makers", "Coffee Maker", "coffee_maker", "coffee_maker_type",
             "Coffee maker type", KINDS, "design", "Design", DESIGNS)

SPEC = TypeSpec(
    key="coffee_maker",
    department=DEPARTMENT,
    product_type="Coffee Maker",
    derivable=True,
    owners=OWNERS,
    rows=ROWS,
    decoys=(
        Decoy(2, "coffee beans", "category", decoy(ROWS[3], "CFMBNS", f"{ROWS[3].title} for Whole Coffee Beans",
              "Grinds whole coffee beans fresh for every cup: the machine only, no beans included.")),
        Decoy(6, "teapot", "generic", decoy(ROWS[0], "CFMTEA", f"Teapot Lane {ROWS[0].title}",
              "From the Teapot Lane range: a ten-cup machine with a glass carafe and a warming plate.")),
    ),
)  # fmt: skip
