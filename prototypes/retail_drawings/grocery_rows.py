"""Grocery families for the retail catalog (gen#154): data only, read by :mod:`grocery`.

A :class:`Family` is one kind of product on one leaf (milk chocolate bars, crisps,
honey). :func:`grocery.build` makes styles from it. A style is a range name and a
brand, plus a subset of the family's flavors (or scents or varieties) and pack sizes.
Its SKUs are flavor x pack.

The shape follows Open Food Facts (ODbL), used only as inspiration: its category
tree, its allergen, trace and label model, and rough distributions. In a bounded
UK sample of chocolate, about half contain milk, about 40% may contain nuts and
most grade E. No name, brand or ingredient list comes from it. Every brand is a
:mod:`house_styles` row.

One category path per product. A family's ``path`` is the retailer's breadcrumb
(``Food & Drink > Fruit & Vegetables > Fresh Fruit > Citrus Fruit > Oranges``) and every
product of the family sits under that one path, never under several. Open Food Facts
tags a product with many categories at once: that is a classification, not a store
tree, so only its node NAMES and depth guide the tree here and no multi-valued tag is
copied. The leaf of a bare-noun family (Oranges, Lemons, Apples, Beer's Lager) is what a
"query names a category" policy boosts; the failure classes it must beat are the families
that share only the WORD (a chocolate orange, a beer battered haddock, a ginger beer).

A flavor's ``codes`` are the allergens it contains: P peanuts, T tree nuts,
M milk, G gluten, S soy, E egg, F fish. Two lower-case flags mark animal ingredients:
``h`` is not vegan but is vegetarian (honey, gelatine), and ``x`` is not
vegetarian (meat, fish). A family's ``may`` is a weighted choice of a style's
may-contain codes: the factory's traces.
"""

# ruff: noqa: E501 -- one family's flavors read better on few lines than wrapped (data only).

from __future__ import annotations

from dataclasses import dataclass

#: The dietary labels a SKU may carry: one closed list (gen#296).
DIETARY: tuple[str, ...] = ("Vegan", "Vegetarian", "Gluten Free", "Dairy Free", "Nut Free", "Organic")

ALLERGENS = {"P": "Peanuts", "T": "Tree Nuts", "M": "Milk", "G": "Gluten", "S": "Soy", "E": "Egg", "F": "Fish"}


@dataclass(frozen=True)
class F:
    """One flavor, scent or variety: its name, pack color and contained allergens."""

    name: str
    hex: str
    codes: str = ""
    abv: float | None = None  # a beer's strength: an attribute, and in only some titles
    extras: tuple[tuple[str, str, str], ...] = ()  # more (key, name, value) attributes: grape, origin


@dataclass(frozen=True)
class Family:
    code: str
    path: tuple[str, ...]
    title: str  # "{line}" and, when a style carries one flavor, "{flavor}"
    product_type: str
    shape: str
    label: str
    storage: str
    grades: str  # the nutrition grades a style draws from
    price: float  # the first pack's price
    packs: tuple[str, ...]  # "100g", "4 x 35g", "1L", "6 pack"
    flavors: tuple[F, ...]
    brands: tuple[str, ...]
    weight: float  # share of the build's SKUs
    base: str = ""  # codes every flavor contains
    may: tuple[tuple[int, str], ...] = ((1, ""),)
    per_style: tuple[int, int] = (1, 1)  # flavors a style carries (min, max)
    axis: str = "flavor"  # or "scent" (a non-food), "variety" (fresh produce)
    department: str = "Food & Drink"
    params: tuple[tuple[str, str], ...] = ()
    noun: str = ""  # a non-food's description noun; "" keeps the overlap rows' own
    axis_name: str = ""  # the axis attribute's display name when it is not the capitalised key
    fits: str = ""  # a non-food's closing sentence, "{x}" the lower-cased axis value (else "Scented with")
    item_g: float = 0.0  # a per-item fruit's typical weight of one item, g: prices a weight pack beside count packs
    depth: bool = False  # built after the core families from its own stream (see ``grocery.build``)

    @property
    def food(self) -> bool:
        return self.department == "Food & Drink"


OWNERS = {
    "Pantry Mill": "own", "Hearth & Table": "own", "Barrowby Kitchen": "own",
    "Crunchworth": "third_party", "Wheatsheaf Lane": "third_party",
    "Crofter's Bakehouse": "third_party", "Goldfield Farms": "third_party",
    "Meadowgate Dairy": "third_party", "Mossgill Dairy": "third_party",
    "Olivar Grove": "third_party", "Copper Hill Preserves": "third_party",
    "Kettleby Tea Co.": "third_party", "Brewhollow Roasters": "third_party",
    "Vine & Valley": "third_party", "Freshfold": "third_party",
    "Clearbrook Household": "third_party", "Soapwell": "third_party",
    "Brightwater Botanics": "third_party", "Velling Apothecary": "third_party",
    "Orrin Skin": "third_party",
    "Hollowbrook Cellars": "third_party", "Stonepine Estate": "third_party",
    "Orchardgate Cider Co.": "third_party",
}  # fmt: skip

#: Range names: invented place words, the head of a style's title.
LINES = (
    "Ashcombe", "Brackley", "Corrow", "Dunmere", "Elstow", "Fallowfield", "Garrick",
    "Harlow Bay", "Ingleby", "Juniper Row", "Kelmscott", "Linthorpe", "Marbury",
    "Netherby", "Oakhurst", "Pennine", "Quarry Hill", "Rydal", "Stanwick", "Tarnside",
    "Upwood", "Varley", "Wexcombe", "Yarrow", "Amberley", "Bellingham", "Coldstream",
    "Deepdale", "Eskdale", "Fernhill", "Greyfriars", "Hartside", "Ivybridge",
    "Kingsmead", "Larkrise", "Millbrook", "Northcote", "Orchard Lane", "Priory",
    "Redbrook", "Silverdale", "Thornbury", "Underhill", "Wansford", "Whitmore",
    "Alderley", "Birchfield", "Cranmore", "Dovedale", "Edgecote",
)  # fmt: skip

_CHOC = ("Crunchworth", "Pantry Mill", "Hearth & Table", "Barrowby Kitchen")
_SNACK = ("Crunchworth", "Pantry Mill", "Wheatsheaf Lane", "Crofter's Bakehouse")
_BREAK = ("Wheatsheaf Lane", "Pantry Mill", "Goldfield Farms")
_BAKE = ("Crofter's Bakehouse", "Hearth & Table", "Wheatsheaf Lane")
_DAIRY = ("Meadowgate Dairy", "Mossgill Dairy", "Pantry Mill")
_MEAL = ("Barrowby Kitchen", "Hearth & Table", "Pantry Mill")
_CUP = ("Pantry Mill", "Olivar Grove", "Copper Hill Preserves", "Hearth & Table")
_DRINK = ("Vine & Valley", "Freshfold", "Pantry Mill")
_FRESH = ("Goldfield Farms", "Freshfold", "Pantry Mill")
_FD = "Food & Drink"
_BREW = ("Vine & Valley", "Freshfold", "Pantry Mill")
_A, _C, _Z = "ambient", "chilled", "frozen"
_NUTS = ((3, ""), (4, "T"), (3, "PT"), (1, "PTM"))  # a chocolate factory's traces
_CEREAL = ((4, ""), (2, "T"), (1, "PT"))


def _p(*parts: str) -> tuple[str, ...]:
    return (_FD, *parts)


_FRUIT = _p("Fruit & Vegetables", "Fresh Fruit")
_STEAK = _p("Meat & Fish", "Fresh Meat", "Steak")
_BEER = _p("Beer, Wine & Spirits", "Beer")
_WINE = _p("Beer, Wine & Spirits", "Wine")
_CIDER = _p("Beer, Wine & Spirits", "Cider")
_SPIRITS = _p("Beer, Wine & Spirits", "Spirits")
_FORTIFIED = _p("Beer, Wine & Spirits", "Wine", "Fortified Wine")
_CELLAR = ("Hollowbrook Cellars", "Stonepine Estate", "Vine & Valley")
_SKIN_BRANDS = ("Velling Apothecary", "Orrin Skin", "Brightwater Botanics")


def _w(name: str, hex_: str, abv: float, grape: str, country: str, style: str) -> F:
    """One wine: its grape, country and style (red, white, rosé, sparkling) are attributes."""
    return F(name, hex_, "", abv, (("grape", "Grape", grape), ("country", "Country", country),
                                   ("wine_style", "Wine style", style)))  # fmt: skip


def _s(name: str, hex_: str, abv: float, country: str, style: str, codes: str = "") -> F:
    """One spirit or mead: its country and style are attributes beside the strength."""
    return F(name, hex_, codes, abv, (("country", "Country", country), ("spirit_style", "Style", style)))


def _o(name: str, hex_: str, origin: str) -> F:
    """One fresh-produce variety with its country of origin."""
    return F(name, hex_, "", None, (("origin", "Origin", origin),))


_HOME_SCENTS = (
    F("Lemon", "#f2d14b"), F("Orange", "#f2a14b"), F("Pine", "#3f7a4a"), F("Lavender", "#9a7ab6"),
    F("Fresh Linen", "#cfe3ee"),
)
_HOME_BRANDS = ("Clearbrook Household", "Soapwell", "Pantry Mill", "Freshfold")
_BODY_SCENTS = (
    F("Honey", "#e0a030"), F("Lemon", "#f2d14b"), F("Coconut", "#efe8d8"), F("Almond", "#c9a96e"),
    F("Lavender", "#9a7ab6"),
)
_BODY_BRANDS = ("Brightwater Botanics", "Velling Apothecary", "Orrin Skin")

