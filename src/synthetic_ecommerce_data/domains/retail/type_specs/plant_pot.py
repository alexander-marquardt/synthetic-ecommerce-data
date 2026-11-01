"""Plant pots (gen#34): a breadth leaf of two plain pots, sold by diameter.

Breadth is not depth: **Home > Home Accessories > Plant Pots** holds two styles, and the plain
word ``pot`` gains a Home category. A pot's color is its material, so it is colorless, and its
SKUs are the measured diameter in centimetres.
"""

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail import (
    kit_plain_goods,  # noqa: F401 -- registers plant_pot
)
from synthetic_ecommerce_data.domains.retail.type_registry import Row, TypeSpec, a, cw

_PATH = ("Home", "Home Accessories", "Plant Pots")
_BRAND = "Hearth & Table"
TERRACOTTA = cw("Terracotta", "#b5623a")
STONEWARE = cw("Stoneware", "#6f7f7a")


def _widths(*pairs: tuple[int, float]) -> tuple[tuple[str, float], ...]:
    """SKU diameters in centimetres and the price at each: a wider pot costs more."""
    return tuple((str(cm), p) for cm, p in pairs)


SPEC = TypeSpec(
    key="plant_pot",
    department="Home",
    product_type="Plant Pot",
    rows=(
        Row("PPTTER", "Terracotta Plant Pot", _BRAND, "Home", _PATH, "Plant Pot", 4.0,
            "plant_pot", "A plain terracotta pot with a drainage hole and a matching saucer, "
            "for herbs and house plants.",
            (TERRACOTTA,), (a("material", "Material", "Terracotta"),
                            a("drainage", "Drainage", "Drainage hole")),
            _widths((15, 4.0), (20, 7.0), (25, 11.0)), colorless=True, size_key="diameter_cm",
            params=(("finish", "plain"),)),
        Row("PPTGLZ", "Glazed Stoneware Plant Pot", _BRAND, "Home", _PATH, "Plant Pot", 12.0,
            "plant_pot", "A glazed stoneware pot for a windowsill or a shelf, with a drainage "
            "hole and a matching saucer.",
            (STONEWARE,), (a("material", "Material", "Stoneware"),
                           a("drainage", "Drainage", "Drainage hole")),
            _widths((20, 12.0), (30, 22.0)), colorless=True, size_key="diameter_cm",
            params=(("finish", "glazed"),)),
    ),
)  # fmt: skip
