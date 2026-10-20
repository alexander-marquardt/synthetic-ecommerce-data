"""Planted distractors of gen#125 (prototype, round 4).

The catalog must hold ordinary products that win the top results when no
policy is applied, so the demo can show what a policy fixes. Each
:class:`Row` of :data:`TABLE` is (query, the intended products, 3 to 10
distractors, the policy that fixes each one).

:func:`check` refuses a row whose distractors cannot outrank the best
intended product on text alone, scored by :class:`BM25` over title plus
description against the whole catalog. Standard library,
:mod:`departments`, :mod:`variants` and :mod:`prints` (print distractors are
products of the print range). Every brand name is invented.
"""

from __future__ import annotations

import math
import re
from collections import Counter
from collections.abc import Callable
from dataclasses import dataclass

import prints
from colorwords import plain
from departments import check as check_departments
from kit_produce import pile_params
from variants import attr, cw, docs, drawing, swatch
from variants import product as style_product

from synthetic_ecommerce_data.core.entry import canonical

MIN_DISTRACTORS, MAX_DISTRACTORS = 3, 10

# ==========================================================================
# A simple BM25 over title + description
# ==========================================================================


def tokens(text: str) -> list[str]:
    """Lower-cased words, with a naive plural strip (``lemons`` -> ``lemon``)."""
    out = []
    for w in re.findall(r"[a-z0-9]+", text.lower()):
        if len(w) > 3 and w.endswith("s") and not w.endswith("ss"):
            w = w[:-1]
        out.append(w)
    return out


def text_of(doc: dict) -> list[str]:
    return tokens(f"{doc['title']} {doc.get('description', '')}")


class BM25:
    """Okapi BM25 (k1 = 1.2, b = 0.75) over each doc's title plus description."""

    def __init__(self, corpus: list[dict], k1: float = 1.2, b: float = 0.75) -> None:
        self.k1, self.b = k1, b
        self.n = len(corpus)
        self.avgdl = sum(len(text_of(d)) for d in corpus) / self.n
        self.df: Counter[str] = Counter(t for d in corpus for t in set(text_of(d)))

    def idf(self, term: str) -> float:
        df = self.df[term]
        return math.log(1 + (self.n - df + 0.5) / (df + 0.5))

    def score(self, query: str, doc: dict) -> float:
        words = text_of(doc)
        tf = Counter(words)
        norm = self.k1 * (1 - self.b + self.b * len(words) / self.avgdl)
        return sum(
            self.idf(t) * tf[t] * (self.k1 + 1) / (tf[t] + norm) for t in tokens(query) if tf[t]
        )


# ==========================================================================
# The table
# ==========================================================================


@dataclass(frozen=True)
class Distractor:
    doc: dict
    fixed_by: str


@dataclass(frozen=True)
class Row:
    cls: str
    query: str
    intended: str
    is_intended: Callable[[dict], bool]
    policy: str
    distractors: tuple[Distractor, ...]
    #: Further products the query also matches that need not outrank: the
    #: observed list carries them below the top 10. :func:`check` ignores them.
    tail: tuple[Distractor, ...] = ()


#: Each single-SKU product's type, by code: stated, never derived from its title.
PRODUCT_TYPES: dict[str, str] = {
    "LEMONS": "Lemons", "ORANGS": "Oranges", "DINTOY": "Toy Figure", "LEMCAK": "Cake",
    "LEMGEL": "Shower Gel", "LEMFLR": "Floor Cleaner", "LEMSPR": "Surface Cleaner",
    "JNSBLT": "Belt", "JNSJKT": "Denim Jacket", "JNSHNG": "Hanger", "JNSSET": "Outfit Set",
    "DUVCOV": "Duvet Cover", "DUVSET": "Duvet Set", "DUVSSK": "Duvet Cover",
    "GBBATH": "Gift Set", "GBSKIN": "Gift Set", "GBHAIR": "Gift Set", "GBWASH": "Wash Bag",
    "GBMKUP": "Make-Up Bag", "GBHOSP": "Hospital Bag", "GBGLOW": "Gift Set",
    "GBLIPC": "Gift Set", "GBTRVL": "Travel Set", "GBSUMR": "Gift Set",
    "GTWALL": "Gift Set", "GTCARD": "Gift Set", "GTTEAH": "Hamper", "GTCHSE": "Hamper",
    "GTBROW": "Letterbox Gift", "GTTEAL": "Letterbox Gift", "GTOLIV": "Plant",
    "GTKEYR": "Keyring", "BOOTORG": "Car Boot Organiser", "BOOTPOL": "Shoe Care Kit",
    "BOOTSOK": "Boot Socks",
}  # fmt: skip


