"""Product ids and SKUs that name what a product is, not where it sits (gen#626).

Stub: the red commit's guard tests import this module and fail on an assertion.
"""

from __future__ import annotations


class IdCollision(ValueError):
    """Two products, or two SKUs, were given one id."""


def check_unique(docs: list[dict]) -> None:
    """Raise :class:`IdCollision` when two documents share a product id or a SKU."""
