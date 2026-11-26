"""Kids Watch (gen#1113): a kids' watch under ``Kids``, sold to girls and boys alike (Unisex).

A SKU is a silicone strap color; the case diameter (``case_mm``, a measured option) is the style's
one size. ``face`` is drawn by :mod:`kit_jewellery`: a time teacher dial (the hours and the minutes
printed, a red hour hand and a blue minute hand) or a digital LCD, so ``watch_type`` and ``display``
follow it. The six main colors (gen#275) are spread over the styles. The rows are derivable, and a
derived style keeps its template's face, display and water resistance
(``scale_text.JEWELLERY_KEYS``).
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.audience import UNISEX
from synthetic_ecommerce_data.domains.retail.breadth_row import Row
from synthetic_ecommerce_data.domains.retail.jewellery_rows import (
    BLACK,
    BLUE,
    CALDERBY,
    CLOTHING,
    GREEN,
    HARBOUR,
    LARKMOOR,
    OWNED,
    RED,
    SKERRY,
    TIDEWELL,
    WHITE,
    WRENFIELD,
    YELLOW,
    a,
    metres,
)
from synthetic_ecommerce_data.domains.retail.type_registry import Decoy, Option, TypeSpec

PATH, PTYPE = ("Kids", "Watches"), "Kids Watch"


def _row(code, title, brand, price, desc, colors, face, water, mm):
    attrs = (
        a("watch_type", "Watch type", "Digital" if face == "digital" else "Analog"),
        a("display", "Display", "LCD" if face == "digital" else "Time Teacher Dial"),
        a("strap", "Strap", "Silicone"), metres("water_resistance", "Water resistance", water),
        a("audience", "Audience", UNISEX),
    )  # fmt: skip
    return Row(code, title, brand, CLOTHING, PATH, PTYPE, price, "kids_watch", desc, colors, attrs,
               ((str(mm), price),), size_key="case_mm", params=(("face", face),))  # fmt: skip


SPEC = TypeSpec(
    key="kids_watch",
    department="Clothing",
    product_type=PTYPE,
    derivable=True,
    options=(Option("case_mm", "case_diameter", "Case diameter", "MMT"),),
    owners=OWNED,
    apparel_exempt="a watch: the color is the strap, not a printed or dyed garment color; it carries its own decoys (gen#1113)",
    rows=(
        _row("KDWTTB", "Kids Time Teacher Watch", HARBOUR, 15.0,
             "A time teacher watch for kids learning to tell the time: every hour and every five minutes printed on the dial, a red hour hand and a blue minute hand.",
             (BLUE, RED, GREEN), "teacher", 30, 30),
        _row("KDWTLT", "Kids Learn the Time Watch", TIDEWELL, 14.0,
             "A kids' analog watch with a clear dial, the minutes printed around the hours and a soft silicone strap with a buckle.",
             (YELLOW, WHITE, BLACK), "teacher", 30, 30),
        _row("KDWTSW", "Kids Swim Time Teacher Watch", SKERRY, 19.0,
             "A time teacher watch water resistant to 100 m, for the pool and the beach, on a soft silicone strap.",
             (BLUE, GREEN, BLACK), "teacher", 100, 32),
        _row("KDWTBF", "Kids Bright Face Analog Watch", WRENFIELD, 16.0,
             "A kids' analog watch with large printed numbers, a red hour hand, a blue minute hand and a silicone strap.",
             (RED, YELLOW, WHITE), "teacher", 30, 28),
        _row("KDWDGT", "Kids Digital Watch", CALDERBY, 12.0,
             "A kids' digital watch with a large backlit LCD, a date display and a soft silicone strap.",
             (BLACK, BLUE, RED), "digital", 50, 34),
        _row("KDWDAL", "Kids Digital Watch with Alarm", LARKMOOR, 14.0,
             "A kids' digital watch with a daily alarm, a stopwatch, a backlight and a silicone strap.",
             (GREEN, YELLOW, WHITE), "digital", 50, 34),
        _row("KDWDLT", "Kids Light Up Digital Watch", HARBOUR, 13.0,
             "A kids' digital watch whose display lights up at the press of a button, on a soft silicone strap.",
             (YELLOW, GREEN, BLUE), "digital", 30, 32),
        _row("KDWDSW", "Kids Waterproof Digital Watch", TIDEWELL, 17.0,
             "A kids' digital watch water resistant to 100 m, with a stopwatch, an alarm and a backlit LCD.",
             (BLACK, RED, WHITE), "digital", 100, 36),
    ),
    decoys=(
        Decoy(5, "pink kids watch", "color",
              _row("KDWDPK", "Kids Watch with Pink Numbers", WRENFIELD, 15.0,
                   "A time teacher watch with pink numbers on a white dial, on a blue silicone strap.",
                   (BLUE,), "teacher", 30, 30)),
        Decoy(4, "kids watch with alarm", "category",
              _row("KDWDST", "Kids Simple Time Watch", CALDERBY, 11.0,
                   "A kids' digital watch that shows the time and the date, with no alarm, no stopwatch and no backlight.",
                   (WHITE,), "digital", 30, 32)),
    ),
)  # fmt: skip
