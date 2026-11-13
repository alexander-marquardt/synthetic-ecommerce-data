"""Pencils (gen#969): Office & school > Pens & pencils > Pencils.

A breadth type: ``derivable`` True, so the scaled build draws more pencils from these four by the
lead grade their titles show (HB, 2B, 4B, 2H). The color is the barrel's; a pencil sold with an eraser
is drawn with its ferrule and eraser, one without with a dipped end (:func:`kit_office.pencil`).
Each SKU is a color in a pack of 6, 12 or 24.
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.office_rows import (
    BLACK,
    CALDERBY,
    DEPARTMENT,
    LANTERNBY,
    PENCILS,
    THISTLE,
    YELLOW,
    decoy,
    packs,
    row,
)
from synthetic_ecommerce_data.domains.retail.type_registry import Decoy, TypeSpec, a


def _pencil(grade: str) -> tuple[tuple, ...]:
    return (a("lead_grade", "Lead grade", grade), a("material", "Material", "Cedar"))


ROWS = (
    row("PNCHBE", "HB Pencils with Eraser", THISTLE, PENCILS, "Pencil", "pencil",
        "Sharpened cedar pencils with a smooth HB lead and an eraser on the end, for writing and school work.",
        _pencil("HB"), packs((6, 2.0), (12, 3.5), (24, 6.0)), (("eraser", "yes"),)),
    row("PNC2BD", "2B Drawing Pencils", CALDERBY, PENCILS, "Pencil", "pencil",
        "Sharpened cedar pencils with a soft 2B lead that shades smoothly, the end dipped in the barrel's color.",
        _pencil("2B"), packs((6, 3.0), (12, 5.0), (24, 9.0)), (("eraser", "no"),)),
    row("PNC4BS", "4B Sketching Pencils", LANTERNBY, PENCILS, "Pencil", "pencil",
        "Sharpened cedar pencils with a dark 4B lead for bold lines and deep shading.",
        _pencil("4B"), packs((6, 3.5), (12, 6.0), (24, 10.0)), (("eraser", "no"),)),
    row("PNC2HT", "2H Technical Pencils", THISTLE, PENCILS, "Pencil", "pencil",
        "Sharpened cedar pencils with a 2H lead that holds its point, for plans, diagrams and technical drawing.",
        _pencil("2H"), packs((6, 2.5), (12, 4.5), (24, 8.0)), (("eraser", "no"),)),
)

SPEC = TypeSpec(
    key="pencil",
    department=DEPARTMENT,
    product_type="Pencil",
    derivable=True,
    rows=ROWS,
    decoys=(
        Decoy(4, "red pencil", "vocabulary", decoy(ROWS[0], "PNCRDE", "HB Pencils with Red Eraser",
              "Yellow cedar pencils with an HB lead and a red eraser on the end.", YELLOW)),
        Decoy(6, "white pencil", "generic", decoy(ROWS[1], "PNCWCL", "White Cliffs 2B Drawing Pencils",
              "From the White Cliffs range: cedar pencils with a soft 2B lead.", BLACK)),
    ),
)  # fmt: skip
