"""Barry Plotter, an invented franchise range of 608 SKUs, named only in the product text
(gen#925): data only.

The invented kids' films (:mod:`kids_films`) sell about 30 SKUs each, from one brand at one price
per type, so a film phrase with a filter (``under 30``, ``age 8``, ``on sale``) leaves one product
or none. Barry Plotter is large enough to filter: a boy gardener's enchanted allotment, sold in
six groups (:data:`GROUPS`: building sets, kids' clothing, adult clothing, accessories, home, and
party and stationery), each type made by two to four existing houses at a value, a standard and a
premium price, about 60% of its SKUs under £30 and about a quarter of its products on sale.

The name follows the invented-brands rule: Barry Plotter is a play on a famous name, and nothing
else of the original appears. The range has motifs of its own (:data:`MOTIFS`): a talking
scarecrow, a moonlit glasshouse, creatures that hatch from enchanted packets, a dragon in the
compost heap. No motif word is a product type, a category or a color word of the catalogue.

As with the films, the name lives only in the title and the description: each product keeps the
brand of the house that makes it, no ``product_line`` and the category of its type, and no
attribute names the range (:func:`structured_names` finds one that does). Every description says
the product is "from the Barry Plotter films", and a few name the range in the description only
(:data:`DESCRIPTION_ONLY`).

The rows are ordinary rows of the types they join: each type's spec reads its own with
:func:`rows_of`. The scaled build keeps them out of the passes that weigh one style against
another, as it does the films', and :func:`on_sale` reduces the products of :data:`SALE` in a
pass of their own (``scale.templates``): the range's share on sale is its own, not a department's.
"""

# ruff: noqa: E501 -- data rows read better whole (prototype only).

from __future__ import annotations

import functools
from dataclasses import dataclass

from synthetic_ecommerce_data.domains.retail import breadth_rows, sale_share
from synthetic_ecommerce_data.domains.retail.breadth_rows import Row
from synthetic_ecommerce_data.domains.retail.class_model import BRAND_OWNER
from synthetic_ecommerce_data.domains.retail.kids_films import (
    BLUE,
    GREEN,
    GREY,
    NAVY,
    PINK,
    PURPLE,
    RED,
    WHITE,
    YELLOW,
)
from synthetic_ecommerce_data.domains.retail.prints import ADULT_SIZES, KIDS_SIZES
from synthetic_ecommerce_data.domains.retail.variants import cw

#: The range's name, as a shopper types it.
NAME = "Barry Plotter"
#: What every description says the product is from.
FROM = f"from the {NAME} films"

#: Each motif, with what a description says of it. A motif's words are in the title; none is a
#: product type, a category or a color word of the catalogue (``watering``, ``night`` and
#: ``lantern`` are, so the range never puts them in a title). No description says "Barry's": the
#: output standard reads the "s" as the size S on a product sold in sizes.
MOTIFS: dict[str, str] = {
    "Talking Scarecrow": "the talking scarecrow who keeps watch over the allotment",
    "Moonlit Glasshouse": "the glasshouse where the enchanted plants grow by moonlight",
    "Enchanted Allotment": "the enchanted allotment and its winding paths",
    "Hatchlings": "the tiny creatures that hatch from enchanted packets",
    "Snail Parade": "the parade of glowing snails that lights up the allotment after dark",
    "Compost Dragon": "the friendly dragon who sleeps in the warm compost heap",
    "Potting Shed": "the crooked potting shed where the adventures begin",
    "Wheelbarrow Race": "the great wheelbarrow race across the allotments",
}

BLACK = cw("Black", "#2a2a2e")
WARM_WHITE = cw("Warm White", "#fbefc9")

breadth_rows.OWNERS.update(
    {b: BRAND_OWNER[b] for b in ("Crofter's Bakehouse",) if b not in breadth_rows.OWNERS}
)


@dataclass(frozen=True)
class Kind:
    """One type of the range: its group, where it sells, the houses that make it, its value,
    standard and premium prices, how its title and description name it, and its colors."""

    group: str
    product_type: str
    department: str
    paths: tuple[tuple[str, ...], ...]
    brands: tuple[str, ...]
    prices: tuple[float, float, float]
    noun: str
    lead: str
    shape: str
    colors: tuple = (WHITE,)
    per_product: int = 1
    sizes: tuple[str, ...] = ()
    size_key: str = "size"
    audience: str = "kids"
    colorless: bool = False
    params: tuple[tuple[str, str], ...] = ()
    attrs: tuple[tuple, ...] = ()
    tail: str = ""


