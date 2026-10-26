"""Running Shoes (gen#427, moved from the legacy list to a spec): the styles stay in
:mod:`footwear_rows`, which states a shoe's size charts and uppers; this registers them.
"""

from footwear_rows import footwear_spec
from type_registry import Home

SPEC = footwear_spec(
    "running_shoes",
    "Running Shoes",
    homes=(Home("nike_rows", False),),
)