def _unit(rest: list[str]) -> tuple:
    """``attr``'s arguments after the name: the value, and for a measured one its unit
    and the canonical the core computes for it."""
    return (rest[0], rest[1], canonical(rest[0], rest[1])) if len(rest) > 1 else (rest[0],)


def product(
    code: str,
    title: str,
    brand: str,
    department: str,
    path: tuple[str, ...],
    price: float,
    description: str,
    draw: dict,
    attrs: tuple[tuple[str, str, str], ...] = (),
    product_type: str | None = None,
) -> dict:
    """One single-SKU product doc in the variant model's shape (:func:`variants.product`).

    A ``color`` in ``attrs`` is the SKU's color, its swatch the drawing's base. An attr is
    ``(key, name, value)``, or ``(key, name, value, unit_code)`` for a measured one.
    """
    check_departments([department], title)
    named = {k: rest[0] for k, _, *rest in attrs}
    sku: dict = {"price": price, "in_stock": True}
    swatches = {}
    if "color" in named:
        sku = {"color": named["color"], **sku}
        swatches[named["color"]] = swatch((named["color"], draw["pattern"], draw["base"], ""))
    return style_product(
        f"PLT-{code}", [sku], swatches,
        title=title, brand=brand, department=[department],
        product_type=product_type or PRODUCT_TYPES[code],
        category_path=list(path), category_leaf=path[-1],
        description=description,
        attributes=[attr(k, n, *_unit(rest)) for k, n, *rest in attrs if k != "color"],
        drawing=draw, collections=[], currency="GBP",
    )  # fmt: skip


YELLOW, WHITE, ORANGE = "#f2d14b", "#ffffff", "#f08a24"
#: Pack counts: the record states each once, and the drawing shows that many fruits.
LEMON_PACK, ORANGE_PACK = 4, 5

#: Intended products that are not part of a variant family.
LEMONS = product(
    "LEMONS", f"Unwaxed Lemons, Pack of {LEMON_PACK}", "Goldfield Farms", "Food & Drink",
    ("Food & Drink", "Fruit & Vegetables", "Fresh Fruit", "Citrus Fruit", "Lemons"), 1.25,
    "Fresh unwaxed lemons for zesting, juicing and baking, grown in sunny groves.",
    drawing("produce_pile", cw("Lemon", YELLOW), "Lemons",
            **pile_params("lemon", "PLT-LEMONS", "bag", count=LEMON_PACK)),
    (("color", "Color", "Yellow"), ("pack_size", "Pack size", f"{LEMON_PACK} pack")),
)  # fmt: skip
ORANGES = product(
    "ORANGS", f"Valencia Oranges, Pack of {ORANGE_PACK}", "Goldfield Farms", "Food & Drink",
    ("Food & Drink", "Fruit & Vegetables", "Fresh Fruit", "Citrus Fruit", "Oranges"), 1.6,
    "Juicy Valencia oranges for squeezing at breakfast, picked ripe and full of juice.",
    drawing("produce_pile", cw("Orange", ORANGE), "Oranges",
            **pile_params("orange", "PLT-ORANGS", "net", count=ORANGE_PACK)),
    (("color", "Color", "Orange"), ("pack_size", "Pack size", f"{ORANGE_PACK} pack")),
)  # fmt: skip
DINOSAUR_TOY = product(
    "DINTOY", "Dinosaur Figure", "Little Fernby", "Toys",
    ("Toys", "Figures & Playsets", "Animal Figures"), 9.0,
    "A hand-painted T. rex figure with a jaw that opens, for play on the floor or in the bath.",
    drawing("dinosaur", cw("Green", "#5f9a4a")),
)  # fmt: skip