BLOCKS, KIDS, ADULT, ACCESSORIES, HOME, PARTY = (
    "Building sets", "Kids' clothing", "Adult clothing", "Accessories", "Home",
    "Party and stationery",
)  # fmt: skip
#: The range's six groups, in the order the doc lists them.
GROUPS = (BLOCKS, KIDS, ADULT, ACCESSORIES, HOME, PARTY)

_FERNBY, _WREN, _LARK, _HARBOUR = "Little Fernby", "Wrenfield", "Larkmoor", "Harbour & Pine"
_PIPWICK, _PUDDLE, _CALDER = "Pipwick Toys", "Puddlecombe Toys", "Calderby & Lune"
_BRACKEN, _HEARTH, _LANTERN = "Brackenmere Home", "Hearth & Table", "Lanternby"
_THISTLE, _QUILLON, _COBBLE, _CROFTER = (
    "Thistle & Wren", "Quillon Sleep", "Cobble & Kiln", "Crofter's Bakehouse",
)  # fmt: skip
_KIDS_COLORS = (NAVY, GREEN, PURPLE, RED, BLUE, PINK, YELLOW, GREY)
_ADULT_COLORS = (BLACK, NAVY, GREY, GREEN)
_MENS_WOMENS = lambda *rest: (("Mens", *rest), ("Womens", *rest))  # noqa: E731

