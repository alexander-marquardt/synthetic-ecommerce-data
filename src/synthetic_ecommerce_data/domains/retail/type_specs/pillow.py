"""Pillow (Home), registered by its spec (gen#537), deepened in gen#963 slice 2.

The microfiber pillow pair stays in the shared row module named by ``homes``. The rows here are
the range a shopper finds under **Home > Bedding > Pillows**: down alternative, memory foam,
shredded memory foam, cooling gel and feather pillows from plush to extra firm, one style per
brand that sells them, by pillow size. A pillow keeps its natural white cover
(``main_colors.EXCEPTIONS``), so :mod:`kit_bedding_storage`'s ``bed_pillow`` shape draws the fill
and the support instead: in a white grid, a pillow that drew every fill alike shared its tile
with most of the leaf. A derivable breadth type: the scaled build draws more styles from these
rows.
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.bedding_storage_rows import (
    DEPARTMENT,
    PILLOW_BRANDS,
    ChartRow,
    decoy,
    table,
)
from synthetic_ecommerce_data.domains.retail.type_registry import Decoy, Home, TypeSpec


def _pillows(standard: float, step: float) -> tuple[tuple[str, float], ...]:
    """The standard, the square and the king pillow (``variants.PILLOWS``), the square half a
    step dearer and the king a step: entries of the bedding chart, which every SKU states in UK,
    EU and US sizes."""
    return (("Standard Pillow", standard), ("Square Pillow", standard + step / 2),
            ("King Pillow", standard + step))  # fmt: skip


#: Each fill: its price, its description and its pillow sizes, each at its price.
KINDS = {
    "Down Alternative": (19.0, "A hypoallergenic pillow filled with a down-alternative cluster fiber, in a cotton cover that goes in the washing machine.", _pillows(19.0, 6.0)),
    "Memory Foam": (39.0, "A solid memory foam pillow that molds to the head and neck and springs back, in a removable bamboo cover.", _pillows(39.0, 10.0)),
    "Shredded Memory Foam": (35.0, "A pillow of shredded memory foam with a zip to add or take out fill, so its loft can be set by hand.", _pillows(35.0, 8.0)),
    "Cooling Gel": (45.0, "A memory foam pillow topped with a cooling gel layer that draws heat away through the night.", _pillows(45.0, 10.0)),
    "Feather": (25.0, "A traditional pillow of duck feathers in a downproof cotton cover, plump and easy to shape.", _pillows(25.0, 7.0)),
}
#: Five supports, so no two of the eleven brands share a fill and a support (a title).
SUPPORTS = ("Plush", "Soft", "Medium", "Firm", "Extra Firm")
PATH = ("Home", "Bedding", "Pillows")

ROWS = table("PLW", PILLOW_BRANDS, PATH, "Pillow", "bed_pillow", ("pillow_fill", "Pillow fill"),
             KINDS, ("support", "Support"), SUPPORTS, "size_eu", white_only=True,
             design_param="support", row_type=ChartRow)

SPEC = TypeSpec(
    key="pillow",
    department=DEPARTMENT,
    product_type="Pillow",
    derivable=True,
    rows=ROWS,
    homes=(Home("samples", True),),
    decoys=(
        Decoy(2, "pillowcase", "category", decoy(ROWS[0], "PLWPCS", f"{ROWS[0].title} in a Zip Pillowcase Cover",
              "A pillow that comes inside a zipped cotton cover; the pillowcase is not sold apart.")),
        Decoy(6, "cushion", "generic", decoy(ROWS[7], "PLWCSH", f"Cushion Hill {ROWS[7].title}",
              "From the Cushion Hill range: a bed pillow for sleeping, not a sofa cushion.")),
    ),
)  # fmt: skip
