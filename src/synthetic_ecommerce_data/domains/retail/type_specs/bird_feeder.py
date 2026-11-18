"""Bird feeder (gen#961, slice 2): Garden > Bird Care > Bird Feeders.

A breadth type: ``derivable`` True, so the scaled build draws more feeders from these five by the
values their titles show (the material and the style). The style draws the feeder (a tube, a
window box, a suet cage, a hanging platform) and the material its surface marks
(:func:`kit_garden_care.bird_feeder`). Each SKU is a color in a single or a pack, and every
style offers the six main colors (gen#275). The type's text-match decoys (gen#294) are in
:mod:`garden_rows`, with the other Garden types'.
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail import (
    kit_garden_care,  # noqa: F401 -- registers bird_feeder
)
from synthetic_ecommerce_data.domains.retail.outdoor_helpers import (
    BLACK,
    BLUE,
    GREEN,
    RED,
    WHITE,
    YELLOW,
    H,
    L,
    M,
    V,
    W,
    a,
    packs,
    row,
)
from synthetic_ecommerce_data.domains.retail.type_registry import Home, TypeSpec

PATH = ("Garden", "Bird Care", "Bird Feeders")
_PT = "Bird Feeder"
SIX = (RED, BLUE, GREEN, YELLOW, BLACK, WHITE)


def _feeder(code: str, material: str, style: str, brand: str, desc: str, sizes: tuple) -> object:
    attrs = (a("style", "Style", style), a("material", "Material", material))
    params = (("style", style.lower()), ("material", material.lower()))
    return row(code, f"{material} {style} Bird Feeder", brand, PATH, _PT, sizes[0][1], "bird_feeder",
               desc, SIX, attrs, sizes, "pack_size", params)  # fmt: skip


ROWS = (
    _feeder(
        "BFRTME",
        "Metal",
        "Tube",
        V,
        "A metal tube feeder with two feeding ports and perches, for sunflower hearts and mixed seed.",
        packs((1, 14.0), (2, 25.0)),
    ),
    _feeder(
        "BFRWPL",
        "Plastic",
        "Window",
        W,
        "A clear-fronted plastic window feeder on suction cups, to watch the birds from indoors.",
        packs((1, 11.0), (2, 19.0)),
    ),
    _feeder(
        "BFRSME",
        "Metal",
        "Suet Cage",
        H,
        "A metal suet cage under a little roof, for a fat block or suet balls in winter.",
        packs((1, 6.0), (2, 10.0), (3, 14.0)),
    ),
    _feeder(
        "BFRPWD",
        "Wood",
        "Platform",
        L,
        "A wood platform feeder that hangs on four cords under a roof, for seed, fruit and mealworms.",
        packs((1, 24.0), (2, 44.0)),
    ),
    _feeder(
        "BFRTPL",
        "Plastic",
        "Tube",
        M,
        "A plastic tube feeder with a seed tray at the foot, for finches and tits.",
        packs((1, 9.0), (2, 16.0), (3, 22.0)),
    ),
)

SPEC = TypeSpec(
    key="bird_feeder",
    homes=(Home("garden_rows", False),),
    department="Garden",
    product_type=_PT,
    derivable=True,
    rows=ROWS,
)
