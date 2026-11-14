"""Fishing Rod (gen#959, slice 1): Sports & Outdoors > Fishing > Fishing Rods.

A breadth type: ``derivable`` True, so the scaled build draws more rods by the values the titles
show (the rod's power, its blank material and its kind). The blank is the SKU's color; the kind
places the guides (:func:`kit_fishing_golf.fishing_rod`). Each SKU is a color in a length.
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.fishing_golf_rows import OWNERS, PENNYWHISTLE, RODS
from synthetic_ecommerce_data.domains.retail.sports_helpers import (
    _H,
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


def _rod(power: str, material: str, kind: str, pieces: str) -> tuple[tuple, ...]:
    return (_a("rod_power", "Rod power", power), _a("material", "Material", material),
            _a("rod_type", "Rod type", kind), _a("pieces", "Pieces", pieces))  # fmt: skip


SPEC = TypeSpec(
    key="fishing_rod",
    department="Sports & Outdoors",
    product_type="Fishing Rod",
    derivable=True,
    owners=OWNERS,
    rows=(
        _row("FRDSPN", "Medium Carbon Spinning Fishing Rod", _W, RODS, "Fishing Rod", 39.0, "fishing_rod",
             "A medium power spinning rod with a carbon blank, a cork handle and a screw reel seat, for lures and float fishing.",
             (BLACK, BLUE, RED, GREEN), _rod("Medium", "Carbon", "Spinning", "2"),
             _axis((183, 39.0), (213, 42.0), (244, 46.0)), "length_cm", (("rod_type", "spinning"),)),
        _row("FRDCST", "Heavy Carbon Casting Fishing Rod", _H, RODS, "Fishing Rod", 55.0, "fishing_rod",
             "A heavy power casting rod with a carbon blank and a trigger grip under the reel seat, for big lures and strong fish.",
             (BLACK, RED, YELLOW, WHITE), _rod("Heavy", "Carbon", "Casting", "1"),
             _axis((198, 55.0), (213, 58.0), (229, 62.0)), "length_cm", (("rod_type", "casting"),)),
        _row("FRDFLY", "Light Fiberglass Fly Fishing Rod", PENNYWHISTLE, RODS, "Fishing Rod", 69.0, "fishing_rod",
             "A light power fly rod with a slow fiberglass blank, snake guides and a cork grip, for small rivers and streams.",
             (GREEN, BLUE, YELLOW, WHITE), _rod("Light", "Fiberglass", "Fly", "4"),
             _axis((244, 69.0), (259, 74.0), (274, 79.0)), "length_cm", (("rod_type", "fly"),)),
    ),
)  # fmt: skip
