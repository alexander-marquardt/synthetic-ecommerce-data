"""Chargers (gen#332): wall, wireless, power bank and car chargers for a named device.

Rows: ``electronics_rows``. Drawing: ``kit_electronics``. Only Apple is a real brand name.
"""

from __future__ import annotations

from electronics_rows import CHARGERS, DECOY_ROWS, ELECTRONICS_OWNERS
from type_registry import Decoy, TypeSpec

SPEC = TypeSpec(
    key="charger",
    department="Electronics",
    product_type="Charger",
    owners=ELECTRONICS_OWNERS,
    rows=CHARGERS,
    decoys=tuple(Decoy(c, q, p, r) for c, q, p, r in DECOY_ROWS["charger"]),
)
