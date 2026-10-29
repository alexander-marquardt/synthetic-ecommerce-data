"""Chukka Boots (gen#427, moved from the legacy list to a spec): the styles stay in
:mod:`footwear_rows`, which states a shoe's size charts and uppers; this registers them.
"""

from synthetic_ecommerce_data.domains.retail.footwear_rows import footwear_spec
from synthetic_ecommerce_data.domains.retail.type_registry import Home

SPEC = footwear_spec(
    "chukka_boots",
    "Chukka Boots",
    homes=(Home("scale_rows", True),),
)