_FOOD_OVER_CLOTHING = "department boost: Food & Drink above Clothing"
LEMON = (
    Distractor(prints.doc("PLT-LEMDRS"), _FOOD_OVER_CLOTHING),
    Distractor(prints.doc("PLT-TEEW5"), _FOOD_OVER_CLOTHING),
    Distractor(prints.doc("PLT-DUVA-LEMON"), "department boost: Food & Drink above Home"),
    Distractor(product(
        "LEMCAK", "Lemon Drizzle Cake", "Crofter's Bakehouse", "Food & Drink",
        ("Food & Drink", "Bakery", "Cakes"), 3.5,
        "A lemon sponge soaked in lemon syrup and topped with lemon icing. Serves 8.",
        drawing("cake", cw("Lemon", "#f6e08a"), "Lemon"),
        (("flavour", "Flavour", "Lemon"),),
    ), "category intent: Fresh Fruit above Bakery"),
    Distractor(product(
        "LEMGEL", "Lemon & Bergamot Shower Gel 250ml", "Velling Apothecary", "Beauty",
        ("Beauty", "Bath & Body", "Shower Gel"), 6.0,
        "A zesty lemon shower gel with lemon peel oil and bergamot. Smells of fresh lemons.",
        drawing("bottle", cw("Lemon", YELLOW), "Lemon"),
        (("fragrance", "Fragrance", "Lemon & Bergamot"),),
    ), "persona boost: a grocery shopper's lemon is Food & Drink"),
    Distractor(product(
        "LEMFLR", "Lemon Floor Cleaner 1L", "Pantry Mill", "Cleaning & Janitorial",
        ("Cleaning", "Floor Care", "Floor Cleaners"), 2.2,
        "A lemon fresh floor cleaner with real lemon oil that leaves floors smelling of lemon.",
        drawing("bottle", cw("Lemon", "#f7e27a"), "Cleaner"),
        (("fragrance", "Fragrance", "Lemon"),),
    ), "department boost: Food & Drink above Cleaning & Janitorial"),
    Distractor(product(
        "LEMSPR", "Lemon Multi-Surface Cleaner Spray", "Pantry Mill", "Cleaning & Janitorial",
        ("Cleaning", "Kitchen & Surfaces", "Multi-Surface Sprays"), 1.9,
        "Lemon scented spray that cuts through grease. Lemon fresh kitchens in seconds.",
        drawing("trigger_spray", cw("Lemon", YELLOW, "solid", "#2f6b3c"), "Spray"),
        (("fragrance", "Fragrance", "Lemon"),),
    ), "department boost: Food & Drink above Cleaning & Janitorial"),
)  # fmt: skip

#: The fruit word as a print and as a color: every one a product of the print range.
ORANGE_WORD = (
    Distractor(prints.doc("PLT-TEEW-ORANGE"), _FOOD_OVER_CLOTHING),
    Distractor(prints.doc("PLT-TEEW6"), _FOOD_OVER_CLOTHING),
    Distractor(prints.doc("PLT-TTW-ORANGE"), "department boost: Food & Drink above Home"),
    Distractor(prints.doc("PLT-MUG-ORANGE"), "department boost: Food & Drink above Home"),
)  # fmt: skip
#: A kids' motif printed on clothes, against the toy a shopper means.
DINOSAUR = tuple(
    Distractor(prints.doc(pid), "department boost: Toys above Clothing")
    for pid in ("PLT-TEEK-DINOSAUR", "PLT-PJK-DINOSAUR", "PLT-SWK-DINOSAUR")
)