#: The types of the range, each with the two letters of its products' codes.
KINDS: dict[str, Kind] = {
    # -- Kids' clothing: every kids' size --
    "TE": Kind(KIDS, "Tee", "Clothing", (("Kids", "Tops", "T-Shirts"),), (_FERNBY, _WREN, _LARK),
               (7.0, 10.0, 14.0), "Kids' Tee", "A soft cotton tee for kids printed with", "tshirt",
               _KIDS_COLORS, 1, KIDS_SIZES, tail=" Machine washable."),
    "SW": Kind(KIDS, "Sweatshirt", "Clothing", (("Kids", "Tops", "Sweatshirts"),),
               (_FERNBY, _PIPWICK, _WREN), (18.0, 24.0, 32.0), "Kids' Sweatshirt",
               "A brushed-back cotton sweatshirt for kids with", "sweatshirt", _KIDS_COLORS, 1,
               KIDS_SIZES),
    "HK": Kind(KIDS, "Hoodie", "Clothing", (("Kids", "Tops", "Hoodies"),), (_FERNBY, _WREN, _PIPWICK),
               (22.0, 30.0, 36.0), "Kids' Hoodie",
               "A fleece pullover hoodie for kids, with a kangaroo pocket and", "hoodie",
               _KIDS_COLORS, 1, KIDS_SIZES, params=(("zip", "pullover"),),
               attrs=(("zip_style", "Zip style", "Pullover"), ("fabric", "Fabric", "Fleece"))),
    "PJ": Kind(KIDS, "Pyjamas", "Lingerie & Nightwear", (("Kids", "Nightwear", "Pyjamas"),),
               (_FERNBY, _PUDDLE, _PIPWICK), (16.0, 22.0, 30.0), "Kids' Pyjamas",
               "Long-sleeve cotton pyjamas for kids, printed with", "pyjamas", _KIDS_COLORS, 2,
               KIDS_SIZES),
    "AO": Kind(KIDS, "All-in-One", "Lingerie & Nightwear", (("Kids", "Nightwear", "All-in-Ones"),),
               (_FERNBY, _QUILLON), (22.0, 30.0, 36.0), "Kids' Fleece All-in-One",
               "A hooded fleece all-in-one for kids with a front zip and", "all_in_one",
               _KIDS_COLORS, 1, KIDS_SIZES, params=(("hood", "yes"), ("fabric", "fleece")),
               attrs=(("fabric", "Fabric", "Fleece"), ("hood", "Hood", "Yes"))),
    # -- Adult clothing: XS to XL, sold under Mens and Womens in turn --
    "AT": Kind(ADULT, "Tee", "Clothing", _MENS_WOMENS("Tops", "T-Shirts"), (_HARBOUR, _LARK, _WREN),
               (16.0, 24.0, 32.0), "Cotton Tee", "A relaxed-fit cotton tee printed with", "tshirt",
               _ADULT_COLORS, 1, ADULT_SIZES, audience="adult"),
    "AH": Kind(ADULT, "Hoodie", "Clothing", _MENS_WOMENS("Coats & Jackets", "Hoodies"),
               (_HARBOUR, _LARK, _CALDER), (30.0, 40.0, 55.0), "Pullover Hoodie",
               "A heavyweight fleece pullover hoodie with a kangaroo pocket and", "hoodie",
               _ADULT_COLORS, 1, ADULT_SIZES, audience="adult", params=(("zip", "pullover"),),
               attrs=(("zip_style", "Zip style", "Pullover"), ("fabric", "Fabric", "Fleece"))),
    "JM": Kind(ADULT, "Jumper", "Clothing", _MENS_WOMENS("Knitwear", "Jumpers"), (_HARBOUR, _WREN),
               (32.0, 38.0, 48.0), "Knitted Jumper", "A soft knitted jumper with", "sweatshirt",
               _ADULT_COLORS, 1, ADULT_SIZES, audience="adult"),
    "JG": Kind(ADULT, "Joggers", "Clothing", _MENS_WOMENS("Joggers"), (_LARK, _HARBOUR),
               (26.0, 32.0, 40.0), "Lounge Joggers",
               "Cotton lounge joggers with cuffed hems and pockets, printed down one leg with",
               "joggers", _ADULT_COLORS, 1, ADULT_SIZES, audience="adult",
               params=(("fit", "regular"), ("cuff", "elastic"), ("rise", "mid"), ("pocket", "yes"),
                       ("cargo", "no")),
               attrs=(("leg_fit", "Leg fit", "Regular"), ("cuff", "Cuff", "Elasticated"),
                      ("fabric", "Fabric", "Cotton"), ("pockets", "Pockets", "Yes"),
                      ("cargo_pockets", "Cargo pockets", "No"))),
    "SK": Kind(ADULT, "Socks", "Clothing", (("Mens", "Socks", "Everyday Socks"),), (_HARBOUR, _WREN),
               (6.0, 8.0, 12.0), "Socks, Pack of 3", "Three pairs of cotton-rich socks with",
               "socks", _ADULT_COLORS, 1, ("S/M", "M/L", "L/XL"), audience="adult",
               params=(("pairs", "3"),), attrs=(("units_per_pack", "Units per pack", "3", "C62"),)),
    # -- Accessories --
    "BP": Kind(ACCESSORIES, "Backpack", "Clothing", (("Womens", "Accessories", "Bags", "Backpacks"),),
               (_LARK, _HARBOUR), (24.0, 34.0, 45.0), "Backpack",
               "A padded school backpack with a front pocket, printed with", "backpack",
               _KIDS_COLORS, 2, audience="adult", params=(("use", "school"), ("pockets", "1")),
               attrs=(("use", "Use", "School"), ("material", "Material", "Polyester"))),
    "LN": Kind(ACCESSORIES, "Lunch Box", "Home", (("Home", "Kitchen & Dining", "Lunch Boxes"),),
               (_HEARTH, _FERNBY), (6.0, 9.0, 14.0), "Lunch Box",
               "A wipe-clean lunch box with a clip lid, printed with", "box", _KIDS_COLORS, 2),
    "TC": Kind(ACCESSORIES, "Travel Cup", "Home",
               (("Home", "Kitchen & Dining", "Drinkware", "Travel Cups"),), (_BRACKEN, _HEARTH),
               (8.0, 12.0, 18.0), "Drinks Bottle", "A leakproof drinks bottle with a flip straw and",
               "travel_cup", _KIDS_COLORS, 2, audience="adult"),
    "HT": Kind(ACCESSORIES, "Hat", "Clothing", (("Womens", "Accessories", "Hats & Caps"),),
               (_WREN, _LARK), (8.0, 12.0, 16.0), "Beanie",
               "A ribbed knit beanie with a deep cuff, stitched with", "hat", _ADULT_COLORS, 2,
               ("One Size",), "hat_size", audience="adult", params=(("kind", "Beanie"),),
               attrs=(("hat_style", "Hat style", "Beanie"), ("material", "Material", "Acrylic"))),
    "SC": Kind(ACCESSORIES, "Scarf", "Clothing", (("Womens", "Accessories", "Scarves"),),
               (_WREN, _HARBOUR), (14.0, 20.0, 30.0), "Knitted Scarf",
               "A long knitted scarf with a fringe at each end, worked with", "scarf",
               _ADULT_COLORS, 2, audience="adult", params=(("kind", "Knitted"),),
               attrs=(("scarf_style", "Scarf style", "Knitted"), ("material", "Material", "Acrylic"))),
    # -- Home --
    "MG": Kind(HOME, "Mug", "Home", (("Home", "Kitchen & Dining", "Drinkware", "Mugs"),),
               (_BRACKEN, _HEARTH, _THISTLE), (7.0, 10.0, 14.0), "Stoneware Mug",
               "A 350 ml stoneware mug printed with", "mug", (WHITE, NAVY, GREEN), 2,
               audience="adult", tail=" Dishwasher safe."),
    "BD": Kind(HOME, "Duvet Set", "Home", (("Home", "Bedding", "Kids' Bedding"),),
               (_FERNBY, _BRACKEN, _QUILLON), (25.0, 38.0, 105.0), "Duvet Set",
               "A cotton duvet cover and pillowcase printed with", "duvet", _KIDS_COLORS, 2,
               tail=" Duvet sold separately."),
    "CU": Kind(HOME, "Cushion", "Home", (("Home", "Soft Furnishings", "Cushions"),),
               (_HEARTH, _LANTERN, _CALDER), (16.0, 24.0, 32.0), "Cushion",
               "A square cotton cushion, filled, printed with", "cushion", _KIDS_COLORS, 2,
               ("45 x 45cm",), audience="adult", attrs=(("fabric", "Fabric", "Cotton"),)),
    "NL": Kind(HOME, "Night Light", "Toys", (("Toys", "Nursery", "Night Lights"),), (_FERNBY, _PUDDLE),
               (12.0, 18.0, 24.0), "Star Night Light",
               "A plug-in star night light for a bedroom, with", "star", (WARM_WHITE,),
               attrs=(("power", "Power", "Plug-In"),)),
    # -- Party and stationery --
    "PB": Kind(PARTY, "Gift Bag", "Gifts", (("Gifts", "Gift Wrap", "Gift Bags"),), (_LANTERN, _THISTLE),
               (4.0, 6.0, 8.0), "Party Bags",
               "Paper party bags, ready to fill for a birthday, printed with", "gift_bag",
               _KIDS_COLORS, 1, audience="adult"),
    "PC": Kind(PARTY, "Party Cup", "Home",
               (("Home", "Kitchen & Dining", "Drinkware", "Disposable Cups"),), (_LANTERN, _COBBLE),
               (3.0, 4.0, 6.0), "Paper Party Cups", "Paper party cups printed with", "party_cup",
               _KIDS_COLORS, 1, audience="adult", params=(("stack", "stacked"),)),
    "CK": Kind(PARTY, "Cake", "Food & Drink", (("Food & Drink", "Bakery", "Cakes"),),
               (_CROFTER, _HEARTH), (14.0, 20.0, 32.0), "Birthday Cake",
               "A vanilla sponge birthday cake, its icing decorated with", "cake", audience="adult",
               colorless=True, tail=" Serves 14."),
    "NB": Kind(PARTY, "Notebook", "Gifts", (("Gifts", "Stationery", "Notebooks"),),
               (_LANTERN, _CALDER, _THISTLE), (4.0, 7.0, 12.0), "A5 Notebook",
               "An A5 lined notebook with a hard cover printed with", "notebook", _KIDS_COLORS, 2,
               audience="adult", params=(("ruling", "lined"), ("cover", "hardback")),
               attrs=(("page_size", "Page size", "A5"), ("ruling", "Ruling", "Lined"),
                      ("cover", "Cover", "Hardback"))),
    "ST": Kind(PARTY, "Stickers", "Toys", (("Toys", "Arts & Crafts", "Stickers"),), (_FERNBY, _PIPWICK),
               (3.0, 4.0, 5.0), "Sticker Sheets", "Four sheets of stickers of", "sticker_sheet",
               (GREEN,), colorless=True),
}  # fmt: skip

