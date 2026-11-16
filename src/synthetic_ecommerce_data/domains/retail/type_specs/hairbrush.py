"""Hairbrushes (gen#957): Beauty > Hair Care > Hairbrushes.

A breadth type: ``derivable`` True, so the scaled build draws more hairbrushes from these four by
the values their titles show (the head and the bristle). The handle is the SKU's color; the head
draws the brush's outline and the bristle the tips of its pins (:func:`kit_hair.hairbrush`). Each
SKU is a color in a size.
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.hair_rows import (
    BRUSHES,
    DEPARTMENT,
    GREEN,
    YELLOW,
    decoy,
    row,
)
from synthetic_ecommerce_data.domains.retail.type_registry import Decoy, TypeSpec, a


def _brush(head: str, bristle: str) -> tuple[tuple, ...]:
    return (a("head", "Head", head), a("bristle", "Bristle", bristle))


def _sizes(price: float) -> tuple[tuple[str, float], ...]:
    return (("Small", price), ("Medium", price + 2.0), ("Large", price + 4.0))


def _params(head: str, bristle: str) -> tuple[tuple[str, str], ...]:
    return (("head", head.lower()), ("bristle", bristle.lower()))


ROWS = (
    row(
        "HBRPAD",
        "Boar Bristle Paddle Hairbrush",
        "Hollin Hair",
        BRUSHES,
        "Hairbrush",
        "hairbrush",
        "A wide cushioned brush with natural bristles that smooths long hair and spreads its oils.",
        _brush("Paddle", "Boar"),
        _sizes(14.0),
        _params("Paddle", "Boar"),
        "size",
    ),
    row(
        "HBRRND",
        "Nylon Round Hairbrush",
        "Fenmere",
        BRUSHES,
        "Hairbrush",
        "hairbrush",
        "A barrel brush with heat-resistant pins for a blow-dry with volume and soft curls.",
        _brush("Round", "Nylon"),
        _sizes(9.0),
        _params("Round", "Nylon"),
        "size",
    ),
    row(
        "HBRVNT",
        "Mixed Bristle Vent Hairbrush",
        "Aldermist",
        BRUSHES,
        "Hairbrush",
        "hairbrush",
        "An open-backed brush that lets warm air through for a quick, everyday blow-dry.",
        _brush("Vent", "Mixed"),
        _sizes(8.0),
        _params("Vent", "Mixed"),
        "size",
    ),
    row(
        "HBRDET",
        "Nylon Detangling Hairbrush",
        "Pearlbrook",
        BRUSHES,
        "Hairbrush",
        "hairbrush",
        "Flexible, widely spaced pins that ease out knots in wet or dry hair without pulling.",
        _brush("Detangling", "Nylon"),
        _sizes(7.0),
        _params("Detangling", "Nylon"),
        "size",
    ),
)

SPEC = TypeSpec(
    key="hairbrush",
    department=DEPARTMENT,
    product_type="Hairbrush",
    derivable=True,
    rows=ROWS,
    owners=(("Hollin Hair", "third_party"), ("Fenmere", "third_party"), ("Aldermist", "third_party"), ("Pearlbrook", "third_party")),
    decoys=(
        Decoy(4, "black hairbrush", "vocabulary", decoy(ROWS[0], "HBRBKP", "Paddle Hairbrush with Black Pins",
              "A yellow paddle hairbrush with black-tipped pins on a soft cushion.", YELLOW)),
        Decoy(6, "red hairbrush", "generic", decoy(ROWS[1], "HBRRDH", "Red Hill Nylon Round Hairbrush",
              "From the Red Hill range: a round barrel brush in green.", GREEN)),
    ),
)  # fmt: skip
