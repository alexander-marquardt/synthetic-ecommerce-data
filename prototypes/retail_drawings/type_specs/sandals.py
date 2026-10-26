"""Sandals (gen#427, moved from the legacy list to a spec): the styles stay in
:mod:`footwear_rows`, which states a shoe's size charts and uppers; this registers them.
"""

from footwear_rows import footwear_spec
from type_registry import Home

SPEC = footwear_spec(
    "sandals",
    "Sandals",
    homes=(Home("decoy_product_words", False),),
)
