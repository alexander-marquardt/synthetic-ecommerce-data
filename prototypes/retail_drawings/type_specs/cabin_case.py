"""Cabin Case (gen#209): carry-on and under-seat cases sized to an airline allowance.

**Womens > Accessories > Travel > Cabin Cases**: three styles from three invented brands, drawn
by :func:`kit_luggage.cabin_case` (``kind``, ``wheels``, ``shell``). The allowance (carry-on or
under-seat) and the dimensions in centimetres are structured entries, so ``cabin bag 55 x 40 x 20``
reads the dimensions, and the capacity and weight are measured entries. A SKU is a color.
Authored rows only. The decoys are real cabin cases whose title or description holds a word that
fools a search (a red piping, the word weekend, a feature the case lacks).
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from luggage_common import (
    BLACK, BLUE, EXEMPT, FENMOOR, GREEN, GREY, NAVY, OWNED, RED, SKERRY, TARNWICK, WHITE, YELLOW,
    a, litres, luggage_row,
)  # fmt: skip
from type_registry import Decoy, TypeSpec

PT, LEAF = "Cabin Case", "Cabin Cases"
SPIN, NONE = "4 Wheel Spinner", "No Wheels"


def _row(code, title, brand, price, desc, colors, allowance, dims, shell, wheels, litre, kg, **kw):
    attrs = (a("airline_allowance", "Airline allowance", allowance), a("dimensions", "Dimensions", dims),
             a("shell", "Shell", shell.title()), a("wheels", "Wheels", SPIN if wheels == "yes" else NONE),
             litres("capacity", "Capacity", litre), ("weight", "Weight", f"{kg:g}", "KGM", kg * 1000.0))  # fmt: skip
    kind = "under-seat" if allowance == "Under-Seat" else "carry-on"
    return luggage_row(code, title, brand, price, desc, colors, PT, LEAF, "cabin_case", attrs, (),
                       (("kind", kind), ("wheels", wheels), ("shell", shell)), **kw)  # fmt: skip


_ROWS = (
    _row("CBCHRD", "Hard Shell Carry-On Cabin Case", TARNWICK, 59.0,
         "A hard shell cabin case with four spinner wheels and a front flap pocket for a laptop. "
         "Fits the overhead locker of most airlines.",
         (RED, BLUE, BLACK), "Carry-On", "55 x 40 x 20 cm", "hard", "yes", 38, 2.5),
    _row("CBCSFT", "Soft Cabin Case, Spinner Carry-On", FENMOOR, 42.0,
         "A soft cabin case in tough polyester with four spinner wheels, a front pocket and an "
         "expandable zip. Carry-on size.",
         (GREEN, NAVY, YELLOW), "Carry-On", "55 x 35 x 23 cm", "soft", "yes", 40, 2.3),
    _row("CBCUND", "Under-Seat Cabin Case", SKERRY, 36.0,
         "A squat soft cabin case that slides under the seat in front, with a grab handle and a "
         "shoulder strap. No wheels, so it stays light.",
         (WHITE, BLACK, GREY), "Under-Seat", "40 x 30 x 20 cm", "soft", "no", 25, 1.2),
)  # fmt: skip


def _decoy(cls, query, policy, code, title, desc, color, allowance, dims, shell, wheels, brand):
    return Decoy(cls, query, policy, _row(code, title, brand, 40.0, desc, (color,), allowance, dims, shell, wheels, 36, 2.4))


SPEC = TypeSpec(
    key="cabin_case",
    department="Clothing",
    product_type=PT,
    rows=_ROWS,
    owners=OWNED,
    apparel_exempt=EXEMPT,
    decoys=(
        _decoy(1, "red cabin case", "color", "CBCDRD", "Cabin Case, Red Piping",
               "A blue hard shell cabin case with red piping round the zip and a red handle grip.",
               BLUE, "Carry-On", "55 x 40 x 20 cm", "hard", "yes", TARNWICK),
        _decoy(6, "weekend bag", "category", "CBCDWK", "Weekender Cabin Case",
               "A soft cabin case sized for a weekend away; it rolls on four wheels and is a trolley "
               "case, not a duffel or a weekend bag.", NAVY, "Carry-On", "55 x 35 x 23 cm", "soft", "yes", FENMOOR),
        _decoy(4, "wheeled cabin case", "generic", "CBCDNW", "Wheel-Free Under-Seat Cabin Case",
               "A black under-seat case with a grab handle and a shoulder strap; it has no wheels.",
               BLACK, "Under-Seat", "40 x 30 x 20 cm", "soft", "no", SKERRY),
    ),
)  # fmt: skip