DENIM = "#4a6a94"
JEANS = (
    Distractor(product(
        "JNSBLT", "Leather Jeans Belt", "Ferrowick Denim", "Clothing",
        ("Mens", "Accessories", "Belts"), 22.0,
        "A wide leather belt cut for jeans, with a brass roller buckle that sits flat in "
        "jeans belt loops.",
        drawing("belt", cw("Tan", "#b07a45")),
        (("color", "Color", "Tan"), ("material", "Material", "Leather")),
    ), "product-type demotion: accessories below jeans"),
    Distractor(product(
        "JNSJKT", "Belted Denim Jacket", "Harbour & Pine", "Clothing",
        ("Womens", "Coats & Jackets", "Denim Jackets"), 45.0,
        "Cut from the same rigid denim as our jeans, in a jeans blue mid wash. Wear it with "
        "jeans for double denim.",
        drawing("coat", cw("Mid Wash", DENIM)),
        (("color", "Color", "Mid Wash"),),
    ), "category intent: Jeans"),
    Distractor(product(
        "JNSHNG", "Jeans Hanger, Pack of 5", "Brackenmere Home", "Home",
        ("Home", "Storage", "Hangers"), 8.0,
        "Clip hangers that hold jeans by the waistband, so jeans hang straight without creases.",
        drawing("hanger", cw("Black", "#2a2a2e")),
        (("color", "Color", "Black"), ("pack_size", "Pack size", "5 pack")),
    ), "category intent: Jeans (a Home item never answers a clothing word)"),
    Distractor(product(
        "JNSSET", "Kids' Jeans & Tee Set", "Little Fernby", "Clothing",
        ("Kids", "Outfits & Sets", "Two-Piece Sets"), 18.0,
        "A two-piece set: slim stretch jeans with an adjustable waist and a cotton tee. "
        "Jeans and tee sold together.",
        drawing("outfit_set", cw("Mid Wash", DENIM), tee="#f2d14b"),
        (("color", "Color", "Mid Wash and Yellow"), ("audience", "Audience", "Boys")),
    ), "product-type demotion: sets below single items"),
)  # fmt: skip

DUVET = (
    Distractor(product(
        "DUVCOV", "Cotton Duvet Cover", "Brackenmere Home", "Home",
        ("Home", "Bedding", "Duvet Covers"), 26.0,
        "A plain cotton duvet cover with a button closure. Fits over any duvet; duvet sold "
        "separately.",
        drawing("duvet", cw("Oyster", "#e4ddd0")),
        (("color", "Color", plain("Oyster")),),
    ), "type-exact intent: Duvets, not Duvet Covers"),
    Distractor(product(
        "DUVSET", "Duvet Cover Set with Pillowcases", "Brackenmere Home", "Home",
        ("Home", "Bedding", "Bedding Sets"), 32.0,
        "A duvet set: one duvet cover and two matching pillowcases. Duvet not included.",
        drawing("duvet", cw("Ticking Stripe", WHITE, "stripe", "#26365c")),
        (("color", "Color", "Navy and White"), ("pattern", "Pattern", "Stripe")),
    ), "type-exact intent: Duvets, not Bedding Sets"),
    Distractor(prints.doc("PLT-DUVKID"), "type-exact intent: Duvets, not Bedding Sets"),
    Distractor(product(
        "DUVSSK", "Seersucker Duvet Cover", "Quillon Sleep", "Home",
        ("Home", "Bedding", "Duvet Covers"), 30.0,
        "A puckered seersucker duvet cover in gingham check. Duvet cover only; duvet not "
        "included.",
        drawing("duvet", cw("Blue Gingham", WHITE, "gingham", "#5b84b8")),
        (("color", "Color", "Blue and White"), ("pattern", "Pattern", "Gingham")),
    ), "type-exact intent: Duvets, not Duvet Covers"),
)  # fmt: skip

# --------------------------------------------------------------------------
# Gift bags: the shape of a "gift bag" failure observed by hand on a live
# retail site (names invented). The query's top 10 held no real gift bag:
# beauty bundles named "... Gift Bag", wash and cosmetic bags, gift sets
# "with Limited Edition Bag" and travel or summer bag sets took it, and
# wallet gift sets, hampers, letterbox gifts, a plant "in ... Gift Bag" and a
# "Gift Boxed" keyring followed. The real ones say "bag" once and never
# "gift": the word lives only in their category, which is what a boost reads.
# --------------------------------------------------------------------------

