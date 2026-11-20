"""Toothbrushes (gen#957, slice 2): Beauty > Dental > Toothbrushes.

A breadth type: ``derivable`` True, so the scaled build draws more toothbrushes from these four
by the values their titles show (the bristle and the power). The handle is the SKU's color; the
power draws the body and the bristle the tufts (:func:`kit_grooming.toothbrush`). Each SKU is a
color times the pack's count of brushes, which ``pack_copies`` draws as that many brushes.
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.grooming_rows import OWNED, TOOTHBRUSHES
from synthetic_ecommerce_data.domains.retail.hair_rows import BLUE, DEPARTMENT, WHITE, decoy, row
from synthetic_ecommerce_data.domains.retail.type_registry import Decoy, TypeSpec, a


def _brush(bristle: str, power: str) -> tuple[tuple, ...]:
    return (a("bristle", "Bristle", bristle), a("power", "Power", power))


def _packs(price: float) -> tuple[tuple[str, float], ...]:
    return (("1", price), ("2", round(price * 1.8, 2)), ("4", round(price * 3.2, 2)))


def _params(bristle: str, power: str) -> tuple[tuple[str, str], ...]:
    return (("bristle", bristle.lower()), ("power", power.lower()))


def _row(code: str, title: str, brand: str, desc: str, bristle: str, power: str, price: float):
    return row(code, title, brand, TOOTHBRUSHES, "Toothbrush", "toothbrush", desc,
               _brush(bristle, power), _packs(price), _params(bristle, power), "units_per_pack")  # fmt: skip


ROWS = (
    _row("TBRMAN", "Medium Manual Toothbrush", "Thornlea Skin",
         "A slim everyday brush with a compact head that reaches the back teeth and a tongue cleaner on the reverse.",
         "Medium", "Manual", 2.5),
    _row("TBRELE", "Soft Electric Toothbrush", "Aldermist",
         "A brush with a small round head that oscillates, a two-minute timer and a charging stand.",
         "Soft", "Electric", 29.0),
    _row("TBRSON", "Extra Soft Sonic Toothbrush", "Pearlbrook",
         "A brush with a slim oval head, three cleaning modes, a pressure sensor for gentle gums and a charging base.",
         "Extra Soft", "Sonic", 45.0),
    _row("TBRBAT", "Firm Battery Toothbrush", "Sorrel & Salt",
         "A light brush that runs on one replaceable cell, with a vibrating head for a deeper daily clean.",
         "Firm", "Battery", 9.0),
)  # fmt: skip

SPEC = TypeSpec(
    key="toothbrush",
    department=DEPARTMENT,
    product_type="Toothbrush",
    derivable=True,
    rows=ROWS,
    owners=OWNED,
    decoys=(
        Decoy(4, "blue toothbrush", "vocabulary", decoy(ROWS[0], "TBRBLB", "Manual Toothbrush with Blue Bristles",
              "A slim manual toothbrush in white, its bristles tipped blue so you know when to change it.", WHITE)),
        Decoy(6, "white toothbrush", "generic", decoy(ROWS[1], "TBRWHC", "White Cliff Electric Toothbrush",
              "From the White Cliff range: an electric toothbrush in blue.", BLUE)),
    ),
)  # fmt: skip
