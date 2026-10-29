"""Party Cups (gen#620): Home > Kitchen & Dining > Drinkware > Disposable Cups.

Three styles from three brands, drawn by :func:`kit_cups.party_cup`. A real party cup carries a
realistic title (material, use, pack) of six to ten words, so a short decoy outscores it on a bare
``cup`` and the cups policy (gen#125 class 15) is what finds it. A pack is a style; the pack count
sits in the title, never in a drawing. Every name here is invented.
"""

# ruff: noqa: E501 -- authored descriptions read better whole (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail import kit_cups  # noqa: F401 -- registers party_cup
from synthetic_ecommerce_data.domains.retail.decor_rows import (
    BLUE,
    COBBLE,
    GREEN,
    HARBOUR,
    LANTERNBY,
    RED,
    WHITE,
    YELLOW,
    row,
)
from synthetic_ecommerce_data.domains.retail.type_registry import TypeSpec, a

DISPOSABLE = ("Home", "Kitchen & Dining", "Drinkware", "Disposable Cups")

ROWS = (
    row("PTYPLS", "Sturdy Reusable Plastic Party Cups, Pack of 20", COBBLE, DISPOSABLE, "Party Cup", 4.0,
        "party_cup",
        "Tapered plastic party cups with a rolled rim, strong enough to wash and use again, sold in a pack of 20.",
        (RED, BLUE, WHITE),
        (a("material", "Material", "Plastic"), a("sold_as", "Sold as", "Pack")), params=(("stack", "single"),)),
    row("PTYSTK", "Stackable Plastic Party Cups with Rolled Rim, Pack of 50", HARBOUR, DISPOSABLE,
        "Party Cup", 7.0, "party_cup",
        "Light plastic party cups that nest into a tidy stack, a pack of 50 for a birthday or a barbecue.",
        (YELLOW, GREEN, RED),
        (a("material", "Material", "Plastic"), a("sold_as", "Sold as", "Pack")), params=(("stack", "stacked"),)),
    row("PTYCLR", "Disposable Colorful Plastic Cups for Birthday Parties", LANTERNBY, DISPOSABLE,
        "Party Cup", 5.0, "party_cup",
        "Bright disposable plastic cups for squash and fizzy drinks at a children's birthday party.",
        (BLUE, YELLOW, GREEN, RED),
        (a("material", "Material", "Plastic"), a("sold_as", "Sold as", "Pack")), params=(("stack", "stacked"),)),
)

SPEC = TypeSpec(
    key="party_cup",
    department="Home",
    product_type="Party Cup",
    rows=ROWS,
)
