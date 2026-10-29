"""Arts and Crafts Kit (Toys), registered by its spec (gen#537).

The rows stay in the shared row modules named by ``homes``; ``derivable`` there says
whether the scaled build draws more of them. Add rows of this type there, and a new
type as its own spec file with its rows.
"""

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.type_registry import Home, TypeSpec

SPEC = TypeSpec(
    key="arts_and_crafts_kit",
    department="Toys",
    product_type="Arts and Crafts Kit",
    rows=(),
    homes=(Home("toys_rows", False),),
)
