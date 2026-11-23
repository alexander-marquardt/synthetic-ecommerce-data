"""Smartphones (gen#332): the gen#332 styles from eight invented brands, with storage tiers, and
the phone range's new models (gen#1117), each also sold unlocked or carrier-locked.

Rows: ``electronics_rows`` and ``phone_range_rows``. Drawing: ``kit_electronics``.
"""

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail import phone_range_rows
from synthetic_ecommerce_data.domains.retail.electronics_rows import ELECTRONICS_OWNERS, SMARTPHONES
from synthetic_ecommerce_data.domains.retail.type_registry import Option, TypeSpec

SPEC = TypeSpec(
    key="smartphone",
    department="Electronics",
    product_type="Smartphone",
    owners=ELECTRONICS_OWNERS,
    options=(
        Option("storage_gb", "storage_capacity", "Storage (GB)"),
        Option("network_lock", "network_lock", "Network lock"),
    ),
    rows=SMARTPHONES + phone_range_rows.SMARTPHONES,
)
