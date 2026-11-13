"""Party plates (gen#966): Gifts > Party Supplies > Party Tableware.

A breadth type: ``derivable`` True, so the scaled build draws more plates from these four by the
values their titles show (the material and the plate's size). Drawn by the tableware ``plate``
(:func:`kit_tableware.plate`): the kind sets the well and the finish a rim band. Each SKU is a
color in a pack of 8, 16 or 24.
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.party_rows import (
    DEPARTMENT,
    FERNBY,
    LANTERNBY,
    PIPWICK,
    PLATES,
    RED,
    THISTLE,
    WHITE,
    decoy,
    packs,
    row,
)
from synthetic_ecommerce_data.domains.retail.type_registry import Decoy, TypeSpec, a


def _plate(material: str, kind: str, finish: str) -> tuple[tuple, ...]:
    return (a("material", "Material", material), a("kind", "Plate size", kind),
            a("finish", "Finish", finish))  # fmt: skip


ROWS = (
    row("PPLPAD", "Paper Dinner Plates", FERNBY, PLATES, "Party Plate", "plate",
        "Sturdy paper dinner plates for a birthday buffet, ready to recycle after the party.",
        _plate("Paper", "Dinner", "Plain"), packs((8, 2.5), (16, 4.5), (24, 6.0)),
        (("kind", "dinner"), ("finish", "plain"))),
    row("PPLPAS", "Paper Side Plates", LANTERNBY, PLATES, "Party Plate", "plate",
        "Paper side plates with a printed rim band, for cake and snacks at a party.",
        _plate("Paper", "Side", "Rim Band"), packs((8, 2.0), (16, 3.5), (24, 5.0)),
        (("kind", "side"), ("finish", "rim band"))),
    row("PPLBMD", "Bamboo Dinner Plates", THISTLE, PLATES, "Party Plate", "plate",
        "Compostable bamboo fibre dinner plates with a rim band, strong enough for a hot meal.",
        _plate("Bamboo", "Dinner", "Rim Band"), packs((8, 4.0), (16, 7.0), (24, 9.5)),
        (("kind", "dinner"), ("finish", "rim band"))),
    row("PPLCDS", "Card Side Plates", PIPWICK, PLATES, "Party Plate", "plate",
        "Coated card side plates for a children's party, wipe-clean and easy to stack.",
        _plate("Card", "Side", "Plain"), packs((8, 2.0), (16, 3.5), (24, 4.5)),
        (("kind", "side"), ("finish", "plain"))),
)

SPEC = TypeSpec(
    key="party_plate",
    department=DEPARTMENT,
    product_type="Party Plate",
    derivable=True,
    rows=ROWS,
    decoys=(
        Decoy(4, "green plates", "vocabulary", decoy(ROWS[2], "PPLGLF", "Green Leaf Bamboo Dinner Plates",
              "Bamboo dinner plates in white, printed with one small green leaf by the rim.", WHITE)),
        Decoy(6, "yellow plates", "generic", decoy(ROWS[0], "PPLYBK", "Yellow Brick Paper Dinner Plates",
              "From the Yellow Brick party range: paper dinner plates in red.", RED)),
    ),
)  # fmt: skip
