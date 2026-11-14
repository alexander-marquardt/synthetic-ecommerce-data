"""Balloons (gen#966): Gifts > Party Supplies > Balloons.

A breadth type: ``derivable`` True, so the scaled build draws more balloons from these four by the
values their titles show (the balloon's finish and its style). The color is the balloon's own, or
the confetti's in a clear one; the style draws a latex oval, a round foil one or a clear one, and
the finish its sheen (:func:`kit_party.balloon`). Each SKU is a color in a pack.
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.party_rows import (
    BALLOONS,
    CALDERBY,
    DEPARTMENT,
    FERNBY,
    LANTERNBY,
    THISTLE,
    WHITE,
    YELLOW,
    decoy,
    packs,
    row,
)
from synthetic_ecommerce_data.domains.retail.type_registry import Decoy, TypeSpec, a


def _balloon(finish: str, style: str) -> tuple[tuple, ...]:
    return (a("finish", "Finish", finish), a("style", "Style", style))


ROWS = (
    row("BALMAT", "Matte Latex Balloons", LANTERNBY, BALLOONS, "Balloon", "balloon",
        "Matte latex balloons for a birthday or a garden party, tied with a curling ribbon.",
        _balloon("Matte", "Latex"), packs((10, 3.0), (25, 6.0), (50, 10.0)),
        (("style", "latex"), ("finish", "matte"))),
    row("BALPRL", "Pearl Latex Balloons", CALDERBY, BALLOONS, "Balloon", "balloon",
        "Pearl latex balloons with a soft sheen, to fill with air or helium for a celebration.",
        _balloon("Pearl", "Latex"), packs((10, 3.5), (25, 7.0), (50, 12.0)),
        (("style", "latex"), ("finish", "pearl"))),
    row("BALFOI", "Metallic Foil Balloons", THISTLE, BALLOONS, "Balloon", "balloon",
        "Round metallic foil balloons that hold helium for days, with a self-sealing valve.",
        _balloon("Metallic", "Foil"), packs((5, 6.0), (10, 10.0), (20, 18.0)),
        (("style", "foil"), ("finish", "metallic"))),
    row("BALCNF", "Clear Confetti Balloons", FERNBY, BALLOONS, "Balloon", "balloon",
        "Clear balloons filled with paper confetti in the color, for a birthday table or a hen party.",
        _balloon("Clear", "Confetti"), packs((5, 4.0), (10, 7.0), (20, 12.0)),
        (("style", "confetti"), ("finish", "clear"))),
)

SPEC = TypeSpec(
    key="balloon",
    department=DEPARTMENT,
    product_type="Balloon",
    derivable=True,
    rows=ROWS,
    decoys=(
        Decoy(4, "red balloons", "vocabulary", decoy(ROWS[2], "BALRRB", "Red Ribbon Foil Balloons",
              "Round foil balloons in white, each tied to a red curling ribbon.", WHITE)),
        Decoy(6, "blue balloons", "generic", decoy(ROWS[0], "BALBMN", "Blue Moon Latex Balloons",
              "From the Blue Moon party range: matte latex balloons in yellow.", YELLOW)),
    ),
)  # fmt: skip
