"""Garden chair (gen#961, slice 1): Garden > Garden Furniture > Garden Chairs.

A breadth type: ``derivable`` True, so the scaled build draws more chairs from these by the values
their titles show (the style and the material). The style draws the frame (crossed legs, straight
legs, a raked back or a slatted back) and the material its marks (:func:`kit_patio.garden_chair`).
Each SKU is a color in a single chair, a pair or a set of four, and every style offers the six
main colors (gen#275). The type's text-match decoys (gen#294) are in :mod:`garden_rows`.
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail import (
    kit_patio,  # noqa: F401 -- registers garden_chair
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
    packs,
    row,
)
from synthetic_ecommerce_data.domains.retail.type_registry import Home, TypeSpec

PATH = ("Garden", "Garden Furniture", "Garden Chairs")
_PT = "Garden Chair"
SIX = (RED, BLUE, GREEN, YELLOW, BLACK, WHITE)


def _chair(code: str, style: str, material: str, brand: str, desc: str, sizes: tuple) -> object:
    attrs = (a("style", "Style", style), a("material", "Material", material))
    params = (("style", style.lower()), ("material", material.lower()))
    return row(code, f"{style} {material} Garden Chair", brand, PATH, _PT, sizes[0][1], "garden_chair",
               desc, SIX, attrs, sizes, "pack_size", params)  # fmt: skip


ROWS = (
    _chair(
        "GCHFAC",
        "Folding",
        "Acacia",
        V,
        "Folding acacia garden chair that packs flat for the shed, with a slatted seat and armrests.",
        packs((1, 39.0), (2, 75.0), (4, 145.0)),
    ),
    _chair(
        "GCHSST",
        "Stacking",
        "Steel",
        W,
        "Stacking steel garden chair with a powder-coated finish, for a bistro table on a terrace.",
        packs((1, 29.0), (2, 55.0), (4, 105.0)),
    ),
    _chair(
        "GCHRAL",
        "Reclining",
        "Aluminum",
        H,
        "Reclining aluminum garden chair with five back positions and a seat pad, for an afternoon on the lawn.",
        packs((1, 69.0), (2, 135.0), (4, 259.0)),
    ),
    _chair(
        "GCHART",
        "Adirondack",
        "Rattan",
        L,
        "Adirondack rattan garden chair with wide armrests and a deep, low seat for a fire pit.",
        packs((1, 119.0), (2, 229.0), (4, 449.0)),
    ),
    _chair(
        "GCHSPL",
        "Stacking",
        "Plastic",
        M,
        "Stacking plastic garden chair that wipes clean and stores in a tower, for a family patio.",
        packs((1, 15.0), (2, 28.0), (4, 52.0)),
    ),
)

SPEC = TypeSpec(
    key="garden_chair",
    homes=(Home("garden_rows", False),),
    department="Garden",
    product_type=_PT,
    derivable=True,
    rows=ROWS,
)
