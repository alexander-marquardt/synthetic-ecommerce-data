"""Sled (gen#959, slice 3): Sports & Outdoors > Winter Sports > Sleds.

A breadth type: ``derivable`` True, so the scaled build draws more sleds by the values the titles
show (the build, the riders and the type). The deck is the SKU's color; the type draws a long toboggan with a pull rope, a round saucer with handles or a deck on runners with a steering bar (:func:`kit_outdoor_winter.sled`). Each SKU is a color in a length.
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.outdoor_winter_rows import SLEDS
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
    _axis,
    _row,
)
from synthetic_ecommerce_data.domains.retail.type_registry import TypeSpec


def _attrs(sled_build: str, sled_riders: str, sled_type: str) -> tuple[tuple, ...]:
    return (
        _a("sled_build", "Sled build", sled_build),
        _a("sled_riders", "Sled riders", sled_riders),
        _a("sled_type", "Sled type", sled_type),
    )


SPEC = TypeSpec(
    key="sled",
    department="Sports & Outdoors",
    product_type="Sled",
    derivable=True,
    rows=(
        _row("SLDMTT", "Molded Plastic 2-Rider Toboggan Sled", _W, SLEDS, "Sled", 39.0, "sled",
             "Molded plastic toboggan with a curled nose, moulded handles and a pull rope, for two on a snowy hill.",
             (RED, BLUE, GREEN, YELLOW), _attrs("Molded Plastic", "2-Rider", "Toboggan"),
             _axis((120, 35.0), (150, 39.0)), "length_cm", (("sled_type", "toboggan"),)),
        _row("SLDFOS", "Foam Core 1-Rider Saucer Sled", _H, SLEDS, "Sled", 29.0, "sled",
             "Foam core saucer with a slick base and two handles, light enough for a child to carry uphill.",
             (YELLOW, BLACK, BLUE, WHITE), _attrs("Foam Core", "1-Rider", "Saucer"),
             _axis((66, 26.0), (80, 29.0)), "length_cm", (("sled_type", "saucer"),)),
        _row("SLDMOS", "Molded Plastic 1-Rider Steerable Sled", _L, SLEDS, "Sled", 79.0, "sled",
             "Steerable sled on two runners, turned by a steering bar and stopped by hand brakes.",
             (RED, BLACK, WHITE, GREEN), _attrs("Molded Plastic", "1-Rider", "Steerable"),
             _axis((100, 75.0), (120, 79.0)), "length_cm", (("sled_type", "steerable"),)),
        _row("SLDITS", "Inflatable 2-Rider Saucer Sled", _L, SLEDS, "Sled", 25.0, "sled",
             "Inflatable snow saucer of thick vinyl with two handles each side, packed flat when the snow is gone.",
             (GREEN, WHITE, BLUE, RED), _attrs("Inflatable", "2-Rider", "Saucer"),
             _axis((90, 22.0), (120, 25.0)), "length_cm", (("sled_type", "saucer"),)),
    ),
)  # fmt: skip
