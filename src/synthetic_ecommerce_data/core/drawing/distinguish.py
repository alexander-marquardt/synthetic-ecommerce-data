"""When two brands' drawings are visibly different, and how many brands that allows (#55)."""

from __future__ import annotations

from typing import NamedTuple

#: Brands the deepened catalog (#53) is sized for.
BRANDS_NEEDED = 135
WEAK_LEVERS_NEEDED = 3
MIN_INK_DELTA_E = 15.0
VISION = ("none", "prot", "deut", "trit")


class Style(NamedTuple):
    ink: int
    paper: int
    frame: int
    mark: object
    outline: int
    dash: int
    margin: int
    texture: int


def style_of(brand: str) -> Style:
    from synthetic_ecommerce_data.core import brands
    from synthetic_ecommerce_data.core.drawing.brand_mark import mark_for

    book = brands.BY_NAME[brand]
    return Style(
        book.ink,
        brands.PAPERS.index(brands.paper_of(brand)),
        book.frame,
        mark_for(brand),
        book.outline,
        book.dash,
        book.margin,
        book.texture,
    )


def ink_delta_e(a: str, b: str, vision: tuple[str, ...] = VISION) -> float:
    return 0.0


def inks_are_safe(a: str, b: str) -> bool:
    return False


def visibly_different(a: Style, b: Style) -> bool:
    return False


def pack() -> list[Style]:
    return []


def capacity() -> int:
    return len(pack())
