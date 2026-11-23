"""Suitcase (gen#209): hard and soft shell cases in cabin, medium and large, by wheels and lock.

**Home > Luggage & Travel > Suitcases**: eight styles from five invented brands, drawn by
:func:`kit_luggage.suitcase` (``size``, ``shell``, ``wheels``). A SKU is a color times a size:
the capacity in litres is the axis, and each litre carries its size name (Cabin, Medium, Large)
its weight in kilograms and its dimensions in centimetres, so ``lightweight suitcase under 3 kg`` and ``red suitcase 65 litre``
are range and equality filters on structured entries. A breadth type: the scaled build derives styles from the rows (gen#1114).
The decoys (gen#294) are real suitcases whose title or description holds a word that fools a
search: a red zip, the word weekend, a lock the case lacks.
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.luggage_common import (
    BLACK,
    BLUE,
    BURGUNDY,
    FENMOOR,
    GREEN,
    GREY,
    MARROWGATE,
    NAVY,
    OWNED,
    PELLBROOK,
    PINK,
    RED,
    SILVER,
    SKERRY,
    TARNWICK,
    TEAL,
    WHITE,
    YELLOW,
    a,
    luggage_row,
    sized,
)  # fmt: skip
from synthetic_ecommerce_data.domains.retail.type_registry import Decoy, Option, TypeSpec

PT, LEAF = "Suitcase", "Suitcases"
SPINNER, TWO, TSA = "4 Wheel Spinner", "2 Wheel", "TSA"


def _row(code, title, brand, price, desc, colors, shell, wheels, lock, expandable, material, sizes, **kw):
    s, extra = sized(*sizes)
    attrs = (a("shell", "Shell", shell.title()), a("wheels", "Wheels", SPINNER if wheels == "4" else TWO),
             a("lock", "Lock", lock), a("expandable", "Expandable", expandable), a("material", "Material", material))  # fmt: skip
    return luggage_row(code, title, brand, price, desc, colors, PT, LEAF, "suitcase", attrs, s,
                       (("shell", shell), ("wheels", wheels)), extra=extra, **kw)  # fmt: skip


#: ``(litres, size, kg, price, dimensions)``: every cabin size is ``55 x 40 x 20 cm`` or within
#: it, the size most airlines allow in the cabin (the demo's ``cabin suitcase 55x40x20``).
_LIGHT = ((38, "Cabin", 2.4, 54.0, "55 x 40 x 20 cm"), (65, "Medium", 3.1, 69.0, "68 x 46 x 27 cm"),
          (95, "Large", 3.9, 84.0, "78 x 52 x 31 cm"))
_HEAVY = ((40, "Cabin", 3.0, 44.0, "55 x 40 x 20 cm"), (70, "Medium", 3.9, 58.0, "69 x 47 x 28 cm"),
          (100, "Large", 4.8, 72.0, "79 x 54 x 32 cm"))
_SOFT = ((35, "Cabin", 2.6, 34.0, "55 x 38 x 20 cm"), (60, "Medium", 3.4, 46.0, "67 x 44 x 27 cm"),
         (85, "Large", 4.2, 58.0, "77 x 50 x 30 cm"))
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
    _row("SUTALU", "Aluminum Hard Shell Spinner Suitcase", TARNWICK, 119.0,
         "A ribbed aluminum hard shell suitcase on four spinner wheels, with corner guards, a TSA "
         "lock and a telescopic handle. Built to last for years of trips.",
         (SILVER, BLACK, BLUE), "hard", "4", TSA, "No", "Aluminum", _HEAVY),
    _row("SUTRCY", "Recycled Polyester Soft Spinner Suitcase", FENMOOR, 39.0,
         "A soft suitcase woven from recycled polyester, on four spinner wheels with an expandable "
         "zip and a padded top handle.",
         (TEAL, GREY, BLACK), "soft", "4", "No", "Yes", "Recycled Polyester", _SOFT),
    _row("SUTLAP", "Hard Shell Suitcase with Laptop Pocket", SKERRY, 64.0,
         "A hard shell suitcase with a padded front pocket that opens for a laptop, a TSA lock and "
         "four spinner wheels.",
         (NAVY, PINK, BLACK), "hard", "4", TSA, "Yes", "Polycarbonate", _LIGHT),
    _row("SUTUPR", "Soft Upright Suitcase, Two Wheel", PELLBROOK, 32.0,
         "A soft upright suitcase on two inline wheels, with a telescopic handle, two front pockets "
         "and an expandable zip.",
         (BURGUNDY, NAVY, GREY), "soft", "2", "No", "Yes", "Polyester", _SOFT),
)  # fmt: skip


def _decoy(cls, query, policy, code, title, desc, color, shell, wheels, lock, brand=MARROWGATE):
    soft = shell == "soft"  # the material, sizes and weights are the shell's, as on SUTSFT
    row = _row(code, title, brand, 49.0, desc, (color,), shell, wheels, lock, "No",
               "Polyester" if soft else "Polypropylene", _SOFT if soft else _HEAVY)  # fmt: skip
    return Decoy(cls, query, policy, row)


SPEC = TypeSpec(
    key="suitcase",
    department="Home",
    product_type=PT,
    options=(
        Option("weight_kg", "weight", "Weight", "KGM"),
        Option("luggage_size", "luggage_size", "Luggage size"),
    ),
    rows=_ROWS,
    owners=OWNED,
    derivable=True,
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
