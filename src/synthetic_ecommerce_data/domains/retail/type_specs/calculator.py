"""Calculators (gen#969, slice 2): Office & school > Office electronics > Calculators.

A breadth type: ``derivable`` True, so the scaled build draws more calculators from these four by
the values their titles show (the digits of the display and the kind). The color is the case's;
the kind draws a pocket, basic, desktop or scientific case and key grid, and the power a solar
strip or none (:func:`kit_office.calculator`). Each SKU is a color sold singly or in
a class pack of 5 or 10.
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.office_rows import (
    BLACK,
    CALCULATORS,
    CALDERBY,
    DEPARTMENT,
    LANTERNBY,
    THISTLE,
    WHITE,
    decoy,
    packs,
    row,
)
from synthetic_ecommerce_data.domains.retail.type_registry import Decoy, TypeSpec, a


def _calc(kind: str, digits: str, power: str) -> tuple[tuple, ...]:
    return (a("calculator_type", "Calculator type", kind), a("display", "Display", digits),
            a("power", "Power", power))  # fmt: skip


ROWS = (
    row("CALP8S", "8 Digit Pocket Calculator", CALDERBY, CALCULATORS, "Calculator", "calculator",
        "A slim calculator with a large display and soft rubber keys that fits a pencil case or a jacket.",
        _calc("Pocket", "8 Digit", "Solar"), packs((1, 4.0), (5, 18.0), (10, 34.0)),
        (("calculator_type", "pocket"), ("power", "solar"))),
    row("CALD12", "12 Digit Desktop Calculator", LANTERNBY, CALCULATORS, "Calculator", "calculator",
        "A calculator with a tilted display, big keys and tax and currency keys for home and office accounts.",
        _calc("Desktop", "12 Digit", "Dual Power"), packs((1, 9.0), (5, 42.0), (10, 80.0)),
        (("calculator_type", "desktop"), ("power", "dual power"))),
    row("CALS10", "10 Digit Scientific Calculator", THISTLE, CALCULATORS, "Calculator", "calculator",
        "A calculator with 240 functions, fractions and statistics, for school maths and science lessons.",
        _calc("Scientific", "10 Digit", "Battery"), packs((1, 12.0), (5, 55.0), (10, 105.0)),
        (("calculator_type", "scientific"), ("power", "battery"))),
    row("CALB10", "10 Digit Basic Calculator", CALDERBY, CALCULATORS, "Calculator", "calculator",
        "An everyday calculator with a percent key, a square root key and a memory, for homework and household sums.",
        _calc("Basic", "10 Digit", "Solar"), packs((1, 6.0), (5, 27.0), (10, 50.0)),
        (("calculator_type", "basic"), ("power", "solar"))),
)

SPEC = TypeSpec(
    key="calculator",
    department=DEPARTMENT,
    product_type="Calculator",
    derivable=True,
    rows=ROWS,
    decoys=(
        Decoy(4, "red calculator", "vocabulary", decoy(ROWS[0], "CALRDK", "8 Digit Pocket Calculator with Red Keys",
              "A white calculator with a large display and red rubber keys.", WHITE)),
        Decoy(6, "blue calculator", "generic", decoy(ROWS[2], "CALBRG", "Blue Ridge 10 Digit Scientific Calculator",
              "From the Blue Ridge range: a black calculator with 240 functions for school maths.", BLACK)),
    ),
)  # fmt: skip
