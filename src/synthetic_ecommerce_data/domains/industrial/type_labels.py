"""The shopper-readable name of each industrial product type (#331)."""

from __future__ import annotations

PRODUCT_TYPE_LABELS: dict[str, str] = {}


def label_for(type_key: str) -> str:
    return PRODUCT_TYPE_LABELS.get(type_key, "")
