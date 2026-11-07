"""Merchandise of twelve invented kids' films, named only in the product text (gen#887): data only.

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
Five names hold a category word (gen#905: The Toy Movie, Frozen Story, The Home Run, The Lady in
High Heels, The Haunted Dollhouse), and none of those films sells in the category it names
(:data:`NAMED_CATEGORIES`), so a search for the name must not become a category filter.

The rows are ordinary rows of the types they join: each type's spec reads its own with
:func:`rows_of` (``type_specs/mug.py``, ...), and the stickers are a type of their own
(``type_specs/stickers.py``). The drawings are the kit's shapes for those types, one per SKU.
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
    "The Toy Movie": "TM",
    "Frozen Story": "FS",
    "The Home Run": "HR",
    "The Lady in High Heels": "LH",
    "The Haunted Dollhouse": "HD",
}
#: The films whose name holds a category word (gen#905), each with the words of the categories it
#: names (High Heels names every shoe). A film sells nothing in a category whose path holds one of
#: its words: the name is its only link to that category, so a search for it must not filter to
#: the category.
NAMED_CATEGORIES: dict[str, tuple[str, ...]] = {
    "The Toy Movie": ("toy",),
    "Frozen Story": ("frozen",),
    "The Home Run": ("home", "run"),
    "The Lady in High Heels": ("heel", "shoe"),
    "The Haunted Dollhouse": ("doll",),
}
#: The word every description puts after the film's name.
MOVIE = "movie"


def called_a_movie(film: str) -> str:
    """What a description of ``film`` says to call it a movie: the name and :data:`MOVIE`, or the
    name alone when it already ends in Movie (``The Toy Movie``)."""
    return film if film.lower().endswith(MOVIE) else f"{film} {MOVIE}"

breadth_rows.OWNERS.update({b: BRAND_OWNER[b] for b in ("Crofter's Bakehouse",) if b not in breadth_rows.OWNERS})

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
_TM, _FS, _HR = "The Toy Movie", "Frozen Story", "The Home Run"
_LH, _HD = "The Lady in High Heels", "The Haunted Dollhouse"

ROWS: tuple[Row, ...] = (
    # -- Plaything Story: a toy box that comes to life --
    _p(_PS, "MG", "Plaything Story Stoneware Mug", "A 350 ml stoneware mug printed with the toy box gang from the Plaything Story movie. Dishwasher safe.", (WHITE, BLUE)),
    _p(_PS, "TE", "Plaything Story Kids' Cotton Tee", "A soft cotton tee for kids with the toy cowboy and his friends from the Plaything Story movie on the front.", (BLUE, RED, WHITE)),
    _p(_PS, "PJ", "Plaything Story Kids' Pyjamas", "Long-sleeve cotton pyjamas for kids, printed with the toys from the Plaything Story movie.", (BLUE, RED)),
    _p(_PS, "LN", "Plaything Story Kids' Lunch Box", "A wipe-clean lunch box with a clip lid and the toy box friends from the Plaything Story movie.", (RED, BLUE, YELLOW)),
    _p(_PS, "TY", "Plaything Story Dinosaur Soft Toy", "A cuddly plush of the nervous green dinosaur from the Plaything Story movie, 30 cm tall.", (GREEN,), shape="dinosaur"),
    _p(_PS, "ST", "Plaything Story Sticker Sheets", "Four sheets of glossy stickers of the toys from the Plaything Story movie, for books, bottles and bags.", (BLUE,)),
    _p(_PS, "CK", "Plaything Story Birthday Cake", "A vanilla sponge birthday cake with buttercream, topped with the toy cowboy from the Plaything Story movie. Serves 12."),
    _p(_PS, "PB", "Kids' Paper Party Bags", "Paper party bags printed with the toys from the Plaything Story movie, ready to fill for a birthday.", (RED, BLUE)),
    # -- Lovely and the Beast: a castle, a rose and a dance --
    _p(_LB, "MG", "Enchanted Castle Stoneware Mug", "A stoneware mug with the enchanted castle and its ballroom from the Lovely and the Beast movie. Dishwasher safe.", (WHITE, PINK)),
    _p(_LB, "TE", "Lovely and the Beast Kids' Cotton Tee", "A soft cotton tee for kids with the dancing pair from the Lovely and the Beast movie on the front.", (YELLOW, PINK, WHITE)),
    _p(_LB, "PJ", "Lovely and the Beast Kids' Pyjamas", "Long-sleeve cotton pyjamas for kids with the castle and its roses from the Lovely and the Beast movie.", (PINK, NAVY)),
    _p(_LB, "BD", "Lovely and the Beast Kids' Duvet Set", "A single duvet cover and pillowcase printed with the castle ballroom from the Lovely and the Beast movie. Duvet sold separately.", (PINK, YELLOW)),
    _p(_LB, "TY", "Lovely and the Beast Plush Beast Soft Toy", "A big, soft plush of the gentle beast from the Lovely and the Beast movie, with a velvet cape.", (GREY,)),
    _p(_LB, "PC", "Lovely and the Beast Paper Party Cups for Birthday Parties", "Paper party cups with the castle and roses from the Lovely and the Beast movie, for a birthday party.", (PINK, YELLOW)),
    _p(_LB, "SS", "Lovely and the Beast Rose Jelly Sweets", "Rose-shaped fruit jelly sweets in a bag printed with the castle from the Lovely and the Beast movie."),
    # -- Duck Run: a farmyard escape --
    _p(_DR, "MG", "Duck Run Stoneware Mug", "A stoneware mug with the escaping ducks from the Duck Run movie. Dishwasher safe.", (WHITE, YELLOW)),
    _p(_DR, "TE", "Duck Run Kids' Cotton Tee", "A soft cotton tee for kids with the duckling hero from the Duck Run movie on the front.", (YELLOW, GREEN, WHITE)),
    _p(_DR, "SW", "Duck Run Kids' Sweatshirt", "A brushed-back cotton sweatshirt for kids with the farmyard gang from the Duck Run movie.", (GREEN, NAVY)),
    _p(_DR, "PJ", "Kids' Farmyard Pyjamas", "Long-sleeve cotton pyjamas for kids, printed with the ducks of the Duck Run movie on the run from the farm.", (YELLOW, NAVY)),
    _p(_DR, "LN", "Duck Run Kids' Lunch Box", "A wipe-clean lunch box with a clip lid and the ducks from the Duck Run movie.", (YELLOW, GREEN)),
    _p(_DR, "TY", "Duck Run Duckling Soft Toy", "A small plush of the duckling hero from the Duck Run movie, with a soft felt beak.", (YELLOW,), shape="bird"),
    _p(_DR, "PC", "Duck Run Paper Party Cups for Birthday Parties", "Paper party cups with the farmyard ducks from the Duck Run movie, for a birthday party.", (YELLOW, GREEN)),
    _p(_DR, "SS", "Duck Run Fruit Gummy Ducks", "Chewy fruit gummies shaped like the ducks of the Duck Run movie."),
    # -- Really Cold: an ice kingdom --
    _p(_RC, "MG", "Really Cold Stoneware Mug", "A stoneware mug with the ice palace from the Really Cold movie, for hot chocolate on a snow day. Dishwasher safe.", (WHITE, BLUE)),
    _p(_RC, "SW", "Kids' Snow Day Sweatshirt", "A brushed-back cotton sweatshirt for kids with the two sisters and their snowman from the Really Cold movie.", (BLUE, PURPLE)),
    _p(_RC, "JM", "Really Cold Knitted Jumper", "A soft knitted jumper with the ice palace and snowflakes from the Really Cold movie, for a family winter photo.", (BLUE, WHITE, NAVY)),
    _p(_RC, "PJ", "Really Cold Kids' Pyjamas", "Long-sleeve cotton pyjamas for kids with the snowman from the Really Cold movie.", (BLUE, PURPLE)),
    _p(_RC, "BD", "Really Cold Kids' Duvet Set", "A single duvet cover and pillowcase printed with the ice palace from the Really Cold movie. Duvet sold separately.", (BLUE, WHITE)),
    _p(_RC, "ST", "Really Cold Sticker Sheets", "Four sheets of glittery stickers of the snowman and the ice palace from the Really Cold movie.", (PURPLE,)),
    _p(_RC, "CK", "Really Cold Snowflake Celebration Cake", "A chocolate sponge cake with white icing and sugar snowflakes from the Really Cold movie. Serves 14."),
    # -- Little Tiny Queen: the smallest queen of a very large kingdom --
    _p(_LQ, "TE", "Little Tiny Queen Kids' Cotton Tee", "A soft cotton tee for kids with the crowned heroine from the Little Tiny Queen movie on the front.", (PURPLE, PINK, WHITE)),
    _p(_LQ, "PJ", "Little Tiny Queen Kids' Pyjamas", "Long-sleeve cotton pyjamas for kids, printed with the crowns and the castle from the Little Tiny Queen movie.", (PURPLE, PINK)),
    _p(_LQ, "LN", "Kids' Royal Picnic Lunch Box", "A wipe-clean lunch box with a clip lid, printed with the royal picnic from the Little Tiny Queen movie.", (PURPLE, PINK)),
    _p(_LQ, "BD", "Little Tiny Queen Kids' Duvet Set", "A single duvet cover and pillowcase with the throne room from the Little Tiny Queen movie. Duvet sold separately.", (PURPLE, WHITE)),
    _p(_LQ, "ST", "Little Tiny Queen Sticker Sheets", "Four sheets of stickers with crowns, jewels and the heroine from the Little Tiny Queen movie.", (PURPLE,)),
    _p(_LQ, "PB", "Little Tiny Queen Party Bags", "Paper party bags with the crowned heroine from the Little Tiny Queen movie, ready to fill for a birthday.", (PURPLE, PINK)),
    _p(_LQ, "SS", "Little Tiny Queen Jewel Sweets", "Fruit jelly sweets shaped like the crown jewels of the Little Tiny Queen movie."),
    # -- Home Without Anybody: a boy home alone for the holidays --
    _p(_HW, "MG", "Home Without Anybody Stoneware Mug", "A stoneware mug with the snowy family house from the Home Without Anybody movie. Dishwasher safe.", (WHITE, RED)),
    _p(_HW, "JM", "Home Without Anybody Knitted Jumper", "A soft knitted holiday jumper with the family house from the Home Without Anybody movie.", (RED, GREEN, NAVY)),
    _p(_HW, "SW", "Home Without Anybody Kids' Sweatshirt", "A brushed-back cotton sweatshirt for kids with the boy and his booby traps from the Home Without Anybody movie.", (RED, NAVY)),
    _p(_HW, "PJ", "Home Without Anybody Kids' Pyjamas", "Long-sleeve cotton pyjamas for kids with the snowy house from the Home Without Anybody movie.", (RED, GREEN)),
    _p(_HW, "LN", "Home Without Anybody Kids' Lunch Box", "A wipe-clean lunch box with a clip lid and the boy from the Home Without Anybody movie.", (RED, NAVY)),
    _p(_HW, "ST", "Home Without Anybody Sticker Sheets", "Four sheets of stickers of the boy, the house and the two burglars from the Home Without Anybody movie.", (RED,)),
    _p(_HW, "CK", "Holiday Family Celebration Cake", "A rich fruit cake with marzipan and white icing, decorated with the snowy house from the Home Without Anybody movie. Serves 16."),
    # -- The Blue Balloon: a balloon that follows a girl across a city --
    _p(_BB, "MG", "The Blue Balloon Stoneware Mug", "A stoneware mug with the girl and her balloon from The Blue Balloon movie. Dishwasher safe.", (BLUE, WHITE)),
    _p(_BB, "TE", "The Blue Balloon Kids' Cotton Tee", "A soft cotton tee for kids with the floating balloon from The Blue Balloon movie on the front.", (BLUE, WHITE)),
    _p(_BB, "SW", "The Blue Balloon Kids' Sweatshirt", "A brushed-back cotton sweatshirt for kids with the city rooftops from The Blue Balloon movie.", (BLUE, NAVY)),
    _p(_BB, "BD", "The Blue Balloon Kids' Duvet Set", "A single duvet cover and pillowcase with the balloon over the rooftops from The Blue Balloon movie. Duvet sold separately.", (BLUE, WHITE)),
    _p(_BB, "PC", "The Blue Balloon Paper Party Cups for Birthday Parties", "Paper party cups with the floating balloon from The Blue Balloon movie, for a birthday party.", (BLUE, WHITE)),
    _p(_BB, "PB", "The Blue Balloon Party Bags", "Paper party bags with the girl and her balloon from The Blue Balloon movie, ready to fill for a birthday.", (BLUE, WHITE)),
    _p(_BB, "ST", "Kids' Sky Adventure Sticker Sheets", "Four sheets of stickers of the balloon, the girl and the city from The Blue Balloon movie.", (BLUE,)),
    _p(_BB, "SS", "The Blue Balloon Bubblegum Sweets", "Round bubblegum sweets in a bag printed with the balloon from The Blue Balloon movie."),
    # gen#905: five films whose names hold a category word, none selling in that category.
    # -- The Toy Movie: the toys of a toy shop wake at night (nothing under Toys) --
    _p(_TM, "MG", "The Toy Movie Stoneware Mug", "A stoneware mug with the wind-up robot and the toy shop at night from The Toy Movie. Dishwasher safe.", (WHITE, RED)),
    _p(_TM, "TE", "The Toy Movie Kids' Cotton Tee", "A soft cotton tee for kids with the wind-up robot from The Toy Movie on the front.", (RED, GREY)),
    _p(_TM, "SW", "The Toy Movie Kids' Sweatshirt", "A brushed-back cotton sweatshirt for kids with the toy shop window from The Toy Movie.", (NAVY, RED)),
    _p(_TM, "PJ", "Kids' Wind-Up Robot Pyjamas", "Long-sleeve cotton pyjamas for kids, printed with the wind-up robot and his friends from The Toy Movie.", (GREY, NAVY)),
    _p(_TM, "LN", "The Toy Movie Kids' Lunch Box", "A wipe-clean lunch box with a clip lid and the toy shop gang from The Toy Movie.", (RED, YELLOW)),
    _p(_TM, "PC", "The Toy Movie Paper Party Cups for Birthday Parties", "Paper party cups with the wind-up robot from The Toy Movie, for a birthday party.", (RED, YELLOW)),
    _p(_TM, "CK", "The Toy Movie Birthday Cake", "A chocolate sponge birthday cake with buttercream, topped with the wind-up robot from The Toy Movie. Serves 12."),
    _p(_TM, "SS", "The Toy Movie Robot Jelly Sweets", "Fruit jelly sweets shaped like the robots of The Toy Movie."),
    # -- Frozen Story: an ice lolly races to the seaside before he melts (nothing under Frozen) --
    _p(_FS, "MG", "Frozen Story Stoneware Mug", "A stoneware mug with the ice lolly hero and his seaside friends from the Frozen Story movie. Dishwasher safe.", (WHITE, BLUE)),
    _p(_FS, "TE", "Frozen Story Kids' Cotton Tee", "A soft cotton tee for kids with the smiling ice lolly from the Frozen Story movie on the front.", (BLUE, PINK, WHITE)),
    _p(_FS, "PJ", "Frozen Story Kids' Pyjamas", "Long-sleeve cotton pyjamas for kids, printed with the ice lolly and the beach from the Frozen Story movie.", (BLUE, PINK)),
    _p(_FS, "LN", "Frozen Story Kids' Lunch Box", "A wipe-clean lunch box with a clip lid and the ice lolly hero from the Frozen Story movie.", (BLUE, YELLOW)),
    _p(_FS, "TY", "Frozen Story Seagull Soft Toy", "A soft plush of the cheeky seagull from the Frozen Story movie, with felt feet.", (WHITE,), shape="bird"),
    _p(_FS, "ST", "Kids' Seaside Race Sticker Sheets", "Four sheets of stickers of the ice lolly, the seagull and the seaside from the Frozen Story movie.", (BLUE,)),
    _p(_FS, "SS", "Frozen Story Fizzy Fruit Sweets", "Fizzy fruit sweets in a bag printed with the ice lolly from the Frozen Story movie."),
    # -- The Home Run: a team of misfits plays its first baseball season (nothing in Home, no running shoes, no marble run) --
    _p(_HR, "TE", "The Home Run Kids' Cotton Tee", "A soft cotton tee for kids with the bat and ball of the team from The Home Run movie on the front.", (WHITE, RED)),
    _p(_HR, "SW", "The Home Run Kids' Sweatshirt", "A brushed-back cotton sweatshirt for kids with the team badge from The Home Run movie.", (NAVY, GREY)),
    _p(_HR, "PJ", "The Home Run Kids' Pyjamas", "Long-sleeve cotton pyjamas for kids, printed with bats, balls and gloves from The Home Run movie.", (NAVY, RED)),
    _p(_HR, "TY", "The Home Run Team Mascot Soft Toy", "A cuddly plush of the team's lion mascot from The Home Run movie, in a baseball cap.", (YELLOW,), shape="cat"),
    _p(_HR, "ST", "The Home Run Sticker Sheets", "Four sheets of stickers of the players, the bats and the ball from The Home Run movie.", (RED,)),
    _p(_HR, "PB", "The Home Run Party Bags", "Paper party bags with the bat and ball from The Home Run movie, ready to fill for a birthday.", (RED, NAVY)),
    _p(_HR, "CK", "Kids' Baseball Birthday Cake", "A vanilla sponge birthday cake shaped like a baseball, with the team badge from The Home Run movie. Serves 12."),
    # -- The Lady in High Heels: a grandmother spy in red high heels (no shoes) --
    _p(_LH, "MG", "The Lady in High Heels Stoneware Mug", "A stoneware mug with the spy grandmother and her shiny heels from The Lady in High Heels movie. Dishwasher safe.", (WHITE, PINK)),
    _p(_LH, "TE", "The Lady in High Heels Kids' Cotton Tee", "A soft cotton tee for kids with the spy grandmother from The Lady in High Heels movie on the front.", (PINK, WHITE)),
    _p(_LH, "PJ", "The Lady in High Heels Kids' Pyjamas", "Long-sleeve cotton pyjamas for kids, printed with magnifying glasses and shiny heels from The Lady in High Heels movie.", (PINK, NAVY)),
    _p(_LH, "LN", "Kids' Secret Agent Lunch Box", "A wipe-clean lunch box with a clip lid, printed with the spy grandmother's gadgets from The Lady in High Heels movie.", (NAVY, PINK)),
    _p(_LH, "ST", "The Lady in High Heels Sticker Sheets", "Four sheets of stickers of the spy grandmother, her gadgets and her shiny heels from The Lady in High Heels movie.", (PINK,)),
    _p(_LH, "PB", "The Lady in High Heels Party Bags", "Paper party bags with the spy grandmother from The Lady in High Heels movie, ready to fill for a birthday.", (PINK, PURPLE)),
    _p(_LH, "CK", "The Lady in High Heels Birthday Cake", "A strawberry sponge birthday cake with pink icing and a sugar high heel from The Lady in High Heels movie. Serves 12."),
    _p(_LH, "SS", "The Lady in High Heels Spy Sweets", "Fruit sweets in a secret-code bag from The Lady in High Heels movie."),
    # -- The Haunted Dollhouse: a friendly ghost lives in an old dollhouse (no dolls or dolls' houses) --
    _p(_HD, "MG", "The Haunted Dollhouse Stoneware Mug", "A stoneware mug with the little house and the ghost at its window from The Haunted Dollhouse movie. Dishwasher safe.", (WHITE, PURPLE)),
    _p(_HD, "TE", "The Haunted Dollhouse Kids' Cotton Tee", "A soft cotton tee for kids with the friendly ghost from The Haunted Dollhouse movie on the front.", (PURPLE, GREY, WHITE)),
    _p(_HD, "SW", "The Haunted Dollhouse Kids' Sweatshirt", "A brushed-back cotton sweatshirt for kids with the moonlit house from The Haunted Dollhouse movie.", (PURPLE, NAVY)),
    _p(_HD, "BD", "Kids' Spooky Night Duvet Set", "A single duvet cover and pillowcase with the ghost and the moonlit house from The Haunted Dollhouse movie. Duvet sold separately.", (PURPLE, GREY)),
    _p(_HD, "TY", "The Haunted Dollhouse Ghost Cat Soft Toy", "A soft plush of the ghost's cat from The Haunted Dollhouse movie, glow-in-the-dark eyes.", (GREY,), shape="cat"),
    _p(_HD, "ST", "The Haunted Dollhouse Sticker Sheets", "Four sheets of glow-in-the-dark stickers of the ghost and the house from The Haunted Dollhouse movie.", (PURPLE,)),
    _p(_HD, "CK", "The Haunted Dollhouse Celebration Cake", "A chocolate sponge cake with purple icing and a sugar ghost from The Haunted Dollhouse movie. Serves 14."),
)


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
