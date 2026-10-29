"""Puffer Jackets (gen#211): puffer jackets, drawn by :mod:`kit_coats`.

The styles are written in :mod:`outerwear_rows` (the eleven outerwear types share their palette,
brands and helpers); this spec registers the type and reads its rows back. Templates only
(``derivable`` False), so the seeded derivation is what it was.
"""

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail import outerwear_rows
from synthetic_ecommerce_data.domains.retail.type_registry import Home, TypeSpec

PRODUCT_TYPE = "Puffer Jacket"

SPEC = TypeSpec(
    key="puffer_jacket",
    homes=(Home("decoy_rows", False),),
    department="Clothing",
    product_type=PRODUCT_TYPE,
    owners=outerwear_rows.owners_of(PRODUCT_TYPE),
    rows=outerwear_rows.rows_of(PRODUCT_TYPE),
)
