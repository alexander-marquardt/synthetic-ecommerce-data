"""Walking sticks (gen#968, slice 3): Health > Mobility Aids > Walking Sticks.

A breadth type (``derivable``): the scaled build draws more sticks by swapping the handle the
title shows. Each style is one SKU. The drawing is a stick on its rubber tip with a crook, derby,
offset or T handle by the row's handle (:func:`kit_health_care.walking_stick`). No stick is
white: a white cane is a sign for sight loss, not a product colour.
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail import (
    kit_health_care,  # noqa: F401 -- registers walking_stick
)
from synthetic_ecommerce_data.domains.retail.health_rows import (
    BLUE,
    GREY,
    HALVERING,
    OWNERS,
    QUELLMOOR,
    ROOT,
    THRENNICK,
    VELLING,
    decoy,
    row,
)
from synthetic_ecommerce_data.domains.retail.type_registry import Decoy, TypeSpec, a, cw

_PATH = (ROOT, "Mobility Aids", "Walking Sticks")
BROWN = cw("Brown", "#8a5a36", "solid", "#ffffff")
BLACK = cw("Black", "#2e2f33", "solid", "#ffffff")


def _stick(code, title, brand, handle, material, price, desc, color) -> object:  # noqa: ANN001
    return row(code, title, brand, _PATH, "Walking Sticks", "walking_stick", desc,
               (a("handle_type", "Handle", handle), a("material", "Material", material)),
               ("handle", handle.lower()), price=price, color=color)  # fmt: skip


ROWS = (
    _stick("HWSCRK", "Wooden Crook Walking Stick", VELLING, "Crook", "Wood", 18.0,
           "A classic beech crook stick with a rubber tip, cut to a standard length.", BROWN),
    _stick("HWSDRB", "Adjustable Derby Walking Stick", QUELLMOOR, "Derby", "Aluminium", 22.0,
           "A light aluminium stick with a shaped derby handle and ten height settings.", BLACK),
    _stick("HWSOFS", "Adjustable Offset Walking Stick", HALVERING, "Offset", "Aluminium", 20.0,
           "The offset shaft puts the hand over the rubber tip, with ten height settings.", GREY),
    _stick("HWSFLD", "Folding T-Handle Walking Stick", THRENNICK, "T-Handle", "Aluminium", 24.0,
           "Folds into four sections for a bag, with a wrist strap and a rubber tip.", BLUE),
    _stick("HWSDRW", "Wooden Derby Walking Stick", THRENNICK, "Derby", "Wood", 26.0,
           "A dark-stained ash stick with a derby handle and a brass collar.", BROWN),
)  # fmt: skip

#: Text-match decoys: the title names a range holding the query's word, the fields say another
#: handle, so only a policy that reads ``handle_type`` puts the real sticks first.
DECOYS = (
    Decoy(6, "derby walking stick", "generic", decoy(
        ROWS[0], "HWSDY1", "Derby Lane Wooden Crook Walking Stick",
        "From the Derby Lane range: a beech crook stick with a rubber tip.")),
    Decoy(6, "crook walking stick", "generic", decoy(
        ROWS[3], "HWSDY2", "Crook Valley Folding T-Handle Walking Stick",
        "From the Crook Valley range: folds into four sections, with a wrist strap.")),
)  # fmt: skip

SPEC = TypeSpec(
    key="walking_sticks",
    department="Health",
    product_type="Walking Sticks",
    derivable=True,
    owners=OWNERS,
    rows=ROWS,
    decoys=DECOYS,
)
