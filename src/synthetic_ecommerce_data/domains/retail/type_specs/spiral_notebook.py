"""Spiral notebooks (gen#969): Office & school > Paper & notebooks > Spiral notebooks.

A breadth type: ``derivable`` True, so the scaled build draws more notebooks from these two by the
values their titles show (the page size and the ruling). The color is the cover's; the binding draws
the coil on the side or the top, and the ruling is printed on the cover panel
(:func:`kit_office.spiral_notebook`). Each SKU is a color in a pack of one, three or five.
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.office_rows import (
    BLUE,
    CALDERBY,
    DEPARTMENT,
    LANTERNBY,
    NOTEBOOKS,
    RED,
    decoy,
    packs,
    row,
)
from synthetic_ecommerce_data.domains.retail.type_registry import Decoy, TypeSpec, a


def _book(size: str, ruling: str, binding: str) -> tuple[tuple, ...]:
    return (a("page_size", "Page size", size), a("ruling", "Ruling", ruling),
            a("binding", "Binding", binding))  # fmt: skip


ROWS = (
    row("SNBA4L", "A4 Lined Spiral Notebook", CALDERBY, NOTEBOOKS, "Spiral Notebook", "spiral_notebook",
        "A wirebound notebook of 80 lined sheets with a margin and a stiff card cover, for lessons and lectures.",
        _book("A4", "Lined", "Side Bound"), packs((1, 3.0), (3, 7.5), (5, 11.0)),
        (("binding", "side bound"), ("ruling", "lined"))),
    row("SNBA5S", "A5 Squared Spiral Notebook", LANTERNBY, NOTEBOOKS, "Spiral Notebook", "spiral_notebook",
        "A wirebound notebook of 60 squared sheets that fold flat over the coil, for maths and sketches.",
        _book("A5", "Squared", "Top Bound"), packs((1, 2.5), (3, 6.0), (5, 9.0)),
        (("binding", "top bound"), ("ruling", "squared"))),
)

SPEC = TypeSpec(
    key="spiral_notebook",
    department=DEPARTMENT,
    product_type="Spiral Notebook",
    derivable=True,
    rows=ROWS,
    decoys=(
        Decoy(4, "black notebook", "vocabulary", decoy(ROWS[0], "SNBBLE", "A4 Lined Spiral Notebook with Black Elastic",
              "A blue wirebound notebook of 80 lined sheets, held shut by a black elastic band.", BLUE)),
        Decoy(6, "black notebook", "generic", decoy(ROWS[1], "SNBBLI", "Black Isle A5 Squared Spiral Notebook",
              "From the Black Isle range: a red wirebound notebook of 60 squared sheets.", RED)),
    ),
)  # fmt: skip
