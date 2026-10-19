"""Shared pieces of the babywear and nursery type specs (gen#213): colors, age sizes, the row
builders and the hand-authored text-match decoys.

Each type is a spec under ``type_specs/`` (``sleepsuit``, ``baby_bodysuit``, ``snowsuit``,
``puddlesuit``, ``all_in_one``, ``baby_blanket``, ``changing_mat``, ``nappy_caddy``,
``nursery_storage``) and :mod:`kit_baby` draws it. Every brand is invented and already owned
in :data:`breadth_rows.OWNERS`; the drawing params are the attributes a record states
(``tests/test_retail_babywear_213.py`` pairs them).
"""

from __future__ import annotations

from dataclasses import replace

import kit_baby  # noqa: F401 -- registers the babywear and nursery shapes
from breadth_rows import Row
from type_registry import Decoy, a, count
from underwear_rows import URow, _pack_attrs, _packs
from variants import cw

RED = cw("Red", "#c8322b", "solid", "#f4d8d6")
BLUE = cw("Blue", "#6b8fc4", "solid", "#e0e8f4")
GREEN = cw("Green", "#6fa07a", "solid", "#e0eee3")
YELLOW = cw("Yellow", "#f2d26b", "solid", "#6b5a1c")
BLACK = cw("Black", "#2f2f35", "solid", "#8f989f")
WHITE = cw("White", "#f4f1ea", "solid", "#b9b4a6")
PINK = cw("Pink", "#f2b8c6", "solid", "#a8324a")
GREY = cw("Grey", "#aeb0b5", "solid", "#55575c")
NAVY = cw("Navy", "#2c3a5e", "solid", "#d8dce8")
CREAM = cw("Cream", "#efe8d8", "solid", "#b9b4a6")
SAGE = cw("Sage", "#a9bfa5", "solid", "#4d6149")

#: Age sizes: a baby grows by the month, then by the year.
NEWBORN = ("Newborn", "0-3 Mths", "3-6 Mths", "6-9 Mths", "9-12 Mths")
BABY = (*NEWBORN, "12-18 Mths", "18-24 Mths")
TODDLER = ("12-18 Mths", "18-24 Mths", "2-3 Yrs", "3-4 Yrs")
ADULT = ("XS", "S", "M", "L", "XL")
KIDS = ("2-3 Yrs", "4-5 Yrs", "6-7 Yrs", "8-9 Yrs")

LITTLE_FERNBY, FENWOLD, HUSHWELL = "Little Fernby", "Fenwold Nursery", "Hushwell"
DOVECOTE, QUILLON, THISTLE = "Dovecote Lane", "Quillon Sleep", "Thistle & Wren"
WRENFIELD, LARKMOOR, HARBOUR = "Wrenfield", "Larkmoor", "Harbour & Pine"


def priced(names: tuple[str, ...], price: float) -> tuple[tuple[str, float], ...]:
    """One ``(size, price)`` pair per size: the price rises a little for each size up."""
    return tuple((n, round(price + 0.5 * i, 2)) for i, n in enumerate(names))


def yes(flag: bool) -> str:
    return "Yes" if flag else "No"


def garment(code, title, brand, path, ptype, shape, price, desc, colors, attrs, params, sizes,
            *, packs: tuple[int, ...] = (), dept: str = "Clothing",
            audience: str = "baby"):  # fmt: skip
    """A babywear or all-in-one style: colors x age sizes (x pack sizes when ``packs``)."""
    common = dict(
        code=code, title=title, brand=brand, department=dept, path=path, product_type=ptype,
        price=price, shape=shape, description=desc, colors=colors, sizes=sizes, params=params,
        audience=audience,
    )  # fmt: skip
    if packs:
        return URow(**common, attrs=(*attrs, *_pack_attrs(_packs(*packs))), packs=_packs(*packs))
    return Row(**common, attrs=attrs)


def nursery(code, title, brand, leaf, ptype, shape, price, desc, colors, attrs, params) -> Row:
    """A nursery product: one SKU per color, under Home > Nursery."""
    return Row(code, title, brand, "Home", ("Home", "Nursery", leaf), ptype, price, shape, desc,
               colors, attrs, params=params)  # fmt: skip


def decoy(cls: int, query: str, row: Row, n: int, title: str, desc: str, *, color=None,
          brand: str = "", attrs: tuple = ()) -> Decoy:  # fmt: skip
    """A text-match decoy of gen#294 for a nursery type: a clone of one of its styles, coded
    ``DB<n>``. It keeps the style's leaf and shape, takes a new title and description and is sold
    in one color; its structured fields tell the truth, only the title or description misleads."""
    clone = replace(row, code=f"DB{n:02d}", title=title, description=desc, brand=brand or row.brand,
                    colors=(color or row.colors[0],), attrs=attrs or row.attrs)  # fmt: skip
    return Decoy(cls, query, "generic", clone)


__all__ = [
    "ADULT", "BABY", "BLACK", "BLUE", "CREAM", "DOVECOTE", "FENWOLD", "GREEN", "GREY", "HARBOUR",
    "HUSHWELL", "KIDS", "LARKMOOR", "LITTLE_FERNBY", "NAVY", "NEWBORN", "PINK", "QUILLON", "RED",
    "SAGE", "THISTLE", "TODDLER", "WHITE", "WRENFIELD", "YELLOW", "a", "count", "decoy",
    "garment", "nursery", "priced", "yes",
]  # fmt: skip
