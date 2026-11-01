"""Batteries (gen#34): a breadth leaf of two plain packs of alkaline cells.

Breadth is not depth: **Electronics > Accessories > Batteries** holds two packs, and the plain word
``batteries`` gains its own category rather than only a mention in a toy or a fan. The drawing reads
the cell the row states, so an AAA is the thinner cell.
"""

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail import (
    kit_plain_goods,  # noqa: F401 -- registers battery
)
from synthetic_ecommerce_data.domains.retail.electronics_rows import ELECTRONICS_OWNERS
from synthetic_ecommerce_data.domains.retail.type_registry import Row, TypeSpec, a, cw

_PATH = ("Electronics", "Accessories", "Batteries")
_BRAND = "Boltwick"
_CELL = cw("Black", "#2d2d33", "solid", "#c9a24b")


def _attrs(cell: str, pack: int) -> tuple[tuple, ...]:
    return (a("battery_size", "Battery size", cell), a("chemistry", "Chemistry", "Alkaline"),
            a("pack_size", "Pack size", f"{pack} pack"))  # fmt: skip


SPEC = TypeSpec(
    key="battery",
    department="Electronics",
    product_type="Battery",
    owners=ELECTRONICS_OWNERS,
    rows=(
        Row("BATAA4", "AA Alkaline Batteries, 4 Pack", _BRAND, "Electronics", _PATH, "Battery", 4.0,
            "battery", "Four AA alkaline cells for remote controls, clocks and toys, with a "
            "long shelf life in the drawer.",
            (_CELL,), _attrs("AA", 4), colorless=True, params=(("cell", "AA"),)),
        Row("BATAA8", "AAA Alkaline Batteries, 8 Pack", _BRAND, "Electronics", _PATH, "Battery",
            6.0, "battery", "Eight AAA alkaline cells for small remotes, torches and "
            "wireless mice, with a long shelf life in the drawer.",
            (_CELL,), _attrs("AAA", 8), colorless=True, params=(("cell", "AAA"),)),
    ),
)  # fmt: skip
