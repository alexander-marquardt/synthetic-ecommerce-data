"""Puddlesuits and rainsuits (gen#213): waterproof all-in-ones with taped seams and elastic
cuffs, fleece lined or unlined, hooded or not. :mod:`kit_baby` draws each as its own shape."""

from __future__ import annotations

from babywear_rows import (
    BLACK,
    BLUE,
    DOVECOTE,
    FENWOLD,
    GREEN,
    HUSHWELL,
    LITTLE_FERNBY,
    NAVY,
    PINK,
    RED,
    SAGE,
    TODDLER,
    WHITE,
    YELLOW,
    a,
    garment,
    priced,
    yes,
)
from type_registry import ApparelPlan, TypeSpec

_P = ("Kids", "Baby", "Puddlesuits")


def _puddle(code, title, brand, price, desc, colors, rating, fleece, hood):  # fmt: skip
    return garment(
        code, title, brand, _P, "Puddlesuit", "puddlesuit", price, desc, colors,
        (a("waterproof_rating", "Waterproof rating", f"{rating} mm"),
         a("lining", "Lining", "Fleece-Lined" if fleece else "Unlined"),
         a("hood", "Hood", yes(hood)), a("season", "Season", "Autumn")),
        (("hood", "yes" if hood else "no"), ("lining", "fleece" if fleece else "none")),
        priced(TODDLER, price),
    )  # fmt: skip


SPEC = TypeSpec(
    key="puddlesuit",
    department="Clothing",
    product_type="Puddlesuit",
    rows=(
        _puddle("PDLHFL", "Hooded Fleece Lined Puddlesuit", LITTLE_FERNBY, 24.0,
                "A waterproof puddlesuit with taped seams, a fleece lining and a grown-on hood.",
                (YELLOW, RED, BLUE, GREEN), 5000, True, True),
        _puddle("PDLUNL", "Unlined Rainsuit", FENWOLD, 18.0,
                "A light waterproof all-in-one with elastic cuffs and ankles, to wear over "
                "clothes.",
                (BLACK, WHITE, NAVY), 3000, False, False),
        _puddle("PDLHUL", "Hooded Waterproof Puddlesuit", HUSHWELL, 20.0,
                "A hooded puddlesuit with taped seams and a front zip, unlined for warm wet days.",
                (GREEN, PINK, YELLOW), 4000, False, True),
        _puddle("PDLFNH", "Fleece Lined Waterproof Suit", DOVECOTE, 26.0,
                "A fleece lined waterproof suit with a storm flap and no hood.",
                (BLUE, RED, SAGE), 5000, True, False),
    ),
    apparel=ApparelPlan(
        compounds=(("rain", "Rain Puddlesuit"), ("waterproof", "Waterproof Puddlesuit"),
            ("fleece", "Fleece Puddlesuit"))
    ),
)  # fmt: skip
