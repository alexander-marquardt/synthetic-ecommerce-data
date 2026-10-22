"""A retail product filed at more than one category path (gen#602).

A mug is both a piece of Home > Kitchen & Dining > Drinkware and a gift: it sat at one of the two
paths, so a shopper who browsed the other tree never met it. A product document now carries
``category_paths``: its primary ``category_path`` first, then each further path it is also filed
at. The mugs are the worked example (``docs/retail-prototype.md``, "A product at several category
paths"); nothing else in the catalogue is filed twice yet.

The pair is keyed by the path the build record sits at. The decoy mugs of :mod:`decor_rows` (an
ornament, a thank-you card) sit at the Home path too, and keep that one path: they are the wrong
answer to "mug".
"""

from __future__ import annotations

import decor_rows

MUG_HOME = ("Home", "Kitchen & Dining", "Drinkware", "Mugs")
MUG_GIFTS = ("Gifts", "Mugs & Drinkware")
#: The pair a mug is filed at, whichever of the two its build record sits at.
MUG_PATHS = (MUG_HOME, MUG_GIFTS)


def other_paths(rec: dict) -> list[tuple[str, ...]]:
    """The further paths ``rec`` is also filed at: empty for a product with one path."""
    here = tuple(rec["category_path"])
    if here not in MUG_PATHS or rec["product_id"] in decor_rows.decoy_ids():
        return []
    return [p for p in MUG_PATHS if p != here]
