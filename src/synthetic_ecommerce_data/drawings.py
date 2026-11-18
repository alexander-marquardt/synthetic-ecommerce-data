"""The public draw call (gen#1022): red-commit stub, the call's names with nothing drawn yet."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from typing import Any

FINISHES: tuple[str, ...] = ("unbranded", "brand")

#: Type -> (view, nominal width, height, depth in inches).
PROPORTIONS: dict[str, tuple[str, float, float, float]] = {
    "sideboard": ("front", 60, 32, 18),
    "bar_cabinet": ("front", 36, 60, 18),
    "storage_cabinet": ("front", 30, 66, 16),
    "shoe_storage": ("front", 32, 22, 12),
    "wall_shelf": ("front", 24, 16, 8),
    "bar_stool": ("front", 17, 41, 17),
    "desk": ("front", 48, 30, 24),
    "office_chair": ("front", 26, 42, 26),
    "tv_stand": ("front", 60, 22, 16),
    "kitchen_island": ("front", 48, 36, 30),
    "bookcase": ("front", 32, 72, 12),
    "wardrobe": ("front", 40, 72, 22),
    "chest_of_drawers": ("front", 32, 44, 18),
    "sofa": ("front", 80, 34, 36),
    "rug": ("top", 96, 0.5, 60),
}

UNBRANDED_FRAMES: tuple[str, ...] = ()


@dataclass(frozen=True)
class UnbrandedLook:
    frame: str
    margin: float
    stroke: float
    dashed: bool
    accent: str


def unbranded_look(product_id: str) -> UnbrandedLook:
    return UnbrandedLook("thin", 1.0, 1.0, False, "#666666")


def figure(type_: str, attributes: Mapping[str, Any]) -> str:
    return ""


def render(
    type_: str,
    attributes: Mapping[str, Any],
    finish: str = "unbranded",
    *,
    product_id: str,
    brand: str | None = None,
) -> str:
    return "<svg/>"


def picture_share(rows: Iterable[Mapping[str, Any]]) -> dict[str, tuple[int, int]]:
    return {}
