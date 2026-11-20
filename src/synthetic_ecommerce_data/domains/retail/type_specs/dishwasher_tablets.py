"""Dishwasher Tablets (gen#962 slice 3): Cleaning > Kitchen & Surfaces > Dishwasher Tablets.

A breadth type: ``derivable`` True, so the scaled build draws more boxes from these four by the
values their titles show (the formula, the scent and the tablet count). A box of tablets is sold
without a color (``colorless``), the declared exception to the six main colors of gen#275 that a
roll of white paper takes in slice 1. Each SKU is a pack of 1, 2 or 3 boxes.
:func:`kit_cleaning_care.tablet_box` draws the box and one tablet before it.
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.bags_wrap_rows import lowered
from synthetic_ecommerce_data.domains.retail.cleaning_care_rows import TABLETS, tablet
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
    """Packs of 1, 2 and 3 boxes, priced up from ``base``."""
    return packs(*((n, round(base * f, 2)) for n, f in ((1, 1.0), (2, 1.9), (3, 2.7))))


def _params(formula: str, scent: str, count: str) -> tuple[tuple[str, str], ...]:
    return lowered(("formula", formula), ("scent", scent), ("tablet_count", count))


ROWS = (
    row("DTCLSR", "Classic Dishwasher Tablets, Spring Rain, 30 Count", HOLLINSBY, TABLETS, "Dishwasher Tablets", "tablet_box",
        "Classic Dishwasher Tablets, 30 Count to a box, in Spring Rain. Each tablet goes in the dispenser whole.",
        tablet("Classic", "Spring Rain", "30 Count"), _packs(4.5), _params("Classic", "Spring Rain", "30 Count")),
    row("DTAOCB", "All in One Dishwasher Tablets, Clean Breeze, 50 Count", MOSSDOWN, TABLETS, "Dishwasher Tablets", "tablet_box",
        "All in One Dishwasher Tablets, 50 Count to a box, in Clean Breeze. One tablet runs one full wash.",
        tablet("All in One", "Clean Breeze", "50 Count"), _packs(8.0), _params("All in One", "Clean Breeze", "50 Count")),
    row("DTMCUN", "Max Clean Dishwasher Tablets, Unscented, 80 Count", FEATHERLEE, TABLETS, "Dishwasher Tablets", "tablet_box",
        "Max Clean Dishwasher Tablets, 80 Count to a box, in Unscented. Store the box closed and dry.",
        tablet("Max Clean", "Unscented", "80 Count"), _packs(14.0), _params("Max Clean", "Unscented", "80 Count")),
    row("DTQWSR", "Quick Wash Dishwasher Tablets, Spring Rain, 50 Count", HOLLINSBY, TABLETS, "Dishwasher Tablets", "tablet_box",
        "Quick Wash Dishwasher Tablets, 50 Count to a box, in Spring Rain. Each tablet goes in the dispenser whole.",
        tablet("Quick Wash", "Spring Rain", "50 Count"), _packs(7.0), _params("Quick Wash", "Spring Rain", "50 Count")),
)

SPEC = TypeSpec(
    key="dishwasher_tablets",
    department=DEPARTMENT,
    product_type="Dishwasher Tablets",
    derivable=True,
    rows=ROWS,
    owners=OWNERS,
    decoys=(
        Decoy(4, "rinse aid", "vocabulary", decoy(ROWS[0], "DTNORA", "No Rinse Aid Classic Dishwasher Tablets, Spring Rain, 30 Count",
              "Classic dishwasher tablets; there is no rinse aid in the box.")),
        Decoy(6, "classic dishwasher tablets", "generic", decoy(ROWS[2], "DTCLPT", "Classic Point Max Clean Dishwasher Tablets, Unscented, 80 Count",
              "From the Classic Point range: Max Clean tablets, not the plain formula.")),
    ),
)  # fmt: skip
