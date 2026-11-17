"""Colored Pencils (gen#969, slice 3): Office & school > Art supplies > Colored pencils.

A breadth type: ``derivable`` True, so the scaled build draws more sets from these four by the
values their titles show (the number of pencils and the kind). A set holds pencils of many colors,
so the SKU's color is its tin's: the drawing is the tin in that color with its pencils standing in
it, a brush before a watercolor set and an eraser before an erasable one
(:func:`kit_office.colored_pencils`). The drawing shows its own count (``count``), so its pencils are never
laid out as copies; a 2 or 3 pack of tins (a classroom pack) is drawn as that many tins. Each SKU
is a tin color, sold singly or in a 2 or 3 pack.
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.office_rows import (
    BLACK,
    CALDERBY,
    COLORED_PENCILS,
    DEPARTMENT,
    LANTERNBY,
    THISTLE,
    YELLOW,
    decoy,
    packs,
    row,
)
from synthetic_ecommerce_data.domains.retail.type_registry import Decoy, TypeSpec, a, count


def _set(kind: str, n: str) -> tuple[tuple, ...]:
    return (a("pencil_type", "Pencil type", kind), count("count", "Pencils in set", int(n)),
            a("material", "Material", "Cedar"))  # fmt: skip


def _params(kind: str, n: str) -> tuple[tuple[str, str], ...]:
    return (("pencil_type", kind.lower()), ("count", n))


ROWS = (
    row("CPCC12", "12 Classic Colored Pencils", CALDERBY, COLORED_PENCILS, "Colored Pencils", "colored_pencils",
        "Pre-sharpened cedar pencils with bright, even leads, in a tin, for drawing, coloring and school projects.",
        _set("Classic", "12"), packs((1, 6.0), (2, 11.0), (3, 16.0)), _params("Classic", "12")),
    row("CPCW24", "24 Watercolor Colored Pencils", LANTERNBY, COLORED_PENCILS, "Colored Pencils", "colored_pencils",
        "Water-soluble pencils that draw like a pencil and wash like a paint with a wet brush, in a tin with a brush.",
        _set("Watercolor", "24"), packs((1, 14.0), (2, 26.0), (3, 38.0)), _params("Watercolor", "24")),
    row("CPCS36", "36 Soft Core Colored Pencils", THISTLE, COLORED_PENCILS, "Colored Pencils", "colored_pencils",
        "Pencils with thick, soft leads that blend and layer smoothly, in a tin, for artists and adult coloring books.",
        _set("Soft Core", "36"), packs((1, 22.0), (2, 42.0), (3, 60.0)), _params("Soft Core", "36")),
    row("CPCE48", "48 Erasable Colored Pencils", THISTLE, COLORED_PENCILS, "Colored Pencils", "colored_pencils",
        "Pencils whose leads rub out cleanly, in a tin with an eraser, so a sketch can be corrected before it is finished.",
        _set("Erasable", "48"), packs((1, 26.0), (2, 50.0), (3, 72.0)), _params("Erasable", "48")),
)

SPEC = TypeSpec(
    key="colored_pencils",
    department=DEPARTMENT,
    product_type="Colored Pencils",
    derivable=True,
    rows=ROWS,
    decoys=(
        Decoy(4, "red colored pencils", "vocabulary", decoy(ROWS[0], "CPCRDL", "12 Classic Colored Pencils with Red Lid Clasp",
              "Classic colored pencils in a yellow tin with a red lid clasp.", YELLOW)),
        Decoy(6, "white colored pencils", "generic", decoy(ROWS[1], "CPCWHT", "White Harbour 24 Watercolor Colored Pencils",
              "From the White Harbour range: water-soluble pencils in a black tin with a brush.", BLACK)),
    ),
)  # fmt: skip
