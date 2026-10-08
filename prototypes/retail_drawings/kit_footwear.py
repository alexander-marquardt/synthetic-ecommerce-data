"""Side-view shoe drawings (stub)."""

from __future__ import annotations

from kit import Fill

__all__ = ["Fill"]

KINDS: dict[str, dict] = {}


def top(kind: str) -> float:
    return 0.0


def shoe(paint: str, fill: Fill, label: str | None, kind: str = "", material: str = "") -> list:
    return []
