"""Car Seats (gen#965, slice 2): Kids > Baby > Travel > Car Seats.

A breadth type: ``derivable`` True, so the scaled build draws more car seats from these six by
the values their titles show (the feature and the seat type: infant carrier, convertible or
high-back booster). The SKU is a color, which the seat's fabric takes; the seat type draws the
seat (:func:`kit_baby_gear.car_seat`): a rear-facing carrier with a carry handle, a harnessed
seat on a base, or a booster with a high back and armrests.
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.baby_gear_rows import (
    BLACK,
    BLUE,
    CALDERBY,
    CAR_SEATS,
    DEPARTMENT,
    FABRIC_NAVY,
    FENWOLD,
    GREEN,
    GREY,
    LANTERNBY,
    LITTLE_FERNBY,
    MIREFIELD,
    RED,
    THISTLE,
    WHITE,
    YELLOW,
    article,
    decoy,
    gear_row,
)
from synthetic_ecommerce_data.domains.retail.type_registry import Decoy, TypeSpec, a


def _seat(feature: str, seat_type: str) -> tuple[tuple, ...]:
    return (a("feature", "Feature", feature), a("seat_type", "Seat type", seat_type))


def _drawn(seat_type: str) -> tuple[tuple[str, str], ...]:
    return (("seat_type", seat_type.lower()),)


def _row(code: str, feature: str, seat_type: str, brand: str, price: float, colors: tuple, rest: str):
    return gear_row(code, f"{feature} {seat_type} Car Seat", brand, CAR_SEATS, "Car Seat", "car_seat",
                    f"{article(feature)} {feature.lower()} {seat_type.lower()} car seat {rest}",
                    _seat(feature, seat_type), price, _drawn(seat_type), colors)  # fmt: skip


ROWS = (
    _row("CSTLIC", "Lightweight", "Infant Carrier", LITTLE_FERNBY, 129.0, (BLACK, GREY, BLUE),
         "with deep side wings, an adjustable headrest and a washable cover, approved to R129 (i-Size)."),
    _row("CSTRIC", "Reclining", "Infant Carrier", FENWOLD, 159.0, (FABRIC_NAVY, RED, GREY),
         "with deep side wings, an adjustable headrest, a sun canopy and a washable cover."),
    _row("CSTSIC", "Side Impact", "Convertible", CALDERBY, 249.0, (BLACK, GREY, GREEN, RED),
         "with deep side wings, an adjustable headrest and a washable cover, that fits a car by its seat belt or by ISOFIX."),
    _row("CSTECC", "Easy Clean", "Convertible", THISTLE, 219.0, (BLUE, BLACK, YELLOW),
         "with deep side wings, an adjustable headrest and a cover that zips off for the washing machine."),
    _row("CSTBHB", "Breathable", "High-Back Booster", LANTERNBY, 89.0, (BLACK, RED, BLUE, WHITE),
         "with deep side wings, an adjustable headrest, cup holders and a washable cover."),
    _row("CSTPHB", "Padded", "High-Back Booster", MIREFIELD, 69.0, (GREY, GREEN, YELLOW, WHITE),
         "with deep side wings, an adjustable headrest and a washable cover, for a child of 15 to 36 kg."),
)  # fmt: skip

SPEC = TypeSpec(
    key="car_seat",
    department=DEPARTMENT,
    product_type="Car Seat",
    derivable=True,
    rows=ROWS,
    decoys=(
        Decoy(2, "stroller", "category", decoy(ROWS[0], "CSTSTA", "Stroller Compatible Lightweight Infant Carrier Car Seat",
              "A lightweight infant carrier car seat that clicks onto a stroller frame with adapters: the stroller is sold separately.")),
        Decoy(1, "red car seat", "vocabulary", decoy(ROWS[3], "CSTRDP", "Easy Clean Convertible Car Seat with Red Shoulder Pads",
              "A black easy clean convertible car seat whose shoulder pads are red.", (BLACK,))),
    ),
)  # fmt: skip
