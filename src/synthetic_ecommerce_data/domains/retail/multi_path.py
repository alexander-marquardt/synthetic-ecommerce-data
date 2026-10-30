"""A retail product filed at more than one category path (gen#602).

A mug is both a piece of Home > Kitchen & Dining > Drinkware and a gift: it sat at one of the two
paths, so a shopper who browsed the other tree never met it. A product document now carries
``category_paths``: its primary ``category_path`` first, then each further path it is also filed
at. The mugs are the worked example (``docs/retail-prototype.md``, "A product at several category
paths"). The court shoes are the other pair (gen#606): a retailer keeps Heels as its own group and
treats dress as an occasion across types, so a court shoe stays under Heels and is under Formal
Shoes too. Its second path ends in ``Court Shoes`` because a leaf is never a parent. Nothing else
in the catalog is filed twice yet.

A pair is keyed by the path the build record sits at. The decoy mugs of :mod:`decor_rows` (an
ornament, a thank-you card) sit at the Home path too, and keep that one path: they are the wrong
answer to "mug". A decoy court shoe is a court shoe, so it is filed at both.
"""

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail import decor_rows

MUG_HOME = ("Home", "Kitchen & Dining", "Drinkware", "Mugs")
MUG_GIFTS = ("Gifts", "Mugs & Drinkware")
COURT_HEELS = ("Womens", "Shoes", "Heels", "Court Shoes")
COURT_FORMAL = ("Womens", "Shoes", "Formal Shoes", "Court Shoes")
#: The pair a mug is filed at, whichever of the two its build record sits at.
MUG_PATHS = (MUG_HOME, MUG_GIFTS)
#: The pair a court shoe is filed at; the build record sits at the Heels path.
COURT_PATHS = (COURT_HEELS, COURT_FORMAL)


def other_paths(rec: dict) -> list[tuple[str, ...]]:
    """The further paths ``rec`` is also filed at: empty for a product with one path."""
    here = tuple(rec["category_path"])
    if here in MUG_PATHS and rec["product_id"] in decor_rows.decoy_ids():
        return []
    for pair in (MUG_PATHS, COURT_PATHS):
        if here in pair:
            return [p for p in pair if p != here]
    return []
