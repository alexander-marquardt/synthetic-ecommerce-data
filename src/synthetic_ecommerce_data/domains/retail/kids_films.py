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
together. The Blue Balloon's products come in red, yellow, white, green and blue, one color
each, and each title names its product's color ("The Blue Balloon Red Stoneware Mug"): ``blue``
in the film's name is no color, and only the emblem's balloon is always blue (gen#904). A title
that names one of its product's own colors is one the output standard's text check passes, so a
red mug whose title also holds "Blue" needs no exemption.

The rows are ordinary rows of the types they join: each type's spec reads its own with
:func:`rows_of` (``type_specs/mug.py``, ...), and the stickers are a type of their own
(``type_specs/stickers.py``). The drawings are the kit's shapes for those types, one per SKU,
each with its film's emblem printed on it (:mod:`film_emblems`, gen#904).
"""

# ruff: noqa: E501 -- data rows read better whole (prototype only).

from __future__ import annotations

import functools
from dataclasses import dataclass

from synthetic_ecommerce_data.domains.retail import breadth_rows, dark_blues
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

breadth_rows.OWNERS.update(
    {b: BRAND_OWNER[b] for b in ("Crofter's Bakehouse",) if b not in breadth_rows.OWNERS}
)

WHITE, NAVY = cw("White", "#f4f1ea", "solid", "#9a9ca0"), cw("Navy", dark_blues.NAVY)
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
    "MG": Kind(
        "Mug",
        "Home",
        ("Home", "Kitchen & Dining", "Drinkware", "Mugs"),
        "Brackenmere Home",
        "mug",
        9.0,
        audience="adult",
    ),
    "TE": Kind(
        "Tee", "Clothing", (*_KIDS_TOPS, "T-Shirts"), "Little Fernby", "tshirt", 8.0, KIDS_SIZES
    ),
    "SW": Kind(
        "Sweatshirt",
        "Clothing",
        (*_KIDS_TOPS, "Sweatshirts"),
        "Little Fernby",
        "sweatshirt",
        14.0,
        KIDS_SIZES,
    ),
    "JM": Kind(
        "Jumper",
        "Clothing",
        ("Womens", "Knitwear", "Jumpers"),
        "Harbour & Pine",
        "sweatshirt",
        28.0,
        ADULT_SIZES,
        audience="adult",
    ),
    "PJ": Kind(
        "Pyjamas",
        "Lingerie & Nightwear",
        ("Kids", "Nightwear", "Pyjamas"),
        "Little Fernby",
        "pyjamas",
        12.0,
        KIDS_SIZES,
    ),
    "LN": Kind(
        "Lunch Box",
        "Home",
        ("Home", "Kitchen & Dining", "Lunch Boxes"),
        "Hearth & Table",
        "box",
        8.0,
    ),
    "BD": Kind(
        "Duvet Set", "Home", ("Home", "Bedding", "Kids' Bedding"), "Little Fernby", "duvet", 22.0
    ),
    "ST": Kind(
        "Stickers",
        "Toys",
        ("Toys", "Arts & Crafts", "Stickers"),
        "Little Fernby",
        "sticker_sheet",
        4.0,
        colorless=True,
    ),
    "PC": Kind(
        "Party Cup",
        "Home",
        ("Home", "Kitchen & Dining", "Drinkware", "Disposable Cups"),
        "Lanternby",
        "party_cup",
        4.0,
        audience="adult",
        params=(("stack", "stacked"),),
    ),
    "PB": Kind(
        "Gift Bag",
        "Gifts",
        ("Gifts", "Gift Wrap", "Gift Bags"),
        "Lanternby",
        "gift_bag",
        5.0,
        audience="adult",
    ),
    "TY": Kind(
        "Soft Toy", "Toys", ("Toys", "Soft Toys", "Cuddly Animals"), "Puddlecombe Toys", "cat", 15.0
    ),
    "CK": Kind(
        "Cake",
        "Food & Drink",
        ("Food & Drink", "Bakery", "Cakes"),
        "Crofter's Bakehouse",
        "cake",
        16.0,
        audience="adult",
        colorless=True,
    ),
    "SS": Kind(
        "Sweets",
        "Food & Drink",
        ("Food & Drink", "Chocolate & Sweets", "Sweets"),
        "Pantry Mill",
        "bag",
        2.5,
        audience="adult",
        colorless=True,
    ),
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

ROWS: tuple[Row, ...] = (
    # -- Plaything Story: a toy box that comes to life --
    _p(
        _PS,
        "MG",
        "Plaything Story Stoneware Mug",
        "A 350 ml stoneware mug printed with the toy box gang from the Plaything Story movie. Dishwasher safe.",
        (WHITE, BLUE),
    ),
    _p(
        _PS,
        "TE",
        "Plaything Story Kids' Cotton Tee",
        "A soft cotton tee for kids with the toy cowboy and his friends from the Plaything Story movie on the front.",
        (BLUE, RED, WHITE),
    ),
    _p(
        _PS,
        "PJ",
        "Plaything Story Kids' Pyjamas",
        "Long-sleeve cotton pyjamas for kids, printed with the toys from the Plaything Story movie.",
        (BLUE, RED),
    ),
    _p(
        _PS,
        "LN",
        "Plaything Story Kids' Lunch Box",
        "A wipe-clean lunch box with a clip lid and the toy box friends from the Plaything Story movie.",
        (RED, BLUE, YELLOW),
    ),
    _p(
        _PS,
        "TY",
        "Plaything Story Dinosaur Soft Toy",
        "A cuddly plush of the nervous green dinosaur from the Plaything Story movie, 30 cm tall.",
        (GREEN,),
        shape="dinosaur",
    ),
    _p(
        _PS,
        "ST",
        "Plaything Story Sticker Sheets",
        "Four sheets of glossy stickers of the toys from the Plaything Story movie, for books, bottles and bags.",
        (BLUE,),
    ),
    _p(
        _PS,
        "CK",
        "Plaything Story Birthday Cake",
        "A vanilla sponge birthday cake with buttercream, topped with the toy cowboy from the Plaything Story movie. Serves 12.",
    ),
    _p(
        _PS,
        "PB",
        "Kids' Paper Party Bags",
        "Paper party bags printed with the toys from the Plaything Story movie, ready to fill for a birthday.",
        (RED, BLUE),
    ),
    # -- Lovely and the Beast: a castle, a rose and a dance --
    _p(
        _LB,
        "MG",
        "Enchanted Castle Stoneware Mug",
        "A stoneware mug with the enchanted castle and its ballroom from the Lovely and the Beast movie. Dishwasher safe.",
        (WHITE, PINK),
    ),
    _p(
        _LB,
        "TE",
        "Lovely and the Beast Kids' Cotton Tee",
        "A soft cotton tee for kids with the dancing pair from the Lovely and the Beast movie on the front.",
        (YELLOW, PINK, WHITE),
    ),
    _p(
        _LB,
        "PJ",
        "Lovely and the Beast Kids' Pyjamas",
        "Long-sleeve cotton pyjamas for kids with the castle and its roses from the Lovely and the Beast movie.",
        (PINK, NAVY),
    ),
    _p(
        _LB,
        "BD",
        "Lovely and the Beast Kids' Duvet Set",
        "A single duvet cover and pillowcase printed with the castle ballroom from the Lovely and the Beast movie. Duvet sold separately.",
        (PINK, YELLOW),
    ),
    _p(
        _LB,
        "TY",
        "Lovely and the Beast Plush Beast Soft Toy",
        "A big, soft plush of the gentle beast from the Lovely and the Beast movie, with a velvet cape.",
        (GREY,),
    ),
    _p(
        _LB,
        "PC",
        "Lovely and the Beast Paper Party Cups for Birthday Parties",
        "Paper party cups with the castle and roses from the Lovely and the Beast movie, for a birthday party.",
        (PINK, YELLOW),
    ),
    _p(
        _LB,
        "SS",
        "Lovely and the Beast Rose Jelly Sweets",
        "Rose-shaped fruit jelly sweets in a bag printed with the castle from the Lovely and the Beast movie.",
    ),
    # -- Duck Run: a farmyard escape --
    _p(
        _DR,
        "MG",
        "Duck Run Stoneware Mug",
        "A stoneware mug with the escaping ducks from the Duck Run movie. Dishwasher safe.",
        (WHITE, YELLOW),
    ),
    _p(
        _DR,
        "TE",
        "Duck Run Kids' Cotton Tee",
        "A soft cotton tee for kids with the duckling hero from the Duck Run movie on the front.",
        (YELLOW, GREEN, WHITE),
    ),
    _p(
        _DR,
        "SW",
        "Duck Run Kids' Sweatshirt",
        "A brushed-back cotton sweatshirt for kids with the farmyard gang from the Duck Run movie.",
        (GREEN, NAVY),
    ),
    _p(
        _DR,
        "PJ",
        "Kids' Farmyard Pyjamas",
        "Long-sleeve cotton pyjamas for kids, printed with the ducks of the Duck Run movie on the run from the farm.",
        (YELLOW, NAVY),
    ),
    _p(
        _DR,
        "LN",
        "Duck Run Kids' Lunch Box",
        "A wipe-clean lunch box with a clip lid and the ducks from the Duck Run movie.",
        (YELLOW, GREEN),
    ),
    _p(
        _DR,
        "TY",
        "Duck Run Duckling Soft Toy",
        "A small plush of the duckling hero from the Duck Run movie, with a soft felt beak.",
        (YELLOW,),
        shape="bird",
    ),
    _p(
        _DR,
        "PC",
        "Duck Run Paper Party Cups for Birthday Parties",
        "Paper party cups with the farmyard ducks from the Duck Run movie, for a birthday party.",
        (YELLOW, GREEN),
    ),
    _p(
        _DR,
        "SS",
        "Duck Run Fruit Gummy Ducks",
        "Chewy fruit gummies shaped like the ducks of the Duck Run movie.",
    ),
    # -- Really Cold: an ice kingdom --
    _p(
        _RC,
        "MG",
        "Really Cold Stoneware Mug",
        "A stoneware mug with the ice palace from the Really Cold movie, for hot chocolate on a snow day. Dishwasher safe.",
        (WHITE, BLUE),
    ),
    _p(
        _RC,
        "SW",
        "Kids' Snow Day Sweatshirt",
        "A brushed-back cotton sweatshirt for kids with the two sisters and their snowman from the Really Cold movie.",
        (BLUE, PURPLE),
    ),
    _p(
        _RC,
        "JM",
        "Really Cold Knitted Jumper",
        "A soft knitted jumper with the ice palace and snowflakes from the Really Cold movie, for a family winter photo.",
        (BLUE, WHITE, NAVY),
    ),
    _p(
        _RC,
        "PJ",
        "Really Cold Kids' Pyjamas",
        "Long-sleeve cotton pyjamas for kids with the snowman from the Really Cold movie.",
        (BLUE, PURPLE),
    ),
    _p(
        _RC,
        "BD",
        "Really Cold Kids' Duvet Set",
        "A single duvet cover and pillowcase printed with the ice palace from the Really Cold movie. Duvet sold separately.",
        (BLUE, WHITE),
    ),
    _p(
        _RC,
        "ST",
        "Really Cold Sticker Sheets",
        "Four sheets of glittery stickers of the snowman and the ice palace from the Really Cold movie.",
        (PURPLE,),
    ),
    _p(
        _RC,
        "CK",
        "Really Cold Snowflake Celebration Cake",
        "A chocolate sponge cake with white icing and sugar snowflakes from the Really Cold movie. Serves 14.",
    ),
    # -- Little Tiny Queen: the smallest queen of a very large kingdom --
    _p(
        _LQ,
        "TE",
        "Little Tiny Queen Kids' Cotton Tee",
        "A soft cotton tee for kids with the crowned heroine from the Little Tiny Queen movie on the front.",
        (PURPLE, PINK, WHITE),
    ),
    _p(
        _LQ,
        "PJ",
        "Little Tiny Queen Kids' Pyjamas",
        "Long-sleeve cotton pyjamas for kids, printed with the crowns and the castle from the Little Tiny Queen movie.",
        (PURPLE, PINK),
    ),
    _p(
        _LQ,
        "LN",
        "Kids' Royal Picnic Lunch Box",
        "A wipe-clean lunch box with a clip lid, printed with the royal picnic from the Little Tiny Queen movie.",
        (PURPLE, PINK),
    ),
    _p(
        _LQ,
        "BD",
        "Little Tiny Queen Kids' Duvet Set",
        "A single duvet cover and pillowcase with the throne room from the Little Tiny Queen movie. Duvet sold separately.",
        (PURPLE, WHITE),
    ),
    _p(
        _LQ,
        "ST",
        "Little Tiny Queen Sticker Sheets",
        "Four sheets of stickers with crowns, jewels and the heroine from the Little Tiny Queen movie.",
        (PURPLE,),
    ),
    _p(
        _LQ,
        "PB",
        "Little Tiny Queen Party Bags",
        "Paper party bags with the crowned heroine from the Little Tiny Queen movie, ready to fill for a birthday.",
        (PURPLE, PINK),
    ),
    _p(
        _LQ,
        "SS",
        "Little Tiny Queen Jewel Sweets",
        "Fruit jelly sweets shaped like the crown jewels of the Little Tiny Queen movie.",
    ),
    # -- Home Without Anybody: a boy home alone for the holidays --
    _p(
        _HW,
        "MG",
        "Home Without Anybody Stoneware Mug",
        "A stoneware mug with the snowy family house from the Home Without Anybody movie. Dishwasher safe.",
        (WHITE, RED),
    ),
    _p(
        _HW,
        "JM",
        "Home Without Anybody Knitted Jumper",
        "A soft knitted holiday jumper with the family house from the Home Without Anybody movie.",
        (RED, GREEN, NAVY),
    ),
    _p(
        _HW,
        "SW",
        "Home Without Anybody Kids' Sweatshirt",
        "A brushed-back cotton sweatshirt for kids with the boy and his booby traps from the Home Without Anybody movie.",
        (RED, NAVY),
    ),
    _p(
        _HW,
        "PJ",
        "Home Without Anybody Kids' Pyjamas",
        "Long-sleeve cotton pyjamas for kids with the snowy house from the Home Without Anybody movie.",
        (RED, GREEN),
    ),
    _p(
        _HW,
        "LN",
        "Home Without Anybody Kids' Lunch Box",
        "A wipe-clean lunch box with a clip lid and the boy from the Home Without Anybody movie.",
        (RED, NAVY),
    ),
    _p(
        _HW,
        "ST",
        "Home Without Anybody Sticker Sheets",
        "Four sheets of stickers of the boy, the house and the two burglars from the Home Without Anybody movie.",
        (RED,),
    ),
    _p(
        _HW,
        "CK",
        "Holiday Family Celebration Cake",
        "A rich fruit cake with marzipan and white icing, decorated with the snowy house from the Home Without Anybody movie. Serves 16.",
    ),
    # -- The Blue Balloon: a balloon that follows a girl across a city --
    _p(
        _BB,
        "MG",
        "The Blue Balloon Red Stoneware Mug",
        "A red stoneware mug printed with the blue balloon in a circle from The Blue Balloon movie. Dishwasher safe.",
        (RED,),
    ),
    _p(
        _BB,
        "TE",
        "The Blue Balloon Kids' Yellow Cotton Tee",
        "A soft yellow cotton tee for kids with the floating blue balloon from The Blue Balloon movie on the front.",
        (YELLOW,),
    ),
    _p(
        _BB,
        "SW",
        "The Blue Balloon Kids' Green Sweatshirt",
        "A brushed-back green cotton sweatshirt for kids with the blue balloon from The Blue Balloon movie on the chest.",
        (GREEN,),
    ),
    _p(
        _BB,
        "BD",
        "The Blue Balloon Kids' White Duvet Set",
        "A single white duvet cover and pillowcase with the blue balloon in a circle from The Blue Balloon movie. Duvet sold separately.",
        (WHITE,),
    ),
    _p(
        _BB,
        "PC",
        "The Blue Balloon Blue Paper Party Cups for Birthday Parties",
        "Blue paper party cups with the floating balloon from The Blue Balloon movie, for a birthday party.",
        (BLUE,),
    ),
    _p(
        _BB,
        "PB",
        "The Blue Balloon Red Party Bags",
        "Red paper party bags with the blue balloon from The Blue Balloon movie, ready to fill for a birthday.",
        (RED,),
    ),
    _p(
        _BB,
        "ST",
        "Kids' Sky Adventure Sticker Sheets",
        "Four sheets of stickers of the balloon, the girl and the city from The Blue Balloon movie.",
        (BLUE,),
    ),
    _p(
        _BB,
        "SS",
        "The Blue Balloon Bubblegum Sweets",
        "Round bubblegum sweets in a bag printed with the balloon from The Blue Balloon movie.",
    ),
)


def film_of(row: Row) -> str:
    """The film a row of :data:`ROWS` sells."""
    return next(f for f, c in FILMS.items() if row.code[2:4] == c)


@functools.cache
def _films_by_id() -> dict[str, str]:
    return {r.product_id: film_of(r) for r in ROWS}


def film_of_id(product_id: str) -> str | None:
    """The film the product sells, or ``None`` for a product of no film: its drawing carries
    that film's emblem (:mod:`film_emblems`, gen#904)."""
    return _films_by_id().get(product_id)


#: The ids of the products whose title does not name their film.
DESCRIPTION_ONLY = frozenset(
    r.product_id for r in ROWS if film_of(r).lower() not in r.title.lower()
)


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
    fields = [
        doc.get("brand") or "",
        doc.get("product_line") or "",
        *doc.get("category_path", ()),
        doc.get("category_leaf") or "",
    ]
    return [f for f in FILMS for v in fields if f.lower() in str(v).lower()]
