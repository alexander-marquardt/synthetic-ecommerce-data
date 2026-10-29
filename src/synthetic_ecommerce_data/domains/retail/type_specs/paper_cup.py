"""Paper Cups (gen#620): Home > Kitchen & Dining > Drinkware > Disposable Cups.

Three styles from three brands, drawn by :func:`kit_cups.paper_cup`: the product's color is the
printed band (or none, for the plain cup). Each title is a realistic six to ten words (material,
use, pack). Every name here is invented.
"""

# ruff: noqa: E501 -- authored descriptions read better whole (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail import kit_cups  # noqa: F401 -- registers paper_cup
from synthetic_ecommerce_data.domains.retail.decor_rows import (
    BLACK,
    BLUE,
    BROWN,
    EMBERLY,
    GREEN,
    LARCHWOOD,
    RED,
    THISTLE,
    WHITE,
    YELLOW,
    row,
)
from synthetic_ecommerce_data.domains.retail.type_registry import TypeSpec, a

DISPOSABLE = ("Home", "Kitchen & Dining", "Drinkware", "Disposable Cups")

ROWS = (
    row("PPRHOT", "Double Wall Paper Cups for Hot Drinks, Pack of 50", EMBERLY, DISPOSABLE, "Paper Cup", 8.0,
        "paper_cup",
        "Double wall paper cups that keep tea and coffee hot without a sleeve, with a printed band, sold in a pack of 50.",
        (BROWN, RED, BLACK),
        (a("material", "Material", "Paper"), a("sold_as", "Sold as", "Pack")), params=(("band", "printed"),)),
    row("PPRCLD", "Printed Paper Cups for Cold Drinks, Pack of 30", THISTLE, DISPOSABLE, "Paper Cup", 5.0,
        "paper_cup",
        "Wax lined paper cups with a bold printed band for cold drinks and ice cream, a pack of 30.",
        (BLUE, GREEN, YELLOW),
        (a("material", "Material", "Paper"), a("sold_as", "Sold as", "Pack")), params=(("band", "printed"),)),
    row("PPRPLN", "Compostable Paper Cups for Coffee to Go, Pack of 40", LARCHWOOD, DISPOSABLE, "Paper Cup", 9.0,
        "paper_cup",
        "Plain compostable paper cups with a curled lip for takeaway coffee, a pack of 40.",
        (WHITE, BROWN, GREEN),
        (a("material", "Material", "Paper"), a("sold_as", "Sold as", "Pack")), params=(("band", "plain"),)),
)

SPEC = TypeSpec(
    key="paper_cup",
    department="Home",
    product_type="Paper Cup",
    rows=ROWS,
)
