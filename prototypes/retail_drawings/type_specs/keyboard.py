"""Keyboards (gen#332): full-size and compact.

Rows: ``electronics_rows``. Drawing: ``kit_electronics``. Only Apple is a real brand name.
"""

from __future__ import annotations

from electronics_rows import DECOY_ROWS, ELECTRONICS_OWNERS, KEYBOARDS
from type_registry import Decoy, TypeSpec

SPEC = TypeSpec(
    key="keyboard",
    department="Electronics",
    product_type="Keyboard",
    owners=ELECTRONICS_OWNERS,
    rows=KEYBOARDS,
    decoys=tuple(Decoy(c, q, p, r) for c, q, p, r in DECOY_ROWS["keyboard"]),
)
