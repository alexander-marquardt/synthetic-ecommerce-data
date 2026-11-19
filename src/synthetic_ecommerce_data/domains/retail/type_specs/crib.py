"""Cribs (gen#965, slice 3): Kids > Baby > Nursery Furniture > Cribs.

A breadth type: ``derivable`` True, so the scaled build draws more cribs from these seven by the
values their titles show (the feature and the style: standard, convertible or mini). Every
feature suits every style, and a description's words after the feature and the style suit any
of them, because a derived style swaps those two words and keeps the rest. The SKU is a color,
which the painted frame takes; the style draws the crib (:func:`kit_baby_gear.crib`):
slatted sides on four short legs, arched end panels with a toddler guard, or a small folding
frame on locking castors.
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.baby_gear_rows import (
    BLACK,
    BLUE,
    CALDERBY,
    CRIBS,
    DEPARTMENT,
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


def _crib(feature: str, style: str) -> tuple[tuple, ...]:
    return (a("feature", "Feature", feature), a("crib_style", "Crib style", style))


def _drawn(style: str) -> tuple[tuple[str, str], ...]:
    return (("crib_style", style.lower()),)


def _row(code: str, feature: str, style: str, brand: str, price: float, colors: tuple, rest: str):
    return gear_row(code, f"{feature} {style} Crib", brand, CRIBS, "Crib", "crib",
                    f"{article(feature)} {feature.lower()} {style.lower()} crib {rest}",
                    _crib(feature, style), price, _drawn(style), colors)  # fmt: skip


ROWS = (
    _row("CRBTRS", "Teething Rail", "Standard", FENWOLD, 249.0, (WHITE, GREY, BLACK),
         "with an adjustable mattress base and rounded corners; the mattress is sold separately."),
    _row("CRBUDS", "Under-Drawer", "Standard", THISTLE, 289.0, (WHITE, GREY, GREEN),
         "in solid pine with a non-toxic painted finish, for a baby from birth."),
    _row("CRBWCS", "Wipe-Clean", "Standard", LANTERNBY, 219.0, (WHITE, RED, BLUE),
         "with slats spaced to keep small arms and legs safely inside."),
    _row("CRBSWC", "Solid Wood", "Convertible", CALDERBY, 349.0, (WHITE, BLUE, GREY),
         "that comes flat-packed with every tool needed to put it together."),
    _row("CRBAHC", "Adjustable Height", "Convertible", MIREFIELD, 399.0, (WHITE, YELLOW, BLACK),
         "in sustainably sourced wood with a water-based finish."),
    _row("CRBRCM", "Rounded Corner", "Mini", LITTLE_FERNBY, 159.0, (WHITE, GREY, RED, BLUE),
         "with smooth rails and a non-toxic finish; the mattress is sold separately."),
    _row("CRBEAM", "Easy Assembly", "Mini", FENWOLD, 189.0, (WHITE, GREEN, YELLOW),
         "with an adjustable mattress base, for a baby from birth."),
)  # fmt: skip

SPEC = TypeSpec(
    key="crib",
    department=DEPARTMENT,
    product_type="Crib",
    derivable=True,
    rows=ROWS,
    decoys=(
        Decoy(2, "baby monitor", "category", decoy(ROWS[0], "CRBBMM", "Teething Rail Standard Crib with Baby Monitor Mount",
              "A teething rail standard crib with a mount on its end post that holds a camera: no baby monitor is included.")),
        Decoy(6, "green crib", "generic", decoy(ROWS[3], "CRBGWL", "Green Willow Solid Wood Convertible Crib",
              "From the Green Willow range: a grey solid wood convertible crib that comes flat-packed.", (GREY,))),
    ),
)  # fmt: skip
