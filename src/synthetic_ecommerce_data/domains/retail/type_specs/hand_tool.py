"""Hand tool (gen#961, slice 2): Garden > Garden Tools > Hand Tools.

A breadth type: ``derivable`` True, so the scaled build draws more tools from these five by the
values their titles show (the head metal and the kind of tool). The kind draws the head (a trowel's
scoop, a fork's tines, a cultivator's claws, a transplanter's depth marks, a pruner's blades) and
the head metal its color and marks (:func:`kit_garden_care.hand_tool`). Each SKU is a handle
color, and every style offers the six main colors (gen#275). The type's text-match decoys
(gen#294) are in :mod:`garden_rows`, with the other Garden types'.
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail import (
    kit_garden_care,  # noqa: F401 -- registers hand_tool
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

PATH = ("Garden", "Garden Tools", "Hand Tools")
_PT = "Hand Tool"
SIX = (RED, BLUE, GREEN, YELLOW, BLACK, WHITE)


def _tool(code: str, head: str, kind: str, brand: str, price: float, desc: str) -> object:
    attrs = (a("tool", "Tool", kind), a("head_material", "Head material", head))
    params = (("kind", kind.lower()), ("head", head.lower()))
    return row(code, f"{head} {kind}", brand, PATH, _PT, price, "hand_tool", desc, SIX, attrs,
               params=params)  # fmt: skip


ROWS = (
    _tool(
        "HTLTRS",
        "Stainless Steel",
        "Trowel",
        V,
        12.0,
        "A stainless steel trowel with a wide scoop and a soft grip, for planting bulbs and bedding.",
    ),
    _tool(
        "HTLFCS",
        "Carbon Steel",
        "Hand Fork",
        W,
        9.0,
        "A carbon steel hand fork with three stiff tines, for loosening soil in a border.",
    ),
    _tool(
        "HTLCAL",
        "Cast Aluminum",
        "Cultivator",
        H,
        11.0,
        "A cast aluminum cultivator with three curved claws, for breaking up a crust of soil.",
    ),
    _tool(
        "HTLTPS",
        "Stainless Steel",
        "Transplanter",
        L,
        13.0,
        "A stainless steel transplanter with a narrow blade marked in depths, for seedlings.",
    ),
    _tool(
        "HTLPRC",
        "Carbon Steel",
        "Pruner",
        M,
        19.0,
        "A carbon steel bypass pruner with a safety catch, for green stems up to 2 cm thick.",
    ),
)

SPEC = TypeSpec(
    key="hand_tool",
    homes=(Home("garden_rows", False),),
    department="Garden",
    product_type=_PT,
    derivable=True,
    rows=ROWS,
)
