"""Garden Statue (Home), registered by its spec (gen#1093).

Its products are the wands-inspired ones: one of our own per picture of the pinned picture
manifest (``picture_products``), shipped as written. The scaled build derives none from them.
"""

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.type_registry import Home, TypeSpec

SPEC = TypeSpec(
    key="garden_statue",
    department="Home",
    product_type="Garden Statue",
    rows=(),
    homes=(Home("picture_products", False),),
)
