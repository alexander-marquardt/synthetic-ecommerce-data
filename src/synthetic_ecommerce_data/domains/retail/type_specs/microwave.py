"""Microwave (#1116): the oven, so ``microwave`` meets microwaves before microwave meals.

**Home > Small Appliances > Microwaves** holds solo, grill and combination worktop microwaves,
one style per brand or design, each sold in the six main colors and by its capacity in litres,
where UK retailers shelve a worktop microwave. Before it ``microwave`` met only ready meals and
porridge that say "microwave" on the pack. :mod:`kit_household_appliances` draws the microwave
its type states. Not derivable: the range is authored.
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail import (
    kit_household_appliances,  # noqa: F401 -- registers microwave
)
from synthetic_ecommerce_data.domains.retail.kitchen_appliance_rows import (
    DEPARTMENT,
    decoy,
    litres,
    table,
)
from synthetic_ecommerce_data.domains.retail.type_registry import Decoy, TypeSpec

#: Each type: its price, its description and its capacities, each at its price.
KINDS = {
    "Solo": (69.0, "An 800 W microwave with a glass turntable, five power levels and a defrost setting by weight.",
             litres((20.0, 69.0), (23.0, 79.0))),
    "Grill": (99.0, "A 900 W microwave with a 1000 W grill element in its roof for browning, and a rack to grill on.",
              litres((23.0, 99.0), (25.0, 119.0))),
    "Combination": (189.0, "A microwave with a browning element and a fan oven in one, which bakes and roasts as well as reheats.",
                    litres((25.0, 189.0), (30.0, 229.0))),
}
DESIGNS = ("Digital", "Dial", "Touch Control", "Flatbed", "Retro", "Compact")

ROWS = table("MCW", "Microwaves", "Microwave", "microwave", "microwave_type", "Microwave type",
             KINDS, "design", "Design", DESIGNS, "capacity_l")

SPEC = TypeSpec(
    key="microwave",
    department=DEPARTMENT,
    product_type="Microwave",
    rows=ROWS,
    decoys=(
        Decoy(2, "microwave rice", "category", decoy(ROWS[0], "MCWRCE", f"{ROWS[0].title} with a Rice Cooking Setting",
              "A solo microwave with a setting that cooks rice in a covered bowl: a microwave, not a pouch of rice.")),
    ),
)  # fmt: skip
