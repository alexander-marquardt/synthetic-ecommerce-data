"""Sheet Set (gen#963, slice 2): the material and the pocket depth vary.

**Home > Bedding > Sheets** holds sheet sets in cotton percale, cotton sateen, microfiber,
bamboo, linen and flannel, one style per brand that sells them. A set is a flat sheet, a fitted
sheet and two pillowcases, sold by bed size in the six main colors. A derivable breadth type: the
scaled build draws more styles from these rows, and :mod:`kit_bedding_storage` draws the
material's texture.
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.bedding_storage_rows import (
    BEDDING_BRANDS,
    DEPARTMENT,
    decoy,
    table,
)
from synthetic_ecommerce_data.domains.retail.class_model import BED_SIZES
from synthetic_ecommerce_data.domains.retail.type_registry import Decoy, TypeSpec


def _beds(single: float, step: float) -> tuple[tuple[str, float], ...]:
    """The four bed sizes, each a step dearer than the last."""
    return tuple((b, single + n * step) for n, b in enumerate(BED_SIZES))


#: Each material: its price, its description and its bed sizes, each at its price.
KINDS = {
    "Cotton Percale": (39.0, "Crisp, cool bed sheets in a 200 thread count cotton percale weave: a flat sheet, a fitted sheet and two pillowcases.", _beds(39.0, 10.0)),
    "Cotton Sateen": (49.0, "Bed sheets in a 400 thread count cotton sateen with a soft sheen: a flat sheet, a fitted sheet and two pillowcases.", _beds(49.0, 12.0)),
    "Microfiber": (22.0, "Brushed microfiber bed sheets that resist wrinkles and dry quickly: a flat sheet, a fitted sheet and two pillowcases.", _beds(22.0, 6.0)),
    "Bamboo": (55.0, "Bed sheets woven from bamboo viscose, smooth and breathable for warm sleepers: a flat sheet, a fitted sheet and two pillowcases.", _beds(55.0, 12.0)),
    "Linen": (89.0, "Stonewashed linen bed sheets with a relaxed texture that softens with every wash: a flat sheet, a fitted sheet and two pillowcases.", _beds(89.0, 20.0)),
    "Flannel": (35.0, "Warm brushed cotton flannel bed sheets for cold nights: a flat sheet, a fitted sheet and two pillowcases.", _beds(35.0, 8.0)),
}
POCKETS = ("Standard Pocket", "Deep Pocket", "Extra Deep Pocket")
PATH = ("Home", "Bedding", "Sheets")

ROWS = table("SHT", BEDDING_BRANDS, PATH, "Sheet Set", "sheet_set", ("sheet_material", "Sheet material"),
             KINDS, ("pocket_depth", "Pocket depth"), POCKETS, "bed_size")

SPEC = TypeSpec(
    key="bed_sheet",
    department=DEPARTMENT,
    product_type="Sheet Set",
    derivable=True,
    rows=ROWS,
    decoys=(
        Decoy(2, "pillowcases", "category", decoy(ROWS[0], "SHTPCS", f"{ROWS[0].title} with Two Pillowcases",
              "A sheet set whose two pillowcases come in the pack; the pillowcases are not sold apart.")),
        Decoy(6, "duvet", "generic", decoy(ROWS[6], "SHTDUV", f"Duvet Lane {ROWS[6].title}",
              "From the Duvet Lane range: a flat sheet, a fitted sheet and two pillowcases, with no duvet.")),
    ),
)  # fmt: skip
