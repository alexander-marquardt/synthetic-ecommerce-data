"""Night Light (Toys), registered by its spec (gen#537).

The rows stay in the shared row modules named by ``homes``; ``derivable`` there says
whether the scaled build draws more of them. Add rows of this type there, and a new
type as its own spec file with its rows. The Barry Plotter range (gen#925) is the one set
of rows the spec reads itself, from :mod:`barry_plotter`.
"""

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail import barry_plotter
from synthetic_ecommerce_data.domains.retail.type_registry import Home, TypeSpec

SPEC = TypeSpec(
    key="night_light",
    department="Toys",
    product_type="Night Light",
    rows=barry_plotter.rows_of("Night Light"),
    homes=(
        Home("breadth_rows", True),
        Home("decoy_product_words", False),
    ),
)
