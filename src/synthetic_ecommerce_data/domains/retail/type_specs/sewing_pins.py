"""Sewing Pins (gen#1118, cut 3): Office & School > Sewing & Knitting > Sewing Pins.

A breadth type: ``derivable`` True, so the scaled build draws more pins from these four by the
values their titles show (the head and the pin's use). The SKU is the color of the pin heads, a
card sold singly or as a 2 pack. Each style comes in three of the six main colors, and the four
styles between them carry all six (gen#275). The count of pins on a card is an attribute and the
description's, never the title's. The drawing shows the card's two rows of pins with their heads
drawn by kind (:func:`kit_sewing_notions.sewing_pins`).
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail import (
    kit_sewing_notions,  # noqa: F401 -- registers sewing_pins
)
from synthetic_ecommerce_data.domains.retail.office_rows import (
    BLACK,
    BLUE,
    GREEN,
    LANTERNBY,
    RED,
    WHITE,
    YELLOW,
    decoy,
    packs,
)
from synthetic_ecommerce_data.domains.retail.sewing_rows import (
    DEPARTMENT,
    OWNERS,
    PINS,
    PURLWICK,
    row,
)
from synthetic_ecommerce_data.domains.retail.type_registry import Decoy, TypeSpec, a


def _row(code: str, head: str, use: str, pins: int, brand: str, colors: tuple, description: str,
         price: float):  # fmt: skip
    attrs = (
        a("head", "Head", head),
        a("use", "Use", use),
        a("pin_count", "Pins on the card", str(pins)),
    )
    params = (("head", head.lower()),)
    return row(code, f"{head} {use} Sewing Pins", brand, PINS, "Sewing Pins", "sewing_pins", description,
               attrs, packs((1, price), (2, round(price * 1.8, 2))), params, colors=colors)  # fmt: skip


ROWS = (
    _row(
        "SPNBHD",
        "Ball Head",
        "Dressmaker",
        100,
        PURLWICK,
        (RED, YELLOW, WHITE),
        "A card of 100 fine 32 mm steel pins with small round heads that are easy to see and to pick up, for pinning patterns and hems.",
        3.5,
    ),
    _row(
        "SPNGHQ",
        "Glass Head",
        "Quilting",
        50,
        PURLWICK,
        (BLUE, GREEN, BLACK),
        "A card of 50 long pins with glass heads that a hot iron does not melt, for holding the layers of a quilt.",
        5.5,
    ),
    _row(
        "SPNFHQ",
        "Flat Head",
        "Quilting",
        80,
        LANTERNBY,
        (RED, GREEN, BLACK),
        "A card of 80 long pins with flat heads that lie flat under a ruler and an iron, for piecing and quilting.",
        4.75,
    ),
    _row(
        "SPNBHT",
        "Ball Head",
        "Tailoring",
        120,
        LANTERNBY,
        (BLUE, YELLOW, WHITE),
        "A card of 120 slim pins with small round heads that pass through fine silks and shirtings without a mark.",
        4.25,
    ),
)

SPEC = TypeSpec(
    key="sewing_pins",
    department=DEPARTMENT,
    product_type="Sewing Pins",
    derivable=True,
    owners=OWNERS,
    rows=ROWS,
    decoys=(
        Decoy(4, "white sewing pins", "vocabulary", decoy(ROWS[0], "SPNWCD", "Ball Head Dressmaker Sewing Pins on a White Card",
              "Red-headed dressmaker pins on a plain printed card.", RED)),
        Decoy(6, "yellow sewing pins", "generic", decoy(ROWS[1], "SPNYRS", "Yellow Rose Glass Head Quilting Sewing Pins",
              "From the Yellow Rose range: glass head quilting pins with blue heads.", BLUE)),
    ),
)  # fmt: skip
