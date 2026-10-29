"""Sippy Cups (gen#620): Home > Kitchen & Dining > Drinkware > Kids' Drinkware.

Three styles from three brands, drawn by :func:`kit_cups.sippy_cup`: a spout lid and, for two of
them, a handle on each side. Each title is a realistic six to ten words (material, age, use). Every
name here is invented.
"""

# ruff: noqa: E501 -- authored descriptions read better whole (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail import kit_cups  # noqa: F401 -- registers sippy_cup
from synthetic_ecommerce_data.domains.retail.decor_rows import (
    BLUE,
    BRACKENMERE,
    CALDERBY,
    GREEN,
    PINK,
    SILVER,
    THISTLE,
    WHITE,
    YELLOW,
    row,
)
from synthetic_ecommerce_data.domains.retail.type_registry import TypeSpec, a

SIPPY = ("Home", "Kitchen & Dining", "Drinkware", "Kids' Drinkware")

ROWS = (
    row("SIPTWO", "Spill Proof Toddler Sippy Cup with Two Handles", BRACKENMERE, SIPPY, "Sippy Cup", 6.0,
        "sippy_cup",
        "A spill proof toddler cup with a soft spout and two easy grip handles, made from BPA free plastic.",
        (BLUE, PINK, GREEN),
        (a("material", "Material", "Plastic"),), params=(("handles", "two"),)),
    row("SIPSOF", "Soft Spout Baby Sippy Cup for Learning to Drink", THISTLE, SIPPY, "Sippy Cup", 5.0,
        "sippy_cup",
        "A first cup for babies learning to drink, with a soft silicone spout and a twist on lid.",
        (YELLOW, WHITE, PINK),
        (a("material", "Material", "Plastic"),), params=(("handles", "two"),)),
    row("SIPSTL", "Insulated Stainless Steel Kids Sippy Cup, Easy Grip", CALDERBY, SIPPY, "Sippy Cup", 12.0,
        "sippy_cup",
        "A double walled stainless steel cup that keeps milk cool, with a spout lid and no handles to snap off.",
        (SILVER, BLUE, GREEN),
        (a("material", "Material", "Stainless Steel"),), params=(("handles", "none"),)),
)

SPEC = TypeSpec(
    key="sippy_cup",
    department="Home",
    product_type="Sippy Cup",
    rows=ROWS,
)