GIFT_SIZES = (
    ("Small", "18 x 23 cm", 1.5),
    ("Medium", "26 x 32 cm", 2.5),
    ("Large", "33 x 45 cm", 3.5),
)
GIFT_PRINTS = (
    cw("Holly Sprig", "#f4efe2", "polka", "#2f6b3c"),
    cw("Gold Star", "#1f2e4a", "polka", "#d6b56a"),
    cw("Candy Stripe", "#ffffff", "stripe", "#c8312e"),
)  # fmt: skip
GIFT_WRAP = ("Gifts", "Gift Wrap", "Gift Bags")


def gift_bags() -> list[dict]:
    """The intended product for *gift bag*: one style, a SKU per print x size."""
    title = "Kraft Paper Bag with Rope Handles"
    skus = [
        {"color": c[0], "size": size, "dimensions": dims, "price": price, "in_stock": True}
        for c in GIFT_PRINTS
        for size, dims, price in GIFT_SIZES
    ]
    return [style_product(
        "GFT-KRAFT", skus, {c[0]: swatch(c) for c in GIFT_PRINTS},
        title=title, brand="Lanternby", department=check_departments(["Gifts"], title),
        product_type="Gift Bag", category_path=list(GIFT_WRAP), category_leaf=GIFT_WRAP[-1],
        description="A sturdy kraft paper carrier with twisted rope handles, a card base and "
        "a matching tag, in three prints and three sizes. Folds flat to store.",
        attributes=[], drawing=drawing("gift_bag", GIFT_PRINTS[0], GIFT_SIZES[0][0]),
        collections=[], currency="GBP",
    )]  # fmt: skip


GIFT_BAGS = tuple(gift_bags())

