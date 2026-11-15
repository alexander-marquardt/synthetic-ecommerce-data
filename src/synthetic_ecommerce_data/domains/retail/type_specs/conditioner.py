"""Conditioner (Beauty), registered by its spec (gen#537), widened by gen#957.

Two rows stay in the shared row module named by ``homes`` (``breadth_beauty``); four more are
this spec's own. A breadth type: ``derivable`` True, so the scaled build draws more
conditioners by the hair type and the ingredient their titles show.
"""

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.type_registry import Home, Row, TypeSpec, a, cw

_PATH = ("Beauty", "Hair Care", "Conditioner")


def _hair(hair: str, ingredient: str) -> tuple[tuple[str, str, str], ...]:
    return (a("hair_type", "Hair type", hair), a("ingredient", "Ingredient", ingredient))


def _row(code: str, title: str, brand: str, price: float, desc: str, color: tuple,
         hair: str, ingredient: str) -> Row:  # fmt: skip
    sizes = ((250.0, price), (400.0, round(price * 1.35, 1)), (750.0, round(price * 1.95, 1)))
    return Row(code, title, brand, "Beauty", _PATH, "Conditioner", price, "bottle", desc,
               (color,), _hair(hair, ingredient), sizes, "Conditioner", colorless=True,
               size_key="net_volume_ml")  # fmt: skip


#: Four more styles beside the two of ``breadth_beauty`` (gen#957): six hair types and six
#: ingredients, so the scaled build draws more conditioners from the wider pools.
ROWS = (
    _row("CNDROS", "Rosemary Conditioner for Fine Hair", "Pearlbrook", 8.0,
         "A weightless rinse-out that detangles fine hair and keeps its volume.",
         cw("Sage", "#9bb08f", "solid", "#2a2a2e"), "Fine", "Rosemary"),
    _row("CNDKER", "Keratin Conditioner for Damaged Hair", "Sorrel & Salt", 10.0,
         "A repairing cream that smooths split ends and protects against heat styling.",
         cw("Cream", "#f1e4d6", "solid", "#7a5a3a"), "Damaged", "Keratin"),
    _row("CNDALO", "Aloe Vera Conditioner for Normal Hair", "Aldermist", 5.0,
         "A light daily conditioner that leaves hair soft and easy to comb.",
         cw("White", "#ffffff", "solid", "#2f6b4a"), "Normal", "Aloe Vera"),
    _row("CNDTEA", "Tea Tree Conditioner for Oily Hair", "Thornlea Skin", 7.0,
         "A light conditioner for the lengths only, with a fresh tea tree scent.",
         cw("Sage", "#b9d6c2", "solid", "#2a2a2e"), "Oily", "Tea Tree"),
)  # fmt: skip

SPEC = TypeSpec(
    key="conditioner",
    department="Beauty",
    product_type="Conditioner",
    derivable=True,
    rows=ROWS,
    owners=(
        ("Pearlbrook", "third_party"),
        ("Sorrel & Salt", "third_party"),
        ("Aldermist", "third_party"),
        ("Thornlea Skin", "third_party"),
    ),
    homes=(Home("breadth_rows", True),),
)
