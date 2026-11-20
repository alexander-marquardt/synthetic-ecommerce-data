"""A retail ``size`` under its size system's key (gen#125): a stub for the red commit."""

from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping
from typing import Any

SIZE = "size"


def entry(value: str, department: str, siblings: Mapping[str, str] | None = None) -> dict[str, Any]:
    return {"key": SIZE, "name": "Size", "value": value}


def siblings_of(entries: Iterable[Mapping[str, Any]]) -> dict[str, str]:
    return {}


def renamed(
    entries: list[dict[str, Any]],
    department: str,
    siblings: Callable[[str], Mapping[str, str]],
) -> list[dict[str, Any]]:
    return entries
