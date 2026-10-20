"""Dishwashers (gen#334): full-size, slimline, integrated and table-top, six models each.

Drawn by :func:`kit_large_appliances.dishwasher`. A model's place settings, width, energy rating
and noise level are structured; its finish is the SKU's color. The word "dishwasher" is also in
the description of mugs, lunch boxes and cutlery ("Dishwasher safe"), and in the title of
dishwasher tablets, salt and rinse aid (``feature_decoys/large_appliances.py``): a category
policy routes the query to Home > Large Appliances > Dishwashers. Every brand is invented.
Not derivable: the range is authored.
"""

# ruff: noqa: E501 -- data tables and descriptions read better whole than wrapped.

from __future__ import annotations

import large_appliance_rows as rows
from type_registry import TypeSpec

SPEC = TypeSpec(
    key="dishwasher",
    department="Home",
    product_type="Dishwasher",
    owners=rows.OWNERS,
    rows=rows.dishwasher_rows(),
)
