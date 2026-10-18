"""Sleepsuits (gen#213): the baby grow, footed or footless, long or short sleeved, closed with
poppers or a zip, sold in packs of one, two or three. :mod:`kit_baby` draws each as its own
shape."""

from __future__ import annotations

from babywear_rows import (
    BABY,
    BLACK,
    BLUE,
    CREAM,
    DOVECOTE,
    FENWOLD,
    GREEN,
    GREY,
    HUSHWELL,
    LITTLE_FERNBY,
    NAVY,
    PINK,
    RED,
    WHITE,
    YELLOW,
    a,
    garment,
    priced,
)
from type_registry import ApparelPlan, TypeSpec

_P = ("Kids", "Baby", "Sleepsuits")


def _suit(code, title, brand, price, desc, colors, feet, sleeve, fastening, fabric, season, packs,
          sizes=BABY):  # fmt: skip
    return garment(
        code, title, brand, _P, "Sleepsuit", "sleepsuit", price, desc, colors,
        (a("feet", "Feet", feet), a("sleeve", "Sleeve", sleeve),
         a("fastening", "Fastening", fastening), a("fabric", "Fabric", fabric),
         a("season", "Season", season)),
        (("feet", feet.lower()), ("sleeve", sleeve.lower()), ("fastening", fastening.lower())),
        priced(sizes, price), packs=packs,
    )  # fmt: skip


SPEC = TypeSpec(
    key="sleepsuit",
    department="Clothing",
    product_type="Sleepsuit",
    rows=(
        _suit("SLPFPP", "Footed Popper Sleepsuit", LITTLE_FERNBY, 6.0,
              "A soft cotton sleepsuit with feet, long sleeves and poppers down the front and "
              "along one leg for quick changes.",
              (BLUE, PINK, WHITE, YELLOW), "Footed", "Long", "Poppers", "Cotton", "All Seasons",
              (1, 2, 3)),
        _suit("SLPZOC", "Organic Cotton Zip Sleepsuit", HUSHWELL, 9.0,
              "A footed sleepsuit in organic cotton with a two-way zip from neck to ankle.",
              (GREEN, WHITE, GREY, RED), "Footed", "Long", "Zip", "Organic Cotton", "All Seasons",
              (1, 2)),
        _suit("SLPFLS", "Footless Short Sleeve Summer Sleepsuit", FENWOLD, 7.0,
              "A lightweight short sleeve sleepsuit with open ankles and poppers, for warm nights.",
              (YELLOW, BLUE, CREAM), "Footless", "Short", "Poppers", "Cotton", "Summer", (1, 3)),
        _suit("SLPFZW", "Footless Zip Winter Sleepsuit", DOVECOTE, 10.0,
              "A brushed cotton sleepsuit with long sleeves, open ankles and a zip.",
              (BLACK, RED, NAVY), "Footless", "Long", "Zip", "Brushed Cotton", "Winter", (1,)),
    ),
    apparel=ApparelPlan(
        compounds=(("pyjama", "Pyjama Sleepsuit"), ("babygrow", "Babygrow Sleepsuit"),
            ("romper", "Romper Sleepsuit"))
    ),
)  # fmt: skip
