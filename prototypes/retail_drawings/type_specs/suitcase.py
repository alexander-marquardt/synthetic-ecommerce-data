"""Suitcase (gen#209): hard and soft shell cases in cabin, medium and large, by wheels and lock.

**Womens > Accessories > Travel > Suitcases**: four styles from four invented brands, drawn by
:func:`kit_luggage.suitcase` (``size``, ``shell``, ``wheels``). A SKU is a color times a size:
the capacity in litres is the axis, and each litre carries its size name (Cabin, Medium, Large)
and its weight in kilograms, so ``lightweight suitcase under 3 kg`` and ``red suitcase 65 litre``
are range and equality filters on structured entries. Authored rows only (not derivable).
The decoys (gen#294) are real suitcases whose title or description holds a word that fools a
search: a red zip, the word weekend, a lock the case lacks.
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from luggage_common import (
    BLACK,
    BLUE,
    EXEMPT,
    FENMOOR,
    GREEN,
    MARROWGATE,
    NAVY,
    OWNED,
    RED,
    SKERRY,
    TARNWICK,
    WHITE,
    YELLOW,
    a,
    luggage_row,
    sized,
)  # fmt: skip
from type_registry import Decoy, TypeSpec

PT, LEAF = "Suitcase", "Suitcases"
SPINNER, TWO, TSA = "4 Wheel Spinner", "2 Wheel", "TSA"


def _row(code, title, brand, price, desc, colors, shell, wheels, lock, expandable, material, sizes, **kw):
    s, extra = sized(*sizes)
    attrs = (a("shell", "Shell", shell.title()), a("wheels", "Wheels", SPINNER if wheels == "4" else TWO),
             a("lock", "Lock", lock), a("expandable", "Expandable", expandable), a("material", "Material", material))  # fmt: skip
    return luggage_row(code, title, brand, price, desc, colors, PT, LEAF, "suitcase", attrs, s,
                       (("shell", shell), ("wheels", wheels)), extra=extra, **kw)  # fmt: skip


_LIGHT = ((38, "Cabin", 2.4, 54.0), (65, "Medium", 3.1, 69.0), (95, "Large", 3.9, 84.0))
_HEAVY = ((40, "Cabin", 3.0, 44.0), (70, "Medium", 3.9, 58.0), (100, "Large", 4.8, 72.0))
_SOFT = ((35, "Cabin", 2.6, 34.0), (60, "Medium", 3.4, 46.0), (85, "Large", 4.2, 58.0))
_ROWS = (
    _row("SUTPCB", "Polycarbonate Hard Shell Spinner Suitcase", TARNWICK, 54.0,
         "A lightweight hard shell suitcase in polycarbonate with four spinner wheels, a TSA lock "
         "and a telescopic handle. Expands by 4 cm for the trip home.",
         (BLACK, NAVY, WHITE, YELLOW), "hard", "4", TSA, "Yes", "Polycarbonate", _LIGHT),
    _row("SUTABS", "ABS Hard Shell Suitcase, Two Wheel", FENMOOR, 44.0,
         "A tough ABS hard shell suitcase on two inline wheels with a TSA lock and a "
         "telescopic handle. Roomy and easy to roll over kerbs.",
         (RED, BLUE, BLACK), "hard", "2", TSA, "No", "ABS", _HEAVY),
    _row("SUTSFT", "Soft Shell Spinner Suitcase with Front Pocket", MARROWGATE, 34.0,
         "A flexible polyester suitcase on four spinner wheels with a zipped front pocket for a "
         "laptop and papers. Expands for extra room.",
         (GREEN, NAVY, BLACK), "soft", "4", "No", "Yes", "Polyester", _SOFT),
    _row("SUTSKY", "Lightweight Hard Shell Suitcase", SKERRY, 59.0,
         "A very light hard shell suitcase with a combination TSA lock, four spinner wheels and "
         "a lined interior with a divider.",
         (WHITE, RED, GREEN, BLUE), "hard", "4", TSA, "No", "Polycarbonate", _LIGHT),
)  # fmt: skip


def _decoy(cls, query, policy, code, title, desc, color, shell, wheels, lock, brand=MARROWGATE):
    soft = shell == "soft"  # the material, sizes and weights are the shell's, as on SUTSFT
    row = _row(code, title, brand, 49.0, desc, (color,), shell, wheels, lock, "No",
               "Polyester" if soft else "Polypropylene", _SOFT if soft else _HEAVY)  # fmt: skip
    return Decoy(cls, query, policy, row)


SPEC = TypeSpec(
    key="suitcase",
    department="Clothing",
    product_type=PT,
    rows=_ROWS,
    owners=OWNED,
    apparel_exempt=EXEMPT,
    decoys=(
        _decoy(1, "red suitcase", "color", "SUTDRZ", "Hard Shell Suitcase, Red Zips",
               "A black hard shell suitcase with red zip pulls and red trim on the handle.",
               BLACK, "hard", "4", TSA),
        _decoy(6, "weekend bag", "category", "SUTDWK", "Weekend Break Suitcase",
               "A soft sided suitcase sized for a weekend break away; it is a rolling suitcase, not "
               "a duffel or a weekend bag.", NAVY, "soft", "2", "No", FENMOOR),
        _decoy(4, "tsa lock suitcase", "generic", "SUTDLK", "Padlock Ready Hard Suitcase",
               "A hard shell suitcase with loops for your own padlock; it is not fitted with a TSA "
               "lock.", GREEN, "hard", "4", "No", TARNWICK),
    ),
)  # fmt: skip