#: A beef cut's own description sentence, by (family code, flavor name): what the cut is and how
#: it cooks, so the six cuts do not share one template (gen#269). Words the SKUs do not carry
#: (a weight, a price) stay out.
CUT_NOTES = {
    ("SKS", "Sirloin Steak"): "A lean cut from the back with a thin edge of fat, best seared hot and left to rest.",
    ("SKR", "Ribeye Steak"): "A well marbled cut from the rib that stays juicy, cooked quickly in a hot pan or on the grill.",
    ("SKF", "Fillet Steak"): "The most tender cut, from the tenderloin, with a mild flavour; cook it briefly and rare to medium.",
    ("SKU", "Rump Steak"): "A full flavoured cut from the hindquarter with a firm bite, good marinated and sliced across the grain.",
    ("SKC", "Chuck Steak"): "A richly flavoured cut from the shoulder with connective tissue, best braised slowly or cooked low and long.",
    ("SKT", "T-Bone Steak"): "A cut across the loin with the bone between a strip and a small fillet, grilled hot for a crust.",
    ("SKL", "Flank Steak"): "A lean, long-grained cut from the belly muscle, marinated, seared quickly and sliced thinly across the grain.",
    ("SKW", "Skirt Steak"): "A thin, beefy cut from the diaphragm with a loose grain, cooked fast over a high heat for fajitas.",
}

