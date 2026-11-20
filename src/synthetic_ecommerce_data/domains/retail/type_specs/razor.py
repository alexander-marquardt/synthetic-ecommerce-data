"""Razors (gen#957, slice 2): Beauty > Shaving > Razors.

A breadth type: ``derivable`` True, so the scaled build draws more razors from these four by the
values their titles show (the handle and the blade count). The handle is the SKU's color; the
handle value draws its form and the blade count the head (:func:`kit_grooming.razor`). Each SKU
is a color times the cartridges in the box.
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.grooming_rows import OWNED, RAZORS
from synthetic_ecommerce_data.domains.retail.hair_rows import BLACK, DEPARTMENT, GREEN, decoy, row
from synthetic_ecommerce_data.domains.retail.type_registry import Decoy, Option, TypeSpec, a


def _razor(handle: str, blades: str) -> tuple[tuple, ...]:
    return (a("handle", "Handle", handle), a("blades", "Blades", blades))


def _box(price: float) -> tuple[tuple[str, float], ...]:
    return (("2", price), ("4", round(price + 5.0, 2)), ("8", round(price + 13.0, 2)))


def _params(handle: str, blades: str) -> tuple[tuple[str, str], ...]:
    return (("handle", handle.lower()), ("blades", blades.lower()))


def _row(code: str, title: str, brand: str, desc: str, handle: str, blades: str, price: float):
    return row(code, title, brand, RAZORS, "Razor", "razor", desc, _razor(handle, blades),
               _box(price), _params(handle, blades), "cartridges")  # fmt: skip


ROWS = (
    _row("RZRGRP", "Rubber Grip 3-Blade Razor", "Thornlea Skin",
         "A pivoting head with a lubricating strip, on a handle that holds firm in the shower.",
         "Rubber Grip", "3-Blade", 7.0),
    _row("RZRWTD", "Weighted 5-Blade Razor", "Aldermist",
         "A heavy handle that does the work, a pivoting head and a precision trimmer on the back.",
         "Weighted", "5-Blade", 14.0),
    _row("RZRSLM", "Slim 2-Blade Razor", "Pearlbrook",
         "A light razor with a narrow head for the upper lip, the jaw line and travel.",
         "Slim", "2-Blade", 5.0),
    _row("RZRERG", "Ergonomic 4-Blade Razor", "Sorrel & Salt",
         "A curved handle that follows the hand, a moisture strip with aloe and a flexible head for legs and underarms.",
         "Ergonomic", "4-Blade", 10.0),
)  # fmt: skip

SPEC = TypeSpec(
    key="razor",
    department=DEPARTMENT,
    product_type="Razor",
    derivable=True,
    rows=ROWS,
    owners=OWNED,
    options=(Option("cartridges", "cartridges", "Cartridges", "C62"),),
    decoys=(
        Decoy(4, "green razor", "vocabulary", decoy(ROWS[0], "RZRGNS", "3-Blade Razor with Green Aloe Strip",
              "A three-blade razor in black, its head lined with a green aloe strip.", BLACK)),
        Decoy(6, "black razor", "generic", decoy(ROWS[1], "RZRBKF", "Black Fen Weighted 5-Blade Razor",
              "From the Black Fen range: a weighted five-blade razor in green.", GREEN)),
    ),
)  # fmt: skip
