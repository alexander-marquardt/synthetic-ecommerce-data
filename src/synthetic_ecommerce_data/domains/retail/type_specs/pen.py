"""Pens (gen#969): Office & school > Pens & pencils > Pens.

A breadth type: ``derivable`` True, so the scaled build draws more pens from these three by the
values their titles show (the pen's style and its point). The ink is the SKU's color, drawn as
the barrel; the style draws the tip and the mechanism a click button or a cap (:func:`kit_office.pen`).
Each SKU is a color in a pack of 4, 10 or 20.
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.office_rows import (
    BLACK,
    BLUE,
    CALDERBY,
    DEPARTMENT,
    LANTERNBY,
    PENS,
    THISTLE,
    decoy,
    packs,
    row,
)
from synthetic_ecommerce_data.domains.retail.type_registry import Decoy, TypeSpec, a


def _pen(style: str, point: str, mechanism: str) -> tuple[tuple, ...]:
    return (a("style", "Style", style), a("point_size", "Point size", point),
            a("mechanism", "Mechanism", mechanism))  # fmt: skip


ROWS = (
    row("PENBAL", "Medium Ballpoint Pens", CALDERBY, PENS, "Pen", "pen",
        "Retractable ballpoint pens with a smooth, quick-drying ink for notes, forms and school work.",
        _pen("Ballpoint", "Medium", "Retractable"), packs((4, 3.0), (10, 6.0), (20, 10.0)),
        (("style", "ballpoint"), ("mechanism", "retractable"))),
    row("PENGEL", "Fine Gel Pens", LANTERNBY, PENS, "Pen", "pen",
        "Capped gel pens with a soft grip and a vivid ink that writes a crisp, even line.",
        _pen("Gel", "Fine", "Capped"), packs((4, 4.0), (10, 8.0), (20, 14.0)),
        (("style", "gel"), ("mechanism", "capped"))),
    row("PENRBB", "Bold Rollerball Pens", THISTLE, PENS, "Pen", "pen",
        "Capped rollerball pens with a free-flowing ink that glides over the page without pressing.",
        _pen("Rollerball", "Bold", "Capped"), packs((4, 5.0), (10, 10.0), (20, 17.0)),
        (("style", "rollerball"), ("mechanism", "capped"))),
)

SPEC = TypeSpec(
    key="pen",
    department=DEPARTMENT,
    product_type="Pen",
    derivable=True,
    rows=ROWS,
    decoys=(
        Decoy(4, "red pen", "vocabulary", decoy(ROWS[0], "PENRDG", "Red Grip Ballpoint Pens",
              "Ballpoint pens in black ink with a red rubber grip for a steady hold.", BLACK)),
        Decoy(6, "green pen", "generic", decoy(ROWS[1], "PENGRP", "Green Park Gel Pens",
              "From the Green Park range: capped gel pens in blue ink.", BLUE)),
    ),
)  # fmt: skip
