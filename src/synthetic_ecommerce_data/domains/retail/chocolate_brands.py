"""Each brand's chocolate packs: the color its wrappers are printed in and the trim round its
mark (gen#1125).

A pack's color is its brand's and its flavour's color is the accent, so two brands' Milk bars
draw apart. The mark is the brand's own house mark (:data:`house_styles.HOUSE_STYLES`), set on
the pack by :func:`kit_chocolate.brand_mark`. Every brand is invented, and every brand that
sells a chocolate has a row here (``tests/test_chocolate_brand_1125.py``).
"""

from __future__ import annotations

from dataclasses import dataclass

#: The drawings that carry their brand: every shape :mod:`kit_chocolate` registers.
SHAPES = frozenset(
    {
        "chocolate_bar",
        "chocolate_box",
        "chocolate_bag",
        "hot_chocolate",
        "chocolate_orange",
        "peanut_butter_cups",
        "advent_calendar",
    }
)


@dataclass(frozen=True)
class Look:
    """A brand's chocolate packs: the wrapper's color and the trim round its mark."""

    wrapper: str
    trim: str


#: One row per brand, every color chosen by hand: no two read alike, and none needs moving to
#: stay visible on white paper (``kit_chocolate.WRAPPER_CONTRAST``).
LOOKS = {
    "Barrowby Kitchen": Look("#1f7a4a", "#e8d9a8"),
    "Brewhollow Roasters": Look("#7a5a10", "#f0d9a0"),
    "Crunchworth": Look("#c2451f", "#f5c542"),
    "Hearth & Table": Look("#6d2348", "#d9b45a"),
    "Pantry Mill": Look("#2f5f94", "#d9e4ee"),
}


def params(rec: dict) -> dict[str, str]:
    """The pack's brand, for a chocolate drawing of a brand in :data:`LOOKS`; else nothing."""
    branded = rec["drawing"]["shape"] in SHAPES and rec["brand"] in LOOKS
    return {"brand": rec["brand"]} if branded else {}
