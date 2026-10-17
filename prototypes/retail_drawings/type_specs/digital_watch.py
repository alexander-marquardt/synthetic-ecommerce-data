"""Digital Watch (gen#423): a new watch type beside the legacy ``Watch``, in Womens and Mens.

A SKU is a silicone strap color times a case diameter in millimetres (``case_mm``). The six main
colors (gen#275) are spread over the styles of each audience. ``buttons`` is drawn by
:mod:`kit_jewellery`. The two decoys carry the word "digital" in their text and are not what the
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
from type_registry import Decoy, TypeSpec

PTYPE = "Digital Watch"
WOMENS_MM = ((34, 0.0), (38, 2.0))
MENS_MM = ((42, 0.0), (46, 2.0))


def _row(code, title, brand, who, price, desc, colors, buttons, water=100, strap="Silicone", **kw):
    mm = WOMENS_MM if who == WOMENS else MENS_MM
    return watch_row(
        code, title, brand, who, "Digital Watches", PTYPE, price, "digital_watch", desc, colors, strap, water,
        tuple((d, round(price + extra, 2)) for d, extra in mm), (("buttons", buttons),),
        extra=(a("watch_type", "Watch type", "Digital"), a("display", "Display", "LCD"), a("backlight", "Backlight", "Yes")), **kw,
    )


SPEC = TypeSpec(
    key="digital_watch",
    department="Clothing",
    product_type=PTYPE,
    owners=OWNED,
    apparel_exempt="a watch: the color is the strap, not a printed or dyed garment color; it carries its own decoys (gen#423)",
    rows=(
        _row("DGWMSP", "Mens Sports Digital Watch", CALDERBY, MENS, 25.0,
             "A digital sports watch with a stopwatch, an alarm, a backlit LCD and a soft silicone strap.",
             (BLACK, WHITE, BLUE, RED), "2"),
        _row("DGWMMF", "Mens Multifunction Digital Watch", TIDEWELL, MENS, 32.0,
             "A digital watch with four buttons, a world time display, a countdown timer and a silicone strap.",
             (GREEN, YELLOW, BLACK, BLUE), "4"),
        _row("DGWWSL", "Womens Slim Digital Watch", WRENFIELD, WOMENS, 22.0,
             "A slim digital watch with a small backlit LCD, a daily alarm and a silicone strap.",
             (BLACK, WHITE, RED, YELLOW), "2"),
        _row("DGWWMF", "Womens Multifunction Digital Watch", HARBOUR, WOMENS, 28.0,
             "A digital watch with four buttons, a stopwatch, a dual time display and a silicone strap.",
             (BLUE, GREEN, WHITE, BLACK), "4"),
    ),
    decoys=(
        Decoy(5, "black digital watch", "color",
              _row("DGWDSW", "Dive Sports Watch", SKERRY, MENS, 36.0,
                   "A digital dive watch with a black display, a depth gauge and a blue silicone strap.",
                   (BLUE,), "4")),
        Decoy(4, "digital watch with alarm", "category",
              _row("DGWDBS", "Basic Time Watch", HARBOUR, WOMENS, 14.0,
                   "A simple digital watch that shows the time and the date, with no alarm, no timer and no backlight.",
                   (WHITE,), "2")),
    ),
)  # fmt: skip
