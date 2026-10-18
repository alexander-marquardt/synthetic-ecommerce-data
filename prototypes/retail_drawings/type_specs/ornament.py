"""Ornaments and decorative objects (gen#217, a spec by gen#351): Home > Home Accessories >
Ornaments.

Four styles from four brands, drawn by :func:`kit_decor.ornament`: the form (vase, bird or orb)
changes the drawing. The material, the occasion and the form are structured entries; a style is a
color. Every name here is invented.
"""

# ruff: noqa: E501 -- authored descriptions read better whole (prototype only).

from __future__ import annotations

import kit_decor  # noqa: F401 -- registers the shapes
from decor_rows import (
    BLACK,
    BLUE,
    BRACKENMERE,
    BROWN,
    COBBLE,
    GREEN,
    LARCHWOOD,
    ORNAMENTS,
    RED,
    THISTLE,
    WHITE,
    YELLOW,
    row,
)
from type_registry import TypeSpec, a

ROWS = (
    row("ORNCVS", "Ceramic Table Vase Ornament", COBBLE, ORNAMENTS, "Ornament", 18.0, "ornament",
         "A glazed ceramic vase for the shelf or the table, a decorative object that holds a few dried stems.",
         (WHITE, BLUE, YELLOW, GREEN),
         (a("material", "Material", "Ceramic"), a("occasion", "Occasion", "Everyday"),
          a("form", "Form", "Vase")),
         params=(("form", "vase"),)),
    row("ORNWBD", "Carved Wooden Bird Ornament", THISTLE, ORNAMENTS, "Ornament", 14.0, "ornament",
         "A bird carved from mango wood and finished by hand, to stand on a shelf or a window sill.",
         (BROWN, BLACK, RED),
         (a("material", "Material", "Wood"), a("occasion", "Occasion", "Everyday"),
          a("form", "Form", "Bird")),
         params=(("form", "bird"),)),
    row("ORNGOR", "Glass Orb Christmas Ornament", LARCHWOOD, ORNAMENTS, "Ornament", 12.0, "ornament",
         "A clear glass orb on a small stand, a winter ornament that catches the light of a candle.",
         (RED, GREEN, WHITE),
         (a("material", "Material", "Glass"), a("occasion", "Occasion", "Christmas"),
          a("form", "Form", "Orb")),
         params=(("form", "orb"),)),
    row("ORNHBD", "Hand Painted Ceramic Bird Ornament", BRACKENMERE, ORNAMENTS, "Ornament", 16.0, "ornament",
         "A small ceramic bird, hand painted, for a shelf or a mantel.",
         (YELLOW, BLACK, BLUE),
         (a("material", "Material", "Ceramic"), a("occasion", "Occasion", "Spring"),
          a("form", "Form", "Bird")),
         params=(("form", "bird"),)),
)


SPEC = TypeSpec(
    key="ornament",
    department="Home",
    product_type="Ornament",
    rows=ROWS,
)
