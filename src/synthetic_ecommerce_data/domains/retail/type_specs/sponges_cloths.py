"""Sponges & Cloths (gen#962 slice 3): Cleaning > Cleaning Tools > Sponges & Cloths.

A breadth type: ``derivable`` True, so the scaled build draws more sponges and cloths from these
five by the values their titles show (the grade, the room and the kind). A sponge or a cloth is sold in the
six main colors (gen#275); each SKU is a color in a pack of 1, 3 or 6.
:func:`kit_cleaning_care.sponge_cloth` draws a sponge block or a folded cloth in its color.
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.bags_wrap_rows import lowered
from synthetic_ecommerce_data.domains.retail.cleaning_care_rows import SPONGES, sponge
from synthetic_ecommerce_data.domains.retail.paper_rows import (
    DEPARTMENT,
    FEATHERLEE,
    HOLLINSBY,
    MOSSDOWN,
    OWNERS,
    SIX,
    WHITE,
    decoy,
    packs,
    row,
)
from synthetic_ecommerce_data.domains.retail.type_registry import Decoy, TypeSpec


def _packs(base: float) -> tuple[tuple[str, float], ...]:
    """Packs of 1, 3 and 6, priced up from ``base``."""
    return packs(*((n, round(base * f, 2)) for n, f in ((1, 1.0), (3, 2.6), (6, 4.6))))


ROWS = (
    row("SCKTSS", "Heavy Duty Kitchen Scrub Sponge", HOLLINSBY, SPONGES, "Sponges & Cloths", "sponge_cloth",
        "This Heavy Duty Scrub Sponge is made for Kitchen cleaning. It rinses clean under the tap and dries between uses.",
        sponge("Heavy Duty", "Scrub Sponge", "Kitchen"), _packs(2.5), lowered(("kind", "Scrub Sponge")), SIX),
    row("SCBTNS", "Everyday Bathroom Non-Scratch Sponge", MOSSDOWN, SPONGES, "Sponges & Cloths", "sponge_cloth",
        "This Everyday Non-Scratch Sponge is made for Bathroom cleaning. Wring it out after use and it is ready for another job.",
        sponge("Everyday", "Non-Scratch Sponge", "Bathroom"), _packs(2.8), lowered(("kind", "Non-Scratch Sponge")), SIX),
    row("SCAPMC", "Everyday All Purpose Microfiber Cloth", FEATHERLEE, SPONGES, "Sponges & Cloths", "sponge_cloth",
        "This Everyday Microfiber Cloth is made for All Purpose cleaning. Rinse it clean after each job and use it again.",
        sponge("Everyday", "Microfiber Cloth", "All Purpose"), _packs(3.5), lowered(("kind", "Microfiber Cloth")), SIX),
    row("SCKTDC", "Everyday Kitchen Dish Cloth", MOSSDOWN, SPONGES, "Sponges & Cloths", "sponge_cloth",
        "This Everyday Dish Cloth is made for Kitchen cleaning. It wipes the counter and the dishes, then rinses clean.",
        sponge("Everyday", "Dish Cloth", "Kitchen"), _packs(2.2), lowered(("kind", "Dish Cloth")), SIX),
    row("SCAPCS", "Heavy Duty All Purpose Cellulose Sponge", FEATHERLEE, SPONGES, "Sponges & Cloths", "sponge_cloth",
        "This Heavy Duty Cellulose Sponge is made for All Purpose cleaning. It soaks up a spill and squeezes out under the tap.",
        sponge("Heavy Duty", "Cellulose Sponge", "All Purpose"), _packs(2.0), lowered(("kind", "Cellulose Sponge")), SIX),
)

SPEC = TypeSpec(
    key="sponges_cloths",
    department=DEPARTMENT,
    product_type="Sponges & Cloths",
    derivable=True,
    rows=ROWS,
    owners=OWNERS,
    decoys=(
        Decoy(4, "scrub sponge", "vocabulary", decoy(ROWS[2], "SCNOSC", "No Scrub Everyday All Purpose Microfiber Cloth",
              "An all purpose microfiber cloth that wipes clean with no rough side, for surfaces a scrub sponge would mark.")),
        Decoy(6, "yellow sponge", "generic", decoy(ROWS[1], "SCYLRG", "Yellow Ridge Everyday Bathroom Non-Scratch Sponge",
              "From the Yellow Ridge range: white non-scratch sponges for the bathroom.", (WHITE,))),
    ),
)  # fmt: skip
