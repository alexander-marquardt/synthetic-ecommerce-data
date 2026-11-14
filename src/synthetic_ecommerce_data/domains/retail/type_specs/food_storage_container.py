"""Food Storage Container (gen#963, slice 2): the material and the lid vary.

**Home > Storage > Food Storage** holds sets of food storage containers in glass, plastic,
stainless steel and collapsible silicone, one style per brand that sells them. A set is sold by
its piece count (each container and each lid is a piece), and its lids come in the six main
colors. A derivable breadth type: the scaled build draws more styles from these rows, and
:mod:`kit_bedding_storage` draws the material of the boxes.
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.bedding_storage_rows import (
    DEPARTMENT,
    KITCHEN_BRANDS,
    decoy,
    table,
)
from synthetic_ecommerce_data.domains.retail.type_registry import Decoy, TypeSpec


def _pieces(*pairs: tuple[int, float]) -> tuple[tuple[str, float], ...]:
    """A set's piece counts, each at its price."""
    return tuple((str(n), p) for n, p in pairs)


#: Each material: its price, its description and its piece counts, each at its price.
KINDS = {
    "Glass": (29.0, "Oven-safe borosilicate glass containers for leftovers and meal prep, that go from the freezer to the microwave.", _pieces((10, 29.0), (18, 45.0), (24, 59.0))),
    "Plastic": (15.0, "Light BPA-free plastic containers that stack and nest, safe in the dishwasher, the microwave and the freezer.", _pieces((10, 15.0), (20, 24.0), (30, 32.0))),
    "Stainless Steel": (35.0, "Stainless steel containers that keep no smell or stain, for lunches, snacks and the fridge.", _pieces((6, 35.0), (10, 49.0), (14, 62.0))),
    "Silicone": (25.0, "Collapsible silicone containers that fold flat into a drawer when empty and pop open to fill.", _pieces((8, 25.0), (12, 34.0), (16, 42.0))),
}
LIDS = ("Snap-Lock", "Airtight", "Leakproof", "Vented")
PATH = ("Home", "Storage", "Food Storage")

ROWS = table("FSC", KITCHEN_BRANDS, PATH, "Food Storage Container", "food_storage",
             ("container_material", "Container material"), KINDS, ("lid_type", "Lid type"), LIDS,
             "piece_count")

SPEC = TypeSpec(
    key="food_storage_container",
    department=DEPARTMENT,
    product_type="Food Storage Container",
    derivable=True,
    rows=ROWS,
    decoys=(
        Decoy(2, "lunch box", "category", decoy(ROWS[1], "FSCLUN", f"{ROWS[1].title} for Lunch Box Packing",
              "Small containers sized to sit inside a lunch box; the lunch box itself is not included.")),
        Decoy(6, "bread bin", "generic", decoy(ROWS[4], "FSCBRD", f"Breadbin Row {ROWS[4].title}",
              "From the Breadbin Row range: a set of food storage containers, with no bread bin.")),
    ),
)  # fmt: skip
