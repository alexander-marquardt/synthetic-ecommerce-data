"""Synthetic industrial-supply catalog records, and drawings rendered from them."""

from __future__ import annotations

from synthetic_ecommerce_data.core.dimensions import (
    DimensionParseError,
    Length,
    Thread,
    parse_length,
    parse_thread,
)
from synthetic_ecommerce_data.domains.industrial.records import FIXTURES
from synthetic_ecommerce_data.domains.industrial.render import CARD, DETAIL, PROFILES, render_record

__all__ = [
    "CARD",
    "DETAIL",
    "FIXTURES",
    "PROFILES",
    "DimensionParseError",
    "Length",
    "Thread",
    "parse_length",
    "parse_thread",
    "render_record",
]
