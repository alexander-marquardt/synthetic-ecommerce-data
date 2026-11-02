"""Sofa (Home), registered by its spec (gen#537).

The rows stay in the shared row modules named by ``homes``; ``derivable`` there says
whether the scaled build draws more of them. Add rows of this type there, and a new
type as its own spec file with its rows.
"""

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.type_registry import Home, Option, TypeSpec

SPEC = TypeSpec(
    key="sofa",
    department="Home",
    product_type="Sofa",
    rows=(),
    homes=(
        Home("decoy_rows", False),
        Home("sofa_rows", False),
    ),
    # A grouped sofa's version, and the seat count and depth that follow it (gen#808).
    options=(
        Option("configuration", "configuration", "Configuration"),
        Option("seat_count", "seat_count", "Seat count", "C62"),
        Option("depth_cm", "item_depth", "Item depth", "CMT"),
    ),
)
