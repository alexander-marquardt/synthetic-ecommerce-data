"""What a lipstick looks like, read from its product (gen#738).

Every lipstick drew one black case and only its shade changed, so a page of separate products read
as a grouping failure. A product's line now chooses its case, the case's color, the bullet's cut,
the emblem and the collar, and its finish the bullet's surface. The shade stays the SKU's own, so
the SKUs of one product share a case and a group reads as one product.

A model of the beauty grammar is one lead word (#851), numbered from its place among the lead
words (:func:`_line_number`), so no two models share a look: the five choices multiply to more
looks than there are places. A row with no model, or a model outside the grammar, is numbered
from its name or title. The numbers are shuffled first (:data:`SCATTERED`), so the
neighboring models of one brand, the ones a page shows together, do not differ in the last choice
alone.
"""

from __future__ import annotations

import zlib

from synthetic_ecommerce_data.domains.retail.kit import INK
from synthetic_ecommerce_data.domains.retail.kit_home import (
    GOLD,
    LIPSTICK_BULLETS,
    LIPSTICK_CASES,
    LIPSTICK_EMBLEMS,
    LIPSTICK_FINISHES,
    METAL,
)
from synthetic_ecommerce_data.domains.retail.line_grammar_families.beauty import LEADS

#: The colors a case comes in. All far enough apart to read at a tile.
CASE_COLORS = (
    INK, "#f1e8d8", "#c9a24e", "#e3a3b0", "#1f3f7a", "#1f7359",
    "#7a1f38", "#b9c1c9", "#2c98a6", "#6a2f8a", "#c4622d", "#8a9a2c",
)  # fmt: skip
COLLARS = (GOLD, METAL, "#d08f73")
#: The places a line's look may take. A lead word takes every :data:`STRIDE` th, so the leads keep
#: apart from one another and a name outside the grammar hashes into all of them.
MODELS = 1920
STRIDE = MODELS // len(LEADS)
#: Chosen by search so that, in the catalog's seed, no two lipstick lines of one brand share both a
#: case and its color: a brand's products fill a page together. A test holds this.
SALT = 295164
#: A model's number -> its place among the looks: every place once, in no order of the grammar.
SCATTERED = sorted(range(MODELS), key=lambda n: zlib.crc32(f"{SALT}:{n}".encode()))


def _line_number(line: str) -> int:
    """``line``'s place: a lead word's own, and a name outside the grammar hashes into them."""
    if line in LEADS:
        return LEADS.index(line) * STRIDE
    return zlib.crc32(line.encode()) % MODELS


def _finish(rec: dict) -> str:
    """``rec``'s finish: its attribute, else the finish its title names, else satin."""
    stated = next((str(a["value"]) for a in rec["attributes"] if a["key"] == "finish"), None)
    words = {w.lower() for w in rec["title"].replace(",", " ").split()}
    named = (f for f in LIPSTICK_FINISHES if f in words)
    return stated.lower() if stated else next(named, "satin")


def params(rec: dict) -> dict[str, str]:
    """The ``lipstick`` drawing's params for ``rec``; another shape's record has none."""
    if rec["drawing"]["shape"] != "lipstick":
        return {}
    n = SCATTERED[_line_number(rec.get("product_line") or rec["title"])]
    look = {}
    for name, choices in (
        ("case", tuple(LIPSTICK_CASES)),
        ("case_color", CASE_COLORS),
        ("bullet", tuple(LIPSTICK_BULLETS)),
        ("emblem", LIPSTICK_EMBLEMS),
        ("collar", COLLARS),
    ):
        n, choice = divmod(n, len(choices))
        look[name] = choices[choice]
    return look | {"finish": _finish(rec)}
