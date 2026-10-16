"""Pamper hampers (gen#425, a spec by gen#351): Gifts > Gift Sets > Pamper Hampers.

A non-food hamper: four styles from three brands, drawn by :func:`kit_gifts.gift_hamper` (the
contents, bath and body, a candle and a diffuser, or socks and a slipper, change the drawing).
The kind of contents and the number of items are structured entries. The SKUs are the six main
colors (gen#275). Not derivable: authored rows only. Every name here is invented.
"""

from __future__ import annotations

import kit_gifts  # noqa: F401 -- registers gift_hamper
from gifts_rows import CALDERBY, DEPARTMENT, HAMPER_PATH, HEARTH, SIX_COLORS, THISTLE
from type_registry import Row, TypeSpec, a, count


def _hamper(code, title, brand, price, kind, contents, items, description) -> Row:
    return Row(
        code, title, brand, DEPARTMENT, HAMPER_PATH, "Gift Hamper", price, "gift_hamper",
        description, SIX_COLORS,
        (a("contents_kind", "Contents", kind), count("items", "Items", items)),
        params=(("contents", contents),),
    )  # fmt: skip


SPEC = TypeSpec(
    key="gift_hamper",
    department=DEPARTMENT,
    product_type="Gift Hamper",
    rows=(
        _hamper("GHPBATL", "Luxury Bath and Body Pamper Hamper", THISTLE, 32.0, "Bath and Body",
                "bath_body", 7,
                "A pamper hamper of bath and body treats: a bubble bath, a body lotion, a soap, "
                "a sponge and three more, in a lined basket."),
        _hamper("GHPBATM", "Mini Bath and Body Pamper Hamper", HEARTH, 16.0, "Bath and Body",
                "bath_body", 4,
                "A small pamper hamper with a bath foam, a hand cream, a soap and a sponge."),
        _hamper("GHPCAND", "Candle and Diffuser Pamper Hamper", CALDERBY, 28.0,
                "Candle and Diffuser", "candle_diffuser", 3,
                "A pamper hamper with a scented candle, a reed diffuser and a box of matches."),
        _hamper("GHPSOCK", "Sock and Slipper Pamper Hamper", HEARTH, 24.0, "Sock and Slipper",
                "sock_slipper", 4,
                "A cosy pamper hamper with two pairs of bed socks, a pair of slippers and an eye mask."),
    ),
)  # fmt: skip
