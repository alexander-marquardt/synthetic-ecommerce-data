"""Three pliers whose title holds the misspelling ``pliars``, for the R&I demo (#944).

The demo serves a misspelled search's literal hits. It offers "You may also consider searching
for <common spelling>" only when the search has 3 Best results or fewer and the common spelling is
at least 5 times more common. Retail sells no pliers, so the issue's fifth word is industrial. With
3 products, ``pliars`` shows the hits and the suggestion "pliers".

Each line is an ordinary product of its own type and leaf (``Tools > Hand tools > Pliers``),
built by the breadth builder with one SKU, at a size its type's own line does not sell. Only the
item text differs from the type's own line. The misspelling is product text only: the title, and
the name and description written from it. The category, type label and attributes are the
type's own, so no vocabulary or category name learns it. No title names a seed noun (``nut``,
``retaining ring``), so the #462 seed decoys gain no line.

The lines are built after the type's own line, from a stream of their own, with the type's own
minter. No other type's draws, ids or SKUs move, and neither does the type's own line. Breadth
types build once at any ``--lines``, so the count stays 3 at every scale. See
docs/retail-prototype/misspelled-words-944.md.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, replace
from typing import TYPE_CHECKING

from synthetic_ecommerce_data.domains.industrial import breadth

if TYPE_CHECKING:
    from synthetic_ecommerce_data.core.model import ProductLine


@dataclass(frozen=True)
class Misspelled:
    """One misspelled line: its item text and its one size."""

    item: str
    size: str


#: type key -> its misspelled lines, each at a size the type's own line does not sell
LINES: dict[str, tuple[Misspelled, ...]] = {
    "conduit_pliers": (Misspelled("Conduit Pliars", "12 in"),),
    "snap_ring_pliers": (
        Misspelled("Snap Ring Pliars", "9 in"),
        Misspelled("Convertible Snap Ring Pliars", "6 in"),
    ),
}


def build(gen, type_key: str) -> list[ProductLine]:
    """``type_key``'s misspelled lines, from their own stream; none for any other type."""
    wanted = LINES.get(type_key, ())
    if not wanted:
        return []
    own = gen.rng
    gen.rng = random.Random(f"{gen.config.seed}:{type_key}:misspelled-944")
    try:
        row = breadth.row_for(type_key)
        return [
            breadth.build_line(
                gen,
                replace(row, item=m.item, size_values=(m.size,), skus=1, featured_sizes=()),
                gen.minter.next_index(),
            )
            for m in wanted
        ]
    finally:
        gen.rng = own
