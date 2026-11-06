"""Jumper (Clothing), registered by its spec (gen#537).

The rows stay in the shared row modules named by ``homes``; ``derivable`` there says
whether the scaled build draws more of them. Add rows of this type there, and a new
type as its own spec file with its rows. The merchandise of the invented kids' films
(gen#887) is the one set of rows the spec reads itself, from :mod:`kids_films`.
"""

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail import kids_films
from synthetic_ecommerce_data.domains.retail.type_registry import Home, TypeSpec

SPEC = TypeSpec(
    key="jumper",
    department="Clothing",
    product_type="Jumper",
    rows=kids_films.rows_of("Jumper"),
    homes=(
        Home("samples", True),
        Home("decoy_product_words", False),
        Home("seasonal_rows", False),
        Home("colorgroup_rows", False),
        Home("knitwear_rows", False),
    ),
)
