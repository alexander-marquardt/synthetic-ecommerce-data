"""Merchandise of seven invented kids' films, named only in the product text (gen#887): data only.

A shopper types ``plaything story mug``: the film is a name that lives in the title and the
description, never in a structured field. Each product keeps the brand of the house that makes it
(Brackenmere Home, Little Fernby, ...), no ``product_line`` and the category of its type, so a
film name is never a brand, a series or a category (:func:`structured_names` finds one that is).
Every description says the film is a movie ("a mug from the Plaything Story movie"), and "movie"
is not part of the name. One product of each film names the film in its description only, not in
its title (:data:`DESCRIPTION_ONLY`), so a description-only match can be ranked.

The names follow the invented-brands rule: no real film title. Several share a word with the
catalogue on purpose (``duck``, ``cold``, ``Home``, ``Blue``): phrase matching has to keep them
together. A Blue Balloon product with a color sells Blue, so its title names a color it has.

The rows are ordinary rows of the types they join: each type's spec reads its own with
:func:`rows_of` (``type_specs/mug.py``, ...), and the stickers are a type of their own
(``type_specs/stickers.py``). The drawings are the kit's shapes for those types, one per SKU.
"""

# ruff: noqa: E501 -- data rows read better whole (prototype only).

from __future__ import annotations

import functools
from dataclasses import dataclass

from synthetic_ecommerce_data.domains.retail import breadth_rows
from synthetic_ecommerce_data.domains.retail.breadth_rows import Row
from synthetic_ecommerce_data.domains.retail.class_model import BRAND_OWNER
from synthetic_ecommerce_data.domains.retail.prints import ADULT_SIZES, KIDS_SIZES
from synthetic_ecommerce_data.domains.retail.variants import cw

#: The films, each with the two letters of its products' codes.
FILMS: dict[str, str] = {
    "Plaything Story": "PS",
    "Lovely and the Beast": "LB",
    "Duck Run": "DR",
    "Really Cold": "RC",
    "Little Tiny Queen": "LQ",
    "Home Without Anybody": "HW",
    "The Blue Balloon": "BB",
}
#: The word every description puts after the film's name.
MOVIE = "movie"

breadth_rows.OWNERS.update({b: BRAND_OWNER[b] for b in ("Crofter's Bakehouse",) if b not in breadth_rows.OWNERS})

WHITE, NAVY = cw("White", "#f4f1ea", "solid", "#9a9ca0"), cw("Navy", "#2c477e")
RED, BLUE = cw("Red", "#c8312e"), cw("Blue", "#2f6db5")
YELLOW, GREEN = cw("Yellow", "#f2c230"), cw("Green", "#3c8d4f")
PINK, PURPLE = cw("Pink", "#f2a1b8"), cw("Purple", "#7b4fa0")
GREY = cw("Grey", "#b9bec4")


@dataclass(frozen=True)
class Kind:
    """What every film product of one type shares: where it sells, its maker, its drawing, its
    price, its sizes and whether its SKUs carry a color."""

    product_type: str
    department: str
    path: tuple[str, ...]
    brand: str
    shape: str
    price: float
    sizes: tuple[str, ...] = ()
    audience: str = "kids"
    colorless: bool = False
    params: tuple[tuple[str, str], ...] = ()


