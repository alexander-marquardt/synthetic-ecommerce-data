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

A flavor's ``codes`` are the allergens it contains: P peanuts, T tree nuts,
M milk, G gluten, S soy, E egg. Two lower-case flags mark animal ingredients:
``h`` is not vegan but is vegetarian (honey, gelatine), and ``x`` is not
vegetarian (meat, fish). A family's ``may`` is a weighted choice of a style's
may-contain codes: the factory's traces.
"""

# ruff: noqa: E501 -- one family's flavors read better on few lines than wrapped (data only).

from __future__ import annotations

from dataclasses import dataclass

ALLERGENS = {"P": "Peanuts", "T": "Tree Nuts", "M": "Milk", "G": "Gluten", "S": "Soy", "E": "Egg"}


@dataclass(frozen=True)
class F:
    """One flavor, scent or variety: its name, pack color and contained allergens."""

    name: str
    hex: str
    codes: str = ""


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
_A, _C, _Z = "ambient", "chilled", "frozen"
_NUTS = ((3, ""), (4, "T"), (3, "PT"), (1, "PTM"))  # a chocolate factory's traces
_CEREAL = ((4, ""), (2, "T"), (1, "PT"))


def _p(*parts: str) -> tuple[str, ...]:
    return (_FD, *parts)


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
            F("Sourdough", "#c9a96e", "G"), F("Gluten Free Brown", "#a8784a", "E")),
           _BAKE, 0.015, may=((3, "S"), (1, "ST"))),
    Family("CAK", _p("Bakery", "Cakes"), "{line} {flavor} Cake", "Cake", "cake", "Cake", _A, "E", 2.5,
           ("400g", "6 pack"),
           (F("Lemon Drizzle", "#f2d14b", "GME"), F("Chocolate Fudge", "#5a3a26", "GMES"),
            F("Coffee & Walnut", "#a8784a", "GMET"), F("Carrot", "#d9822b", "GME"), F("Victoria Sponge", "#f2e6c8", "GME")),
           _BAKE, 0.015, may=((2, ""), (2, "TP"))),
    # Dairy & Alternatives, Cheese
    Family("MLK", _p("Dairy & Alternatives", "Milk"), "{line} {flavor} Milk", "Milk", "carton", "Milk", _C, "AB",
           1.0, ("1 pint", "2 pint", "4 pint"),
           (F("Whole", "#3b6fb6", "M"), F("Semi Skimmed", "#3a8f6a", "M"), F("Skimmed", "#c8312e", "M"),
            F("Lactose Free", "#5a4a8a", "M")),
           _DAIRY, 0.03),
    Family("PLM", _p("Dairy & Alternatives", "Plant Milk"), "{line} {flavor} Drink", "Plant Milk", "carton",
           "Plant Milk", _A, "AB", 1.5, ("1L", "6 x 1L"),
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
           3.0, ("500ml", "900ml"),
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
            F("Chickpeas", "#d9b97a"), F("Tuna in Spring Water", "#3b6fb6", "x"), F("Peach Slices", "#f2a14b")),
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
           "CD", 1.4, ("250ml", "500ml"),
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
           ("1L", "1.75L"),
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
    Family("FRU", _p("Fresh", "Fruit"), "{line} {flavor}", "Fresh Fruit", "produce_pile", "Fruit", _C, "A", 0.6,
           ("Single", "4 pack", "1kg"),
           (F("Unwaxed Lemons", "#f2d14b"), F("Oranges", "#f2a14b"), F("Easy Peelers", "#f29a3b"),
            F("Gala Apples", "#c8312e"), F("Bramley Apples", "#7ab648")),
           _FRESH, 0.03, axis="variety"),
    Family("VEG", _p("Fresh", "Vegetables"), "{line} {flavor}", "Fresh Vegetables", "punnet", "Veg", _C, "A", 0.8,
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
           (F("Salmon Fillets", "#f29a7b", "x"), F("Cod Loins", "#f4f0e6", "x"), F("Smoked Mackerel", "#c48a3a", "x"),
            F("Lemon & Pepper Haddock", "#f2d14b", "x")),
           ("Barrowby Kitchen", "Goldfield Farms"), 0.015),
    # Overlaps: the words a food shares with a scent
    Family("CLN", ("Cleaning & Janitorial", "Kitchen", "Kitchen Cleaners"), "{line} {flavor} Multi-Surface Cleaner",
           "Kitchen Cleaner", "bottle", "Cleaner", _A, "", 1.5, ("500ml", "750ml"),
           (F("Lemon", "#f2d14b"), F("Orange", "#f2a14b"), F("Mint", "#3a8f6a"), F("Lavender", "#9a7ab6")),
           ("Clearbrook Household", "Soapwell"), 0.004, axis="scent", department="Cleaning & Janitorial"),
    Family("BOD", ("Beauty", "Body Care", "Body Lotion"), "{line} {flavor} Body Milk", "Body Lotion", "bottle",
           "Body Milk", _A, "", 4.0, ("250ml", "400ml"),
           (F("Honey", "#e0a030"), F("Coconut", "#efe8d8"), F("Shea", "#e8dcc0"), F("Almond", "#c9a96e")),
           ("Brightwater Botanics", "Velling Apothecary", "Orrin Skin"), 0.004, axis="scent", department="Beauty"),
)  # fmt: skip

#: The styles every build plants first, so each demo case exists at any size:
#: (family, the flavors it carries, its may-contain codes).
ANCHORS: tuple[tuple[str, tuple[str, ...], str], ...] = (
    ("CHB", ("Peanut Caramel", "Milk"), ""),  # contains peanuts
    ("CHB", ("Milk", "Dark 70%"), "PT"),  # may contain peanuts
    ("CHB", ("Dark 70%", "Mint Dark", "Orange Dark", "Coconut Dark"), ""),  # vegan, nut free
    ("CHB", ("Milk", "Salted Caramel Milk", "White"), ""),  # milk chocolate, nut free
    ("FRU", ("Unwaxed Lemons",), ""),
    ("FRU", ("Oranges",), ""),
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
