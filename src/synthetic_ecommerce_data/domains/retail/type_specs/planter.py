"""Planter (gen#961, slice 1): Garden > Pots & Planters > Planters.

A breadth type: ``derivable`` True, so the scaled build draws more planters from these four by
the values their titles show (the form and the material). The form draws the pot's outline and
the material its surface marks (:func:`kit_patio.planter`). Each SKU is a color times a width in
centimetres, and every style offers the six main colors (gen#275). The type's text-match decoys
(gen#294) are in :mod:`garden_rows`, with the other Garden types'.
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail import kit_patio  # noqa: F401 -- registers planter
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

PATH = ("Garden", "Pots & Planters", "Planters")
_PT = "Planter"
SIX = (RED, BLUE, GREEN, YELLOW, BLACK, WHITE)


def _attrs(form: str, material: str) -> tuple:
    return (a("shape", "Shape", form), a("material", "Material", material))


def _params(form: str, material: str) -> tuple:
    return (("form", form.lower()), ("material", material.lower()))


def _planter(code: str, form: str, material: str, brand: str, desc: str, sizes: tuple) -> object:
    return row(code, f"{form} {material} Planter", brand, PATH, _PT, sizes[0][1], "planter", desc,
               SIX, _attrs(form, material), sizes, "width_cm", _params(form, material))  # fmt: skip


ROWS = (
    _planter(
        "PLNRCR",
        "Round",
        "Ceramic",
        V,
        "A round ceramic planter with a drainage hole and a raised rim, for herbs and bedding plants on a patio.",
        axis((25, 24.0), (35, 39.0), (45, 59.0)),
    ),
    _planter(
        "PLNSPL",
        "Square",
        "Plastic",
        W,
        "A square plastic planter that is light to move, with a drainage hole and a raised rim.",
        axis((30, 12.0), (40, 18.0), (50, 26.0)),
    ),
    _planter(
        "PLNTFG",
        "Tall",
        "Fiberglass",
        H,
        "A tall fiberglass planter for a shrub or a small tree beside a door, light for its size.",
        axis((30, 49.0), (40, 69.0), (50, 89.0)),
    ),
    _planter(
        "PLNTRC",
        "Trough",
        "Concrete",
        L,
        "A trough concrete planter for a row of herbs or bulbs along a terrace edge.",
        axis((60, 39.0), (80, 54.0), (100, 69.0)),
    ),
    _planter(
        "PLNRGS",
        "Round",
        "Galvanized Steel",
        M,
        "A round galvanized steel planter with a drainage hole, for a vegetable bed on a balcony.",
        axis((30, 29.0), (40, 39.0), (50, 49.0)),
    ),
)

SPEC = TypeSpec(
    key="planter",
    homes=(Home("garden_rows", False),),
    department="Garden",
    product_type=_PT,
    derivable=True,
    rows=ROWS,
)
