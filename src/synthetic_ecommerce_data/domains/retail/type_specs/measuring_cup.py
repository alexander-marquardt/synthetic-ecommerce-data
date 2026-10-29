"""Measuring Cups (gen#620): Home > Kitchen & Dining > Measuring Cups.

Three styles from three brands, drawn by :func:`kit_cups.measuring_cup`: a pouring spout, a handle
and graduation marks. Each title is a realistic six to ten words (material, markings, use). Every
name here is invented.
"""

# ruff: noqa: E501 -- authored descriptions read better whole (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail import (
    kit_cups,  # noqa: F401 -- registers measuring_cup
)
from synthetic_ecommerce_data.domains.retail.decor_rows import (
    BLUE,
    BRACKENMERE,
    COBBLE,
    EMBERLY,
    GREEN,
    RED,
    SILVER,
    WHITE,
    row,
)
from synthetic_ecommerce_data.domains.retail.type_registry import TypeSpec, a

MEASURING = ("Home", "Kitchen & Dining", "Measuring Cups")

ROWS = (
    row("MSRPLS", "Clear Plastic Measuring Cup with Metric and Imperial Markings", BRACKENMERE, MEASURING,
        "Measuring Cup", 5.0, "measuring_cup",
        "A clear plastic measuring cup with a pouring spout and a comfortable handle, marked in millilitres and fluid ounces.",
        (WHITE, RED, BLUE),
        (a("material", "Material", "Plastic"),), params=(("marks", "metric"),)),
    row("MSRSTL", "Stainless Steel Measuring Cup with Pouring Spout and Handle", COBBLE, MEASURING,
        "Measuring Cup", 9.0, "measuring_cup",
        "A brushed stainless steel measuring cup with a pouring spout, a riveted handle and etched marks.",
        (SILVER, GREEN, RED),
        (a("material", "Material", "Stainless Steel"),), params=(("marks", "metric"),)),
    row("MSRGLS", "Heatproof Glass Measuring Cup for Baking and Cooking", EMBERLY, MEASURING,
        "Measuring Cup", 11.0, "measuring_cup",
        "A heatproof glass measuring cup with a handle and a spout, safe in the microwave and the oven.",
        (WHITE, BLUE, GREEN),
        (a("material", "Material", "Glass"),), params=(("marks", "plain"),)),
)

SPEC = TypeSpec(
    key="measuring_cup",
    department="Home",
    product_type="Measuring Cup",
    rows=ROWS,
)
