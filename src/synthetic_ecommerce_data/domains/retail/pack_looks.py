"""What a beauty pack looks like, read from its product (gen#748).

A foundation, a face cream, a moisturiser, a bath salt and a perfume each drew one pack, and only
the shade changed, so a page of separate products read as a grouping failure, as lipstick did
(:mod:`lipstick_looks`, gen#738). A product's line now chooses its pack's form, its top, the top's
color, the emblem and the trim (:mod:`kit_packs`). The shade and the size stay the SKU's own, so
the SKUs of one product share a pack and a group reads as one product.

A model of the beauty grammar is numbered as a lipstick's is, and a kind raises its base to that
number (:func:`place`). Each base is a primitive root of :data:`PRIME`, so no two models of a kind
share a look, and neighboring models land far apart. :data:`BASES` are chosen so that no two lines
of a kind draw one picture with the colors taken out, and no two lines of a brand share a form and
a top: a new line that lands on a taken one needs a new entry, and a test names it.
"""

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail import kit_packs
from synthetic_ecommerce_data.domains.retail.kit_home import LIPSTICK_EMBLEMS
from synthetic_ecommerce_data.domains.retail.lipstick_looks import (
    CASE_COLORS,
    COLLARS,
    _line_number,
)

#: The kinds that draw a line's pack, and the shape each is drawn as. The other kinds of those
#: shapes print their model's name on the pack, so a tile tells them apart already.
KINDS = {
    "Foundation": "bottle",
    "Face Cream": "moisturiser_jar",
    "Moisturiser": "moisturiser_jar",
    "Bath Salts": "jar",
    "Perfume": "fragrance",
}
#: Below every family's number of looks and above the grammar's number of models.
PRIME = 6047
#: A kind's ``(base, start)``. Chosen by search: see the module's docstring.
BASES = {
    "Foundation": (3423, 6),
    "Face Cream": (685, 3787),
    "Moisturiser": (5403, 4596),
    "Bath Salts": (2572, 2828),
    "Perfume": (2372, 5984),
}


def choices(kind: str) -> dict[str, tuple[str, ...]]:
    """Each param of ``kind``'s look and what it can be."""
    family = kit_packs.FAMILIES[KINDS[kind]]
    return {
        "form": tuple(family.forms),
        "top": tuple(family.tops),
        "emblem": LIPSTICK_EMBLEMS,
        "top_color": CASE_COLORS,
        "trim": COLLARS,
    }


def place(kind: str, line: str) -> int:
    """``line``'s place among ``kind``'s looks."""
    base, start = BASES[kind]
    return pow(base, start + _line_number(line), PRIME)


def params(rec: dict) -> dict[str, str]:
    """The pack's params for ``rec``; a kind or a shape outside :data:`KINDS` has none."""
    kind = rec["product_type"]
    if KINDS.get(kind) != rec["drawing"]["shape"]:
        return {}
    n = place(kind, rec.get("product_line") or rec["title"])
    look = {}
    for name, options in choices(kind).items():
        n, choice = divmod(n, len(options))
        look[name] = options[choice]
    return look
