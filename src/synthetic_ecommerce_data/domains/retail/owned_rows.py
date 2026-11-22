"""Every module-level retail row sells an owned brand, checked before any ``doc()`` (gen#1039).

Red stub: names nothing yet.
"""

from __future__ import annotations

from collections.abc import Iterator

from synthetic_ecommerce_data.domains.retail.breadth_row import Row


class UnownedBrand(ValueError):
    """A module-level row sells a brand :func:`brand_owners.table` does not own."""


def rows() -> Iterator[tuple[str, Row]]:
    yield from ()


def unowned() -> list[str]:
    return []


def check() -> None:
    return None
