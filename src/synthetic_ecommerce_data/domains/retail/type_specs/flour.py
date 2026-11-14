"""Flour (gen#964, slice 1): baking flour by the bag's weight.

**Food & Drink > Food Cupboard > Baking > Flour** holds bags whose title names the milling and
the flour; each SKU is a bag's net weight. The bag is drawn (``bag``).
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.pantry_rows import (
    CROFTER,
    DEPARTMENT,
    FOREST,
    GOLDFIELD,
    HEARTH,
    NAVY,
    OWNERS,
    PANTRY_MILL,
    PLUM,
    RUST,
    SAND,
    SKY,
    TEAL,
    decoy,
    grams,
    row,
)  # fmt: skip
from synthetic_ecommerce_data.domains.retail.type_registry import Decoy, TypeSpec, a

PATH = (DEPARTMENT, "Food Cupboard", "Baking", "Flour")


def _attrs(milling: str, flour: str) -> tuple[tuple, ...]:
    return (a("milling", "Milling", milling), a("flour_type", "Flour type", flour))


def _row(code: str, milling: str, flour: str, brand: str, desc: str,
         sizes: tuple[tuple[str, float], ...], color: tuple) -> object:  # fmt: skip
    return row(code, f"{milling} {flour} Flour", brand, PATH, "Flour", "bag", desc,
               _attrs(milling, flour), sizes, "net_weight_g", color, f"{milling} {flour}")  # fmt: skip


_EVERYDAY = grams((0.5, 0.9), (1.0, 1.4), (1.5, 1.9), (5.0, 5.5))
_SPECIALTY = grams((0.5, 1.8), (1.0, 2.9), (1.5, 3.9))

ROWS = (
    _row("FLRSWS", "Stoneground", "Wholemeal Spelt", HEARTH,
         "Milled from grain grown on partner farms, in a paper bag that keeps it dry.", _SPECIALTY, SAND),
    _row("FLRFPL", "Fine Milled", "Plain", PANTRY_MILL,
         "An everyday flour from our own mill, in a paper bag.", _EVERYDAY, NAVY),
    _row("FLRTSR", "Roller Milled", "Self-Raising", PANTRY_MILL,
         "Milled and sifted for an even bake, in a paper bag with a fold-down top.", _EVERYDAY, RUST),
    _row("FLRSRY", "Stoneground", "Rye", CROFTER,
         "Milled in small batches from grain grown on partner farms.", _SPECIALTY, PLUM),
    _row("FLRFIT", "Fine Milled", "Pizza", CROFTER,
         "Milled from carefully chosen grain and sifted for an even texture.", _SPECIALTY, TEAL),
    _row("FLRTWW", "Roller Milled", "Wholemeal Wheat", HEARTH,
         "Milled from grain grown within fifty miles of the mill, in a paper bag.", _EVERYDAY, FOREST),
    _row("FLRSBW", "Stoneground", "Buckwheat", GOLDFIELD,
         "Milled in small batches, in a paper bag that keeps it dry.", _SPECIALTY, SKY),
    _row("FLRFCK", "Fine Milled", "Chickpea", GOLDFIELD,
         "Milled from carefully chosen crops and sifted for an even texture.", _SPECIALTY, SAND),
    _row("FLRTSB", "Roller Milled", "Strong Bread", HEARTH,
         "A baker's flour from a family mill, in a paper bag with a fold-down top.", _EVERYDAY, RUST),
    _row("FLRSSP", "Stoneground", "Plain", CROFTER,
         "Milled in small batches at a family mill, in a paper bag.", _EVERYDAY, FOREST),
)  # fmt: skip

SPEC = TypeSpec(
    key="flour",
    department=DEPARTMENT,
    product_type="Flour",
    derivable=True,
    owners=OWNERS,
    rows=ROWS,
    decoys=(
        Decoy(6, "rice flour", "generic", decoy(ROWS[0], "FLRRIC", "Rice Hill Stoneground Wholemeal Spelt Flour",
              "From the Rice Hill range: milled from grain grown on partner farms.")),
        Decoy(6, "coconut flour", "generic", decoy(ROWS[1], "FLRCOC", "Coconut Lane Fine Milled Plain Flour",
              "From the Coconut Lane range: an everyday wheat flour, in a paper bag.")),
    ),
)  # fmt: skip
