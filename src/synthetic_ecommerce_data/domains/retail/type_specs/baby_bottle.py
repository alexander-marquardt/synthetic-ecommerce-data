"""Baby Bottles (gen#965, slice 1): Kids > Baby > Feeding > Baby Bottles.

A breadth type: ``derivable`` True, so the scaled build draws more bottles from these four by the
values their titles show (the feature and the material). The SKU's color is the bottle's collar
(:func:`kit_baby_gear.baby_bottle`), and the material draws the body: tinted plastic, clear glass
or soft silicone. Each SKU is a color in a capacity in milliliters.
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.baby_gear_rows import (
    BLACK,
    BLUE,
    BOTTLES,
    CALDERBY,
    DEPARTMENT,
    FENWOLD,
    GREEN,
    GREY,
    LANTERNBY,
    LITTLE_FERNBY,
    MIREFIELD,
    PINK,
    RED,
    THISTLE,
    WHITE,
    YELLOW,
    decoy,
    row,
)
from synthetic_ecommerce_data.domains.retail.type_registry import Decoy, TypeSpec, a


def _bottle(feature: str, material: str) -> tuple[tuple, ...]:
    return (a("feature", "Feature", feature), a("material", "Material", material))


def _drawn(material: str) -> tuple[tuple[str, str], ...]:
    return (("material", material.lower()),)


def _ml(*pairs: tuple[int, float]) -> tuple[tuple[str, float], ...]:
    return tuple((str(ml), p) for ml, p in pairs)


ROWS = (
    row("BBTACP", "Anti-Colic Plastic Baby Bottle", LITTLE_FERNBY, BOTTLES, "Baby Bottle", "baby_bottle",
        "A plastic feeding bottle with a vented base that lets air out, not into your baby, to ease colic and wind.",
        _bottle("Anti-Colic", "Plastic"), _ml((150, 5.0), (260, 6.0), (330, 7.0)), "capacity_ml", _drawn("Plastic"), (BLUE, RED, WHITE)),
    row("BBTWNG", "Wide Neck Glass Baby Bottle", CALDERBY, BOTTLES, "Baby Bottle", "baby_bottle",
        "A heat-resistant glass bottle with a wide neck that is easy to fill and to clean, and a soft silicone teat.",
        _bottle("Wide Neck", "Glass"), _ml((150, 9.0), (260, 11.0)), "capacity_ml", _drawn("Glass"), (GREEN, GREY, BLACK)),
    row("BBTNFS", "Natural Feel Silicone Baby Bottle", FENWOLD, BOTTLES, "Baby Bottle", "baby_bottle",
        "A squeezable silicone bottle with a breast-shaped teat, made for switching between breast and bottle.",
        _bottle("Natural Feel", "Silicone"), _ml((150, 10.0), (260, 12.0)), "capacity_ml", _drawn("Silicone"), (PINK, YELLOW, GREEN)),
    row("BBTSFP", "Slow Flow Plastic Baby Bottle", LANTERNBY, BOTTLES, "Baby Bottle", "baby_bottle",
        "A light plastic bottle with a slow flow newborn teat, so first feeds come at a gentle pace.",
        _bottle("Slow Flow", "Plastic"), _ml((150, 4.5), (260, 5.5), (330, 6.5)), "capacity_ml", _drawn("Plastic"), (YELLOW, WHITE, BLACK, RED)),
    row("BBTEGP", "Easy Grip Plastic Baby Bottle", MIREFIELD, BOTTLES, "Baby Bottle", "baby_bottle",
        "A plastic bottle with a narrow waist that small hands can hold, and a medium flow teat.",
        _bottle("Easy Grip", "Plastic"), _ml((150, 5.5), (260, 6.5), (330, 7.5)), "capacity_ml", _drawn("Plastic"), (GREEN, BLUE, YELLOW)),
    row("BBTFFG", "Fast Flow Glass Baby Bottle", THISTLE, BOTTLES, "Baby Bottle", "baby_bottle",
        "A glass bottle with a fast flow teat for hungry older babies, safe in the steriliser and the dishwasher.",
        _bottle("Fast Flow", "Glass"), _ml((150, 9.5), (260, 11.5)), "capacity_ml", _drawn("Glass"), (WHITE, RED, BLACK)),
)  # fmt: skip

SPEC = TypeSpec(
    key="baby_bottle",
    department=DEPARTMENT,
    product_type="Baby Bottle",
    derivable=True,
    rows=ROWS,
    decoys=(
        Decoy(1, "pink baby bottle", "vocabulary", decoy(ROWS[0], "BBTPKT", "Anti-Colic Plastic Baby Bottle with Pink Teat Cover",
              "A blue anti-colic bottle with a pink cover that snaps over the teat.", (BLUE,))),
        Decoy(6, "red baby bottle", "generic", decoy(ROWS[3], "BBTRDF", "Red Fox Slow Flow Plastic Baby Bottle",
              "From the Red Fox range: a white slow flow bottle with a fox on its side.", (WHITE,))),
    ),
)  # fmt: skip
