"""Watering can (gen#961, slice 2): Garden > Watering > Watering Cans.

A breadth type: ``derivable`` True, so the scaled build draws more cans from these five by the
values their titles show (the style and the material). The style draws the body and the spout
and the material its surface marks (:func:`kit_garden_care.watering_can`). Each SKU is a color
times a capacity in litres, and every style offers the six main colors (gen#275). The type's
text-match decoys (gen#294) are in :mod:`garden_rows`, with the other Garden types'.
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail import (
    kit_garden_care,  # noqa: F401 -- registers watering_can
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

PATH = ("Garden", "Watering", "Watering Cans")
_PT = "Watering Can"
SIX = (RED, BLUE, GREEN, YELLOW, BLACK, WHITE)


def _can(code: str, style: str, material: str, brand: str, desc: str, sizes: tuple) -> object:
    attrs = (a("style", "Style", style), a("material", "Material", material))
    params = (("style", style.lower()), ("material", material.lower()))
    return row(code, f"{style} {material} Watering Can", brand, PATH, _PT, sizes[0][1], "watering_can",
               desc, SIX, attrs, sizes, "capacity_l", params)  # fmt: skip


ROWS = (
    _can(
        "WCNCPL",
        "Classic",
        "Plastic",
        W,
        "A classic plastic watering can with a long spout and a removable rose, light to carry when full.",
        axis((5, 9.0), (7, 11.0), (10, 14.0)),
    ),
    _can(
        "WCNLGS",
        "Long Reach",
        "Galvanized Steel",
        M,
        "A long reach galvanized steel can with a low body and a long spout, for the back of a border.",
        axis((5, 29.0), (7, 34.0), (9, 39.0)),
    ),
    _can(
        "WCNIPC",
        "Indoor",
        "Powder-Coated Steel",
        V,
        "A small indoor can in powder-coated steel with a slim spout, for house plants on a sill.",
        axis((1, 15.0), (1.5, 18.0), (2, 21.0)),
    ),
    _can(
        "WCNSPL",
        "Slimline",
        "Plastic",
        H,
        "A tall slimline plastic can that fits under an outside tap, with a fine brass-faced rose.",
        axis((4, 8.0), (6, 10.0), (8, 12.0)),
    ),
    _can(
        "WCNCGS",
        "Classic",
        "Galvanized Steel",
        L,
        "A classic galvanized steel watering can with riveted seams and a round rose for seedlings.",
        axis((5, 25.0), (7, 30.0), (10, 36.0)),
    ),
)

SPEC = TypeSpec(
    key="watering_can",
    homes=(Home("garden_rows", False),),
    department="Garden",
    product_type=_PT,
    derivable=True,
    rows=ROWS,
)
