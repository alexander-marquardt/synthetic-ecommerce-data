"""Phone cases (gen#332). Each names the phone it fits: the model-word decoy.

Rows: ``electronics_rows``. Drawing: ``kit_electronics``.
"""

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.electronics_rows import (
    DECOY_ROWS,
    ELECTRONICS_OWNERS,
    PHONE_CASES,
)
from synthetic_ecommerce_data.domains.retail.type_registry import Decoy, TypeSpec

SPEC = TypeSpec(
    key="phone_case",
    department="Electronics",
    product_type="Phone Case",
    owners=ELECTRONICS_OWNERS,
    rows=PHONE_CASES,
    decoys=tuple(Decoy(c, q, p, r) for c, q, p, r in DECOY_ROWS["phone_case"]),
)
