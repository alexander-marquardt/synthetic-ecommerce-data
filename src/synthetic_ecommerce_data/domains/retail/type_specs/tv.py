"""TVs (#721): flat and curved, a screen size per SKU, in Electronics > TVs.

Rows: ``electronics_rows``. Drawing: ``kit_electronics``. Every brand is invented.
"""

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.electronics_rows import (
    DECOY_ROWS,
    ELECTRONICS_OWNERS,
    TVS,
)
from synthetic_ecommerce_data.domains.retail.type_registry import Decoy, Option, TypeSpec

SPEC = TypeSpec(
    key="tv",
    department="Electronics",
    product_type="TV",
    owners=ELECTRONICS_OWNERS,
    options=(Option("screen_size_in", "screen_size", "Screen size", "INH"),),
    rows=TVS,
    decoys=tuple(Decoy(c, q, p, r) for c, q, p, r in DECOY_ROWS["tv"]),
)
