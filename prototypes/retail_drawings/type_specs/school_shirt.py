"""School Shirt (Clothing), registered by its spec (gen#537).

The rows stay in the shared row modules named by ``homes``; ``derivable`` there says
whether the scaled build draws more of them. Add rows of this type there, and a new
type as its own spec file with its rows.
"""

from __future__ import annotations

from type_registry import Home, TypeSpec

SPEC = TypeSpec(
    key="school_shirt",
    department="Clothing",
    product_type="School Shirt",
    rows=(),
    homes=(Home("school_rows", False),),
)
