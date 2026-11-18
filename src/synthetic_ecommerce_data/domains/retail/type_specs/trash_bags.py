"""Trash Bags (gen#962 slice 2): Cleaning > Bags & Wraps > Trash Bags.

A breadth type: ``derivable`` True, so the scaled build draws more bags from these four by the
values their titles show (the strength, the closure and the bin a bag is sized for). A trash bag
is sold in the six main colors (gen#275); each SKU is a color in a pack of 1, 2 or 4 rolls.
:func:`kit_bags_wrap.trash_bag` draws a full bag in its color, closed at its neck.
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.bags_wrap_rows import TRASH, lowered, trash
from synthetic_ecommerce_data.domains.retail.paper_rows import (
    DEPARTMENT,
    FEATHERLEE,
    HOLLINSBY,
    MOSSDOWN,
    OWNERS,
    SIX,
    WHITE,
    decoy,
    packs,
    row,
)
from synthetic_ecommerce_data.domains.retail.type_registry import Decoy, TypeSpec


def _packs(base: float) -> tuple[tuple[str, float], ...]:
    """Packs of 1, 2 and 4 rolls, priced up from ``base``."""
    return packs(*((n, round(base * f, 2)) for n, f in ((1, 1.0), (2, 1.9), (4, 3.6))))


def _params(closure: str, use: str) -> tuple[tuple[str, str], ...]:
    return lowered(("closure", closure), ("use", use))


ROWS = (
    row("TBHDRW", "Heavy Duty Drawstring Kitchen Trash Bags", HOLLINSBY, TRASH, "Trash Bags", "trash_bag",
        "Heavy Duty trash bags with a Drawstring closure, sized for the Kitchen bin. Each roll holds thirty bags that tear off one at a time.",
        trash("Heavy Duty", "Drawstring", "Kitchen"), _packs(4.5), _params("Drawstring", "Kitchen"), SIX),
    row("TBEVTH", "Everyday Tie Handle Bathroom Trash Bags", MOSSDOWN, TRASH, "Trash Bags", "trash_bag",
        "Everyday trash bags with a Tie Handle closure, sized for the Bathroom bin. Two handles knot the bag shut when it is full.",
        trash("Everyday", "Tie Handle", "Bathroom"), _packs(2.0), _params("Tie Handle", "Bathroom"), SIX),
    row("TBTRFT", "Tear Resistant Flap Tie Outdoor Trash Bags", HOLLINSBY, TRASH, "Trash Bags", "trash_bag",
        "Tear Resistant trash bags with a Flap Tie closure, sized for the Outdoor bin. The bags stand open in the bin while it fills.",
        trash("Tear Resistant", "Flap Tie", "Outdoor"), _packs(6.0), _params("Flap Tie", "Outdoor"), SIX),
    row("TBEVDK", "Everyday Drawstring Bathroom Trash Bags", FEATHERLEE, TRASH, "Trash Bags", "trash_bag",
        "Everyday trash bags with a Drawstring closure, sized for the Bathroom bin. The cord pulls the neck closed and carries the bag out.",
        trash("Everyday", "Drawstring", "Bathroom"), _packs(2.2), _params("Drawstring", "Bathroom"), SIX),
)

SPEC = TypeSpec(
    key="trash_bags",
    department=DEPARTMENT,
    product_type="Trash Bags",
    derivable=False,
    rows=ROWS,
    owners=OWNERS,
    decoys=(
        Decoy(4, "scented trash bags", "vocabulary", decoy(ROWS[0], "TBUNSC", "Unscented Heavy Duty Drawstring Kitchen Trash Bags",
              "Heavy Duty kitchen trash bags with no scented film, for a home that prefers none.")),
        Decoy(6, "black trash bags", "generic", decoy(ROWS[1], "TBBKRK", "Black Rock Everyday Tie Handle Bathroom Trash Bags",
              "From the Black Rock range: white bathroom trash bags that knot shut.", (WHITE,))),
    ),
)  # fmt: skip
