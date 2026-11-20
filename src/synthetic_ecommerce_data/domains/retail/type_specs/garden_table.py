"""Garden table (gen#961, slice 3): Garden > Garden Furniture > Garden Tables.

A breadth type: ``derivable`` True, so the scaled build draws more tables from these five by the
values their titles show (the style and the material). The style draws the top and the legs and
the material its surface marks (:func:`kit_garden_yard.garden_table`). Each SKU is a color times
a width in centimetres, and every style offers the six main colors (gen#275). The type's
text-match decoys (gen#294) are in :mod:`garden_rows`, with the other Garden types'.
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail import (
    kit_garden_yard,  # noqa: F401 -- registers garden_table
)
from synthetic_ecommerce_data.domains.retail.outdoor_helpers import (
    BLACK,
    BLUE,
    GREEN,
    RED,
    WHITE,
    YELLOW,
    H,
    L,
    M,
    V,
    W,
    a,
    axis,
    row,
)
from synthetic_ecommerce_data.domains.retail.type_registry import Home, TypeSpec

PATH = ("Garden", "Garden Furniture", "Garden Tables")
_PT = "Garden Table"
SIX = (RED, BLUE, GREEN, YELLOW, BLACK, WHITE)


def _table(code: str, style: str, material: str, brand: str, desc: str, sizes: tuple) -> object:
    attrs = (a("style", "Style", style), a("material", "Material", material))
    params = (("style", style.lower()), ("material", material.lower()))
    return row(code, f"{style} {material} Garden Table", brand, PATH, _PT, sizes[0][1], "garden_table",
               desc, SIX, attrs, sizes, "width_cm", params)  # fmt: skip


ROWS = (
    _table(
        "GTLBAC",
        "Bistro",
        "Acacia",
        V,
        "An acacia bistro table for two chairs on a balcony, with a hole for a parasol.",
        axis((60, 59.0), (70, 69.0), (80, 79.0)),
    ),
    _table(
        "GTLDAL",
        "Dining",
        "Aluminum",
        W,
        "An aluminum dining table with levelling feet, for a family meal on the patio.",
        axis((120, 189.0), (150, 229.0), (180, 269.0)),
    ),
    _table(
        "GTLSST",
        "Side",
        "Steel",
        H,
        "A steel side table to set a drink and a book beside a lounger.",
        axis((40, 29.0), (45, 34.0), (50, 39.0)),
    ),
    _table(
        "GTLFAC",
        "Folding",
        "Acacia",
        L,
        "An acacia folding table that packs flat for the shed between summers.",
        axis((80, 79.0), (100, 99.0), (120, 119.0)),
    ),
    _table(
        "GTLDST",
        "Dining",
        "Steel",
        M,
        "A steel dining table with a hole for a parasol, for lunch outside with friends.",
        axis((120, 159.0), (150, 199.0), (180, 239.0)),
    ),
)

SPEC = TypeSpec(
    key="garden_table",
    homes=(Home("garden_rows", False),),
    department="Garden",
    product_type=_PT,
    derivable=True,
    rows=ROWS,
)
