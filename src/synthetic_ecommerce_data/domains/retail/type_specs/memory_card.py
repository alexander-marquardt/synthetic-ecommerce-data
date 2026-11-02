"""Memory cards (gen#796): microSD and SD cards, sold by capacity, with a speed class.

The "memory card" a shopper searches for; its word decoys (a storage wallet, a laptop sleeve with a
card pocket) are in ``feature_decoys/memory_card_796.py``.

Rows: ``electronics_rows``. Drawing: ``kit_electronics``.
"""

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.electronics_rows import (
    ELECTRONICS_OWNERS,
    MEMORY_CARDS,
)
from synthetic_ecommerce_data.domains.retail.type_registry import TypeSpec

SPEC = TypeSpec(
    key="memory_card",
    department="Electronics",
    product_type="Memory Card",
    owners=ELECTRONICS_OWNERS,
    rows=MEMORY_CARDS,
)
