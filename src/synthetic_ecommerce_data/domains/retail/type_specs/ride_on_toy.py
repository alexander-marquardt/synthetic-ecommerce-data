"""Ride-On Toy (Toys), registered by its spec (gen#537).

The rows stay in the shared row modules named by ``homes``; ``derivable`` there says
whether the scaled build draws more of them. Add rows of this type there, and a new
type as its own spec file with its rows.
"""

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.type_registry import Home, TypeSpec

SPEC = TypeSpec(
    key="ride_on_toy",
    department="Toys",
    product_type="Ride-On Toy",
    rows=(),
    homes=(
        Home("decoy_product_words", False),
        Home("toys_rows", False),
    ),
)