_BOOST = "category boost: Gift Wrap above "
GIFT = (
    Distractor(product(
        "GBBATH", "Bath & Body Gift Bag", "Velling Apothecary", "Beauty",
        ("Beauty", "Gift Sets", "Bath & Body Gifts"), 25.0,
        "A gift bag of bath and body favourites: shower gel, body lotion and hand cream in a "
        "reusable gift bag. A ready-made gift.",
        drawing("gift_bag", cw("Lilac", "#c9b6d9", "solid", "#5e4b6e"), "Bath"),
        (("contents", "Contents", "3 items"),),
    ), _BOOST + "Beauty Gift Sets"),
    Distractor(product(
        "GBSKIN", "Skincare Gift Bag", "Velling Apothecary", "Beauty",
        ("Beauty", "Gift Sets", "Skincare Gifts"), 30.0,
        "Cleanser, serum and moisturiser in a gift bag. The skincare gift bag for anyone who "
        "loves a routine.",
        drawing("gift_bag", cw("Sage", "#9bb08f", "solid", "#2f4a3a"), "Skin"),
        (("contents", "Contents", "3 items"),),
    ), _BOOST + "Beauty Gift Sets"),
    Distractor(product(
        "GBHAIR", "Haircare Gift Bag", "Kestlewood Cosmetics", "Beauty",
        ("Beauty", "Gift Sets", "Haircare Gifts"), 22.0,
        "Shampoo, conditioner and a hair mask in a satin gift bag. A gift for good hair days.",
        drawing("gift_bag", cw("Blush", "#f3c6cf", "solid", "#c2185b"), "Hair"),
        (("contents", "Contents", "3 items"),),
    ), _BOOST + "Beauty Gift Sets"),
    Distractor(product(
        "GBWASH", "Waffle Wash Bag", "Saltmarsh", "Beauty",
        ("Beauty", "Accessories", "Wash Bags"), 14.0,
        "A roomy wash bag in waffle cotton with a wipe-clean lining. The wash bag that packs flat.",
        drawing("pouch", cw("Sea Green", "#7fb3a8", "solid", "#1c7c7d"), "Wash"),
        (("color", "Color", plain("Sea Green")),),
    ), _BOOST + "Wash Bags (only *bag* matches)"),
    Distractor(product(
        "GBMKUP", "Quilted Make-Up Bag", "Kestlewood Cosmetics", "Beauty",
        ("Beauty", "Accessories", "Make-Up Bags"), 12.0,
        "A quilted make-up bag with a gold zip. Voted a Top 10 Gift: the bag everyone asks about.",
        drawing("pouch", cw("Black Quilt", "#2a2a2e", "gingham", "#4a4a50"), "Top Gift"),
        (("color", "Color", "Black"), ("badge", "Badge", "Top 10 Gift")),
    ), _BOOST + "Make-Up Bags (a gift badge, not a gift bag)"),
    Distractor(product(
        "GBHOSP", "Hospital Bag Kit", "Little Fernby", "Beauty",
        ("Beauty", "Mother & Baby", "Hospital Bags"), 28.0,
        "Everything for the hospital bag: travel-size wash, balm and maternity pads, with a zip "
        "bag to keep it together.",
        drawing("pouch", cw("Pale Blue", "#bcd3e6", "solid", "#2f4a6b"), "Kit"),
        (("contents", "Contents", "8 items"),),
    ), _BOOST + "Hospital Bags"),
    Distractor(product(
        "GBGLOW", "Glow Make-Up Gift Set with Limited Edition Bag", "Kestlewood Cosmetics",
        "Beauty", ("Beauty", "Gift Sets", "Make-Up Gift Sets"), 35.0,
        "Mascara, lipstick and highlighter in a limited edition bag. A make-up gift set worth "
        "giving.",
        drawing("pouch", cw("Rose Gold", "#e8b8a8", "solid", "#c2185b"), "Glow"),
        (("contents", "Contents", "3 items"),),
    ), _BOOST + "Make-Up Gift Sets"),
    Distractor(product(
        "GBLIPC", "Lip & Cheek Gift Set with Limited Edition Velvet Bag", "Kestlewood Cosmetics",
        "Beauty", ("Beauty", "Gift Sets", "Make-Up Gift Sets"), 26.0,
        "A lip and cheek duo with a velvet bag. Our best-loved gift set.",
        drawing("pouch", cw("Berry Velvet", "#7a1f4a", "solid", "#e9c46a"), "Lip"),
        (("contents", "Contents", "2 items"),),
    ), _BOOST + "Make-Up Gift Sets"),
    Distractor(product(
        "GBTRVL", "Weekend Away Travel Bag Set", "Velling Apothecary", "Beauty",
        ("Beauty", "Travel & Minis", "Travel Sets"), 18.0,
        "Six travel minis in a clear travel bag, ready for the security tray. A bag set that "
        "makes a handy gift.",
        drawing("pouch", cw("Clear", "#e6eef2", "solid", "#5e4b6e"), "Travel"),
        (("contents", "Contents", "6 items"),),
    ), _BOOST + "Travel Sets"),
    Distractor(product(
        "GBSUMR", "Summer Bag Bundle", "Saltmarsh", "Beauty",
        ("Beauty", "Suncare", "Summer Sets"), 24.0,
        "Sun cream, after-sun and a lip balm in a striped beach bag. The summer bag bundle.",
        drawing("pouch", cw("Beach Stripe", "#ffffff", "stripe", "#1c7c7d"), "Summer"),
        (("contents", "Contents", "3 items"),),
    ), _BOOST + "Summer Sets"),
)  # fmt: skip

