"""Gift Bag (Gifts), registered by its spec (gen#537).

The rows stay in the shared row modules named by ``homes``; ``derivable`` there says
whether the scaled build draws more of them. Add rows of this type there, and a new
type as its own spec file with its rows. The merchandise of the invented kids' films
(gen#887) is the one set of rows the spec reads itself, from :mod:`kids_films`.
"""

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail import kids_films
from synthetic_ecommerce_data.domains.retail.type_registry import Home, TypeSpec

SPEC = TypeSpec(
    key="gift_bag",
    department="Gifts",
    product_type="Gift Bag",
    rows=kids_films.rows_of("Gift Bag"),
    homes=(
        Home("samples", True),
        Home("seasonal_rows", False),
    ),
)
