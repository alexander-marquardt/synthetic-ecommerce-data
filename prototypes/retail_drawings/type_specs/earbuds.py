"""Earbuds and headphones (gen#332).

Rows: ``electronics_rows``. Drawing: ``kit_electronics``. Only Apple is a real brand name.
"""

from __future__ import annotations

from electronics_rows import EARBUDS, ELECTRONICS_OWNERS
from type_registry import TypeSpec

SPEC = TypeSpec(
    key="earbuds",
    department="Electronics",
    product_type="Earbuds",
    owners=ELECTRONICS_OWNERS,
    rows=EARBUDS,
)