GIFT_TAIL = (
    Distractor(product(
        "GTWALL", "Leather Wallet & Card Holder Gift Set", "Calderby & Lune", "Gifts",
        ("Gifts", "Gifts for Him", "Wallet Gift Sets"), 40.0,
        "A bifold wallet and a matching card holder in a presentation box. A gift set for him.",
        drawing("wallet", cw("Tan", "#b07a45"), pieces="wallet+card_holder"),
        (("material", "Material", "Leather"),),
    ), _BOOST + "Wallet Gift Sets"),
    Distractor(product(
        "GTCARD", "Slim Card Holder Gift Set", "Calderby & Lune", "Gifts",
        ("Gifts", "Gifts for Her", "Wallet Gift Sets"), 28.0,
        "A slim card holder and a coin purse, gift boxed.",
        drawing("wallet", cw("Oxblood", "#6b1f2a"), pieces="card_holder+coin_purse"),
        (("material", "Material", "Leather"),),
    ), _BOOST + "Wallet Gift Sets"),
    Distractor(product(
        "GTTEAH", "Afternoon Tea Gift Hamper", "Hearth & Table", "Food & Drink",
        ("Food & Drink", "Hampers & Gifts", "Hampers"), 45.0,
        "Tea, shortbread, jam and a fruit cake in a wicker hamper. A gift to share.",
        drawing("box_wide", cw("Wicker", "#c8a46a"), "Hamper"), (("serves", "Serves", "4"),),
    ), _BOOST + "Hampers"),
    Distractor(product(
        "GTCHSE", "Cheese & Chutney Gift Hamper", "Copper Hill Preserves", "Food & Drink",
        ("Food & Drink", "Hampers & Gifts", "Hampers"), 38.0,
        "Three cheeses, a chutney and oat crackers, packed as a gift.",
        drawing("box_wide", cw("Kraft", "#c9a77c"), "Hamper"), (("serves", "Serves", "4"),),
    ), _BOOST + "Hampers"),
    Distractor(product(
        "GTBROW", "Letterbox Brownie Gift", "Crofter's Bakehouse", "Food & Drink",
        ("Food & Drink", "Hampers & Gifts", "Letterbox Gifts"), 20.0,
        "Twelve brownie squares that fit through the letterbox. A gift by post.",
        drawing("box_wide", cw("Cocoa", "#5a3426"), "Brownies"), (("pieces", "Pieces", "12"),),
    ), _BOOST + "Letterbox Gifts"),
    Distractor(product(
        "GTTEAL", "Letterbox Tea Gift", "Hearth & Table", "Food & Drink",
        ("Food & Drink", "Hampers & Gifts", "Letterbox Gifts"), 16.0,
        "Four loose-leaf teas and a tea strainer in a slim letterbox box.",
        drawing("box_wide", cw("Teal", "#1c7c7d"), "Tea"), (("pieces", "Pieces", "5"),),
    ), _BOOST + "Letterbox Gifts"),
    Distractor(product(
        "GTOLIV", "Olive Tree in Hessian Gift Bag", "Thistle & Wren", "Garden",
        ("Garden", "Plants", "Gift Plants"), 30.0,
        "A young olive tree, about 60 cm tall, potted and wrapped in hessian for giving.",
        drawing("potted_tree", cw("Hessian", "#b89b6e", "solid", "#6b5a3a"), "Olive"),
        (("item_height", "Item height", "60", "CMT"),),
    ), _BOOST + "Gift Plants"),
    Distractor(product(
        "GTKEYR", "Gift Boxed Brass Keyring", "Calderby & Lune", "Gifts",
        ("Gifts", "Gifts for Him", "Keyrings"), 15.0,
        "A solid brass keyring on a leather fob, gift boxed.",
        drawing("keyring", cw("Navy", "#26365c")), (("material", "Material", "Brass"),),
    ), _BOOST + "Keyrings"),
)  # fmt: skip

#: The product a duplicate listing publishes twice, and its second category.
DUPLICATED = "PLT-GBSKIN"
DUPLICATE_PATH = ("Gifts", "Gifts for Her", "Beauty Gifts")

#: The planted rows scored over :func:`corpus`. A new :class:`Row` plugs in here
#: when its products are in that corpus; a row over another catalog (the boots
#: row, :data:`footwear_rows.BOOTS`, over ``footwear_rows.catalog()``) stays in
#: its own module and is added by hand to ``build_preview4._planted()`` and
#: ``_score_table()``. Either way, add its line to the class table in docs/retail-prototype.md.
TABLE = (
    Row("Print, flavour and scent words", "lemon", "fresh lemons",
        lambda d: d["category_path"][:3] == ["Food & Drink", "Fruit & Vegetables", "Fresh Fruit"]
        and "lemon" in tokens(d["title"]),
        "department or persona boost", LEMON),
    Row("Fruit words as prints and colors", "oranges", "fresh oranges",
        lambda d: d["category_path"][:3] == ["Food & Drink", "Fruit & Vegetables", "Fresh Fruit"]
        and "orange" in tokens(d["title"]),
        "department or persona boost", ORANGE_WORD),
    Row("Complements and accessories", "jeans", "a pair of jeans",
        lambda d: d["product_id"].startswith("JEA-"),
        "category intent; product-type demotion", JEANS),
    Row("Bedding types", "duvet", "a duvet",
        lambda d: d["category_path"][-1] == "Duvets",
        "type-exact intent", DUVET),
    Row("Motif words on kids' clothes", "dinosaur", "a dinosaur toy",
        lambda d: d["department"] == ["Toys"],
        "department boost: Toys", DINOSAUR),
    Row("Gift words on gift-packed products", "gift bag", "a gift bag (gift wrap)",
        lambda d: d["category_path"][:2] == list(GIFT_WRAP[:2]),
        "category boost: Gift Wrap", GIFT, GIFT_TAIL),
)  # fmt: skip


