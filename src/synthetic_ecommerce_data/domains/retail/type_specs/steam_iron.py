"""Steam Iron (#1116): a clothes iron, so ``iron`` meets irons as well as iron the metal.

**Home > Small Appliances > Irons** holds corded, cordless, steam generator and travel irons,
one style per brand or soleplate, each sold in the six main colors. ``steam iron`` finds only
these; the bare ``iron`` also meets cast iron pans, iron dumbbells and iron minerals, and a
category policy, not the data, picks the intent. :mod:`kit_household_appliances` draws the iron
its type states. Not derivable: the range is authored.
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail import (
    kit_household_appliances,  # noqa: F401 -- registers steam_iron
)
from synthetic_ecommerce_data.domains.retail.kitchen_appliance_rows import (
    DEPARTMENT,
    decoy,
    table,
)
from synthetic_ecommerce_data.domains.retail.type_registry import Decoy, TypeSpec

#: Each type: its price, its description and its sizes (none: one SKU per color).
KINDS = {
    "Standard": (29.0, "A 2600 W corded iron with a 300 ml water tank, a steam shot for creases, a vertical steam setting and an anti-drip valve.", ()),
    "Cordless": (49.0, "An iron that lifts off its charging base, heated in seconds when you set it back, with a 250 ml tank and no cord to drag across the board.", ()),
    "Steam Generator": (159.0, "An iron fed by a 1.5 litre water tank in its base through a hose, with steady high-pressure steam for a whole basket of shirts.", ()),
    "Travel": (19.0, "A small dual-voltage iron with a folding handle and a 60 ml tank, for a suitcase.", ()),
}
SOLEPLATES = ("Ceramic", "Stainless Steel", "Non-Stick", "Titanium", "Anodised", "Ceramic Glide")

ROWS = table("IRN", "Irons", "Steam Iron", "steam_iron", "iron_type", "Iron type", KINDS,
             "soleplate", "Soleplate", SOLEPLATES)

SPEC = TypeSpec(
    key="steam_iron",
    department=DEPARTMENT,
    product_type="Steam Iron",
    rows=ROWS,
    decoys=(
        Decoy(2, "ironing board", "category", decoy(ROWS[0], "IRNBRD", f"{ROWS[0].title} with a Heel Rest for Ironing Boards",
              "A corded steam iron that stands on its heel at the end of the board: an iron, not an ironing board.")),
    ),
)  # fmt: skip