#: The building sets: per motif, one set at each of these piece counts, with its age and the
#: three prices a set of that count is sold at in turn (gen#925: £4.99 to £149.99).
SET_SIZES: tuple[tuple[int, str, tuple[float, ...]], ...] = (
    (60, "4", (4.99, 5.99, 6.99)),
    (220, "6", (12.99, 14.99, 16.99)),
    (520, "8", (24.99, 29.99, 34.99)),
    (1100, "12", (44.99, 49.99, 59.99)),
    (2500, "18", (99.99, 119.99, 149.99)),
)
_SET_BRAND = _PIPWICK

#: The products of each kind that are on sale: one in four, the first at a kind's own offset, so
#: the range holds about a quarter of its products on sale (the catalogue holds about 8%).
SALE_EVERY = 4
#: The products whose title does not name the range, by (kind, index): the description does.
_DESCRIPTION_ONLY = {("PJ", 0), ("MG", 0), ("NB", 0), ("BS", 0), ("AH", 0)}


def _title(kind: str, i: int, motif: str, noun: str) -> str:
    return f"{motif} {noun}" if (kind, i) in _DESCRIPTION_ONLY else f"{NAME} {motif} {noun}"


def _rows_of_kind(code: str, k: Kind) -> list[Row]:
    rows = []
    for i, (motif, says) in enumerate(MOTIFS.items()):
        price = k.prices[i % 3]
        colors = tuple(k.colors[(i + j) % len(k.colors)] for j in range(k.per_product))
        rows.append(
            Row(
                f"BYP{code}{i + 1:02d}", _title(code, i, motif, k.noun), k.brands[i % len(k.brands)],
                k.department, k.paths[i % len(k.paths)], k.product_type, price, k.shape,
                f"{k.lead} {says}, {FROM}.{k.tail}", colors, k.attrs,
                tuple((s, price) for s in k.sizes), audience=k.audience, colorless=k.colorless,
                params=k.params, size_key=k.size_key,
            )
        )  # fmt: skip
    return rows