#: The intended products that are not part of a variant family or the print range.
INTENDED = (LEMONS, ORANGES, DINOSAUR_TOY)


def distractor_docs() -> list[dict]:
    return [x.doc for row in TABLE for x in row.distractors]


def duplicate_record() -> dict:
    """:data:`DUPLICATED` published a second time under :data:`DUPLICATE_PATH`."""
    first = next(d for d in distractor_docs() if d["product_id"] == DUPLICATED)
    return {**first, "category_path": list(DUPLICATE_PATH)}


def corpus(duplicate_listing: bool = False) -> list[dict]:
    """The catalog the text score is taken over: every variant doc, the intended products
    of :data:`INTENDED`, every distractor, the rest of the print range, the real gift bags
    and the gift-bag tail; with ``duplicate_listing``, one product twice."""
    planted = distractor_docs()
    ids = {d["product_id"] for d in planted}
    out = [*docs(), *INTENDED, *planted, *(d for d in prints.docs() if d["product_id"] not in ids),
           *GIFT_BAGS, *(x.doc for x in GIFT_TAIL)]  # fmt: skip
    return [*out, duplicate_record()] if duplicate_listing else out


def scores(row: Row, catalog: list[dict]) -> tuple[float, list[tuple[str, float]]]:
    """The best intended score for ``row.query``, and each distractor's (product_id, score)."""
    bm = BM25(catalog)
    intended = [d for d in catalog if row.is_intended(d)]
    if not intended:
        raise ValueError(f"{row.query!r}: no intended product in the catalog")
    best = max(bm.score(row.query, d) for d in intended)
    return best, [(x.doc["product_id"], bm.score(row.query, x.doc)) for x in row.distractors]


def check(table: tuple[Row, ...] = TABLE, catalog: list[dict] | None = None) -> None:
    """ValueError naming every distractor that cannot outrank the best intended product."""
    catalog = corpus() if catalog is None else catalog
    problems = []
    for row in table:
        n = len(row.distractors)
        if not MIN_DISTRACTORS <= n <= MAX_DISTRACTORS:
            problems.append(
                f"{row.query!r}: {n} distractors, not {MIN_DISTRACTORS}-{MAX_DISTRACTORS}"
            )
        for x in row.distractors:
            if row.is_intended(x.doc):
                problems.append(f"{row.query!r}: {x.doc['product_id']} is an intended product")
        best, each = scores(row, catalog)
        problems += [
            f"{row.query!r}: {pid} scores {s:.3f}, not above the intended {best:.3f}"
            for pid, s in each
            if s <= best
        ]
    if problems:
        raise ValueError("refused distractors:\n" + "\n".join(problems))


def table_markdown() -> str:
    """The table as the demo script and persona tests read it."""
    out = [
        "| Class | Query → intended | Distractors that outrank without policies | Fixed by |",
        "|---|---|---|---|",
    ]
    for row in TABLE:
        names = "; ".join(
            f"{x.doc['title']} [{x.doc['product_id']}] ({x.fixed_by})" for x in row.distractors
        )
        out.append(f"| {row.cls} | *{row.query}* → {row.intended} | {names} | {row.policy} |")
    return "\n".join(out)


if __name__ == "__main__":
    check()
    cat = corpus()
    for row in TABLE:
        best, each = scores(row, cat)
        print(row.query, f"intended {best:.3f}", [f"{s:.3f}" for _, s in each])
    print(table_markdown())
