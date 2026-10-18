"""Fitness Band (gen#423): a new activity tracker type under Watches, in Womens and Mens.

A SKU is a silicone band color times a case diameter in millimetres (``case_mm``). The six main
colors (gen#275) are spread over the styles of each audience. ``screen`` is drawn by
:mod:`kit_jewellery`. The two decoys carry the word "fitness" in their text and are not what the
query they target asks for, by their fields.
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from audience import MENS, WOMENS
from jewellery_rows import (
    BLACK,
    BLUE,
    CALDERBY,
    GREEN,
    HARBOUR,
    OWNED,
    RED,
    SKERRY,
    TIDEWELL,
    WHITE,
    WRENFIELD,
    YELLOW,
    a,
    watch_row,
)
from type_registry import Decoy, Option, TypeSpec

PTYPE = "Fitness Band"
MM = ((40, 0.0), (44, 3.0))


def _row(code, title, brand, who, price, desc, colors, screen, water=50, heart="Yes", **kw):
    return watch_row(
        code, title, brand, who, "Fitness Bands", PTYPE, price, "fitness_band", desc, colors, "Silicone", water,
        tuple((d, round(price + extra, 2)) for d, extra in MM), (("screen", screen),),
        extra=(a("tracker_type", "Tracker type", "Fitness band"), a("heart_rate_monitor", "Heart rate monitor", heart)), **kw,
    )


SPEC = TypeSpec(
    options=(
        Option("case_mm", "case_diameter", "Case diameter", "MMT"),
    ),
    key="fitness_band",
    department="Clothing",
    product_type=PTYPE,
    owners=OWNED,
    apparel_exempt="a watch: the color is the strap, not a printed or dyed garment color; it carries its own decoys (gen#423)",
    rows=(
        _row("FTBMHR", "Mens Heart Rate Fitness Band", CALDERBY, MENS, 39.0,
             "A fitness band with a heart rate sensor, a touch screen and a ribbed silicone band.",
             (BLACK, BLUE, RED, WHITE), "heart"),
        _row("FTBMST", "Mens Step Counting Fitness Band", TIDEWELL, MENS, 29.0,
             "A fitness band that counts steps and distance and shows them on a bright touch screen.",
             (GREEN, YELLOW, BLACK, BLUE), "steps", heart="No"),
        _row("FTBWHR", "Womens Heart Rate Fitness Band", WRENFIELD, WOMENS, 42.0,
             "A slim fitness band with a heart rate sensor, a sleep tracker and a soft silicone band.",
             (BLACK, WHITE, RED, YELLOW), "heart"),
        _row("FTBWCL", "Womens Clock Fitness Band", HARBOUR, WOMENS, 33.0,
             "A fitness band with a clock face, a step counter and an alarm that wakes you with a buzz.",
             (BLUE, GREEN, WHITE, BLACK), "clock", heart="No"),
    ),
    decoys=(
        Decoy(4, "heart rate fitness band", "category",
              _row("FTBDST", "Step Counter Band", SKERRY, MENS, 18.0,
                   "A fitness band that counts steps only: no heart rate sensor and no GPS.",
                   (BLACK,), "steps", heart="No")),
        Decoy(5, "red fitness band", "color",
              _row("FTBDWB", "Activity Wristband", SKERRY, WOMENS, 15.0,
                   "A plain fitness wristband for everyday steps in blue with a red clasp.",
                   (BLUE,), "clock", heart="No")),
    ),
)  # fmt: skip
