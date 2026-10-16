"""Notebooks and journals (gen#425, a spec by gen#351): Gifts > Stationery > Notebooks.

Eight styles from three brands, drawn by :func:`kit_gifts.notebook`: the ruling (lined, dotted,
plain) and the cover (hardback, softback, leather-effect) change the drawing. The page size (A5 or
A6), the ruling and the cover are structured entries. The SKUs are the six main colors (gen#275).
Not derivable: authored rows only. Every name here is invented.
"""

from __future__ import annotations

import kit_gifts  # noqa: F401 -- registers notebook
from gifts_rows import CALDERBY, DEPARTMENT, LANTERNBY, NOTEBOOK_PATH, SIX_COLORS, THISTLE
from type_registry import Row, TypeSpec, a

_COVER = {"hardback": "Hardback", "softback": "Softback", "leather": "Leather-Effect"}


def _nb(code, title, brand, price, size, ruling, cover, description) -> Row:
    return Row(
        code, title, brand, DEPARTMENT, NOTEBOOK_PATH, "Notebook", price, "notebook",
        description, SIX_COLORS,
        (a("page_size", "Page Size", size), a("ruling", "Ruling", ruling.title()),
         a("cover", "Cover", _COVER[cover])),
        params=(("ruling", ruling), ("cover", cover)),
    )  # fmt: skip


SPEC = TypeSpec(
    key="notebook",
    department=DEPARTMENT,
    product_type="Notebook",
    rows=(
        _nb("GNBA5DH", "A5 Dotted Hardback Notebook", LANTERNBY, 9.0, "A5", "dotted", "hardback",
            "An A5 notebook with dotted pages and a hard cover, with a ribbon marker."),
        _nb("GNBA5LH", "A5 Lined Hardback Notebook", CALDERBY, 8.0, "A5", "lined", "hardback",
            "An A5 notebook with lined pages and a hard cover, sewn so it lies flat."),
        _nb("GNBA5PS", "A5 Plain Softback Notebook", THISTLE, 6.0, "A5", "plain", "softback",
            "An A5 notebook with plain pages and a flexible cover, for sketches and notes."),
        _nb("GNBA5LL", "A5 Lined Leather-Effect Journal", LANTERNBY, 14.0, "A5", "lined", "leather",
            "An A5 journal in a leather-effect cover with a strap, lined pages and a pen loop."),
        _nb("GNBA5DL", "A5 Dotted Leather-Effect Journal", CALDERBY, 15.0, "A5", "dotted", "leather",
            "An A5 journal in a leather-effect cover, dotted pages for lists and bullet planning."),
        _nb("GNBA6DS", "A6 Dotted Softback Notebook", THISTLE, 4.0, "A6", "dotted", "softback",
            "A pocket A6 notebook with dotted pages and a flexible cover."),
        _nb("GNBA6LS", "A6 Lined Softback Notebook", LANTERNBY, 4.0, "A6", "lined", "softback",
            "A pocket A6 notebook with lined pages and a flexible cover."),
        _nb("GNBA6PH", "A6 Plain Hardback Notebook", CALDERBY, 6.0, "A6", "plain", "hardback",
            "A small A6 notebook with plain pages and a hard cover, for a bag or a coat pocket."),
    ),
)  # fmt: skip
