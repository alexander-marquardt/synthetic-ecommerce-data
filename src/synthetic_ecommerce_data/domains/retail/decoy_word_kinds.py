"""The class-8 decoys' true kinds and their one new brand (:mod:`decoy_product_words`)."""

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.breadth_rows import OWNERS
from synthetic_ecommerce_data.domains.retail.class_model import BRAND_OWNER
from synthetic_ecommerce_data.domains.retail.decoy_rows import KINDS as BASE_KINDS
from synthetic_ecommerce_data.domains.retail.decoy_rows import UK, Kind

#: The invented class-7 brand: a color word in the name of a footwear house (not a real shop).
NEW_BRANDS = ("Blue Bull",)
OWNERS.update(dict.fromkeys(NEW_BRANDS, "third_party"))
BRAND_OWNER.update(dict.fromkeys(NEW_BRANDS, "third_party"))

_BR = (("kind", "brogue"), ("material", "leather"), ("closure", "Lace-Up"))
_CARE = ("Mens", "Accessories", "Shoe Care")  # one node, one department: Footwear (gen#448)
_STORE = ("Home", "Storage")
_DIY = ("Home", "DIY & Car")
_SOFT = ("Home", "Soft Furnishings")
_WOMENS = (("audience", "Audience", "Womens"),)

