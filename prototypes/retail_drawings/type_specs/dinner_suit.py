"""Dinner suits (gen#215, a spec by gen#351): a Mens tailoring type with its own decoys.

The rows are not written out one by one: ``mens_depth_rows`` generates them from its floor
leaf, its matching suits and its seven decoy classes (a suit's jacket, trousers and waistcoat
share one cloth, so the three types draw on one table). This spec registers the type and reads
its rows and decoys back with ``mens_depth_rows.spec_rows`` and ``spec_decoys``.
"""

from __future__ import annotations

import mens_depth_rows
from type_registry import TypeSpec

PRODUCT_TYPE = "Dinner Suit"

SPEC = TypeSpec(
    key="dinner_suit",
    department="Clothing",
    product_type=PRODUCT_TYPE,
    rows=mens_depth_rows.spec_rows(PRODUCT_TYPE),
    decoys=mens_depth_rows.spec_decoys(PRODUCT_TYPE),
    apparel_exempt="a Mens tailoring type (gen#215), with its own decoys",
)
