"""Synthetic industrial-supply catalog records, and drawings rendered from them."""

from __future__ import annotations

from .dimensions import DimensionParseError, Length, Thread, parse_length, parse_thread
from .records import FIXTURES
from .render import CARD, DETAIL, PROFILES, render_record

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
