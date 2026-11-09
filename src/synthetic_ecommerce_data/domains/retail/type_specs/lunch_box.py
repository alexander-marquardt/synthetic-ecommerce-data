"""Lunch Box (Home), registered by its spec (gen#537).

The rows stay in the shared row modules named by ``homes``; ``derivable`` there says
whether the scaled build draws more of them. Add rows of this type there, and a new
type as its own spec file with its rows. The merchandise of the invented kids' films
(gen#887) and the Barry Plotter range (gen#925) are the rows the spec reads itself, from
:mod:`kids_films` and :mod:`barry_plotter`.
"""

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail import barry_plotter, kids_films
from synthetic_ecommerce_data.domains.retail.type_registry import Home, TypeSpec

SPEC = TypeSpec(
    key="lunch_box",
    department="Home",
    product_type="Lunch Box",
    rows=(*kids_films.rows_of("Lunch Box"), *barry_plotter.rows_of("Lunch Box")),
    homes=(
        Home("breadth_rows", True),
        Home("decoy_product_words", False),
    ),
)
