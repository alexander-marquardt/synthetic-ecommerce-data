"""Food Wrap (gen#962 slice 2): Cleaning > Bags & Wraps > Food Wrap.

A breadth type: ``derivable`` True, so the scaled build draws more rolls from these four by the
values their titles show (the grade, the material and the roll). A roll of wrap is sold without a
color (``colorless``), the declared exception to the six main colors of gen#275: its color is its
material's. Each SKU is a pack of 1, 2 or 3 rolls. :func:`kit_bags_wrap.wrap_box` draws the box
and a sheet of the wrap pulled over its cutting edge.
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.bags_wrap_rows import WRAP, lowered, wrap
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
    """Packs of 1, 2 and 3 rolls, priced up from ``base``."""
    return packs(*((n, round(base * f, 2)) for n, f in ((1, 1.0), (2, 1.9), (3, 2.7))))


def _params(grade: str, material: str, roll: str) -> tuple[tuple[str, str], ...]:
    return lowered(("grade", grade), ("material", material), ("roll", roll))


ROWS = (
    row("FWHDAF", "Heavy Duty Aluminum Foil, Jumbo Roll", HOLLINSBY, WRAP, "Food Wrap", "wrap_box",
        "Heavy Duty Aluminum Foil on a Jumbo Roll, in a box with a cutting edge that tears a clean sheet.",
        wrap("Heavy Duty", "Aluminum Foil", "Jumbo"), _packs(5.5), _params("Heavy Duty", "Aluminum Foil", "Jumbo")),
    row("FWEVPW", "Everyday Plastic Wrap, Regular Roll", MOSSDOWN, WRAP, "Food Wrap", "wrap_box",
        "Everyday Plastic Wrap on a Regular Roll that covers bowls and plates and keeps leftovers fresh.",
        wrap("Everyday", "Plastic Wrap", "Regular"), _packs(2.5), _params("Everyday", "Plastic Wrap", "Regular")),
    row("FWEWPP", "Extra Wide Parchment Paper, Large Roll", FEATHERLEE, WRAP, "Food Wrap", "wrap_box",
        "Extra Wide Parchment Paper on a Large Roll, wide enough to cover a whole tray in one sheet.",
        wrap("Extra Wide", "Parchment Paper", "Large"), _packs(3.8), _params("Extra Wide", "Parchment Paper", "Large")),
    row("FWEVWP", "Everyday Wax Paper, Regular Roll", MOSSDOWN, WRAP, "Food Wrap", "wrap_box",
        "Everyday Wax Paper on a Regular Roll for wrapping sandwiches and covering a dish.",
        wrap("Everyday", "Wax Paper", "Regular"), _packs(2.8), _params("Everyday", "Wax Paper", "Regular")),
)

SPEC = TypeSpec(
    key="food_wrap",
    department=DEPARTMENT,
    product_type="Food Wrap",
    derivable=True,
    rows=ROWS,
    owners=OWNERS,
    decoys=(
        Decoy(4, "aluminum foil", "vocabulary", decoy(ROWS[2], "FWOVLN", "Oven Liner Extra Wide Parchment Paper, Large Roll",
              "Parchment paper that lines a baking tray in place of aluminum foil.")),
        Decoy(6, "wax paper", "generic", decoy(ROWS[0], "FWWXLN", "Wax Lane Heavy Duty Aluminum Foil, Jumbo Roll",
              "From the Wax Lane range: heavy duty aluminum foil, with no wax coating.")),
    ),
)  # fmt: skip
