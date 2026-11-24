"""Vacuum Cleaner (#1116): the floor-care machine, so ``vacuum cleaner`` meets no floor cleaner.

**Home > Small Appliances > Vacuum Cleaners** holds upright, cylinder, cordless stick, handheld
and robot vacuums, one style per brand or design, each sold in the six main colors. Before it the
catalog's only "cleaner" for a floor was the liquid floor cleaner. :mod:`kit_household_appliances`
draws the vacuum its type states. Not derivable: the range is authored.
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail import (
    kit_household_appliances,  # noqa: F401 -- registers vacuum_cleaner
)
from synthetic_ecommerce_data.domains.retail.kitchen_appliance_rows import (
    DEPARTMENT,
    decoy,
    table,
)
from synthetic_ecommerce_data.domains.retail.type_registry import Decoy, TypeSpec

#: Each type: its price, its description and its sizes (none: one SKU per color).
KINDS = {
    "Upright": (149.0, "An upright with a 2 litre dust bin, a brush bar for carpets that switches off for hard floors, and a 9 m cord.", ()),
    "Cylinder": (119.0, "A cylinder on wheels with a 1.5 litre bin, a hose, a telescopic wand and a crevice tool for stairs.", ()),
    "Cordless Stick": (199.0, "A light stick vacuum on a 40-minute battery whose motor lifts off its wand for stairs, with a wall dock that charges it.", ()),
    "Handheld": (49.0, "A small battery vacuum for the car, the sofa and spills, with a crevice nozzle and a washable filter.", ()),
    "Robot": (249.0, "A round robot that maps the rooms, cleans on a schedule set in its app and returns to its dock to charge.", ()),
}
DESIGNS = ("Bagless", "Pet", "Lightweight", "Allergy", "Compact", "Multi Floor")

ROWS = table("VAC", "Vacuum Cleaners", "Vacuum Cleaner", "vacuum_cleaner", "vacuum_type",
             "Vacuum type", KINDS, "design", "Design", DESIGNS)

SPEC = TypeSpec(
    key="vacuum_cleaner",
    department=DEPARTMENT,
    product_type="Vacuum Cleaner",
    rows=ROWS,
    decoys=(
        Decoy(2, "vacuum bags", "category", decoy(ROWS[0], "VACBAG", f"{ROWS[0].title} with No Vacuum Bags Needed",
              "A bagless upright that empties its bin into the bin: a vacuum cleaner, not a pack of bags.")),
    ),
)  # fmt: skip
