"""Diapers (gen#965, slice 1): Kids > Baby > Diapering > Diapers.

A breadth type: ``derivable`` True, so the scaled build draws more diapers from these five by
the values their titles show (the protection and the style, tape or pull-up). A pack carries no
color; its one pack color is drawn (:func:`kit_baby_gear.diaper_pack`), and the style draws the
diaper in its window. Each SKU is a diaper size, Size 1 to Size 6.
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.baby_gear_rows import (
    CALDERBY,
    DEPARTMENT,
    DIAPERS,
    FENWOLD,
    LANTERNBY,
    LEMON,
    LILAC,
    LITTLE_FERNBY,
    MINT,
    MIREFIELD,
    NAVY,
    PEACH,
    QUILLON,
    SKY,
    THISTLE,
    decoy,
    row,
)
from synthetic_ecommerce_data.domains.retail.type_registry import Decoy, Option, TypeSpec, a


def _sizes(first: float) -> tuple[tuple[str, float], ...]:
    """Size 1 to Size 6, a larger size costing a little more."""
    return tuple((f"Size {n}", round(first + 0.5 * (n - 1), 2)) for n in range(1, 7))


def _diaper(style: str, protection: str, indicator: str) -> tuple[tuple, ...]:
    return (a("diaper_style", "Diaper style", style), a("protection", "Protection", protection),
            a("wetness_indicator", "Wetness indicator", indicator))  # fmt: skip


def _drawn(style: str) -> tuple[tuple[str, str], ...]:
    return (("diaper_style", style.lower()),)


ROWS = (
    row("DPRUDT", "Ultra Dry Tape Diapers", LITTLE_FERNBY, DIAPERS, "Diapers", "diaper_pack",
        "Soft tape diapers with a quick-absorbing core that keeps skin dry for up to twelve hours, and stretchy side tabs for a snug fit.",
        _diaper("Tape", "Ultra Dry", "Yes"), _sizes(8.0), "diaper_size", _drawn("Tape"), (SKY,), colorless=True),
    row("DPRSST", "Sensitive Skin Tape Diapers", FENWOLD, DIAPERS, "Diapers", "diaper_pack",
        "Fragrance-free tape diapers with a cotton-soft top sheet, made for delicate and newborn skin.",
        _diaper("Tape", "Sensitive Skin", "Yes"), _sizes(9.0), "diaper_size", _drawn("Tape"), (MINT,), colorless=True),
    row("DPRLGP", "Leak Guard Pull-Up Diapers", CALDERBY, DIAPERS, "Diapers", "diaper_pack",
        "Pull-up diapers with raised leg cuffs and an all-round stretchy waist, easy to change while your toddler stands.",
        _diaper("Pull-Up", "Leak Guard", "No"), _sizes(9.5), "diaper_size", _drawn("Pull-Up"), (LILAC,), colorless=True),
    row("DPRPBP", "Plant-Based Pull-Up Diapers", THISTLE, DIAPERS, "Diapers", "diaper_pack",
        "Pull-up diapers with a plant-based outer layer and a chlorine-free core, gentle on skin and on the planet.",
        _diaper("Pull-Up", "Plant-Based", "No"), _sizes(10.5), "diaper_size", _drawn("Pull-Up"), (LEMON,), colorless=True),
    row("DPRONT", "Overnight Tape Diapers", QUILLON, DIAPERS, "Diapers", "diaper_pack",
        "Thick tape diapers for the long stretch of the night, with a wetness line that turns blue when it is time to change.",
        _diaper("Tape", "Overnight", "Yes"), _sizes(10.0), "diaper_size", _drawn("Tape"), (NAVY,), colorless=True),
    row("DPREAP", "Extra Absorbent Pull-Up Diapers", MIREFIELD, DIAPERS, "Diapers", "diaper_pack",
        "Pull-up diapers with an extra layer in the core for active toddlers, and tear-away sides for quick changes.",
        _diaper("Pull-Up", "Extra Absorbent", "Yes"), _sizes(11.0), "diaper_size", _drawn("Pull-Up"), (PEACH,), colorless=True),
    row("DPRHAT", "Hypoallergenic Tape Diapers", LANTERNBY, DIAPERS, "Diapers", "diaper_pack",
        "Dermatologist-tested tape diapers free of lotions and dyes, with a breathable outer cover.",
        _diaper("Tape", "Hypoallergenic", "No"), _sizes(9.0), "diaper_size", _drawn("Tape"), (SKY,), colorless=True),
)  # fmt: skip

SPEC = TypeSpec(
    key="diapers",
    department=DEPARTMENT,
    product_type="Diapers",
    derivable=True,
    rows=ROWS,
    options=(Option("diaper_size", "diaper_size", "Diaper size"),),
    decoys=(
        Decoy(2, "changing bag", "category", decoy(ROWS[0], "DPRCBG", "Changing Bag Travel Pack: Ultra Dry Tape Diapers",
              "Ultra dry tape diapers in a slim pack that slips into a changing bag: the diapers only, no bag.")),
        Decoy(6, "swim diapers", "generic", decoy(ROWS[2], "DPRSWC", "Swim Club Leak Guard Pull-Up Diapers",
              "Everyday pull-up diapers from the Swim Club range: not swim diapers, they swell in the water.")),
    ),
)  # fmt: skip