#: Kinds this module adds (a decoy's true type), then the kinds of :mod:`decoy_rows` it reuses.
NEW_KINDS = {
    "brogue": Kind(
        "Footwear",
        ("Mens", "Shoes", "Formal Shoes", "Brogues"),
        "Brogues",
        "shoe",
        "Stridewell",
        54.0,
        params=_BR,
    ),
    "polish": Kind(
        "Footwear",
        (*_CARE, "Shoe Polish"),
        "Shoe Polish",
        "tin",
        "Calderby & Lune",
        4.5,
        colorless=True,
    ),
    "laces": Kind(
        "Footwear", (*_CARE, "Shoe Laces"), "Shoe Laces", "shoe_laces", "Calderby & Lune", 2.5
    ),
    "cover": Kind(
        "Home", (*_SOFT, "Sofa Covers"), "Sofa Covers", "sofa_cover", "Hearth & Table", 34.0
    ),
    "throw": Kind("Home", (*_SOFT, "Throws"), "Throws", "throw", "Hearth & Table", 22.0),
    "carrier": Kind(
        "Home",
        (*_STORE, "Garment Storage"),
        "Garment Bags",
        "garment_bag",
        "Brackenmere Home",
        12.0,
    ),
    "hooks": Kind(
        "Home", (*_STORE, "Wall Hooks"), "Wall Hooks", "hook_rail", "Brackenmere Home", 15.0
    ),
    "stand": Kind(
        "Home",
        (*_STORE, "Hallway Stands"),
        "Hallway Stands",
        "coat_stand",
        "Brackenmere Home",
        38.0,
    ),
    "hangers": Kind(
        "Home", (*_STORE, "Hangers"), "Clothes Hangers", "hangers", "Brackenmere Home", 7.0
    ),
    "hat_box": Kind(
        "Home",
        (*_STORE, "Storage Boxes"),
        "Storage Boxes",
        "storage_box",
        "Brackenmere Home",
        14.0,
        params=(("form", "round"), ("lid", "yes")),
    ),
    "rack": Kind(
        "Home",
        ("Home", "Laundry", "Drying Racks"),
        "Drying Racks",
        "clothes_airer",
        "Brackenmere Home",
        26.0,
    ),
    "valance": Kind(
        "Home", ("Home", "Bedding", "Valances"), "Valances", "sheet", "Quillon Sleep", 18.0
    ),
    "wash_bag": Kind(
        "Home", ("Home", "Laundry", "Wash Bags"), "Wash Bags", "mesh_bag", "Brackenmere Home", 4.0
    ),
    "knit_care": Kind(
        "Cleaning & Janitorial",
        ("Cleaning", "Laundry", "Fabric Softener"),
        "Fabric Softener",
        "tin",
        "Calderby & Lune",
        4.0,
    ),
    "case": Kind(
        "Clothing",
        ("Womens", "Accessories", "Travel", "Travel Cases"),
        "Travel Cases",
        "pouch",
        "Hearth & Table",
        9.0,
        extra=_WOMENS,
    ),
    "waist": Kind(
        "Clothing",
        ("Womens", "Accessories", "Bags", "Waist Bags"),
        "Waist Bags",
        "pouch",
        "Larkmoor",
        19.0,
        extra=_WOMENS,
    ),
    "clip": Kind(
        "Clothing",
        ("Womens", "Accessories", "Keyrings", "Key Clips"),
        "Key Clips",
        "keyring",
        "Larkmoor",
        6.0,
        extra=_WOMENS,
    ),
    "beaker": Kind(
        "Home",
        ("Kids", "Baby", "Feeding", "Beakers"),
        "Baby Beakers",
        "mug",
        "Little Fernby",
        4.0,
        "kids",
    ),
    "parfum": Kind(
        "Beauty",
        ("Beauty", "Fragrance", "Eau de Parfum"),
        "Eau de Parfum",
        "fragrance",
        "Velling Apothecary",
        38.0,
    ),
    "ties": Kind(
        "Home",
        (*_DIY, "Cable Ties"),
        "Cable Ties",
        "cable_ties",
        "Brackenmere Home",
        3.5,
        units_per_pack=100,
    ),
    "jumper": Kind(
        "Home", (*_DIY, "Jump Leads"), "Jump Leads", "jumper_cables", "Brackenmere Home", 16.0
    ),
    "paint": Kind(
        "Home", (*_DIY, "Paint"), "Paint", "tin", "Brackenmere Home", 14.0, colorless=True
    ),
    "bike_pump": Kind(
        "Sports & Outdoors",
        ("Sports & Outdoors", "Cycling", "Bike Pumps"),
        "Bike Pump",
        "pump",
        "Stridewell",
        12.0,
    ),
    "foot_pump": Kind(
        "Home", (*_DIY, "Foot Pumps"), "Foot Pumps", "pump", "Brackenmere Home", 10.0
    ),
    "pasta": Kind(
        "Food & Drink",
        ("Food & Drink", "Food Cupboard", "Pasta"),
        "Pasta",
        "box",
        "Pantry Mill",
        1.8,
        colorless=True,
    ),
    "potatoes": Kind(
        "Food & Drink",
        ("Food & Drink", "Fruit & Vegetables", "Potatoes"),
        "Potatoes",
        "tray",
        "Pantry Mill",
        2.2,
        params=(("label", "Potatoes"),),
        colorless=True,
    ),
    "crisps": Kind(
        "Food & Drink",
        ("Food & Drink", "Biscuits & Snacks", "Crisps"),
        "Crisps",
        "crisps_bag",
        "Copper Hill Preserves",
        1.2,
        colorless=True,
    ),
    "bb_trainer": Kind(
        "Footwear",
        ("Mens", "Shoes", "Trainers"),
        "Trainers",
        "shoe",
        "Blue Bull",
        42.0,
        params=(("kind", "trainer"), ("material", "canvas"), ("closure", "Lace-Up")),
    ),
    "bb_chelsea": Kind(
        "Footwear",
        ("Mens", "Shoes", "Boots", "Chelsea Boots"),
        "Chelsea Boots",
        "shoe",
        "Blue Bull",
        66.0,
        params=(("kind", "chelsea"), ("material", "leather"), ("closure", "Elastic Gusset")),
    ),
    "bb_court": Kind(
        "Footwear",
        ("Womens", "Shoes", "Heels", "Court Shoes"),
        "Court Shoes",
        "shoe",
        "Blue Bull",
        48.0,
        params=(("kind", "court"), ("material", "patent"), ("closure", "Slip-On")),
    ),
}
# -- the Sports & Outdoors decoys (gen#368): products of other departments, each an existing type
_UKW = {"sizes": UK, "size_range": "regular"}
_FOOT = "Footwear"
_SPORTS_KINDS = {
    "s_blockheel": Kind(_FOOT, ("Womens", "Shoes", "Heels", "Block Heels"), "Block Heels", "shoe",
                        "Wrenfield", 39.0, params=(("kind", "block_heel"), ("material", "suede"),
                                                   ("closure", "Ankle Strap"))),
    "s_sandal": Kind(_FOOT, ("Womens", "Shoes", "Sandals"), "Sandals", "shoe", "Wrenfield", 32.0,
                     params=(("kind", "sandal"), ("material", "leather"), ("closure", "Buckle"))),
    "s_ballet": Kind(_FOOT, ("Womens", "Shoes", "Flats", "Ballet Pumps"), "Ballet Pumps", "shoe",
                     "Wrenfield", 29.0, params=(("kind", "ballet"), ("material", "leather"),
                                                ("closure", "Slip-On"))),
    "s_loafer": Kind(_FOOT, ("Womens", "Shoes", "Formal Shoes", "Loafers"), "Loafers", "shoe",
                     "Larkmoor", 49.0,
                     params=(("kind", "loafer"), ("material", "leather"), ("closure", "Slip-On"))),
    "s_blocks": Kind("Toys", ("Toys", "Building & Construction", "Building Sets"), "Building Set",
                     "building_set", "Little Fernby", 15.0, "kids"),
    "s_scooter2": Kind("Toys", ("Toys", "Outdoor Toys", "Ride-On Toys"), "Ride-On Toy", "ride_on",
                       "Little Fernby", 35.0, "kids", (("kind", "scooter"), ("wheels", "2"))),
    "s_scooter3": Kind("Toys", ("Toys", "Outdoor Toys", "Ride-On Toys"), "Ride-On Toy", "ride_on",
                       "Little Fernby", 30.0, "kids", (("kind", "scooter"), ("wheels", "3"))),
    "s_watch": Kind("Clothing", ("Womens", "Watches", "Bracelet Watches"), "Watch", "watch",
                    "Calderby & Lune", 69.0, params=(("strap", "mesh"),)),
    "s_blouse": Kind("Clothing", ("Womens", "Shirts & Blouses", "Blouses"), "Blouse", "blouse",
                     "Calderby & Lune", 41.0, **_UKW),
    "s_dress": Kind("Clothing", ("Womens", "Dresses", "Wrap Dresses"), "Dress", "dress",
                    "Larkmoor", 28.0, **_UKW),
    "s_jumper": Kind("Clothing", ("Womens", "Knitwear", "Jumpers"), "Jumper", "top",
                     "Harbour & Pine", 45.0, **_UKW,
                     params=(("neckline", "crew"), ("sleeve", "long"), ("kind", "jumper"))),
    "s_bomber": Kind("Clothing", ("Womens", "Coats & Jackets", "Bomber Jackets"), "Bomber Jacket",
                     "bomber_jacket", "Calderby & Lune", 69.0, **_UKW),
    "s_tee": Kind("Clothing", ("Womens", "Tops", "T-Shirts"), "Tee", "tshirt", "Larkmoor", 14.0,
                  **_UKW),
    "s_tote": Kind("Clothing", ("Womens", "Accessories", "Bags", "Tote Bags"), "Tote Bag",
                   "tote_bag", "Larkmoor", 9.0, params=(("gusset", "wide"), ("pocket", "no")),
                   extra=_WOMENS),
    "s_rucksack": Kind("Clothing", ("Womens", "Accessories", "Bags", "Backpacks"), "Backpack",
                       "backpack", "Larkmoor", 22.0,
                       params=(("use", "rucksack"), ("pockets", "1")), extra=_WOMENS),
    "s_cuff": Kind("Clothing", ("Womens", "Jewellery", "Bracelets"), "Bracelet", "bracelet",
                   "Larkmoor",
                   14.0, params=(("kind", "cuff"),)),
    "s_tennisbr": Kind("Clothing", ("Womens", "Jewellery", "Bracelets"), "Bracelet", "bracelet",
                       "Wrenfield", 12.0,
                       params=(("kind", "chain"), ("stone", "clear crystal"))),
    "s_candle": Kind("Gifts", ("Gifts", "Home Fragrance", "Scented Candles"), "Scented Candle",
                     "jar", "Lanternby", 18.0, extra=(("scent", "Scent", "Vanilla"),)),
    "s_wrap": Kind("Gifts", ("Gifts", "Gift Wrap", "Wrapping Paper"), "Wrapping Paper",
                   "wrapping_paper", "Lanternby", 4.0),
    # A boxed mix is a food box, never the celebration cake the "cake" shape draws (gen#449).
    "cake_mix": Kind("Food & Drink", ("Food & Drink", "Bakery", "Cakes"), "Cake", "box",
                     "Crofter's Bakehouse", 4.5, colorless=True),
    "s_handwash": Kind("Beauty", ("Beauty", "Bath & Body", "Hand Wash"), "Hand Wash", "bottle",
                       "Velling Apothecary", 5.0, params=(("label", "Hand Wash"),), colorless=True),
    "s_organizer": Kind("Home", ("Home", "Storage", "Car Boot Organisers"), "Car Boot Organiser",
                        "box_wide", "Brackenmere Home", 18.0),
    "s_duvet_set": Kind("Home", ("Home", "Bedding", "Bedding Sets"), "Duvet Set", "duvet",
                        "Brackenmere Home", 32.0),
    "s_duvet": Kind("Home", ("Home", "Bedding", "Duvets"), "Duvet", "duvet", "Quillon Sleep", 35.0),
    # a bath towel leaf, not the Beach Towels breadth leaf (test_retail_breadth_34): the swim
    # towel is a decoy of the existing Towel type, as the face cloth is
    "s_towel": Kind("Home", ("Home", "Bathroom", "Bath Towels"), "Towel", "bath_towel",
                    "Calderby & Lune", 14.0),
}
NEW_KINDS.update(_SPORTS_KINDS)
# -- the clothing and shoe seed-phrase decoys (gen#460): two kinds the build lacks, the rest reused
_SEED_KINDS = {
    "seed_belt": Kind("Clothing", ("Womens", "Accessories", "Belts"), "Belt", "belt", "Larkmoor",
                      14.0, extra=(*_WOMENS, ("material", "Material", "Leather"))),
    "seed_jeggings": Kind("Clothing", ("Womens", "Leggings"), "Leggings", "leggings", "Larkmoor",
                          16.0, sizes=UK, size_range="regular",
                          params=(("length", "full"), ("rise", "high"))),
}

