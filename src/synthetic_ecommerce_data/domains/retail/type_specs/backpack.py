"""Backpack (Clothing), registered by its spec (gen#537).

The rows stay in the shared row modules named by ``homes``; ``derivable`` there says
whether the scaled build draws more of them. Add rows of this type there, and a new
type as its own spec file with its rows. The Barry Plotter range (gen#925) is the one set
of rows the spec reads itself, from :mod:`barry_plotter`.
"""

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail import barry_plotter
from synthetic_ecommerce_data.domains.retail.type_registry import Home, TypeSpec

SPEC = TypeSpec(
    key="backpack",
    department="Clothing",
    product_type="Backpack",
    rows=barry_plotter.rows_of("Backpack"),
    homes=(
        Home("decoy_product_words", False),
        Home("accessory_rows", False),
        Home("knacks_rows", False),
    ),
)
