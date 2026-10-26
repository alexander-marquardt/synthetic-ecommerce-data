"""Shower Curtains (gen#204): three styles from three brands, drawn by
:func:`kit_softfurn.shower_curtain` with the hem they state (weighted or plain). A style is its
colors times its width x drop sizes. Hand-authored text-match decoys sit in the same node.
"""

# ruff: noqa: E501 -- authored descriptions read better whole (prototype only).

from __future__ import annotations

from softfurn_rows import (
    BM,
    CL,
    GREY,
    HP,
    MAIN,
    NAVY,
    SHOWER_PATH,
    WHITE,
    SoftRow,
    attr,
    decoy,
    params,
    row,
    stripe,
    yes,
)
from type_registry import Option, TypeSpec


def _shower(code: str, title: str, brand: str, price: float, description: str, material: str,
            colors: tuple, weighted: bool = False, waterproof: bool = True) -> SoftRow:  # fmt: skip
    attrs = [attr("material", "Material", material)]
    if waterproof:
        attrs.append(yes("waterproof", "Waterproof"))
    if weighted:
        attrs.append(yes("weighted_hem", "Weighted hem"))
    sizes = (("180x180", price), ("180x200", price + 3.0))
    return row(code, title, brand, SHOWER_PATH, "Shower Curtain", price, "shower_curtain", description,
                colors, tuple(attrs), sizes, params(hem="weighted" if weighted else "plain"))  # fmt: skip


ROWS = (
    _shower(
        "HSFSPEV",
        "PEVA Shower Curtain with Weighted Hem",
        HP,
        9.0,
        "A waterproof PEVA shower curtain with a weighted hem that keeps it from blowing in. "
        "It comes with 12 rings.",
        "PEVA",
        (*MAIN, GREY),
        weighted=True,
    ),
    _shower(
        "HSFSPLY",
        "Polyester Shower Curtain",
        CL,
        12.0,
        "A heavy polyester shower curtain with a water-repellent finish and reinforced eyelets.",
        "Polyester",
        (*MAIN, GREY, NAVY),
    ),
    _shower(
        "HSFSCTN",
        "Cotton Striped Shower Curtain",
        BM,
        18.0,
        "A cotton shower curtain in a woven stripe, with a plain hem. Use it with a liner.",
        "Cotton",
        (
            stripe("Blue", "#3f6fb5"),
            stripe("Red", "#c8312e"),
            stripe("Green", "#4f8a3a"),
            stripe("Yellow", "#f2c230"),
            stripe("Black", "#2d2d33"),
            WHITE,
        ),
        waterproof=False,
    ),
)


SPEC = TypeSpec(
    key="shower_curtain",
    department="Home",
    product_type="Shower Curtain",
    rows=ROWS,
    options=(Option("drop_cm", "drop_length", "Drop length", "CMT"),),
    decoys=(
        decoy(1, "red shower curtain", ROWS[1], 16, "Red Ring Polyester Shower Curtain",
              "A white polyester curtain on red plastic rings; the curtain itself is white.", color=WHITE),
        decoy(4, "waterproof shower curtain", ROWS[2], 17, "Waterproof Look Cotton Striped Shower Curtain",
              "A cotton curtain that looks smooth and sealed, but it is not waterproof and needs a liner.",
              attrs=(attr("material", "Material", "Cotton"),), color=NAVY),
        decoy(6, "bath", ROWS[0], 18, "Bath Time PEVA Shower Curtain with Weighted Hem",
              "From the Bath Time range; the print is of ducks and has nothing to do with a bath mat or a bath tub.",
              color=GREY),
    ),
)  # fmt: skip