#: The kinds of the seed decoys (gen#461): another type's product whose name holds a seed phrase.
_KIDS_AUD = "kids"
_SEED_KINDS_461 = {
    "makeup_bag": Kind("Beauty", ("Beauty", "Accessories", "Make-Up Bags"), "Make-Up Bag", "pouch",
                       "Kestlewood Cosmetics", 7.0),
    "house_plant": Kind("Garden", ("Garden", "Plants", "House Plants"), "Plant", "potted_tree",
                        "Thistle & Wren", 9.0, colorless=True),
    "basket": Kind("Home", ("Home", "Storage", "Storage Baskets"), "Storage Basket", "storage_box",
                   "Lanternby", 16.0),
    "ld_candle": Kind("Gifts", ("Gifts", "Home Fragrance", "Scented Candles"), "Scented Candle",
                      "jar", "Lanternby", 16.0, extra=(("scent", "Scent", "Lemon"),)),
    "olive_candle": Kind("Gifts", ("Gifts", "Home Fragrance", "Scented Candles"), "Scented Candle",
                         "jar", "Lanternby", 16.0,
                         extra=(("scent", "Scent", "Olive Leaf"),)),
    "dino_soft": Kind("Toys", ("Toys", "Soft Toys", "Cuddly Animals"), "Soft Toy", "dinosaur",
                      "Little Fernby", 14.0, _KIDS_AUD),
    "dino_bath": Kind("Toys", ("Toys", "Baby & Toddler", "Bath Toys"), "Bath Toy", "dinosaur",
                      "Little Fernby", 5.0, _KIDS_AUD),
    "dino_light": Kind("Toys", ("Toys", "Nursery", "Night Lights"), "Night Light", "dinosaur",
                       "Little Fernby", 14.0, _KIDS_AUD),
}  # fmt: skip
NEW_KINDS.update(_SEED_KINDS_461)
NEW_KINDS.update(_SEED_KINDS)
for _key in NEW_KINDS:
    if _key in BASE_KINDS:
        raise ValueError(
            f"kind {_key!r} is in decoy_rows.KINDS (or a feature_decoys module) and in "
            "decoy_product_words.NEW_KINDS: one key, two meanings"
        )
KINDS = {**BASE_KINDS, **NEW_KINDS}
