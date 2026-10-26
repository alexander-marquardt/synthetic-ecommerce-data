"""Curtains (gen#204): four styles from four brands, drawn by :func:`kit_softfurn.curtains` with the
heading and the lining they state. A style is its colors times its width x drop sizes. Hand-
authored text-match decoys sit in the same node.
"""

# ruff: noqa: E501 -- authored descriptions read better whole (prototype only).

from __future__ import annotations

from softfurn_rows import (
    BLUE,
    BM,
    CL,
    CREAM,
    CURTAINS_PATH,
    GREY,
    HT,
    LB,
    MAIN,
    NAVY,
    YELLOW,
    SoftRow,
    attr,
    decoy,
    params,
    row,
)
from type_registry import Option, TypeSpec


def _curtain(code: str, title: str, brand: str, price: float, description: str, heading: str,
             lining: str, material: str, panels: str, colors: tuple) -> SoftRow:  # fmt: skip
    head = {"Eyelet": "eyelet", "Pencil Pleat": "pencil", "Tab Top": "tab"}[heading]
    sizes = (("117x137", price), ("167x183", price + 14.0), ("229x183", price + 28.0))
    return row(code, title, brand, CURTAINS_PATH, "Curtains", price, "curtains", description, colors,
                (attr("heading", "Heading", heading), attr("lining", "Lining", lining),
                 attr("material", "Material", material), attr("panels", "Panels", panels)),
                sizes, params(heading=head, lined="no" if lining == "Unlined" else "yes"))  # fmt: skip


ROWS = (
    _curtain(
        "HSFCEYE",
        "Eyelet Curtains, Thermal Lined",
        HT,
        26.0,
        "Ready made eyelet curtains with a thermal lining that keeps a room warm. Sold as a pair.",
        "Eyelet",
        "Thermal",
        "Polyester",
        "Pair",
        (*MAIN, GREY, NAVY),
    ),
    _curtain(
        "HSFCPNC",
        "Velvet Pencil Pleat Curtains",
        BM,
        38.0,
        "Heavy velvet curtains with a pencil pleat tape, for a pole or a track. Sold as a pair.",
        "Pencil Pleat",
        "Thermal",
        "Velvet",
        "Pair",
        MAIN,
    ),
    _curtain(
        "HSFCTAB",
        "Linen-Look Tab Top Curtains",
        LB,
        22.0,
        "Light, loose woven curtains that hang from fabric tabs on a pole. Unlined, one panel.",
        "Tab Top",
        "Unlined",
        "Linen-Look",
        "Single Panel",
        (*MAIN, CREAM),
    ),
    _curtain(
        "HSFCBLK",
        "Blackout Eyelet Curtains",
        CL,
        32.0,
        "Triple-weave blackout curtains for a bedroom or a nursery that block out the light. Sold as a pair.",
        "Eyelet",
        "Blackout",
        "Cotton",
        "Pair",
        (*MAIN, GREY),
    ),
)


SPEC = TypeSpec(
    key="curtains",
    department="Home",
    product_type="Curtains",
    rows=ROWS,
    options=(Option("drop_cm", "drop_length", "Drop length", "CMT"),),
    decoys=(
        decoy(1, "red curtains", ROWS[0], 1, "Red Trim Eyelet Curtains, Thermal Lined",
              "Cream curtains with a red ribbon down the leading edge; the curtain itself is cream.",
              color=CREAM),
        decoy(4, "blackout curtains", ROWS[1], 2, "Blackout Look Velvet Pencil Pleat Curtains",
              "Velvet curtains in a deep shade that look dark; they are thermal lined, not blackout, and the light shows through.",
              color=BLUE),
        decoy(6, "garden", ROWS[2], 3, "Garden Party Tab Top Curtains",
              "Named for the leaf print on the tabs; these are a window dressing, not a garden product.",
              color=YELLOW),
    ),
)  # fmt: skip
