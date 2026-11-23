"""The sewing and knitting range's shared pieces (gen#1118): its paths, brands, colors and rows.

Sewing and knitting sit in Office & School beside Art Supplies (``Office & School > Sewing &
Knitting``), the department #837's taxonomy gives crafts, and take its build record department
(``office_rows.DEPARTMENT``), which keys the brand pools. Each type is a spec of its own
(``type_specs/sewing_thread.py``, ``yarn.py``, ``fabric.py``) drawn by :mod:`kit_sewing`. Every
style offers the six main colors (gen#275) and the range's two more (navy and grey, the colors a
sewing basket runs out of first). Every brand here is invented.
"""

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail import (
    kit_sewing,  # noqa: F401 -- registers the range's shapes
)
from synthetic_ecommerce_data.domains.retail.office_rows import DEPARTMENT, ROOT, SIX
from synthetic_ecommerce_data.domains.retail.type_registry import Row, cw

NODE = (ROOT, "Sewing & Knitting")
THREAD = (*NODE, "Sewing Thread")
YARN = (*NODE, "Yarn")
FABRIC = (*NODE, "Fabric")

#: The range's own invented brands; the stationery brands of :mod:`office_rows` sell it too.
BOBBINMERE = "Bobbinmere"
PURLWICK = "Purlwick"
OWNERS = ((BOBBINMERE, "own"), (PURLWICK, "own"))

NAVY = cw("Navy", "#26345a", "solid", "#ffffff")
GREY = cw("Grey", "#8a8d93", "solid", "#ffffff")
#: The six main colors and the two a sewing range adds.
EIGHT = (*SIX, NAVY, GREY)


def row(code: str, title: str, brand: str, path: tuple[str, ...], product_type: str, shape: str,
        description: str, attrs: tuple[tuple, ...], sizes: tuple[tuple[str, float], ...],
        params: tuple[tuple[str, str], ...], size_key: str = "pack_size") -> Row:  # fmt: skip
    """One sewing style: its eight colors times its ``size_key`` values are its SKUs."""
    return Row(code, title, brand, DEPARTMENT, path, product_type, sizes[0][1], shape, description,
               EIGHT, attrs, sizes, params=params, size_key=size_key)  # fmt: skip