_KIDS_TOPS = ("Kids", "Tops")
KINDS: dict[str, Kind] = {
    "MG": Kind("Mug", "Home", ("Home", "Kitchen & Dining", "Drinkware", "Mugs"), "Brackenmere Home", "mug", 9.0, audience="adult"),
    "TE": Kind("Tee", "Clothing", (*_KIDS_TOPS, "T-Shirts"), "Little Fernby", "tshirt", 8.0, KIDS_SIZES),
    "SW": Kind("Sweatshirt", "Clothing", (*_KIDS_TOPS, "Sweatshirts"), "Little Fernby", "sweatshirt", 14.0, KIDS_SIZES),
    "JM": Kind("Jumper", "Clothing", ("Womens", "Knitwear", "Jumpers"), "Harbour & Pine", "sweatshirt", 28.0, ADULT_SIZES, audience="adult"),
    "PJ": Kind("Pyjamas", "Lingerie & Nightwear", ("Kids", "Nightwear", "Pyjamas"), "Little Fernby", "pyjamas", 12.0, KIDS_SIZES),
    "LN": Kind("Lunch Box", "Home", ("Home", "Kitchen & Dining", "Lunch Boxes"), "Hearth & Table", "box", 8.0),
    "BD": Kind("Duvet Set", "Home", ("Home", "Bedding", "Kids' Bedding"), "Little Fernby", "duvet", 22.0),
    "ST": Kind("Stickers", "Toys", ("Toys", "Arts & Crafts", "Stickers"), "Little Fernby", "sticker_sheet", 4.0, colorless=True),
    "PC": Kind("Party Cup", "Home", ("Home", "Kitchen & Dining", "Drinkware", "Disposable Cups"), "Lanternby", "party_cup", 4.0, audience="adult", params=(("stack", "stacked"),)),
    "PB": Kind("Gift Bag", "Gifts", ("Gifts", "Gift Wrap", "Gift Bags"), "Lanternby", "gift_bag", 5.0, audience="adult"),
    "TY": Kind("Soft Toy", "Toys", ("Toys", "Soft Toys", "Cuddly Animals"), "Puddlecombe Toys", "cat", 15.0),
    "CK": Kind("Cake", "Food & Drink", ("Food & Drink", "Bakery", "Cakes"), "Crofter's Bakehouse", "cake", 16.0, audience="adult", colorless=True),
    "SS": Kind("Sweets", "Food & Drink", ("Food & Drink", "Chocolate & Sweets", "Sweets"), "Pantry Mill", "bag", 2.5, audience="adult", colorless=True),
}


def _p(film: str, kind: str, title: str, description: str, colors=(WHITE,), **params: str) -> Row:
    """One product of ``film``: ``kind`` is a key of :data:`KINDS`, and ``params`` add to the
    kind's drawing parameters (a soft toy's animal is its shape)."""
    k = KINDS[kind]
    shape = params.pop("shape", k.shape)
    return Row(
        f"KF{FILMS[film]}{kind}", title, k.brand, k.department, k.path, k.product_type, k.price,
        shape, description, tuple(colors), sizes=tuple((s, k.price) for s in k.sizes),
        audience=k.audience, colorless=k.colorless, params=(*k.params, *params.items()),
    )  # fmt: skip


_PS, _LB, _DR, _RC = "Plaything Story", "Lovely and the Beast", "Duck Run", "Really Cold"
_LQ, _HW, _BB = "Little Tiny Queen", "Home Without Anybody", "The Blue Balloon"

ROWS: tuple[Row, ...] = ()


def film_of(row: Row) -> str:
    """The film a row of :data:`ROWS` sells."""
    return next(f for f, c in FILMS.items() if row.code[2:4] == c)


#: The ids of the products whose title does not name their film.
DESCRIPTION_ONLY = frozenset(r.product_id for r in ROWS if film_of(r).lower() not in r.title.lower())


@functools.cache
def ids() -> frozenset[str]:
    """Every film product's id."""
    return frozenset(r.product_id for r in ROWS)


def rows_of(product_type: str) -> tuple[Row, ...]:
    """The film products of ``product_type``: the rows its spec declares."""
    return tuple(r for r in ROWS if r.product_type == product_type)


def structured_names(doc: dict) -> list[str]:
    """Each film a document names in a structured field: its brand, its series
    (``product_line``), its category path or its leaf. A film product names none."""
    fields = [doc.get("brand") or "", doc.get("product_line") or "", *doc.get("category_path", ()), doc.get("category_leaf") or ""]
    return [f for f in FILMS for v in fields if f.lower() in str(v).lower()]
