"""Strollers (gen#965, slice 2): Kids > Baby > Travel > Strollers.

A breadth type: ``derivable`` True, so the scaled build draws more strollers from these seven by
the values their titles show (the feature and the style: full-size, compact or jogging). The SKU
is a color, which the seat and hood take; the style draws the stroller
(:func:`kit_baby_gear.stroller`): a deep seat under a big hood on four wheels, a slim frame on twin
wheels, or a three-wheeler on air tyres.
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.baby_gear_rows import (
    BLACK,
    BLUE,
    CALDERBY,
    DEPARTMENT,
    FENWOLD,
    GREEN,
    GREY,
    HUSHWELL,
    LANTERNBY,
    LITTLE_FERNBY,
    MIREFIELD,
    NAVY,
    RED,
    STROLLERS,
    THISTLE,
    WHITE,
    YELLOW,
    decoy,
    gear_row,
)
from synthetic_ecommerce_data.domains.retail.type_registry import Decoy, TypeSpec, a


def _stroller(feature: str, style: str) -> tuple[tuple, ...]:
    return (a("feature", "Feature", feature), a("stroller_style", "Stroller style", style))


def _drawn(style: str) -> tuple[tuple[str, str], ...]:
    return (("stroller_style", style.lower()),)


def _row(code: str, feature: str, style: str, brand: str, price: float, colors: tuple, rest: str):
    return gear_row(code, f"{feature} {style} Stroller", brand, STROLLERS, "Stroller", "stroller",
                    f"A {feature.lower()} {style.lower()} stroller {rest}",
                    _stroller(feature, style), price, _drawn(style), colors)  # fmt: skip


ROWS = (
    _row("STRLWC", "Lightweight", "Compact", LITTLE_FERNBY, 149.0, (BLACK, GREY, BLUE, RED),
         "with a five-point harness, a sun hood and a basket underneath, that folds small enough for a car boot."),
    _row("STROHC", "One-Hand Fold", "Compact", HUSHWELL, 179.0, (NAVY, GREY, YELLOW),
         "with a five-point harness, a sun hood with a peek-a-boo window and a basket underneath."),
    _row("STRRSF", "Reversible Seat", "Full-Size", CALDERBY, 449.0, (BLACK, GREEN, GREY, WHITE),
         "with a five-point harness, a sun hood and a basket underneath, for a newborn and on to a toddler of 22 kg."),
    _row("STRLFF", "Lie-Flat", "Full-Size", FENWOLD, 379.0, (NAVY, RED, GREY),
         "with a five-point harness, a sun hood, a footmuff and a basket underneath."),
    _row("STRATJ", "All-Terrain", "Jogging", LANTERNBY, 329.0, (BLACK, GREEN, YELLOW, BLUE),
         "with a five-point harness, a sun hood, a hand brake and a basket underneath."),
    _row("STRSAJ", "Shock-Absorbing", "Jogging", MIREFIELD, 399.0, (GREY, RED, BLACK),
         "with a five-point harness, a sun hood, a wrist strap and a basket underneath, for park paths and gravel."),
    _row("STRPPF", "Puncture-Proof", "Full-Size", THISTLE, 349.0, (BLUE, WHITE, BLACK),
         "with a five-point harness, a sun hood, foam-filled tyres and a basket underneath."),
)  # fmt: skip

SPEC = TypeSpec(
    key="stroller",
    department=DEPARTMENT,
    product_type="Stroller",
    derivable=True,
    rows=ROWS,
    decoys=(
        Decoy(2, "car seat", "category", decoy(ROWS[0], "STRCSA", "Car Seat Adapter Ready Lightweight Compact Stroller",
              "A lightweight compact stroller that takes an infant car seat on its adapters: the car seat is sold separately.")),
        Decoy(6, "green stroller", "generic", decoy(ROWS[2], "STRGMD", "Green Meadow Reversible Seat Full-Size Stroller",
              "From the Green Meadow range: a black reversible seat full-size stroller with a sun hood and a basket underneath.", (BLACK,))),
    ),
)  # fmt: skip
