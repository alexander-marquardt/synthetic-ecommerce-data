"""Blender (gen#963, slice 1): the type of blender and its design vary.

**Home > Small Appliances > Blenders** holds jug blenders, personal blenders and hand blenders,
one style per brand that sells them. Each style is sold in the six main colors, one SKU per color.
A derivable breadth type: the scaled build draws more styles from these rows, and
:mod:`kit_kitchen_appliances` draws the blender its type states.
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
    "Jug": (49.0, "A 1.5 L jar on a 1000 W motor base, with four speeds, a pulse setting and blades that crush ice.", ()),
    "Personal": (29.0, "Blends a smoothie straight into a cup you drink from, with a travel lid and a one-touch motor.", ()),
    "Hand": (29.0, "A stick with a stainless steel foot for soups and sauces in the pan, with a beaker and a whisk attachment.", ()),
}
DESIGNS = ("Classic", "Compact", "Pro", "Digital", "Retro")

ROWS = table("BLN", "Blenders", "Blender", "blender", "blender_type", "Blender type", KINDS,
             "design", "Design", DESIGNS)

SPEC = TypeSpec(
    key="blender",
    department=DEPARTMENT,
    product_type="Blender",
    derivable=True,
    owners=OWNERS,
    rows=ROWS,
    decoys=(
        Decoy(2, "blender bottle", "category", decoy(ROWS[1], "BLNBTL", f"{ROWS[1].title} with a Travel Bottle Lid",
              "Blends a smoothie into a cup with a travel lid: a blender, not a shaker bottle.")),
        Decoy(6, "mixer", "generic", decoy(ROWS[0], "BLNMIX", f"Mixer Hill {ROWS[0].title}",
              "From the Mixer Hill range: a jar on a motor base with four speeds and a pulse setting.")),
    ),
)  # fmt: skip
