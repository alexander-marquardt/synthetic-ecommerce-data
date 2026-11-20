"""Garden storage (gen#961, slice 3): Garden > Garden Storage > Storage Boxes and Outbuildings.

A breadth type: ``derivable`` True, so the scaled build draws more storage from these by the
values their titles show (the style and the material). The scale pools values per leaf, so a box
never takes a shed's roof. The style draws the body and its lid or roof and the material its
marks (:func:`kit_garden_yard.garden_storage`). Each SKU is a color times a capacity in litres (a
box) or a width in centimetres (a shed), and every style offers the six main colors (gen#275).
The type's text-match decoys (gen#294) are in :mod:`garden_rows`.
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail import (
    kit_garden_yard,  # noqa: F401 -- registers garden_storage
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

_ROOT = ("Garden", "Garden Storage")
PATH_BOXES = (*_ROOT, "Storage Boxes")
PATH_SHEDS = (*_ROOT, "Outbuildings")
_PT = "Garden Storage"
SIX = (RED, BLUE, GREEN, YELLOW, BLACK, WHITE)


def _box(code: str, material: str, style: str, brand: str, desc: str, sizes: tuple) -> object:
    attrs = (a("style", "Style", style), a("material", "Material", material))
    params = (("style", style.lower()), ("material", material.lower()))
    return row(code, f"{material} {style}", brand, PATH_BOXES, _PT, sizes[0][1], "garden_storage",
               desc, SIX, attrs, sizes, "capacity_l", params)  # fmt: skip


def _shed(code: str, material: str, roof: str, brand: str, desc: str, sizes: tuple) -> object:
    attrs = (a("roof", "Roof", roof), a("material", "Material", material))
    params = (("style", roof.lower()), ("material", material.lower()))
    return row(code, f"{material} {roof} Shed", brand, PATH_SHEDS, _PT, sizes[0][1], "garden_storage",
               desc, SIX, attrs, sizes, "width_cm", params)  # fmt: skip


ROWS = (
    _box(
        "GDBDRS",
        "Resin",
        "Deck Box",
        V,
        "A weatherproof resin deck box with a lockable lid, for cushions and toys on the patio.",
        axis((270, 69.0), (420, 99.0), (570, 139.0)),
    ),
    _box(
        "GDBBWD",
        "Wood",
        "Storage Bench",
        W,
        "A wood storage bench that keeps the hose and the cushions dry by the back door.",
        axis((180, 129.0), (240, 159.0), (300, 189.0)),
    ),
    _box(
        "GDBCRS",
        "Resin",
        "Tall Cabinet",
        H,
        "A resin tall cabinet that keeps long tools and pots dry by the back door.",
        axis((300, 119.0), (450, 159.0), (600, 199.0)),
    ),
    _shed(
        "GDBAST",
        "Steel",
        "Apex",
        L,
        "A steel apex shed with double doors and a floor, for the mower and the bikes.",
        axis((183, 249.0), (244, 349.0), (305, 449.0)),
    ),
    _shed(
        "GDBPWD",
        "Wood",
        "Pent",
        M,
        "A wood pent shed with double doors and a floor, to stand against a fence.",
        axis((183, 299.0), (244, 399.0), (305, 529.0)),
    ),
)

SPEC = TypeSpec(
    key="garden_storage",
    homes=(Home("garden_rows", False),),
    department="Garden",
    product_type=_PT,
    derivable=True,
    rows=ROWS,
)
