"""Size charts (gen#125, slice 2 of the 2026-10-28 ruling): a stub, filled by the next commit."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any

Row = tuple[str, str, str]

KEYS = ("size_uk", "size_eu", "size_us")

WOMENS: dict[int, Row] = {}
MENS_WAIST: dict[int, Row] = {}
KIDS_AGES: dict[str, Row] = {}
BABY_AGES: dict[str, Row] = {}
LETTER: dict[str, Row] = {}
WOMENS_SHOES: dict[str, Row] = {}
MENS_SHOES: dict[str, Row] = {}
KIDS_SHOES: dict[str, Row] = {}
SLIPPERS_WOMEN: dict[str, Row] = {}
SLIPPERS_MEN: dict[str, Row] = {}
BRA_BANDS: tuple[int, ...] = ()
BRA_CUPS: tuple[Row, ...] = ()
BRAS: dict[str, Row] = {}
BEDDING: dict[str, Row] = {}
CHARTS: dict[str, Mapping[Any, Row]] = {}


def problems(where: str, attributes: Iterable[Any]) -> list[str]:
    """Stub: reports nothing."""
    return []
