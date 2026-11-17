"""School Backpacks (gen#969, slice 3): Office & school > Bags & cases > School backpacks.

A breadth type: ``derivable`` True, so the scaled build draws more backpacks from these four by
the values their titles show (the capacity and the style). It is its own product type, apart from
Clothing's ``Backpack`` accessories. The color is the bag's; the style draws a classic, laptop,
rolling or mini bag (:func:`kit_office.school_backpack`). A backpack is sold singly, so each SKU
is a color.
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.office_rows import (
    BACKPACKS,
    BLUE,
    CALDERBY,
    DEPARTMENT,
    LANTERNBY,
    RED,
    THISTLE,
    decoy,
    packs,
    row,
)
from synthetic_ecommerce_data.domains.retail.type_registry import Decoy, TypeSpec, a


def _bag(style: str, litres: str) -> tuple[tuple, ...]:
    """The capacity in litres (``LTR``), its canonical value in millilitres, as every other ``capacity``."""
    return (a("backpack_style", "Backpack style", style), ("capacity", "Capacity", litres, "LTR", float(litres) * 1000),
            a("material", "Material", "Polyester"))  # fmt: skip


ROWS = (
    row("SBPC20", "20 L Classic School Backpack", CALDERBY, BACKPACKS, "School Backpack", "school_backpack",
        "A padded school backpack with a zipped main compartment, a front pocket for pens and a side pocket for a bottle.",
        _bag("Classic", "20"), packs((1, 22.0)), (("backpack_style", "classic"),)),
    row("SBPL25", "25 L Laptop School Backpack", LANTERNBY, BACKPACKS, "School Backpack", "school_backpack",
        "A school backpack with a padded laptop sleeve, a front organizer pocket and cushioned shoulder straps.",
        _bag("Laptop", "25"), packs((1, 32.0)), (("backpack_style", "laptop"),)),
    row("SBPR30", "30 L Rolling School Backpack", THISTLE, BACKPACKS, "School Backpack", "school_backpack",
        "A school backpack on two wheels with a telescopic handle, for heavy books on the walk to school.",
        _bag("Rolling", "30"), packs((1, 45.0)), (("backpack_style", "rolling"),)),
    row("SBPM15", "15 L Mini School Backpack", THISTLE, BACKPACKS, "School Backpack", "school_backpack",
        "A small school backpack for younger pupils, with a name tag window and a reflective strip.",
        _bag("Mini", "15"), packs((1, 16.0)), (("backpack_style", "mini"),)),
)

SPEC = TypeSpec(
    key="school_backpack",
    department=DEPARTMENT,
    product_type="School Backpack",
    derivable=True,
    rows=ROWS,
    decoys=(
        Decoy(4, "red backpack", "vocabulary", decoy(ROWS[0], "SBPRDZ", "20 L Classic School Backpack with Red Zips",
              "A blue padded school backpack with red zips and a front pocket for pens.", BLUE)),
        Decoy(6, "green backpack", "generic", decoy(ROWS[1], "SBPGVL", "Green Valley 25 L Laptop School Backpack",
              "From the Green Valley range: a red school backpack with a padded laptop sleeve.", RED)),
    ),
)  # fmt: skip