FAMILIES: tuple[Family, ...] = (
    # Chocolate & Sweets
    Family("CHB", _p("Chocolate & Sweets", "Chocolate Bars"), "{line} Chocolate Bar", "Chocolate Bar",
           "bar", "Chocolate", _A, "DE", 1.5, ("100g", "4 x 35g", "200g"),
           (F("Milk", "#8a5a3c", "M"), F("Dark 70%", "#3b2416"), F("Hazelnut Milk", "#9a6a44", "MT"),
            F("Peanut Caramel", "#b07a3c", "MP"), F("Mint Dark", "#2f6b52"), F("Orange Dark", "#d9822b"),
            F("Coconut Dark", "#efe8d8"), F("Salted Caramel Milk", "#c48a3a", "M"),
            F("White", "#f2e6c8", "M"), F("Almond Dark", "#7a4a2a", "T"), F("Lemon White", "#f2d14b", "M"),
            F("Raspberry Dark", "#a3214a")),
           _CHOC, 0.09, base="S", may=_NUTS, per_style=(3, 7)),
    Family("CHX", _p("Chocolate & Sweets", "Chocolate Boxes"), "{line} {flavor} Chocolate Selection",
           "Chocolate Box", "box", "Chocolates", _A, "E", 6.0, ("150g", "250g", "400g"),
           (F("Classic Milk", "#8a5a3c", "M"), F("Praline", "#9a6a44", "MT"), F("Dark Truffle", "#3b2416", "M"),
            F("Mint Crisp", "#2f6b52", "M"), F("Orange Cream", "#d9822b", "M"), F("Vegan Dark", "#2a1a10")),
           _CHOC, 0.03, base="S", may=_NUTS),
    Family("SWT", _p("Chocolate & Sweets", "Sweets"), "{line} Sweets", "Sweets", "bag", "Sweets",
           _A, "E", 1.0, ("150g", "300g"),
           (F("Fruit Gums", "#c8312e", "h"), F("Lemon Sherbets", "#f2d14b"), F("Mint Imperials", "#e8f0ea"),
            F("Fizzy Cola", "#5a3a26", "h"), F("Toffee", "#b07a3c", "M"), F("Vegan Jellies", "#7ab648")),
           _SNACK, 0.04, may=((3, ""), (1, "M")), per_style=(2, 5)),
    # Biscuits & Snacks
    Family("BIS", _p("Biscuits & Snacks", "Biscuits"), "{line} Biscuits", "Biscuits", "box",
           "Biscuits", _A, "DE", 1.2, ("200g", "300g", "3 x 150g"),
           (F("Chocolate Chip", "#7a4a2a", "GMS"), F("Ginger Snap", "#c48a3a", "G"), F("Shortbread", "#efd9a8", "GM"),
            F("Oat & Coconut", "#d8c9a8", "G"), F("Lemon Puff", "#f2d14b", "GME"), F("Milk Chocolate Digestive", "#8a5a3c", "GMS")),
           _SNACK, 0.04, may=_CEREAL, per_style=(2, 5)),
    Family("CRS", _p("Biscuits & Snacks", "Crisps"), "{line} Crisps", "Crisps", "crisps_bag",
           "Crisps", _A, "CD", 1.0, ("150g", "6 x 25g", "40g"),
           (F("Sea Salt", "#3b6fb6"), F("Cheese & Onion", "#2f6b52", "M"), F("Salt & Vinegar", "#3a8f6a"),
            F("Sweet Chilli", "#c8312e"), F("Smoky Bacon", "#8c3b2a"), F("Sour Cream & Chive", "#7ab648", "M")),
           _SNACK, 0.04, may=((3, ""), (1, "GM")), per_style=(3, 6)),
    Family("NUT", _p("Biscuits & Snacks", "Nuts & Popcorn"), "{line} {flavor}", "Nuts & Popcorn", "bag",
           "Snacks", _A, "BC", 1.8, ("100g", "200g"),
           (F("Salted Peanuts", "#c48a3a", "P"), F("Honey Roast Cashews", "#d9a441", "Th"),
            F("Mixed Nuts", "#9a6a44", "TP"), F("Sweet & Salty Popcorn", "#f2e6c8"),
            F("Coconut Chips", "#efe8d8"), F("Toffee Popcorn", "#b07a3c", "M")),
           _SNACK, 0.03, may=((2, ""), (2, "PT"))),
    Family("CBR", _p("Biscuits & Snacks", "Cereal Bars"), "{line} Cereal Bars", "Cereal Bar", "bar",
           "Oat Bar", _A, "CD", 1.6, ("5 x 30g", "3 x 40g"),
           (F("Oat & Honey", "#d9a441", "Gh"), F("Chocolate Chip", "#7a4a2a", "GMS"), F("Peanut Butter", "#b07a3c", "GP"),
            F("Apple & Cinnamon", "#7ab648", "G"), F("Coconut & Cashew", "#efe8d8", "T"), F("Lemon & Poppy", "#f2d14b", "G")),
           _SNACK, 0.03, may=_CEREAL, per_style=(2, 4)),
    # Breakfast
    Family("CER", _p("Breakfast", "Cereals"), "{line} {flavor} Cereal", "Cereal", "box", "Cereal", _A, "ABC",
           2.2, ("375g", "500g", "750g"),
           (F("Honey Oat Crunch", "#d9a441", "Gh"), F("Chocolate Hoops", "#5a3a26", "GM"), F("Bran Flakes", "#b07a3c", "G"),
            F("Fruit & Nut Muesli", "#9a6a44", "GT"), F("Corn Flakes", "#f2c14b"), F("Coconut Granola", "#efe8d8", "G")),
           _BREAK, 0.03, may=_CEREAL),
    Family("OAT", _p("Breakfast", "Porridge & Oats"), "{line} {flavor} Porridge", "Porridge", "box", "Porridge",
           _A, "AB", 1.4, ("500g", "8 x 36g", "1kg"),
           (F("Original", "#efd9a8", "G"), F("Golden Syrup", "#d9a441", "G"), F("Apple & Blueberry", "#5a4a8a", "G"),
            F("Gluten Free Oat", "#e8dcc0")),
           _BREAK, 0.02, may=((3, ""), (1, "M"))),
    # Bakery
    Family("BRD", _p("Bakery", "Bread"), "{line} {flavor} Loaf", "Bread", "loaf", "Bread", _A, "AB", 1.1,
           ("400g", "800g"),
           (F("White", "#efd9a8", "G"), F("Wholemeal", "#b07a3c", "G"), F("Seeded", "#9a6a44", "G"),
            F("Sourdough", "#c9a96e", "G"), F("Gluten Free Brown", "#a8784a", "E"),
            F("Malted Beer", "#8a5a30", "G")),
           _BAKE, 0.015, may=((3, "S"), (1, "ST"))),
    Family("CAK", _p("Bakery", "Cakes"), "{line} {flavor} Cake", "Cake", "cake", "Cake", _A, "E", 2.5,
           ("400g", "6 pack"),
           (F("Lemon Drizzle", "#f2d14b", "GME"), F("Chocolate Fudge", "#5a3a26", "GMES"),
            F("Coffee & Walnut", "#a8784a", "GMET"), F("Carrot", "#d9822b", "GME"), F("Victoria Sponge", "#f2e6c8", "GME")),
           _BAKE, 0.015, item_g=60, may=((2, ""), (2, "TP"))),
    # Dairy & Alternatives, Cheese
    Family("MLK", _p("Dairy & Alternatives", "Milk"), "{line} {flavor} Milk", "Milk", "carton", "Milk", _C, "AB",
           1.0, ("1 pint", "2 pint", "4 pint"),
           (F("Whole", "#3b6fb6", "M"), F("Semi Skimmed", "#3a8f6a", "M"), F("Skimmed", "#c8312e", "M"),
            F("Lactose Free", "#5a4a8a", "M")),
           _DAIRY, 0.03),
    Family("PLM", _p("Dairy & Alternatives", "Milk", "Plant Milk"), "{line} {flavor} Drink", "Plant Milk", "carton",
           "Plant Milk", _A, "AB", 1.5, ("1L", "6 x 1L", "500ml"),
           (F("Oat", "#d8c9a8", "G"), F("Almond", "#c9a96e", "T"), F("Soya", "#efe8d8", "S"), F("Coconut", "#f4f0e6"),
            F("Barista Oat", "#a8784a", "G")),
           _DAIRY, 0.025),
    Family("YOG", _p("Dairy & Alternatives", "Yogurt"), "{line} Yogurt", "Yogurt", "tub", "Yogurt", _C, "BC", 1.0,
           ("4 x 125g", "500g"),
           (F("Natural", "#f4f0e6", "M"), F("Strawberry", "#c8312e", "M"), F("Lemon Curd", "#f2d14b", "ME"),
            F("Coconut", "#efe8d8", "M"), F("Honey", "#d9a441", "Mh"), F("Vanilla", "#f2e6c8", "M")),
           _DAIRY, 0.03, per_style=(2, 4)),
    Family("BUT", _p("Dairy & Alternatives", "Butter & Spreads"), "{line} {flavor}", "Butter & Spreads", "tub",
           "Butter", _C, "DE", 1.8, ("250g", "500g"),
           (F("Salted Butter", "#f2d14b", "M"), F("Unsalted Butter", "#f2e6c8", "M"), F("Spreadable Butter", "#efd9a8", "M"),
            F("Plant Spread", "#7ab648")),
           _DAIRY, 0.015),
    Family("CHE", _p("Cheese", "Cheese"), "{line} {flavor}", "Cheese", "tray", "Cheese", _C, "D", 2.4,
           ("200g", "400g"),
           (F("Mature Cheddar", "#f2c14b", "M"), F("Red Leicester", "#d9822b", "M"), F("Wensleydale & Cranberry", "#f4f0e6", "M"),
            F("Blue Stilton", "#e8e4d8", "M"), F("Smoked Applewood", "#c48a3a", "M"), F("Vegan Cheddar Style", "#f2d14b")),
           _DAIRY, 0.03),
    # Chilled, Frozen
    Family("RDY", _p("Chilled", "Ready Meals"), "{line} {flavor}", "Ready Meal", "tray", "Meal", _C, "BC", 3.5,
           ("400g", "800g"),
           (F("Chicken Tikka Masala", "#d9822b", "Mx"), F("Beef Lasagne", "#a8502e", "GMx"), F("Vegetable Chilli", "#c8312e"),
            F("Macaroni Cheese", "#f2c14b", "GM"), F("Thai Green Curry", "#7ab648", "x"), F("Lemon Chicken", "#f2d14b", "x")),
           _MEAL, 0.03),
    Family("PIZ", _p("Chilled", "Pizza"), "{line} Pizza", "Pizza", "box", "Pizza", _C, "C", 3.0,
           ("10 inch", "12 inch"),
           (F("Margherita", "#c8312e", "GM"), F("Pepperoni", "#8c3b2a", "GMx"), F("Vegan Garden", "#7ab648", "G"),
            F("Four Cheese", "#f2c14b", "GM"), F("Ham & Pineapple", "#d9a441", "GMx")),
           _MEAL, 0.02, per_style=(2, 4)),
    Family("ICE", _p("Frozen", "Ice Cream"), "{line} Ice Cream", "Ice Cream", "lidded_tub", "Ice Cream", _Z, "DE",
           3.0, ("500ml", "900ml", "150ml"),
           (F("Vanilla", "#f2e6c8", "ME"), F("Mint Choc Chip", "#9bd3b0", "MS"), F("Honeycomb", "#d9a441", "Mh"),
            F("Lemon Sorbet", "#f2d14b"), F("Coconut Dairy Free", "#efe8d8"), F("Salted Caramel", "#c48a3a", "M")),
           _MEAL, 0.025, may=((2, ""), (2, "PT")), per_style=(2, 5)),
    Family("FRV", _p("Frozen", "Frozen Vegetables"), "{line} Frozen {flavor}", "Frozen Vegetables", "bag", "Frozen",
           _Z, "A", 1.2, ("750g", "1.5kg"),
           (F("Garden Peas", "#5a9a3a"), F("Sweetcorn", "#f2c14b"), F("Mixed Vegetables", "#7ab648"),
            F("Broccoli Florets", "#3a7a3a"), F("Edamame Beans", "#6aa84a", "S")),
           _MEAL, 0.015),
    # Food Cupboard
    Family("TIN", _p("Food Cupboard", "Tinned"), "{line} {flavor}", "Tinned Food", "tin", "Tinned", _A, "AB", 0.8,
           ("400g", "4 x 400g"),
           (F("Chopped Tomatoes", "#c8312e"), F("Baked Beans", "#d9822b"), F("Coconut Milk", "#efe8d8"),
            F("Chickpeas", "#d9b97a"), F("Tuna in Spring Water", "#3b6fb6", "xF"), F("Peach Slices", "#f2a14b")),
           _CUP, 0.04),
    Family("PAS", _p("Food Cupboard", "Pasta"), "{line} {flavor}", "Pasta", "bag", "Pasta", _A, "A", 0.9,
           ("500g", "1kg"),
           (F("Penne", "#f2d14b", "G"), F("Fusilli", "#efd9a8", "G"), F("Spaghetti", "#f2c14b", "G"),
            F("Egg Tagliatelle", "#e8c060", "GE"), F("Gluten Free Penne", "#e0c890"), F("Lemon & Pepper Linguine", "#f2e04b", "G")),
           _CUP, 0.03),
    Family("RIC", _p("Food Cupboard", "Rice & Grains"), "{line} {flavor}", "Rice & Grains", "bag", "Rice", _A, "A",
           1.5, ("500g", "1kg", "2kg"),
           (F("Basmati Rice", "#f4f0e6"), F("Long Grain Rice", "#efe8d8"), F("Brown Rice", "#c9a96e"),
            F("Coconut Jasmine Rice", "#f2ece0"), F("Quinoa", "#d8c9a8"), F("Couscous", "#efd9a8", "G")),
           _CUP, 0.025),
    Family("SAU", _p("Food Cupboard", "Sauces & Condiments"), "{line} {flavor}", "Sauce", "bottle", "Sauce", _A,
           "CD", 1.4, ("250ml", "500ml", "1L"),
           (F("Tomato Ketchup", "#c8312e"), F("Mayonnaise", "#f4f0e6", "E"), F("Brown Sauce", "#5a3a26", "G"),
            F("Sweet Chilli Sauce", "#d9822b"), F("Mint Sauce", "#3a8f6a"), F("Honey & Mustard Dressing", "#d9a441", "h")),
           _CUP, 0.035),
    Family("JAM", _p("Food Cupboard", "Jam & Honey"), "{line} {flavor}", "Jam & Honey", "jar", "Jam", _A, "D", 2.0,
           ("340g", "454g"),
           (F("Clear Honey", "#e0a030", "h"), F("Set Honey", "#d9a441", "h"), F("Strawberry Jam", "#b8322f"),
            F("Lemon Curd", "#f2d14b", "ME"), F("Seville Orange Marmalade", "#d9822b"), F("Raspberry Jam", "#a3214a")),
           _CUP, 0.03),
    Family("SPR", _p("Food Cupboard", "Nut Butters & Spreads"), "{line} {flavor}", "Spread", "jar", "Spread", _A,
           "CE", 2.2, ("340g", "1kg"),
           (F("Smooth Peanut Butter", "#b07a3c", "P"), F("Crunchy Peanut Butter", "#a06a30", "P"),
            F("Almond Butter", "#c9a96e", "T"), F("Chocolate Hazelnut Spread", "#5a3a26", "TMS"),
            F("Cashew Butter", "#d9b97a", "T"), F("Smooth Chocolate Spread", "#4a2a1a", "M")),
           _CUP, 0.02, may=((2, ""), (2, "PT"))),
    Family("WLD", _p("World Foods", "World Foods"), "{line} {flavor}", "World Food", "jar", "Paste", _A, "C", 2.0,
           ("190g", "350g"),
           (F("Korma Paste", "#e0c060", "TM"), F("Red Thai Curry Paste", "#c8312e"), F("Mango Chutney", "#f2a14b"),
            F("Harissa", "#a8322e"), F("Coconut & Lemongrass Paste", "#efe8d8"), F("Miso Paste", "#a8784a", "S")),
           _CUP, 0.02),
    # Drinks
    Family("TEA", _p("Drinks", "Tea"), "{line} Tea", "Tea", "box", "Tea", _A, "A", 2.0,
           ("40 bags", "80 bags", "240 bags"),
           (F("English Breakfast", "#8c3b2a"), F("Earl Grey", "#26365c"), F("Peppermint", "#3a8f6a"),
            F("Lemon & Ginger", "#f2d14b"), F("Green", "#7ab648"), F("Honey & Vanilla Rooibos", "#d9a441", "h")),
           ("Kettleby Tea Co.", "Pantry Mill", "Hearth & Table"), 0.03, per_style=(2, 5)),
    Family("COF", _p("Drinks", "Coffee"), "{line} {flavor} Coffee", "Coffee", "jar", "Coffee", _A, "A", 4.0,
           ("100g", "200g"),
           (F("Medium Roast Instant", "#5a3a26"), F("Dark Roast Ground", "#3a2618"), F("Decaf Instant", "#7a5a3a"),
            F("Hazelnut Flavored Ground", "#9a6a44"), F("Colombian Ground", "#4a3020")),
           ("Brewhollow Roasters", "Pantry Mill"), 0.025),
    Family("SFT", _p("Drinks", "Soft Drinks"), "{line} Soft Drinks", "Soft Drink", "bottle", "Drink", _A, "BCE", 1.2,
           ("500ml", "1.5L", "6 x 330ml"),
           (F("Cloudy Lemonade", "#f2e04b"), F("Orange Crush", "#f2a14b"), F("Cola", "#3a2618"),
            F("Ginger Beer", "#d9b97a"), F("Elderflower Presse", "#e8f0d8"), F("Sparkling Mint Water", "#bfe3d0")),
           _DRINK, 0.035, per_style=(2, 5)),
    Family("JUI", _p("Drinks", "Juice"), "{line} {flavor} Juice", "Juice", "carton", "Juice", _C, "C", 1.8,
           ("1L", "1.75L", "330ml"),
           (F("Smooth Orange", "#f2a14b"), F("Orange with Bits", "#e8902b"), F("Apple", "#d9c84b"),
            F("Pineapple", "#f2d14b"), F("Coconut Water", "#efe8d8")),
           _DRINK, 0.025),
    # Baby, Free From
    Family("BAB", _p("Baby & Toddler", "Baby Food"), "{line} {flavor} Baby Food", "Baby Food", "jar", "Baby", _A,
           "A", 1.0, ("120g", "4 x 120g"),
           (F("Apple & Pear", "#d9c84b"), F("Sweet Potato & Carrot", "#d9822b"), F("Banana & Mango", "#f2d14b"),
            F("Creamy Porridge", "#efd9a8", "GM")),
           _BREAK, 0.01),
    Family("FRE", _p("Free From", "Free From Snacks"), "{line} Free From {flavor}", "Free From Snack", "box",
           "Free From", _A, "CD", 2.0, ("150g", "4 x 30g"),
           (F("Chocolate Brownies", "#4a2a1a"), F("Lemon Slices", "#f2d14b"), F("Oat Cookies", "#d8c9a8"),
            F("Orange Shortbread", "#f2a14b")),
           _BAKE, 0.01),
    # Fresh
    # Fresh fruit: one bare-noun leaf each, so a query that names the leaf can be routed to it.
    # "Easy Peelers" holds no "orange" in its title: a type match, not a word match.
    Family("ORA", _FRUIT + ("Citrus Fruit", "Oranges"), "{line} {flavor}", "Fresh Fruit", "produce_pile", "Fruit",
           _C, "A", 0.6, ("Single", "4 pack", "1kg"),
           (F("Oranges", "#f2a14b"), F("Blood Oranges", "#c8432e"), F("Orange Segments", "#f29a3b"),
            F("Easy Peelers", "#f39c33")),
           _FRESH, 0.012, item_g=200, axis="variety"),
    Family("LEM", _FRUIT + ("Citrus Fruit", "Lemons"), "{line} {flavor}", "Fresh Fruit", "produce_pile", "Fruit",
           _C, "A", 0.6, ("Single", "4 pack", "1kg"),
           (F("Unwaxed Lemons", "#f2d14b"), F("Lemons", "#f2e04b"), F("Meyer Lemons", "#f4c95a")),
           _FRESH, 0.006, item_g=120, axis="variety"),
    Family("APP", _FRUIT + ("Apples & Pears", "Apples"), "{line} {flavor}", "Fresh Fruit", "produce_pile", "Fruit",
           _C, "A", 0.6, ("Single", "4 pack", "1kg"),
           (F("Gala Apples", "#c8312e"), F("Bramley Apples", "#7ab648"), F("Braeburn Apples", "#b8432e"),
            F("Fuji Apples", "#d9566a")),
           _FRESH, 0.008, item_g=180, axis="variety"),
    Family("VEG", _p("Fruit & Vegetables", "Fresh Vegetables"), "{line} {flavor}", "Fresh Vegetables", "punnet", "Veg", _C, "A", 0.8,
           ("250g", "500g"),
           (F("Cherry Tomatoes", "#c8312e"), F("Baby Carrots", "#d9822b"), F("Mint", "#3a8f6a"),
            F("Button Mushrooms", "#e8e4d8"), F("Green Beans", "#5a9a3a")),
           _FRESH, 0.02, axis="variety"),
    # Meat & Fish
    Family("MEA", _p("Meat & Fish", "Packaged Meat"), "{line} {flavor}", "Meat", "tray", "Meat", _C, "BC", 3.0,
           ("300g", "500g"),
           (F("Chicken Breast Fillets", "#f2c8b0", "x"), F("Beef Mince", "#a8322e", "x"), F("Pork Sausages", "#c87a6a", "Gx"),
            F("Smoked Bacon", "#b04a3a", "x"), F("Lemon & Herb Chicken Thighs", "#f2d14b", "x")),
           ("Barrowby Kitchen", "Goldfield Farms"), 0.025),
    Family("FSH", _p("Meat & Fish", "Fish"), "{line} {flavor}", "Fish", "tray", "Fish", _C, "AB", 3.5,
           ("240g", "400g"),
           (F("Salmon Fillets", "#f29a7b", "xF"), F("Cod Loins", "#f4f0e6", "xF"), F("Smoked Mackerel", "#c48a3a", "xF"),
            F("Lemon & Pepper Haddock", "#f2d14b", "xF")),
           ("Barrowby Kitchen", "Goldfield Farms"), 0.015),
    # Class "beer": the Beer node holds five leaves (each beer has an ABV attribute, a title
    # states it for about half) and the word "beer" also names a soft drink, a batter, a loaf.
    Family("BLG", _BEER + ("Lager",), "{line} {flavor}{abv}", "Beer", "tin", "Lager", _A, "CD", 1.6,
           ("330ml", "440ml", "4 x 440ml"),
           (F("Premium Lager", "#e8b04a", "G", 4.6), F("Helles Lager", "#f2c14e", "G", 4.8),
            F("Pilsner", "#f0d060", "G", 5.0), F("Golden Table Beer", "#d9a441", "G", 2.8),
            F("Export Lager", "#c8902e", "G", 4.2)),
           _BREW, 0.014),
    Family("BPA", _BEER + ("Pale Ale",), "{line} {flavor}{abv}", "Beer", "bottle", "Pale Ale", _A, "CD", 1.9,
           ("330ml", "500ml", "4 x 500ml"),
           (F("Session Pale Ale", "#c8802e", "G", 3.8), F("American Pale Ale", "#b86a24", "G", 5.2),
            F("Hazy Pale Ale", "#e0a040", "G", 5.5), F("Hazy Wheat Beer", "#e8b04a", "G", 5.5)),
           _BREW, 0.012),
    Family("BSO", _BEER + ("Sour Beer",), "{line} {flavor}{abv}", "Beer", "tin", "Sour Beer", _A, "CD", 2.4,
           ("330ml", "440ml", "4 x 440ml"),
           (F("Tropical Pineapple Sour Beer", "#f2c14e", "G", 4.8), F("Raspberry Sour Beer", "#c8312e", "G", 4.5),
            F("Passion Fruit Sour Beer", "#f2a14b", "G", 5.0), F("Salted Gose Sour Beer", "#e8d8a8", "G", 4.2),
            F("Blackcurrant Sour Beer", "#5a1f4a", "G", 4.6), F("Mango Sour Beer", "#f2b13e", "G", 4.4),
            F("Cherry Sour Beer", "#a3214a", "G", 5.2), F("Lemon & Lime Sour Beer", "#cfe05a", "G", 4.0)),
           _BREW, 0.008),
    Family("BFR", _BEER + ("Fruit Beer",), "{line} {flavor}{abv}", "Beer", "bottle", "Fruit Beer", _A, "CD", 2.2,
           ("330ml", "500ml", "440ml"),
           (F("Raspberry Fruit Beer", "#a3214a", "G", 2.5), F("Cherry Fruit Beer", "#8c1f35", "G", 4.0),
            F("Blood Orange Fruit Beer", "#c8432e", "G", 3.6), F("Peach Fruit Beer", "#f2a07b", "G", 3.2),
            F("Strawberry Fruit Beer", "#d9364a", "G", 2.8), F("Apricot Fruit Beer", "#f2b05a", "G", 3.4),
            F("Blackcurrant Fruit Beer", "#4a1f4a", "G", 3.9), F("Elderflower Fruit Beer", "#e8e0a8", "G", 3.0),
            F("Pineapple Fruit Beer", "#f2d14b", "G", 3.3), F("Plum Fruit Beer", "#6a2a5a", "G", 3.8),
            F("Pear Fruit Beer", "#c8d86a", "G", 2.9), F("Mango Fruit Beer", "#f2b13e", "G", 3.5),
            F("Gooseberry Fruit Beer", "#a8c85a", "G", 3.1), F("Lychee Fruit Beer", "#f2d8d0", "G", 3.2),
            F("Damson Fruit Beer", "#3a1f4a", "G", 4.1), F("Rhubarb Fruit Beer", "#d9566a", "G", 3.0)),
           _BREW, 0.006),
    Family("BAF", _BEER + ("Alcohol Free",), "{line} {flavor}{abv}", "Beer", "tin", "Alcohol Free", _A, "BC", 1.4,
           ("330ml", "440ml", "4 x 440ml"),
           (F("Alcohol Free Lager", "#e8b04a", "G", 0.0), F("Alcohol Free Pale Ale", "#c8802e", "G", 0.5),
            F("Low Alcohol Pilsner", "#f0d060", "G", 0.5), F("Alcohol Free Wheat Beer", "#e0a040", "G", 0.3),
            F("Alcohol Free Amber Ale", "#a8501f", "G", 0.5), F("Alcohol Free Stout", "#2a1810", "G", 0.0),
            F("Low Alcohol Golden Ale", "#d9a030", "G", 0.4), F("Alcohol Free Citrus Lager", "#f0d060", "G", 0.0),
            F("Alcohol Free Session IPA", "#c8802e", "G", 0.5), F("Alcohol Free Dark Lager", "#5a3020", "G", 0.5),
            F("Low Alcohol Amber Lager", "#b86a24", "G", 0.5), F("Alcohol Free Hazy Pale Ale", "#e0a040", "G", 0.3),
            F("Alcohol Free Blonde Ale", "#e8c050", "G", 0.5), F("Low Alcohol Pale Lager", "#f0d060", "G", 0.5),
            F("Alcohol Free Porter", "#3a2418", "G", 0.0), F("Alcohol Free Lime Lager", "#d9e05a", "G", 0.0)),
           _BREW, 0.006),
    Family("GNB", _p("Drinks", "Soft Drinks"), "{line} {flavor}", "Soft Drink", "bottle", "Ginger Beer", _A, "DE",
           1.1, ("330ml", "6 x 330ml", "1L"),
           (F("Ginger Beer", "#d9b97a"), F("Fiery Ginger Beer", "#c98b2b"), F("Root Beer", "#5a3020")),
           _DRINK, 0.004),
    Family("BBF", _p("Frozen", "Battered Fish"), "{line} {flavor}", "Battered Fish", "box", "Battered Fish", _Z,
           "CD", 3.8, ("280g", "4 x 140g"),
           (F("Beer Battered Scottish Haddock", "#d8a548", "GxF"), F("Beer Battered Cod Fillets", "#e0b058", "GxF"),
            F("Crispy Battered Haddock", "#d8a548", "GxF")),
           ("Barrowby Kitchen", "Goldfield Farms"), 0.008),
    Family("VIN", _p("Food Cupboard", "Vinegar"), "{line} {flavor}", "Vinegar", "bottle", "Vinegar", _A, "A", 1.2,
           ("250ml", "500ml", "1L"),
           (F("Cider Vinegar", "#d9b97a"), F("Raw Cider Vinegar", "#c8a050"), F("Balsamic Vinegar", "#3b2416"),
            F("White Wine Vinegar", "#f2e6c8")),
           _CUP, 0.004),
    Family("WGM", _p("Chocolate & Sweets", "Sweets"), "{line} {flavor}", "Sweets", "bag", "Wine Gums", _A, "E",
           1.0, ("150g", "300g"),
           (F("Wine Gums", "#8c1f35", "h"), F("Sour Wine Gums", "#c8312e", "h"), F("Vegan Wine Gums", "#7a1f4a")),
           _SNACK, 0.003, may=((3, ""), (1, "M"))),
    # Class "oranges": the word names a flavour in a bar, a bake, a biscuit and a drink, in
    # categories other than Oranges.
    Family("CHO", _p("Chocolate & Sweets", "Chocolate Bars"), "{line} {flavor}", "Chocolate Bar", "bar",
           "Chocolate Orange", _A, "DE", 1.8, ("100g", "175g"),
           (F("Milk Chocolate Orange", "#d9822b", "M"), F("Dark Chocolate Orange", "#8a4a1c")),
           _CHOC, 0.008, base="S", may=_NUTS),
    Family("PAN", _p("Bakery", "Festive Bakes"), "{line} {flavor}", "Festive Bake", "cake", "Festive Bake", _A,
           "DE", 4.0, ("500g", "750g"),
           (F("Cranberry & Orange Panettone", "#d9a441", "GME"), F("Lemon & Orange Panettone", "#f2c14b", "GME"),
            F("Cherry & Orange Christmas Pudding", "#4a2a1a", "GE"), F("Chocolate Panettone", "#7a4a2a", "GME")),
           _BAKE, 0.006, may=((2, ""), (1, "T"))),
    Family("ORB", _p("Biscuits & Snacks", "Biscuits"), "{line} {flavor}", "Biscuits", "box", "Biscuits", _A, "DE",
           1.5, ("150g", "250g"),
           (F("Orange Shortbread", "#efd9a8", "GM"), F("Chocolate & Orange Cookies", "#7a4a2a", "GME"),
            F("Orange Cream Sandwich Biscuits", "#f2a14b", "GMS")),
           _SNACK, 0.006, may=((3, ""), (1, "T"))),
    Family("HOT", _p("Drinks", "Hot Chocolate"), "{line} {flavor}", "Hot Chocolate", "jar", "Drinking Chocolate",
           _A, "CD", 2.6, ("250g", "400g"),
           (F("Orange Drinking Chocolate", "#d9822b", "M"), F("Classic Drinking Chocolate", "#5a3a26", "M"),
            F("Salted Caramel Hot Chocolate", "#c48a3a", "M")),
           ("Pantry Mill", "Hearth & Table", "Brewhollow Roasters"), 0.004),
    # Overlaps: the words a food shares with a scent
    Family("CLN", ("Cleaning", "Kitchen & Surfaces", "Cleaners", "Kitchen Cleaners"), "{line} {flavor} Multi-Surface Cleaner",
           "Kitchen Cleaner", "bottle", "Cleaner", _A, "", 1.5, ("500ml", "750ml", "1L"),
           (F("Lemon", "#f2d14b"), F("Orange", "#f2a14b"), F("Mint", "#3a8f6a"), F("Lavender", "#9a7ab6")),
           ("Clearbrook Household", "Soapwell"), 0.004, axis="scent", department="Cleaning & Janitorial"),
    Family("BOD", ("Beauty", "Body Care", "Body Lotion"), "{line} {flavor} Body Milk", "Body Lotion", "bottle",
           "Body Milk", _A, "", 4.0, ("250ml", "400ml", "100ml"),
           (F("Honey", "#e0a030"), F("Coconut", "#efe8d8"), F("Shea", "#e8dcc0"), F("Almond", "#c9a96e")),
           ("Brightwater Botanics", "Velling Apothecary", "Orrin Skin"), 0.004, axis="scent", department="Beauty"),
    # Scent depth (gen#154): the demo word "lemon" is a scent in dozens of household SKUs, as it
    # is a fruit and a flavor; "honey" a scent in dozens of body-care SKUs. Each family is one
    # leaf with its own scent list and the same ``scent`` attribute the Kitchen Cleaner uses,
    # so one policy routes on the attribute and the product type. Drawn from their own stream.
    Family("DSH", ("Cleaning", "Kitchen & Surfaces", "Dish Soap"), "{line} {flavor} Dish Soap", "Dish Soap", "bottle",
           "Dish Soap", _A, "", 1.2, ("500ml", "1L"), _HOME_SCENTS, _HOME_BRANDS, 0.01, axis="scent",
           department="Cleaning & Janitorial", noun="washing-up liquid that cuts through grease", depth=True),
    Family("GLS", ("Cleaning", "Kitchen & Surfaces", "Cleaners", "Glass Cleaners"), "{line} {flavor} Glass Cleaner", "Glass Cleaner",
           "bottle", "Glass Cleaner", _A, "", 1.6, ("500ml", "750ml"), _HOME_SCENTS, _HOME_BRANDS, 0.01,
           axis="scent", department="Cleaning & Janitorial", noun="streak-free spray for windows and mirrors", depth=True),
    Family("FLR", ("Cleaning", "Floor Care", "Floor Cleaners"), "{line} {flavor} Floor Cleaner", "Floor Cleaner",
           "bottle", "Floor Cleaner", _A, "", 2.0, ("1L", "2L", "750ml"), _HOME_SCENTS, _HOME_BRANDS, 0.016, axis="scent",
           department="Cleaning & Janitorial", noun="concentrated cleaner for sealed floors", depth=True),
    Family("BTH", ("Cleaning", "Bathroom", "Bathroom Cleaners"), "{line} {flavor} Bathroom Cleaner", "Bathroom Cleaner",
           "bottle", "Bathroom Cleaner", _A, "", 1.8, ("500ml", "750ml", "1L"), _HOME_SCENTS, _HOME_BRANDS, 0.01,
           axis="scent", department="Cleaning & Janitorial", noun="spray that removes limescale and soap scum", depth=True),
    Family("LDY", ("Cleaning", "Laundry", "Laundry Detergent"), "{line} {flavor} Laundry Liquid", "Laundry Detergent",
           "bottle", "Laundry Liquid", _A, "", 4.0, ("1.5L", "3L"), _HOME_SCENTS, _HOME_BRANDS, 0.01, axis="scent",
           department="Cleaning & Janitorial", noun="liquid detergent for every wash", depth=True),
    Family("HWS", ("Beauty", "Bath & Body", "Hand Wash"), "{line} {flavor} Hand Wash", "Hand Wash", "bottle",
           "Hand Wash", _A, "", 1.8, ("250ml", "500ml"), _BODY_SCENTS, _BODY_BRANDS, 0.016, axis="scent",
           department="Beauty", noun="gentle liquid hand wash", depth=True),
    Family("SGL", ("Beauty", "Bath & Body", "Shower Gel"), "{line} {flavor} Shower Gel", "Shower Gel", "bottle",
           "Shower Gel", _A, "", 2.5, ("250ml", "500ml", "750ml"), _BODY_SCENTS, _BODY_BRANDS, 0.016, axis="scent",
           department="Beauty", noun="creamy shower gel", depth=True),
    # Everyday drinks and skincare the demo asks for by name (gen#176). Depth families: drawn
    # from their own stream, so the core families' ids and draws do not move.
    Family("WRD", _WINE + ("Red Wine",), "{line} {flavor}{abv}", "Wine", "bottle", "Red Wine", _A, "CD", 6.5,
           ("750ml", "1.5L", "375ml"),
           (_w("Malbec Red Wine", "#6a1f3a", 13.5, "Malbec", "Argentina", "Red"),
            _w("Merlot Red Wine", "#7a2a3a", 13.0, "Merlot", "Chile", "Red"),
            _w("Rioja Tempranillo Red Wine", "#5a1a2a", 13.5, "Tempranillo", "Spain", "Red"),
            _w("Cabernet Sauvignon Red Wine", "#4a1a2e", 14.0, "Cabernet Sauvignon", "Australia", "Red"),
            _w("Pinot Noir Red Wine", "#8a3a4a", 12.5, "Pinot Noir", "France", "Red"),
            _w("Shiraz Red Wine", "#5a1a3a", 14.5, "Shiraz", "South Africa", "Red"),
            _w("Chianti Sangiovese Red Wine", "#7a2a2a", 13.0, "Sangiovese", "Italy", "Red")),
           _CELLAR, 0.012, depth=True),
    Family("WWH", _WINE + ("White Wine",), "{line} {flavor}{abv}", "Wine", "bottle", "White Wine", _A, "CD", 6.0,
           ("750ml", "1.5L", "375ml"),
           (_w("Sauvignon Blanc White Wine", "#d8d878", 12.5, "Sauvignon Blanc", "New Zealand", "White"),
            _w("Chardonnay White Wine", "#e0c868", 13.0, "Chardonnay", "France", "White"),
            _w("Pinot Grigio White Wine", "#e8e098", 12.0, "Pinot Grigio", "Italy", "White"),
            _w("Riesling White Wine", "#d8e088", 11.5, "Riesling", "Germany", "White"),
            _w("Albarino White Wine", "#e0d880", 12.5, "Albarino", "Spain", "White"),
            _w("Chenin Blanc White Wine", "#e0c070", 13.0, "Chenin Blanc", "South Africa", "White")),
           _CELLAR, 0.012, depth=True),
    Family("WRS", _WINE + ("Rosé Wine",), "{line} {flavor}{abv}", "Wine", "bottle", "Rosé Wine", _A, "CD", 6.0,
           ("750ml", "1.5L", "375ml"),
           (_w("Provence Style Rosé Wine", "#f0b0b0", 12.5, "Grenache", "France", "Rosé"),
            _w("Zinfandel Blush Rosé Wine", "#e88aa0", 10.5, "Zinfandel", "United States", "Rosé"),
            _w("Pinot Grigio Blush Rosé Wine", "#f2b8a0", 11.5, "Pinot Grigio", "Italy", "Rosé"),
            _w("Garnacha Rosé Wine", "#e8788a", 13.0, "Garnacha", "Spain", "Rosé")),
           _CELLAR, 0.005, depth=True),
    Family("WSP", _WINE + ("Sparkling Wine",), "{line} {flavor}{abv}", "Wine", "bottle", "Sparkling Wine", _A, "CD", 8.0,
           ("750ml", "200ml", "1.5L"),
           (_w("Prosecco Sparkling Wine", "#e8e098", 11.0, "Glera", "Italy", "Sparkling"),
            _w("Cava Brut Sparkling Wine", "#e0d890", 11.5, "Macabeo", "Spain", "Sparkling"),
            _w("Sparkling Rosé Wine", "#f0a0a8", 11.0, "Pinot Noir", "Italy", "Sparkling"),
            _w("English Sparkling Wine", "#e8e0a0", 12.0, "Chardonnay", "United Kingdom", "Sparkling"),
            _w("Crémant Sparkling Wine", "#ece0a2", 12.0, "Chenin Blanc", "France", "Sparkling")),
           _CELLAR, 0.006, depth=True),
    Family("WCH", _WINE + ("Champagne",), "{line} {flavor}{abv}", "Champagne", "bottle", "Champagne", _A, "CD", 24.0,
           ("750ml", "1.5L", "375ml"),
           (_w("Brut Champagne", "#e8d88a", 12.0, "Chardonnay", "France", "Sparkling"),
            _w("Rosé Champagne", "#f0a8a8", 12.0, "Pinot Noir", "France", "Sparkling"),
            _w("Blanc de Blancs Champagne", "#f0e090", 12.0, "Chardonnay", "France", "Sparkling"),
            _w("Demi Sec Champagne", "#e8d070", 12.0, "Pinot Meunier", "France", "Sparkling")),
           ("Hollowbrook Cellars", "Stonepine Estate"), 0.004, depth=True),
    Family("CDR", _CIDER, "{line} {flavor}{abv}", "Cider", "bottle", "Cider", _A, "CD", 1.9,
           ("500ml", "4 x 440ml", "2L"),
           (F("Farmhouse Cider", "#d8b04a", "", 4.5, (("cider_style", "Cider style", "Traditional"),)),
            F("Medium Cider", "#d8a83a", "", 4.5, (("cider_style", "Cider style", "Medium"),)),
            F("Sweet Cider", "#d09a2e", "", 4.0, (("cider_style", "Cider style", "Sweet"),)),
            F("Scrumpy Cider", "#b88a2a", "", 6.0, (("cider_style", "Cider style", "Traditional"),)),
            F("Pear Cider", "#d8d078", "", 4.0, (("cider_style", "Cider style", "Fruit"),)),
            F("Strawberry & Lime Cider", "#e87a7a", "", 4.0, (("cider_style", "Cider style", "Fruit"),)),
            F("Alcohol Free Cider", "#d8b04a", "", 0.0, (("cider_style", "Cider style", "Alcohol Free"),))),
           ("Orchardgate Cider Co.", "Vine & Valley", "Freshfold"), 0.010, depth=True),
    Family("HCR", ("Beauty", "Skincare", "Creams", "Hand Creams"), "{line} Hand Cream for {flavor}", "Hand Cream",
           "moisturiser_jar", "Hand Cream", _A, "", 3.5, ("50ml", "100ml", "30ml"),
           (F("Dry Skin", "#f4efe6"), F("Cracked Skin", "#efe4d6"), F("Sensitive Skin", "#eef1ea"),
            F("Everyday Care", "#f2ecdf")),
           _SKIN_BRANDS, 0.008, axis="skin_concern", axis_name="Skin concern", department="Beauty",
           noun="nourishing hand cream", fits="Made for {x}.", depth=True),
    Family("ECR", ("Beauty", "Skincare", "Creams", "Eye Creams"), "{line} Eye Cream for {flavor}", "Eye Cream",
           "moisturiser_jar", "Eye Cream", _A, "", 9.0, ("15ml", "30ml", "50ml"),
           (F("Dark Circles", "#efe8dc"), F("Puffiness", "#eaf0ee"), F("Fine Lines", "#f2ebe0"),
            F("Dry Skin", "#f4efe6")),
           _SKIN_BRANDS, 0.005, axis="skin_concern", axis_name="Skin concern", department="Beauty",
           noun="light eye cream", fits="Made for {x}.", depth=True),
    Family("LIM", _FRUIT + ("Citrus Fruit", "Limes"), "{line} {flavor}", "Fresh Fruit", "produce_pile", "Fruit",
           _C, "A", 0.6, ("Single", "4 pack", "1kg"),
           (_o("Limes", "#7ab63a", "Brazil"), _o("Unwaxed Limes", "#8cc24a", "Mexico"),
            _o("Key Limes", "#a8c84a", "Peru")),
           _FRESH, 0.003, item_g=70, axis="variety", depth=True),
    Family("STR", _FRUIT + ("Berries", "Strawberries"), "{line} {flavor}", "Fresh Fruit", "produce_pile", "Fruit",
           _C, "A", 2.2, ("250g", "400g", "800g"),
           (_o("Ripe Strawberries", "#c8312e", "United Kingdom"), _o("Large Strawberries", "#c8312e", "United Kingdom"),
            _o("Spanish Strawberries", "#d03a36", "Spain"), _o("Sweet Strawberries", "#d9364a", "Morocco")),
           _FRESH, 0.0045, axis="variety", depth=True),
    # Sibling families (gen#177): spirits, fortified wine, perry and mead, the other citrus and
    # berries, foot and body cream. Depth families, so the core families' draws do not move.
    Family("SWH", _SPIRITS + ("Whisky",), "{line} {flavor}{abv}", "Whisky", "bottle", "Whisky", _A, "CD", 18.0,
           ("700ml", "1L", "350ml"),
           (_s("Blended Scotch Whisky", "#b8741f", 40.0, "Scotland", "Blended"),
            _s("Single Malt Scotch Whisky", "#a8641a", 40.0, "Scotland", "Single Malt"),
            _s("Bourbon Whiskey", "#a85a1a", 40.0, "United States", "Bourbon"),
            _s("Irish Whiskey", "#c88a2a", 40.0, "Ireland", "Blended")),
           _CELLAR, 0.005, depth=True),
    Family("SGN", _SPIRITS + ("Gin",), "{line} {flavor}{abv}", "Gin", "bottle", "Gin", _A, "CD", 16.0,
           ("700ml", "1L", "350ml"),
           (_s("London Dry Gin", "#d6e6ee", 40.0, "United Kingdom", "London Dry"),
            _s("Pink Gin", "#f0b8c0", 37.5, "United Kingdom", "Flavoured"),
            _s("Sloe Gin", "#7a2a4a", 26.0, "United Kingdom", "Liqueur"),
            _s("Navy Strength Gin", "#cfe0ea", 57.0, "United Kingdom", "Navy Strength")),
           _CELLAR, 0.005, depth=True),
    Family("SVD", _SPIRITS + ("Vodka",), "{line} {flavor}{abv}", "Vodka", "bottle", "Vodka", _A, "CD", 14.0,
           ("700ml", "1L", "350ml"),
           (_s("Premium Vodka", "#dfe9ee", 40.0, "Poland", "Plain"),
            _s("Triple Distilled Vodka", "#e3edf0", 40.0, "Sweden", "Plain"),
            _s("Lemon Vodka", "#f0e68a", 37.5, "Poland", "Flavoured"),
            _s("Vanilla Vodka", "#efe3c0", 37.5, "Sweden", "Flavoured")),
           _CELLAR, 0.004, depth=True),
    Family("SRM", _SPIRITS + ("Rum",), "{line} {flavor}{abv}", "Rum", "bottle", "Rum", _A, "CD", 17.0,
           ("700ml", "1L", "350ml"),
           (_s("White Rum", "#e6eaea", 37.5, "Barbados", "White"),
            _s("Gold Rum", "#c8902a", 40.0, "Jamaica", "Gold"),
            _s("Dark Rum", "#5a2e1a", 40.0, "Guyana", "Dark"),
            _s("Spiced Rum", "#8a4a22", 35.0, "Caribbean", "Spiced")),
           _CELLAR, 0.004, depth=True),
    Family("STQ", _SPIRITS + ("Tequila",), "{line} {flavor}{abv}", "Tequila", "bottle", "Tequila", _A, "CD", 21.0,
           ("700ml", "1L", "350ml"),
           (_s("Blanco Tequila", "#e2eceb", 38.0, "Mexico", "Blanco"),
            _s("Reposado Tequila", "#d8b45a", 38.0, "Mexico", "Reposado"),
            _s("Anejo Tequila", "#b8782a", 40.0, "Mexico", "Anejo")),
           _CELLAR, 0.003, depth=True),
    Family("FPT", _FORTIFIED + ("Port",), "{line} {flavor}{abv}", "Fortified Wine", "bottle", "Port", _A, "CD", 10.0,
           ("750ml", "1.5L", "500ml"),
           (_w("Ruby Port", "#6a1a2e", 19.5, "Touriga Nacional", "Portugal", "Fortified"),
            _w("Tawny Port", "#9a4a2a", 20.0, "Touriga Franca", "Portugal", "Fortified"),
            _w("Late Bottled Vintage Port", "#5a1a2a", 20.0, "Tinta Roriz", "Portugal", "Fortified"),
            _w("White Port", "#e0c868", 19.0, "Malvasia Fina", "Portugal", "Fortified")),
           _CELLAR, 0.004, depth=True),
    Family("FSY", _FORTIFIED + ("Sherry",), "{line} {flavor}{abv}", "Fortified Wine", "bottle", "Sherry", _A, "CD", 7.5,
           ("750ml", "1.5L", "500ml"),
           (_w("Fino Sherry", "#e8d88a", 15.0, "Palomino", "Spain", "Fortified"),
            _w("Medium Sherry", "#c8903a", 17.5, "Palomino", "Spain", "Fortified"),
            _w("Cream Sherry", "#8a4a22", 17.5, "Pedro Ximenez", "Spain", "Fortified"),
            _w("Amontillado Sherry", "#b87a2a", 18.0, "Palomino", "Spain", "Fortified")),
           _CELLAR, 0.004, depth=True),
    Family("FVM", _FORTIFIED + ("Vermouth",), "{line} {flavor}{abv}", "Fortified Wine", "bottle", "Vermouth", _A, "CD", 7.0,
           ("750ml", "1L", "500ml"),
           (_w("Rosso Vermouth", "#7a2a1a", 15.0, "Trebbiano", "Italy", "Fortified"),
            _w("Bianco Vermouth", "#e8dc9a", 15.0, "Trebbiano", "Italy", "Fortified"),
            _w("Extra Dry Vermouth", "#e6e2b0", 18.0, "Ugni Blanc", "France", "Fortified")),
           _CELLAR, 0.003, depth=True),
    Family("PRY", _p("Beer, Wine & Spirits", "Perry"), "{line} {flavor}{abv}", "Perry", "bottle", "Perry", _A, "CD", 2.2,
           ("500ml", "4 x 440ml", "2L"),
           (F("Traditional Perry", "#dad48a", "", 5.5, (("cider_style", "Cider style", "Traditional"),)),
            F("Medium Perry", "#d8d27a", "", 5.0, (("cider_style", "Cider style", "Medium"),)),
            F("Sparkling Perry", "#e6e29a", "", 5.0, (("cider_style", "Cider style", "Sparkling"),)),
            F("Elderflower Perry", "#e8e4aa", "", 4.0, (("cider_style", "Cider style", "Fruit"),))),
           ("Orchardgate Cider Co.", "Vine & Valley", "Freshfold"), 0.004, depth=True),
    Family("MED", _p("Beer, Wine & Spirits", "Mead"), "{line} {flavor}{abv}", "Mead", "bottle", "Mead", _A, "CD", 9.0,
           ("500ml", "750ml", "375ml"),
           (_s("Traditional Mead", "#d8a830", 12.5, "United Kingdom", "Traditional", "h"),
            _s("Sweet Honey Mead", "#e0b040", 14.0, "United Kingdom", "Sweet", "h"),
            _s("Spiced Mead", "#b87a2a", 12.0, "United Kingdom", "Spiced", "h"),
            _s("Berry Mead", "#a8403a", 11.0, "United Kingdom", "Fruit", "h")),
           _CELLAR, 0.003, depth=True),
    Family("GRF", _FRUIT + ("Citrus Fruit", "Grapefruit"), "{line} {flavor}", "Fresh Fruit", "produce_pile", "Fruit",
           _C, "A", 0.7, ("Single", "4 pack", "1kg"),
           (_o("Ruby Red Grapefruit", "#e8665a", "South Africa"), _o("Pink Grapefruit", "#f09a8a", "Israel"),
            _o("White Grapefruit", "#f2dc6a", "Spain")),
           _FRESH, 0.003, item_g=350, axis="variety", depth=True),
    Family("MAN", _FRUIT + ("Citrus Fruit", "Mandarins"), "{line} {flavor}", "Fresh Fruit", "produce_pile", "Fruit",
           _C, "A", 0.4, ("Single", "4 pack", "1kg"),
           (_o("Mandarins", "#f39c33", "Spain"), _o("Easy Peel Mandarins", "#f5a43a", "Israel"),
            _o("Baby Mandarins", "#f2a03a", "Peru")),
           _FRESH, 0.003, item_g=80, axis="variety", depth=True),
    Family("CLM", _FRUIT + ("Citrus Fruit", "Clementines"), "{line} {flavor}", "Fresh Fruit", "produce_pile", "Fruit",
           _C, "A", 0.4, ("Single", "4 pack", "1kg"),
           (_o("Clementines", "#f39c33", "Spain"), _o("Seedless Clementines", "#f5a03a", "Morocco"),
            _o("Spanish Clementines", "#f29a30", "Spain")),
           _FRESH, 0.003, item_g=75, axis="variety", depth=True),
    Family("SAT", _FRUIT + ("Citrus Fruit", "Satsumas"), "{line} {flavor}", "Fresh Fruit", "produce_pile", "Fruit",
           _C, "A", 0.4, ("Single", "4 pack", "1kg"),
           (_o("Satsumas", "#f4a23a", "Spain"), _o("Seedless Satsumas", "#f5a83e", "South Africa"),
            _o("Easy Peel Satsumas", "#f2a03a", "Peru")),
           _FRESH, 0.003, item_g=80, axis="variety", depth=True),
    Family("RSP", _FRUIT + ("Berries", "Raspberries"), "{line} {flavor}", "Fresh Fruit", "produce_pile", "Fruit",
           _C, "A", 2.5, ("150g", "300g"),
           (_o("Ripe Raspberries", "#c8283e", "United Kingdom"), _o("Sweet Raspberries", "#c42a44", "Spain"),
            _o("Large Raspberries", "#c8304a", "Morocco")),
           _FRESH, 0.003, axis="variety", depth=True),
    Family("BLU", _FRUIT + ("Berries", "Blueberries"), "{line} {flavor}", "Fresh Fruit", "produce_pile", "Fruit",
           _C, "A", 2.0, ("150g", "300g"),
           (_o("Plump Blueberries", "#3a4a8a", "Spain"), _o("Sweet Blueberries", "#3a4a82", "Peru"),
            _o("Large Blueberries", "#3e4e8e", "Chile")),
           _FRESH, 0.003, axis="variety", depth=True),
    Family("BLK", _FRUIT + ("Berries", "Blackberries"), "{line} {flavor}", "Fresh Fruit", "produce_pile", "Fruit",
           _C, "A", 2.0, ("150g", "300g"),
           (_o("Juicy Blackberries", "#2e1a3a", "United Kingdom"), _o("Sweet Blackberries", "#2a1a38", "Mexico"),
            _o("Large Blackberries", "#321e3e", "Serbia")),
           _FRESH, 0.003, axis="variety", depth=True),
    Family("FTC", ("Beauty", "Skincare", "Creams", "Foot Creams"), "{line} Foot Cream for {flavor}", "Foot Cream",
           "moisturiser_jar", "Foot Cream", _A, "", 3.5, ("75ml", "150ml", "200ml"),
           (F("Dry Skin", "#f4efe6"), F("Cracked Heels", "#efe4d6"), F("Tired Feet", "#e6f0ea"),
            F("Everyday Care", "#f2ecdf")),
           _SKIN_BRANDS, 0.005, axis="skin_concern", axis_name="Skin concern", department="Beauty",
           noun="softening foot cream", fits="Made for {x}.", depth=True),
    Family("BCR", ("Beauty", "Body Care", "Body Creams"), "{line} {flavor} Body Cream", "Body Cream",
           "moisturiser_jar", "Body Cream", _A, "", 4.5, ("250ml", "400ml", "500ml"),
           (F("Shea", "#e8dcc0"), F("Cocoa Butter", "#d8c4a0"), F("Almond", "#c9a96e"), F("Oat", "#ece3cf")),
           _SKIN_BRANDS, 0.005, axis="scent", department="Beauty",
           noun="rich body cream for dry skin", depth=True),
    # The "steak" class (gen#264, gen#296): a fresh-meat Steak PARENT with one child per cut, so a
    # shopper's "steak" names the parent and "sirloin steak" its child. Each label names the
    # product on its own ("Skirt Steak", never "Skirt", which is also a garment). The cuts are
    # depth families, last in the list, so no earlier family's draw moves; a style's title names
    # the cut, says "steak" once and runs to five words or more ("Ashcombe British Beef Ribeye
    # Steak"), as a butcher's title does: the text match then favors the short "Steak Knife"
    # titles. Steak knives, sauce and seasoning stay in their own categories as the decoys.
    Family("SKS", _STEAK + ("Sirloin Steak",), "{line} British Beef {flavor}", "Meat", "steak_tray", "Steak", _C, "BC", 4.8,
           ("227g", "2 x 225g"), (F("Sirloin Steak", "#a8322e", "x"),),
           ("Barrowby Kitchen", "Goldfield Farms"), 0.0013, depth=True),
    Family("SKR", _STEAK + ("Ribeye Steak",), "{line} British Beef {flavor}", "Meat", "steak_tray", "Steak", _C, "BC", 4.8,
           ("227g", "2 x 225g"), (F("Ribeye Steak", "#9c2a2a", "x"),),
           ("Barrowby Kitchen", "Goldfield Farms"), 0.0013, depth=True),
    Family("SKU", _STEAK + ("Rump Steak",), "{line} British Beef {flavor}", "Meat", "steak_tray", "Steak", _C, "BC", 4.8,
           ("227g", "2 x 225g"), (F("Rump Steak", "#a63a30", "x"),),
           ("Barrowby Kitchen", "Goldfield Farms"), 0.0013, depth=True),
    Family("SKF", _STEAK + ("Fillet Steak",), "{line} British Beef {flavor}", "Meat", "steak_tray", "Steak", _C, "BC", 4.8,
           ("227g", "2 x 225g"), (F("Fillet Steak", "#b8403a", "x"),),
           ("Barrowby Kitchen", "Goldfield Farms"), 0.0013, depth=True),
    Family("SKC", _STEAK + ("Chuck Steak",), "{line} British Beef {flavor}", "Meat", "steak_tray", "Steak", _C, "BC", 4.8,
           ("227g", "2 x 225g"), (F("Chuck Steak", "#8e2a28", "x"),),
           ("Barrowby Kitchen", "Goldfield Farms"), 0.0013, depth=True),
    Family("SKT", _STEAK + ("T-Bone Steak",), "{line} British Beef {flavor}", "Meat", "steak_tray", "Steak", _C, "BC", 4.8,
           ("227g", "2 x 225g"), (F("T-Bone Steak", "#a02e2c", "x"),),
           ("Barrowby Kitchen", "Goldfield Farms"), 0.0013, depth=True),
    Family("SKL", _STEAK + ("Flank Steak",), "{line} British Beef {flavor}", "Meat", "steak_tray", "Steak", _C, "BC", 4.8,
           ("227g", "2 x 225g"), (F("Flank Steak", "#b0382f", "x"),),
           ("Barrowby Kitchen", "Goldfield Farms"), 0.0013, depth=True),
    Family("SKW", _STEAK + ("Skirt Steak",), "{line} British Beef {flavor}", "Meat", "steak_tray", "Steak", _C, "BC", 4.8,
           ("227g", "2 x 225g"), (F("Skirt Steak", "#9a2c32", "x"),),
           ("Barrowby Kitchen", "Goldfield Farms"), 0.0013, depth=True),
    # Decoys for "steak" in the grocery tree: a sauce and a seasoning (gen#296).
    Family("SSA", _p("Food Cupboard", "Sauces & Condiments"), "{line} {flavor}", "Sauce", "bottle", "Sauce", _A, "CD", 1.9,
           ("250ml", "500ml"), (F("Steak Sauce", "#5a3a26", "G"), F("Peppercorn Steak Sauce", "#4a3020", "G")),
           _CUP, 0.0015, depth=True),
    Family("SSN", _p("Food Cupboard", "Herbs & Spices"), "{line} {flavor}", "Seasoning", "jar", "Seasoning", _A, "A", 1.6,
           ("50g", "100g"), (F("Steak Seasoning", "#7a4a2a"), F("Smoky Steak Rub", "#6a3a22")),
           _CUP, 0.0015, depth=True),
    # Fresh grapes (gen#296): one bare-noun leaf under Fresh Fruit, so a query that names it can
    # be routed; the grape juice and grape sweets below share only the word.
    Family("GRP", _FRUIT + ("Grapes",), "{line} {flavor}", "Fresh Fruit", "produce_pile", "Fruit",
           _C, "A", 2.2, ("250g", "500g", "1kg"),
           (_o("Red Seedless Grapes", "#a3243b", "South Africa"), _o("Green Seedless Grapes", "#a8c84a", "Spain"),
            _o("Black Seedless Grapes", "#3a1f4a", "Chile"), _o("Sweet Red Grapes", "#b02a44", "Peru"),
            _o("Crisp Green Grapes", "#b4d254", "Egypt"), _o("Midnight Black Grapes", "#2e1a40", "South Africa")),
           _FRESH, 0.008, axis="variety", depth=True),
    Family("GJU", _p("Drinks", "Juice"), "{line} {flavor}", "Juice", "carton", "Juice", _C, "C", 1.9,
           ("1L", "1.75L"), (F("Red Grape Juice", "#6a1a3a"), F("White Grape Juice", "#d9d27a")),
           _DRINK, 0.002, depth=True),
    Family("GCH", _p("Chocolate & Sweets", "Sweets"), "{line} {flavor}", "Sweets", "bag", "Sweets", _A, "E", 1.2,
           ("150g", "300g"), (F("Grape Fruit Chews", "#6a2a7a", "h"), F("Grape Jellies", "#7a3a8a")),
           _SNACK, 0.001, depth=True),
    Family("TUS", _p("Food Cupboard", "Tinned"), "{line} {flavor}", "Tinned Food", "tin", "Tinned", _A, "AB", 1.6,
           ("145g", "3 x 145g"),
           (F("Tuna Steaks in Brine", "#3b6fb6", "xF"), F("Tuna Steaks in Sunflower Oil", "#d9a441", "xF")),
           _CUP, 0.002, depth=True),
    # The "chocolate without peanuts" class (gen#294): text search ignores "without", so a chocolate
    # that holds the word "peanut" wins, and so does one that says "peanut-free". Planted by
    # ``DECOY_ANCHORS`` only (a depth family's budget is spent by them); the ingredient fields
    # (``facets.ingredient_base``, ``contains``, ``may_contain``) are the truth the policy reads.
    Family("PNT", _p("Chocolate & Sweets", "Chocolate Bars"), "{line} {flavor}", "Chocolate Bar",
           "bar", "Chocolate", _A, "DE", 1.8, ("100g", "200g"),
           (F("Chocolate Peanut Butter Cups", "#a06a30", "MP"), F("Milk Chocolate with Crunchy Peanuts", "#8a5a3c", "MP"),
            F("Chocolate Coated Peanuts", "#7a4a2a", "MP"), F("Peanut Caramel Chocolate Bar", "#b07a3c", "MP"),
            F("Dark Chocolate Peanut Clusters", "#3b2416", "P"), F("Chocolate Peanut Brittle", "#c48a3a", "MP")),
           _CHOC, 0.001, base="S", depth=True),
    Family("PNH", _p("Chocolate & Sweets", "Chocolate Bars"), "{line} {flavor}", "Chocolate Bar",
           "bar", "Chocolate", _A, "DE", 1.6, ("100g", "200g"),
           (F("Milk Chocolate Praline Bar", "#9a6a44", "MP"), F("Triple Chocolate Biscuit Bar", "#6a3a22", "GMP"),
            F("Dark Chocolate Crunch Bar", "#3b2416", "P")),
           _CHOC, 0.001, base="S", depth=True),
    Family("PNF", _p("Chocolate & Sweets", "Chocolate Bars"), "{line} {flavor}", "Chocolate Bar",
           "bar", "Chocolate", _A, "DE", 1.7, ("100g", "200g"),
           (F("Peanut-Free Milk Chocolate Bar", "#8a5a3c", "M"), F("Peanut-Free Dark Chocolate Bar", "#3b2416"),
            F("No Peanuts Hazelnut Milk Chocolate Bar", "#9a6a44", "MT"), F("No Peanuts Orange Dark Chocolate Bar", "#d9822b"),
            F("Peanut-Free Salted Caramel Chocolate Bar", "#c48a3a", "M")),
           _CHOC, 0.001, base="S", depth=True),
)  # fmt: skip

