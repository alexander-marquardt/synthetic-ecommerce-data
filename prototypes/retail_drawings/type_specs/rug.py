"""Rugs (gen#204): four styles from four brands, drawn by :func:`kit_softfurn.rug` with the form
(rectangle, runner or round) and the pile they state. A rug's size is a width x length, or a
diameter for a round one. Hand-authored text-match decoys sit in the same node.
"""

# ruff: noqa: E501 -- authored descriptions read better whole (prototype only).

from __future__ import annotations

from softfurn_rows import (
    BM,
    CL,
    CREAM,
    GREY,
    HT,
    LB,
    MAIN,
    RUGS_PATH,
    WHITE,
    SoftRow,
    attr,
    decoy,
    params,
    row,
    yes,
)
from type_registry import TypeSpec


def _rug(code: str, title: str, brand: str, price: float, description: str, shape: str, pile: str,
         material: str, colors: tuple, washable: bool = False, outdoor: bool = False) -> SoftRow:  # fmt: skip
    prm = params(form={"Rectangular": "rectangle", "Round": "round", "Runner": "runner"}[shape],
             pile={"Flat Weave": "flat", "Shag": "shag", "Short Pile": "short"}[pile])  # fmt: skip
    attrs = [attr("rug_shape", "Shape", shape), attr("pile", "Pile", pile), attr("material", "Material", material),
             attr("indoor_outdoor", "Indoor or outdoor", "Outdoor" if outdoor else "Indoor")]  # fmt: skip
    if washable:
        attrs.append(yes("washable", "Washable"))
    if shape == "Round":
        sizes = (("100", price), ("150", price + 40.0), ("200", price + 90.0))
        keys = ("diameter_cm",)
    elif shape == "Runner":
        sizes = (("66x200", price), ("66x300", price + 20.0), ("80x400", price + 40.0))
        keys = ("width_cm", "length_cm")
    else:
        sizes = (("120x170", price), ("160x230", price + 60.0), ("200x290", price + 130.0))
        keys = ("width_cm", "length_cm")
    return row(code, title, brand, RUGS_PATH, "Rug", price, "rug", description, colors,
                tuple(attrs), sizes, prm, keys)  # fmt: skip


ROWS = (
    _rug(
        "HSFRSHG",
        "Shaggy Deep Pile Rug",
        HT,
        49.0,
        "A soft, thick shaggy rug for a bedroom or a living room, with a deep pile that sheds little.",
        "Rectangular",
        "Shag",
        "Polyester",
        (*MAIN, GREY, CREAM),
    ),
    _rug(
        "HSFRFLT",
        "Washable Flatweave Runner",
        BM,
        39.0,
        "A flat woven runner for a hallway or a kitchen. It goes in the washing machine.",
        "Runner",
        "Flat Weave",
        "Cotton",
        (*MAIN, GREY),
        washable=True,
    ),
    _rug(
        "HSFRJUT",
        "Round Jute Rug",
        LB,
        45.0,
        "A natural round jute rug with a braided edge, for a hall or a reading corner.",
        "Round",
        "Short Pile",
        "Jute",
        (*MAIN, CREAM),
    ),
    _rug(
        "HSFROUT",
        "Outdoor Rug for a Patio",
        CL,
        35.0,
        "A rug for a patio or a balcony, woven from weatherproof polypropylene that dries fast.",
        "Rectangular",
        "Short Pile",
        "Polypropylene",
        (*MAIN, GREY),
        outdoor=True,
    ),
)


SPEC = TypeSpec(
    key="rug",
    department="Home",
    product_type="Rug",
    rows=ROWS,
    decoys=(
        decoy(1, "blue rug", ROWS[0], 7, "Blue Fringe Shaggy Deep Pile Rug",
              "A white shaggy rug with a blue fringe at each end; the rug itself is white.", color=WHITE),
        decoy(2, "door mat", ROWS[3], 8, "Door Mat Style Outdoor Rug for a Patio",
              "A patio rug woven in a coir look pattern; it is a rug, not a door mat.", color=GREY),
        decoy(4, "washable rug", ROWS[2], 9, "Washable Look Round Jute Rug",
              "A natural jute round rug with a clean finish; jute must be brushed and spot cleaned, never washed.",
              color=CREAM),
    ),
)  # fmt: skip