def _building_sets() -> list[Row]:
    rows = []
    for i, (motif, says) in enumerate(MOTIFS.items()):
        for j, (pieces, age, prices) in enumerate(SET_SIZES):
            n = i * len(SET_SIZES) + j
            count = f"{pieces:,}"
            ages = "For adult builders." if age == "18" else f"For ages {age} and up."
            rows.append(
                Row(
                    f"BYPBS{n + 1:02d}", _title("BS", n, motif, f"Building Set, {count} Pieces"),
                    _SET_BRAND, "Toys", ("Toys", "Building & Construction", "Building Sets"),
                    "Building Set", prices[i % 3], "building_set",
                    f"A {count}-piece building set of {says}, {FROM}. Fits every standard brick. {ages}",
                    (GREEN,),
                    (("theme", "Theme", "Fantasy"), ("age_range", "Age range", f"{age}+ years"),
                     ("compatible_system", "Compatible system", "Standard Bricks")),
                    ((str(pieces), prices[i % 3]),), audience="adult" if age == "18" else "kids",
                    colorless=True, params=(("theme", "castle"),), size_key="piece_count",
                )
            )  # fmt: skip
    return rows


ROWS: tuple[Row, ...] = (
    *_building_sets(),
    *(r for code, k in KINDS.items() for r in _rows_of_kind(code, k)),
)


def _kind_of(row: Row) -> str:
    return row.code[3:5]


#: The ids of the products on sale (:func:`on_sale`): in each kind, every :data:`SALE_EVERY`-th
#: product from the kind's own offset.
SALE = frozenset(
    r.product_id
    for n, code in enumerate(("BS", *KINDS))
    for i, r in enumerate(x for x in ROWS if _kind_of(x) == code)
    if (i + n) % SALE_EVERY == 0
)

#: The ids of the products whose title does not name the range.
DESCRIPTION_ONLY = frozenset(r.product_id for r in ROWS if NAME.lower() not in r.title.lower())


def group_of(row: Row) -> str:
    """The group of the range a row sells in."""
    kind = _kind_of(row)
    return BLOCKS if kind == "BS" else KINDS[kind].group


@functools.cache
def ids() -> frozenset[str]:
    """Every product id of the range."""
    return frozenset(r.product_id for r in ROWS)


def rows_of(product_type: str) -> tuple[Row, ...]:
    """The range's products of ``product_type``: the rows its spec declares."""
    return tuple(r for r in ROWS if r.product_type == product_type)


def on_sale(rec: dict) -> dict:
    """``rec`` as the range sells it: a reduced copy when it is in :data:`SALE` and not reduced
    already, the same way :mod:`sale_share` reduces a style; else ``rec`` itself."""
    if rec["product_id"] not in SALE or "was_price" in rec:
        return rec
    out = dict(rec)
    sale_share.reduce(out)
    return out


def structured_names(doc: dict) -> list[str]:
    """The fields of a document that name the range: its brand, its series (``product_line``),
    its category path, its leaf or an attribute's value. A range product names it in none."""
    fields = {
        "brand": doc.get("brand") or "",
        "product_line": doc.get("product_line") or "",
        **{f"category_path[{i}]": v for i, v in enumerate(doc.get("category_path", ()))},
        "category_leaf": doc.get("category_leaf") or "",
        **{f"attribute {a['key']}": a.get("value") for a in doc.get("attributes", ())},
    }
    return [f for f, v in fields.items() if NAME.lower() in str(v).lower()]
