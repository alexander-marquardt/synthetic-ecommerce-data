"""Bath Mats (gen#204): three styles from three brands, drawn by :func:`kit_softfurn.bath_mat` with
the texture they state (ribbed, tufted or slatted). A mat's size is a width x length. Hand-
authored text-match decoys sit in the same node.
"""

# ruff: noqa: E501 -- authored descriptions read better whole (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.softfurn_rows import (
    BATH_MATS_PATH,
    BLACK,
    BM,
    CREAM,
    GREEN,
    GREY,
    HT,
    LB,
    MAIN,
    WHITE,
    SoftRow,
    attr,
    decoy,
    params,
    row,
    yes,
)
from synthetic_ecommerce_data.domains.retail.type_registry import TypeSpec
from synthetic_ecommerce_data.domains.retail.variants import cw


def _mat(code: str, title: str, brand: str, price: float, description: str, material: str,
         texture: str, colors: tuple, quick_dry: bool = False) -> SoftRow:  # fmt: skip
    attrs = [attr("material", "Material", material), yes("non_slip", "Non-slip"),
             attr("texture", "Texture", texture)]  # fmt: skip
    if quick_dry:
        attrs.append(yes("quick_dry", "Quick dry"))
    sizes = (("40x60", price), ("50x80", price + 4.0), ("60x90", price + 8.0))
    return row(code, title, brand, BATH_MATS_PATH, "Bath Mat", price, "bath_mat", description, colors,
                tuple(attrs), sizes, params(texture=texture.lower()), ("width_cm", "length_cm"))  # fmt: skip


ROWS = (
    _mat(
        "HSFMRIB",
        "Ribbed Cotton Bath Mat",
        HT,
        8.0,
        "A thick ribbed bath mat with a non-slip backing, soft underfoot.",
        "Cotton",
        "Ribbed",
        (*MAIN, GREY, CREAM),
    ),
    _mat(
        "HSFMMEM",
        "Memory Foam Tufted Bath Mat",
        BM,
        14.0,
        "A tufted memory foam bath mat that springs back, with a non-slip base.",
        "Memory Foam",
        "Tufted",
        (*MAIN, GREY),
        quick_dry=True,
    ),
    _mat(
        "HSFMBAM",
        "Bamboo Slatted Bath Mat",
        LB,
        16.0,
        "A bamboo duckboard bath mat of slats on two cords, with rubber feet that grip the floor.",
        "Bamboo",
        "Slatted",
        (cw("Natural", "#c9a96e"), *MAIN[:4], BLACK, WHITE),
    ),
)


SPEC = TypeSpec(
    key="bath_mat",
    department="Home",
    product_type="Bath Mat",
    rows=ROWS,
    decoys=(
        decoy(1, "blue bath mat", ROWS[0], 13, "Blue Border Ribbed Cotton Bath Mat",
              "A cream ribbed mat with a blue border stripe; the mat itself is cream.", color=CREAM),
        decoy(4, "quick dry mat", ROWS[0], 14, "Quick Dry Look Ribbed Cotton Bath Mat",
              "A thick cotton mat in a fresh shade that suggests it dries fast; thick cotton is slow to dry.",
              color=GREEN),
        decoy(2, "shower mat", ROWS[2], 15, "Shower Mat Style Bamboo Slatted Bath Mat",
              "A bamboo duckboard for the floor beside the bath; it is a bath mat and not a mat for inside a shower tray.",
              color=GREY),
    ),
)  # fmt: skip
