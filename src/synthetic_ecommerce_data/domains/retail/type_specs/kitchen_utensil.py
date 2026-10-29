"""Kitchen Utensil (Home), registered by its spec (gen#537).

The rows stay in the shared row modules named by ``homes``; ``derivable`` there says
whether the scaled build draws more of them. Add rows of this type there, and a new
type as its own spec file with its rows.
"""

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.type_registry import Home, TypeSpec

SPEC = TypeSpec(
    key="kitchen_utensil",
    department="Home",
    product_type="Kitchen Utensil",
    rows=(),
    homes=(
        Home("breadth_rows", True),
        Home("distractor_rows", False),
        Home("decor_rows", False),
    ),
)
