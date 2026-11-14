"""Golf Glove (gen#959, slice 1): Sports & Outdoors > Golf > Golf Gloves.

A breadth type: ``derivable`` True, so the scaled build draws more gloves by the values the titles
show (the material and the hand it is worn on). The back of the glove is the SKU's color; the
material draws perforations, stretch panels or both (:func:`kit_fishing_golf.golf_glove`). Each
SKU is a color in a size.
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.fishing_golf_rows import GLOVES, LARCHMERE, OWNERS
from synthetic_ecommerce_data.domains.retail.sports_helpers import (
    _H,
    _L,
    _W,
    BLACK,
    BLUE,
    GREEN,
    RED,
    WHITE,
    YELLOW,
    _a,
    _row,
    _words,
)
from synthetic_ecommerce_data.domains.retail.type_registry import TypeSpec


def _glove(material: str, hand: str) -> tuple[tuple, ...]:
    return (_a("material", "Material", material), _a("worn_on", "Worn on", hand))


def _sizes(price: float) -> tuple[tuple[str, float], ...]:
    return _words(("S", price), ("M", price), ("L", price), ("XL", price))


SPEC = TypeSpec(
    key="golf_glove",
    department="Sports & Outdoors",
    product_type="Golf Glove",
    derivable=True,
    owners=OWNERS,
    rows=(
        _row("GGLCAB", "Cabretta Leather Golf Glove, Left Hand", LARCHMERE, GLOVES, "Golf Glove", 18.0, "golf_glove",
             "A soft cabretta leather golf glove for the left hand, with perforated fingers and a hook-and-loop wrist tab.",
             (WHITE, BLACK, BLUE, RED), _glove("Cabretta Leather", "Left Hand"), _sizes(18.0), "size",
             (("material", "cabretta leather"),)),
        _row("GGLSYN", "Synthetic Golf Glove, Right Hand", _W, GLOVES, "Golf Glove", 11.0, "golf_glove",
             "A synthetic golf glove for the right hand, with stretch panels over the knuckles that keep their shape in the rain.",
             (WHITE, GREEN, YELLOW, BLACK), _glove("Synthetic", "Right Hand"), _sizes(11.0), "size",
             (("material", "synthetic"),)),
        _row("GGLHYB", "Hybrid Golf Glove, Left Hand", _L, GLOVES, "Golf Glove", 15.0, "golf_glove",
             "A hybrid golf glove for the left hand: a leather palm for grip and stretch panels on the back for fit.",
             (WHITE, RED, BLUE, GREEN), _glove("Hybrid", "Left Hand"), _sizes(15.0), "size",
             (("material", "hybrid"),)),
        _row("GGLCAR", "Cabretta Leather Golf Glove, Right Hand", _H, GLOVES, "Golf Glove", 19.0, "golf_glove",
             "A cabretta leather golf glove for the right hand, worn by left-handed players, with perforated fingers for air.",
             (WHITE, YELLOW, GREEN, BLACK), _glove("Cabretta Leather", "Right Hand"), _sizes(19.0), "size",
             (("material", "cabretta leather"),)),
    ),
)  # fmt: skip
