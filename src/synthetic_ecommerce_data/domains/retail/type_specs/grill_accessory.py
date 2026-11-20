"""Grill accessory (gen#961, slice 3): Garden > Barbecues & Grills > Grill Tools and Grill Covers.

A breadth type: ``derivable`` True, so the scaled build draws more accessories from these by the
values their titles show (the tool or the grill a cover fits, and the material). The scale pools
values per leaf, so a cover never takes a tool's material. The kind draws the tools or the cover
and the material its marks (:func:`kit_garden_yard.grill_accessory`). Each SKU is a color, and
every style offers the six main colors (gen#275). The type's text-match decoys (gen#294) are in
:mod:`garden_rows`.
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail import (
    kit_garden_yard,  # noqa: F401 -- registers grill_accessory
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
    row,
)
from synthetic_ecommerce_data.domains.retail.type_registry import Home, TypeSpec

_ROOT = ("Garden", "Barbecues & Grills")
PATH_TOOLS = (*_ROOT, "Grill Tools")
PATH_COVERS = (*_ROOT, "Grill Covers")
_PT = "Grill Accessory"
SIX = (RED, BLUE, GREEN, YELLOW, BLACK, WHITE)


def _tool(code: str, material: str, tool: str, brand: str, price: float, desc: str) -> object:
    attrs = (a("tool", "Tool", tool), a("material", "Material", material))
    params = (("kind", tool.lower()), ("material", material.lower()))
    return row(code, f"{material} Grill {tool}", brand, PATH_TOOLS, _PT, price, "grill_accessory",
               desc, SIX, attrs, params=params)  # fmt: skip


def _cover(code: str, material: str, fits: str, brand: str, price: float, desc: str) -> object:
    attrs = (a("fits", "Fits", fits), a("material", "Material", material))
    params = (("kind", fits.lower()), ("material", material.lower()))
    return row(code, f"{material} {fits} Grill Cover", brand, PATH_COVERS, _PT, price, "grill_accessory",
               desc, SIX, attrs, params=params)  # fmt: skip


ROWS = (
    _tool(
        "GRATSS",
        "Stainless Steel",
        "Tool Set",
        V,
        24.0,
        "A stainless steel grill tool set with soft grips and a loop on each handle, to hang by the grill.",
    ),
    _tool(
        "GRATSB",
        "Bamboo",
        "Tool Set",
        W,
        19.0,
        "A bamboo grill tool set whose handles stay cool by the coals.",
    ),
    _tool(
        "GRABSS",
        "Stainless Steel",
        "Brush",
        H,
        12.0,
        "A stainless steel grill brush with a long handle, for the bars of a hot grate.",
    ),
    _tool(
        "GRATGB",
        "Bamboo",
        "Tongs",
        L,
        11.0,
        "Bamboo grill tongs with a long handle, for turning sausages at arm's length.",
    ),
    _cover(
        "GRAKPO",
        "Polyester",
        "Kettle",
        M,
        22.0,
        "A fitted polyester kettle grill cover with a hem cord, to keep the grill dry all year.",
    ),
    _cover(
        "GRACCV",
        "Canvas",
        "Cabinet",
        V,
        39.0,
        "A canvas cabinet grill cover with a buckle strap and vents, to keep the grill dry all year.",
    ),
)

SPEC = TypeSpec(
    key="grill_accessory",
    homes=(Home("garden_rows", False),),
    department="Garden",
    product_type=_PT,
    derivable=True,
    rows=ROWS,
)
