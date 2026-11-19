"""Food Storage Bags (gen#962 slice 2): Cleaning > Bags & Wraps > Food Storage Bags.

A breadth type: ``derivable`` True, so the scaled build draws more bags from these four by the
values their titles show (the closure, the kind and the size). A food bag is clear film and is sold
without a color (``colorless``), the declared exception to the six main colors of gen#275, as a
roll of white paper is; each SKU is a pack of 1, 2, 3, 4 or 6 boxes.
:func:`kit_bags_wrap.zip_bag` draws the bag lying flat, its seal and what it holds.
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.bags_wrap_rows import FOOD_BAGS, food_bag, lowered
from synthetic_ecommerce_data.domains.retail.paper_rows import (
    DEPARTMENT,
    FEATHERLEE,
    HOLLINSBY,
    MOSSDOWN,
    OWNERS,
    decoy,
    packs,
    row,
)
from synthetic_ecommerce_data.domains.retail.type_registry import Decoy, TypeSpec


def _packs(base: float) -> tuple[tuple[str, float], ...]:
    """Packs of 1, 2, 3, 4 and 6 boxes, priced up from ``base``."""
    return packs(*((n, round(base * f, 2)) for n, f in
                   ((1, 1.0), (2, 1.9), (3, 2.7), (4, 3.5), (6, 5.0))))  # fmt: skip


def _params(closure: str, kind: str, size: str) -> tuple[tuple[str, str], ...]:
    return lowered(("closure", closure), ("kind", kind), ("bag_size", size))


ROWS = (
    row("FSZSFR", "Zip Seal Freezer Bags, Large", FEATHERLEE, FOOD_BAGS, "Food Storage Bags", "zip_bag",
        "Freezer bags with a Zip Seal closure, in the Large size. Each box holds fifty bags.",
        food_bag("Zip Seal", "Freezer", "Large"), _packs(2.8), _params("Zip Seal", "Freezer", "Large")),
    row("FSSLSW", "Slider Sandwich Bags, Medium", MOSSDOWN, FOOD_BAGS, "Food Storage Bags", "zip_bag",
        "Sandwich bags with a Slider closure, in the Medium size. Clear film, so what is inside shows at a glance.",
        food_bag("Slider", "Sandwich", "Medium"), _packs(2.4), _params("Slider", "Sandwich", "Medium")),
    row("FSFTSN", "Fold Top Snack Bags, Small", HOLLINSBY, FOOD_BAGS, "Food Storage Bags", "zip_bag",
        "Snack bags with a Fold Top closure, in the Small size. Each box holds one hundred bags.",
        food_bag("Fold Top", "Snack", "Small"), _packs(1.6), _params("Fold Top", "Snack", "Small")),
    row("FSZSSW", "Zip Seal Sandwich Bags, Small", MOSSDOWN, FOOD_BAGS, "Food Storage Bags", "zip_bag",
        "Sandwich bags with a Zip Seal closure, in the Small size. The seal presses shut along its whole length.",
        food_bag("Zip Seal", "Sandwich", "Small"), _packs(2.0), _params("Zip Seal", "Sandwich", "Small")),
)

SPEC = TypeSpec(
    key="food_storage_bags",
    department=DEPARTMENT,
    product_type="Food Storage Bags",
    derivable=True,
    rows=ROWS,
    owners=OWNERS,
    decoys=(
        Decoy(4, "freezer bags", "vocabulary", decoy(ROWS[1], "FSNOFZ", "Thin Slider Sandwich Bags, Medium",
              "Sandwich bags of a thin film for a packed lunch: not freezer bags, they split in the cold.")),
        Decoy(6, "freezer bags", "generic", decoy(ROWS[2], "FSFZPT", "Freezer Point Fold Top Snack Bags, Small",
              "From the Freezer Point range: snack bags for the lunchbox, too thin for the cold.")),
    ),
)  # fmt: skip
