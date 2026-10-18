"""Baby bodysuits (gen#213): the popper-fastened vest in multipacks of three, five or seven,
short or long sleeved, with an envelope or a crew neck. :mod:`kit_baby` draws each."""

from __future__ import annotations

from babywear_rows import (
    BABY,
    BLACK,
    BLUE,
    CREAM,
    FENWOLD,
    GREEN,
    GREY,
    HUSHWELL,
    LITTLE_FERNBY,
    NAVY,
    PINK,
    RED,
    SAGE,
    THISTLE,
    WHITE,
    YELLOW,
    a,
    garment,
    priced,
)
from type_registry import ApparelPlan, TypeSpec

_P = ("Kids", "Baby", "Bodysuits")


def _body(code, title, brand, price, desc, colors, sleeve, neck, fabric, season,
          packs):  # fmt: skip
    return garment(
        code, title, brand, _P, "Baby Bodysuit", "baby_bodysuit", price, desc, colors,
        (a("sleeve", "Sleeve", sleeve), a("neck", "Neck", neck), a("fabric", "Fabric", fabric),
         a("season", "Season", season)),
        (("sleeve", sleeve.lower()), ("neck", neck.lower())), priced(BABY, price),
        packs=packs,
    )  # fmt: skip


SPEC = TypeSpec(
    key="baby_bodysuit",
    department="Clothing",
    product_type="Baby Bodysuit",
    rows=(
        _body("BBYSEN", "Short Sleeve Envelope Neck Bodysuits", LITTLE_FERNBY, 2.0,
              "Cotton bodysuits with an envelope neck that slips off over the shoulders, and a "
              "popper crotch.",
              (WHITE, BLUE, PINK, YELLOW), "Short", "Envelope", "Cotton", "All Seasons", (3, 5, 7)),
        _body("BBYLCR", "Long Sleeve Crew Neck Bodysuits", HUSHWELL, 3.0,
              "Soft long sleeve bodysuits in stretch cotton, with a crew neck and a popper crotch.",
              (GREY, GREEN, BLACK, RED), "Long", "Crew", "Stretch Cotton", "Winter", (3, 5)),
        _body("BBYSOC", "Organic Cotton Short Sleeve Bodysuits", FENWOLD, 2.5,
              "Organic cotton bodysuits with short sleeves and an envelope neck.",
              (WHITE, CREAM, SAGE), "Short", "Envelope", "Organic Cotton", "Summer", (3, 7)),
        _body("BBYLEN", "Long Sleeve Envelope Neck Bodysuits", THISTLE, 3.5,
              "Long sleeve bodysuits with an envelope neck and a popper crotch.",
              (NAVY, WHITE, RED), "Long", "Envelope", "Cotton", "Winter", (5, 7)),
    ),
    apparel=ApparelPlan(compounds=(("vest", "Vest Bodysuit"), ("romper", "Romper Bodysuit"),
            ("sleep", "Sleep Bodysuit"))),
)  # fmt: skip
