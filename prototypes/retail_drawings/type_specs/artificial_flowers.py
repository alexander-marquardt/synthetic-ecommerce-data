"""Artificial flowers and stems (gen#217, a spec by gen#351): Home > Home Accessories > Artificial
Flowers.

Five styles from five brands, drawn by :func:`kit_decor.stems`: the flower (eucalyptus, peony,
rose or pampas) and whether the stems stand in a vase or lie loose change the drawing. The flower,
the holder and the material are structured entries; a style is a color times a stem height. Every
name here is invented.
"""

# ruff: noqa: E501 -- authored descriptions read better whole (prototype only).

from __future__ import annotations

import kit_decor  # noqa: F401 -- registers the shapes
from decor_rows import (
    BLACK,
    BLUE,
    BRACKENMERE,
    COBBLE,
    CREAM,
    EMBERLY,
    GREEN,
    GREY,
    LARCHWOOD,
    NATURAL,
    PINK,
    RED,
    STEMS,
    THISTLE,
    WHITE,
    YELLOW,
    axis,
    row,
)
from type_registry import TypeSpec, a

LOOSE = a("holder", "Holder", "Loose")
IN_VASE = a("holder", "Holder", "In a Vase")

ROWS = (
    row("STMEUC", "Artificial Eucalyptus Stems", THISTLE, STEMS, "Artificial Flowers", 9.0, "stems",
         "Artificial eucalyptus stems with soft leaves, sold loose, for a vase or a wreath.",
         (GREEN, GREY, WHITE),
         (a("flower", "Flower", "Eucalyptus"), LOOSE, a("material", "Material", "Polyester")),
         axis((45, 9.0), (60, 11.0), (80, 14.0)), "height_cm", (("flower", "eucalyptus"), ("holder", "loose"))),
    row("STMPNY", "Artificial Peony Stems", BRACKENMERE, STEMS, "Artificial Flowers", 12.0, "stems",
         "Artificial peony stems with full layered blooms, sold loose, for a table or a mantel.",
         (PINK, WHITE, RED, YELLOW),
         (a("flower", "Flower", "Peony"), LOOSE, a("material", "Material", "Silk")),
         axis((45, 12.0), (60, 15.0)), "height_cm", (("flower", "peony"), ("holder", "loose"))),
    row("STMROV", "Artificial Rose Stems in Vase", COBBLE, STEMS, "Artificial Flowers", 28.0, "stems",
         "Artificial rose stems arranged in a glass vase, ready to stand on a table.",
         (RED, BLUE, BLACK, YELLOW),
         (a("flower", "Flower", "Rose"), IN_VASE, a("material", "Material", "Silk")),
         axis((30, 28.0), (40, 34.0)), "height_cm", (("flower", "rose"), ("holder", "vase"))),
    row("STMPMP", "Artificial Pampas Grass Stems", LARCHWOOD, STEMS, "Artificial Flowers", 15.0, "stems",
         "Artificial pampas grass stems with tall feathery plumes, sold loose.",
         (NATURAL, CREAM, WHITE),
         (a("flower", "Flower", "Pampas"), LOOSE, a("material", "Material", "Dried-Look Polyester")),
         axis((70, 15.0), (90, 19.0), (110, 24.0)), "height_cm", (("flower", "pampas"), ("holder", "loose"))),
    row("STMPVS", "Artificial Pampas Stems in Vase", EMBERLY, STEMS, "Artificial Flowers", 35.0, "stems",
         "Artificial pampas stems in a ceramic vase, a tall floor arrangement.",
         (NATURAL, BLACK),
         (a("flower", "Flower", "Pampas"), IN_VASE, a("material", "Material", "Dried-Look Polyester")),
         axis((90, 35.0), (110, 42.0)), "height_cm", (("flower", "pampas"), ("holder", "vase"))),
)


SPEC = TypeSpec(
    key="artificial_flowers",
    department="Home",
    product_type="Artificial Flowers",
    rows=ROWS,
)
