"""Product id and SKU minting, domain-neutral (#128, blocker 5)."""

from __future__ import annotations


def check_prefix(prefix: str) -> None:
    """Refuse a prefix that is not empty or one or two capital letters."""


def claim_prefix(domain: str, prefix: str) -> None:
    """Record that ``domain`` mints with ``prefix``; refuse a prefix another domain holds."""


class IdMinter:
    """One type's product ids and SKUs, behind a per-domain prefix."""

    def __init__(self, prefix: str, type_key: str, block: int) -> None:
        self.prefix = prefix
        self.type_key = type_key
        self.block = block

    def next_index(self) -> int:
        return 0

    def new_sku(self) -> str:
        return ""

    def product_id(self, brand_code: str, series: str, index: int) -> str:
        return ""
