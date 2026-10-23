"""Synthetic industrial-supply catalog records, and the text-free drawings of them."""

from __future__ import annotations

from synthetic_ecommerce_data.core.dimensions import (
    DimensionParseError,
    Length,
    Thread,
    parse_length,
    parse_thread,
)
from synthetic_ecommerce_data.domains.industrial.records import FIXTURES

__all__ = [
    "FIXTURES",
    "DimensionParseError",
    "Length",
    "Thread",
    "parse_length",
    "parse_thread",
]
