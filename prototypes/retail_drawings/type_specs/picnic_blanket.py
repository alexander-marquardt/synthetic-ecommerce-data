"""Picnic blankets (gen#217, a spec by gen#351): Sports & Outdoors > Camping > Picnic Blankets.

Three styles from three brands, drawn by :func:`kit_decor.picnic_blanket`: the backing (plain or
waterproof) changes the drawing. The waterproof backing and the material are structured entries; a
style is a color times its dimensions. Every name here is invented.
"""

# ruff: noqa: E501 -- authored descriptions read better whole (prototype only).

from __future__ import annotations

import kit_decor  # noqa: F401 -- registers the shapes
from decor_rows import (
    BLACK,
    BLANKETS,
    BLUE,
    GREEN,
    HARBOUR,
    LARCHWOOD,
    NAVY,
    RED,
    TAN,
    THISTLE,
    WHITE,
    YELLOW,
    row,
    yes,
)
from type_registry import TypeSpec, a

ROWS = (
    row("PCBWTP", "Waterproof Picnic Blanket", HARBOUR, BLANKETS, "Picnic Blanket", 18.0, "picnic_blanket",
         "A picnic blanket with a waterproof backing that keeps out damp grass, folding to a carry bag.",
         (RED, BLUE, GREEN, YELLOW),
         (yes("waterproof_backing", "Waterproof backing"), a("material", "Material", "Fleece")),
         (("130 x 150 cm", 18.0), ("150 x 200 cm", 24.0)), "dimensions", (("backing", "waterproof"),)),
    row("PCBWLN", "Wool Picnic Blanket", THISTLE, BLANKETS, "Picnic Blanket", 32.0, "picnic_blanket",
         "A thick wool picnic blanket with a fringed edge and a leather carry strap.",
         (NAVY, TAN, BLACK),
         (a("waterproof_backing", "Waterproof backing", "No"), a("material", "Material", "Wool")),
         (("140 x 170 cm", 32.0),), "dimensions", (("backing", "plain"),)),
    row("PCBXLG", "Extra Large Waterproof Picnic Blanket", LARCHWOOD, BLANKETS, "Picnic Blanket", 28.0, "picnic_blanket",
         "A big picnic blanket with a waterproof backing, wide enough for a family and a basket.",
         (WHITE, BLACK, GREEN),
         (yes("waterproof_backing", "Waterproof backing"), a("material", "Material", "Polyester")),
         (("200 x 200 cm", 28.0), ("200 x 230 cm", 34.0)), "dimensions", (("backing", "waterproof"),)),
)


SPEC = TypeSpec(
    key="picnic_blanket",
    department="Sports & Outdoors",
    product_type="Picnic Blanket",
    rows=ROWS,
)

