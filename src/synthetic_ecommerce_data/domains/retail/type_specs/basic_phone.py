"""Basic phones (gen#332): a bar, a flip and a big-button phone, calls and messages only.

Rows: ``electronics_rows``. Drawing: ``kit_electronics``. Only Apple is a real brand name.
"""

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.electronics_rows import (
    BASIC_PHONES,
    ELECTRONICS_OWNERS,
)
from synthetic_ecommerce_data.domains.retail.type_registry import TypeSpec

SPEC = TypeSpec(
    key="basic_phone",
    department="Electronics",
    product_type="Basic Phone",
    owners=ELECTRONICS_OWNERS,
    rows=BASIC_PHONES,
)