#: The styles every build plants first, so each demo case exists at any size:
#: (family, the flavors it carries, its may-contain codes).
ANCHORS: tuple[tuple[str, tuple[str, ...], str], ...] = (
    ("CHB", ("Peanut Caramel", "Milk"), ""),  # contains peanuts
    ("CHB", ("Milk", "Dark 70%"), "PT"),  # may contain peanuts
    ("CHB", ("Dark 70%", "Mint Dark", "Orange Dark", "Coconut Dark"), ""),  # vegan, nut free
    ("CHB", ("Milk", "Salted Caramel Milk", "White"), ""),  # milk chocolate, nut free
    ("LEM", ("Unwaxed Lemons",), ""),
    ("ORA", ("Oranges",), ""),
    ("ORA", ("Blood Oranges",), ""),
    ("ORA", ("Orange Segments",), ""),
    ("ORA", ("Easy Peelers",), ""),
    ("APP", ("Gala Apples",), ""),
    ("BLG", ("Premium Lager",), ""),
    ("BSO", ("Tropical Pineapple Sour Beer",), ""),
    ("BAF", ("Alcohol Free Lager",), ""),
    ("GNB", ("Ginger Beer",), ""),
    ("BBF", ("Beer Battered Scottish Haddock",), ""),
    ("BBF", ("Beer Battered Cod Fillets",), ""),
    ("VIN", ("Cider Vinegar",), ""),
    ("WGM", ("Wine Gums",), ""),
    ("CHO", ("Milk Chocolate Orange",), ""),
    ("PAN", ("Cranberry & Orange Panettone",), ""),
    ("ORB", ("Orange Shortbread",), ""),
    ("ORB", ("Chocolate & Orange Cookies",), ""),
    ("HOT", ("Orange Drinking Chocolate",), ""),
    ("JAM", ("Clear Honey",), ""),
    ("JAM", ("Lemon Curd",), ""),
    ("JUI", ("Smooth Orange",), ""),
    ("TIN", ("Coconut Milk",), ""),
    ("MLK", ("Whole", "Semi Skimmed"), ""),
    ("CLN", ("Lemon",), ""),
    ("CLN", ("Orange",), ""),
    ("CLN", ("Mint",), ""),
    ("BOD", ("Honey",), ""),
    ("BOD", ("Coconut",), ""),
)


#: The text-match decoys of the grocery build (gen#294), planted after :data:`ANCHORS` from the
#: depth stream (so no core family's draw moves): (family, its flavors, may-contain codes, the
#: range-name offset). Two ranges per peanut-in-title flavor, so a title and a brand repeat nowhere.
DECOY_ANCHORS: tuple[tuple[str, tuple[str, ...], str, int], ...] = (
    *(("PNT", (f.name,), "", 60 + 7 * k + j) for j in range(2) for k, f in enumerate(
        next(f for f in FAMILIES if f.code == "PNT").flavors)),
    *(("PNH", (f.name,), "", 90 + 5 * k + j) for j in range(2) for k, f in enumerate(
        next(f for f in FAMILIES if f.code == "PNH").flavors)),
    *(("PNF", (f.name,), "", 120 + 5 * k) for k, f in enumerate(
        next(f for f in FAMILIES if f.code == "PNF").flavors)),
)
