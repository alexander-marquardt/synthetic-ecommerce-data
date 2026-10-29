"""Tee (Clothing), registered by its spec (gen#537).

The rows stay in the shared row modules named by ``homes``; ``derivable`` there says
whether the scaled build draws more of them. Add rows of this type there, and a new
type as its own spec file with its rows.
"""

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.type_registry import Home, TypeSpec

SPEC = TypeSpec(
    key="tee",
    department="Clothing",
    product_type="Tee",
    rows=(),
    homes=(
        Home("samples", True),
        Home("decoy_product_words", False),
        Home("nike_rows", False),
    ),
)
