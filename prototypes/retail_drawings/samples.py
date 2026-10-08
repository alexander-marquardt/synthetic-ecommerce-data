"""About two dozen sample retail records in the #125 output shape (prototype).

Each record carries the standard top-level fields (``title``, ``brand``,
``department``, ``collections``, ``category_path``, ``price``), the nested
``attributes`` list of ``{key, name, value[, unit_code, value_canonical]}``
and, for clothing and footwear, ``size_uk``, ``size_eu`` and ``size_us``
derived from ONE size chart per type, so the three systems never disagree.

Every brand name is invented. ``drawing`` holds the kit inputs the preview
renders the picture from.
"""

from __future__ import annotations

# --------------------------------------------------------------------------
# Size charts: one row per size, (UK, EU, US)
# --------------------------------------------------------------------------

WOMENS = [
    (str(uk), str(uk + 28), str(uk - 4)) for uk in range(6, 21, 2)
]  # UK 6-20 / EU 34-48 / US 2-16
SHOES = [
    ("3", "36", "5"),
    ("4", "37", "6"),
    ("5", "38", "7"),
    ("6", "39", "8"),
    ("7", "40", "9"),
    ("8", "42", "10"),
]
LETTER = [(s, s, s) for s in ("XS", "S", "M", "L", "XL", "XXL")]
_BAND = {30: 65, 32: 70, 34: 75, 36: 80, 38: 85, 40: 90}
_CUP = {
    "A": ("A", "A"),
    "B": ("B", "B"),
    "C": ("C", "C"),
    "D": ("D", "D"),
    "DD": ("E", "DD"),
    "E": ("F", "DDD"),
}
BRA = [(f"{b}{c}", f"{_BAND[b]}{eu}", f"{b}{us}") for b in _BAND for c, (eu, us) in _CUP.items()]


def sizes(
    chart: list[tuple[str, str, str]], first: str, last: str, only: set[str] | None = None
) -> dict:
    """The UK/EU/US size lists for the UK range ``first``..``last`` of ``chart``."""
    uks = [row[0] for row in chart]
    rows = chart[uks.index(first) : uks.index(last) + 1]
    if only is not None:
        rows = [r for r in rows if r[0] in only]
    return {
        "size_uk": [r[0] for r in rows],
        "size_eu": [r[1] for r in rows],
        "size_us": [r[2] for r in rows],
    }


# --------------------------------------------------------------------------
# Attribute helpers
# --------------------------------------------------------------------------

COLOURS = {
    "Navy": "#26365c",
    "White": "#ffffff",
    "Ecru": "#efe7d4",
    "Olive": "#6b7240",
    "Sky Blue": "#9cc3e6",
    "Leopard": "#d9a95b",
    "Red": "#c8312e",
    "Indigo": "#34466e",
    "Black": "#2a2a2e",
    "Stone": "#cdbb98",
    "Tan": "#b07a45",
    "Blush": "#e8b4b0",
    "Green": "#2f6b3c",
}


def attr(
    key: str, name: str, value, unit_code: str | None = None, canonical: float | None = None
) -> dict:
    a = {"key": key, "name": name, "value": str(value)}
    if unit_code is not None:
        a["unit_code"] = unit_code
        a["value_canonical"] = float(value if canonical is None else canonical)
    return a


def many(key: str, name: str, values: list[str]) -> list[dict]:
    """A multi-valued attribute: one entry per value under the same key."""
    return [attr(key, name, v) for v in values]


def clothing_attrs(colour, pattern, fit, who, fabric, extra=()) -> list[dict]:
    return [
        attr("colour", "Colour", colour),
        attr("pattern", "Pattern", pattern),
        attr("fit", "Fit / Cut", fit),
        attr("who", "Who it's for", who),
        attr("fabric", "Fabric", fabric),
        *extra,
    ]


def food_attrs(size, unit_code, storage, dietary, allergens, flavour, serves=None) -> list[dict]:
    canon = {"GRM": 1, "KGM": 1000, "MLT": 1, "LTR": 1000, "C62": 1}[unit_code] * size
    out = [
        attr("pack_size", "Pack size", f"{size:g}", unit_code, canon),
        attr("storage", "Storage", storage),
        *many("dietary", "Dietary", dietary),
        *many("allergens", "Allergens", allergens),
        attr("flavour", "Flavour", flavour),
    ]
    if serves:
        out.append(attr("serves", "Serves", serves, "C62"))
    return out


def drawing(
    shape, pattern="solid", base="#cccccc", accent="#333333", label=None, third="#f2d14b"
) -> dict:
    return {
        "shape": shape,
        "pattern": pattern,
        "base": base,
        "accent": accent,
        "third": third,
        "label": label,
    }


C = COLOURS

# --------------------------------------------------------------------------
# The records
# --------------------------------------------------------------------------

CLOTHING = [
    {
        "title": "Breton Stripe Cotton T-Shirt",
        "brand": "Harbour & Pine",
        "department": ["clothing"],
        "collections": ["summer", "new"],
        "category_path": ["Women", "Tops", "T-Shirts"],
        "price": 14.00,
        **sizes(WOMENS, "6", "20"),
        "attributes": clothing_attrs("Navy / Ecru", "Stripe", "Regular", "Womens", "100% Cotton"),
        "drawing": drawing("tshirt", "stripe", C["Ecru"], C["Navy"]),
    },
    {
        "title": "Organic Cotton Crew Neck T-Shirt",
        "brand": "Wrenfield",
        "department": ["clothing"],
        "collections": [],
        "category_path": ["Men", "Tops", "T-Shirts"],
        "price": 9.50,
        **sizes(LETTER, "S", "XXL"),
        "attributes": clothing_attrs("Olive", "Plain", "Relaxed", "Mens", "100% Organic Cotton"),
        "drawing": drawing("tshirt", "solid", C["Olive"]),
    },
    {
        "title": "Pinstripe Button-Through Blouse",
        "brand": "Larkmoor",
        "department": ["clothing"],
        "collections": [],
        "category_path": ["Women", "Tops", "Blouses & Shirts"],
        "price": 26.00,
        **sizes(WOMENS, "8", "18"),
        "attributes": clothing_attrs(
            "Sky Blue / White", "Stripe", "Regular", "Womens", "Cotton Poplin"
        ),
        "drawing": drawing("blouse", "stripe", C["White"], C["Sky Blue"]),
    },
    {
        "title": "Leopard Print Tiered Sundress",
        "brand": "Larkmoor",
        "department": ["clothing"],
        "collections": ["summer"],
        "category_path": ["Women", "Dresses", "Sundresses"],
        "price": 35.00,
        **sizes(WOMENS, "6", "20"),
        "attributes": clothing_attrs(
            "Tan / Black",
            "Leopard",
            "Fit and Flare",
            "Womens",
            "Viscose",
            [attr("length", "Length", "Midi")],
        ),
        "drawing": drawing("dress", "leopard", C["Leopard"], C["Black"]),
    },
    {
        "title": "Gingham Paperbag Waist Shorts",
        "brand": "Harbour & Pine",
        "department": ["clothing"],
        "collections": ["summer", "sale"],
        "category_path": ["Women", "Shorts"],
        "price": 16.00,
        **sizes(WOMENS, "6", "18"),
        "attributes": clothing_attrs(
            "Red / White", "Gingham", "High Waist", "Womens", "Cotton Seersucker"
        ),
        "drawing": drawing("shorts", "gingham", C["White"], C["Red"]),
    },
    {
        "title": "Bootcut Stretch Jeans",
        "brand": "Ottery Denim",
        "department": ["clothing"],
        "collections": [],
        "category_path": ["Women", "Jeans", "Bootcut Jeans"],
        "price": 30.00,
        **sizes(WOMENS, "6", "20"),
        "attributes": clothing_attrs(
            "Indigo",
            "Plain",
            "Bootcut",
            "Womens",
            "98% Cotton, 2% Elastane",
            [attr("leg_length", "Leg length", "Regular")],
        ),
        "drawing": drawing("jeans_bootcut", "solid", C["Indigo"]),
    },
    {
        "title": "Straight Leg Jeans",
        "brand": "Ottery Denim",
        "department": ["clothing"],
        "collections": ["new"],
        "category_path": ["Women", "Jeans", "Straight Jeans"],
        "price": 30.00,
        **sizes(WOMENS, "6", "18"),
        "attributes": clothing_attrs(
            "Black",
            "Plain",
            "Straight",
            "Womens",
            "100% Cotton Denim",
            [attr("leg_length", "Leg length", "Long")],
        ),
        "drawing": drawing("jeans_straight", "solid", C["Black"]),
    },
    {
        "title": "Tartan Pleated Mini Skirt",
        "brand": "Thistle & Wren",
        "department": ["clothing"],
        "collections": ["christmas"],
        "category_path": ["Women", "Skirts", "Mini Skirts"],
        "price": 22.00,
        **sizes(WOMENS, "6", "16"),
        "attributes": clothing_attrs("Red / Green", "Tartan", "A-Line", "Womens", "Brushed Twill"),
        "drawing": drawing("skirt", "tartan", C["Red"], C["Green"], third="#f2d14b"),
    },
    {
        "title": "Belted Double-Breasted Trench Coat",
        "brand": "Wrenfield",
        "department": ["clothing"],
        "collections": [],
        "category_path": ["Women", "Coats & Jackets", "Trench Coats"],
        "price": 79.00,
        **sizes(WOMENS, "6", "20"),
        "attributes": clothing_attrs(
            "Stone",
            "Plain",
            "Regular",
            "Womens",
            "Cotton Gabardine",
            [attr("length", "Length", "Knee")],
        ),
        "drawing": drawing("coat", "solid", C["Stone"]),
    },
    {
        "title": "Lace-Up Running Trainers",
        "brand": "Stridewell",
        "department": ["footwear", "clothing"],
        "collections": ["new"],
        "category_path": ["Women", "Shoes", "Trainers"],
        "price": 45.00,
        **sizes(SHOES, "3", "8"),
        "attributes": clothing_attrs(
            "Navy",
            "Plain",
            "Standard Fit",
            "Womens",
            "Mesh Upper",
            [attr("sole", "Sole", "Rubber")],
        ),
        "drawing": drawing("trainer", "solid", C["Navy"]),
    },
    {
        "title": "Cross-Strap Footbed Sandals",
        "brand": "Saltmarsh",
        "department": ["footwear"],
        "collections": ["summer"],
        "category_path": ["Women", "Shoes", "Sandals"],
        "price": 24.00,
        **sizes(SHOES, "3", "8"),
        "attributes": clothing_attrs("Tan", "Plain", "Wide Fit", "Womens", "Leather Upper"),
        "drawing": drawing("sandal", "solid", C["Tan"]),
    },
    {
        "title": "Polka Dot Non-Wired Bra",
        "brand": "Bramblewood",
        "department": ["clothing"],
        "collections": [],
        "category_path": ["Women", "Lingerie", "Bras"],
        "price": 18.00,
        **sizes(
            BRA, "32A", "36E", only={f"{b}{c}" for b in (32, 34, 36) for c in ("B", "C", "D", "DD")}
        ),
        "attributes": clothing_attrs(
            "Blush / Black", "Polka Dot", "Non-Wired", "Womens", "Recycled Polyester, Elastane"
        ),
        "drawing": drawing("bra", "polka", C["Blush"], C["Black"]),
    },
]

FOOD = [
    {
        "title": "Semi-Skimmed Milk 2 Litres",
        "brand": "Meadowgate Dairy",
        "category_path": ["Food", "Dairy", "Milk"],
        "price": 1.65,
        "attributes": food_attrs(2, "LTR", "Chilled", ["Vegetarian"], ["Milk"], "Plain"),
        "drawing": drawing("carton", "solid", "#3f8fd2", label="Milk"),
    },
    {
        "title": "Smooth Spanish Red Wine 75cl",
        "brand": "Vine & Valley",
        "category_path": ["Food", "Drinks", "Wine", "Red Wine"],
        "price": 7.50,
        "attributes": food_attrs(
            750, "MLT", "Cupboard", ["Vegan"], ["Sulphites"], "Cherry & Spice"
        ),
        "drawing": drawing("bottle", "solid", "#5a1f2e", label="Wine"),
    },
    {
        "title": "Extra Virgin Olive Oil 500ml",
        "brand": "Olivar Grove",
        "category_path": ["Food", "Cupboard", "Oils & Vinegars"],
        "price": 5.25,
        "attributes": food_attrs(500, "MLT", "Cupboard", ["Vegan", "Gluten Free"], [], "Fruity"),
        "drawing": drawing("bottle", "solid", "#8a9a2c", label="Oil"),
    },
    {
        "title": "Strawberry Conserve 340g",
        "brand": "Copper Hill Preserves",
        "category_path": ["Food", "Cupboard", "Jams & Spreads"],
        "price": 2.10,
        "attributes": food_attrs(340, "GRM", "Cupboard", ["Vegetarian", "Vegan"], [], "Strawberry"),
        "drawing": drawing("jar", "solid", "#b8242f", "#e6e1d8", label="Jam"),
    },
    {
        "title": "Baked Beans in Tomato Sauce 415g",
        "brand": "Pantry Mill",
        "category_path": ["Food", "Cupboard", "Tinned Food"],
        "price": 0.85,
        "attributes": food_attrs(415, "GRM", "Cupboard", ["Vegan", "Gluten Free"], [], "Tomato", 2),
        "drawing": drawing("tin", "solid", "#2f7fb5", label="Beans"),
    },
    {
        "title": "Honey Oat Crunch Cereal 500g",
        "brand": "Goldfield Farms",
        "category_path": ["Food", "Cupboard", "Cereals"],
        "price": 2.75,
        "attributes": food_attrs(
            500, "GRM", "Cupboard", ["Vegetarian"], ["Oats", "Gluten"], "Honey"
        ),
        "drawing": drawing("box", "solid", "#e7a42b", label="Cereal"),
    },
    {
        "title": "All Butter Shortbread Fingers Gift Tin 300g",
        "brand": "Thistle & Wren",
        "collections": ["christmas", "gifts"],
        "category_path": ["Food", "Biscuits & Sweets", "Biscuits"],
        "price": 6.00,
        "attributes": food_attrs(
            300, "GRM", "Cupboard", ["Vegetarian"], ["Wheat", "Milk"], "Butter"
        ),
        "drawing": drawing(
            "box_wide", "tartan", "#1f4f8a", "#2f6b3c", label="Biscuits", third="#f2d14b"
        ),
    },
    {
        "title": "Sea Salt & Cider Vinegar Crisps 150g",
        "brand": "Crunchworth",
        "category_path": ["Food", "Cupboard", "Crisps & Snacks"],
        "price": 1.90,
        "attributes": food_attrs(150, "GRM", "Cupboard", ["Vegan"], [], "Salt & Vinegar"),
        "drawing": drawing("crisps_bag", "solid", "#3aa3a0", label="Crisps"),
    },
    {
        "title": "Beef Lasagne Ready Meal 400g",
        "brand": "Hearth & Table",
        "category_path": ["Food", "Ready Meals", "Italian"],
        "price": 3.50,
        "attributes": food_attrs(
            400, "GRM", "Chilled", [], ["Wheat", "Milk", "Egg", "Celery"], "Beef & Tomato", 1
        ),
        "drawing": drawing("tray", "solid", "#c9472d", label="Lasagne"),
    },
    {
        "title": "Sweet Strawberries 400g",
        "brand": "Goldfield Farms",
        "collections": ["summer"],
        "category_path": ["Food", "Fresh Produce", "Fruit", "Berries"],
        "price": 2.50,
        "attributes": food_attrs(400, "GRM", "Chilled", ["Vegan", "Gluten Free"], [], "Strawberry"),
        "drawing": drawing("punnet", "solid", "#2f6b3c", label="Strawberries"),
    },
    {
        "title": "Greek Style Natural Yogurt 500g",
        "brand": "Meadowgate Dairy",
        "category_path": ["Food", "Dairy", "Yogurts"],
        "price": 1.45,
        "attributes": food_attrs(
            500, "GRM", "Chilled", ["Vegetarian", "Gluten Free"], ["Milk"], "Natural"
        ),
        "drawing": drawing("tub", "solid", "#e9eef4", label="Yogurt"),
    },
    {
        "title": "Seeded Wholemeal Loaf 800g",
        "brand": "Crofter's Bakehouse",
        "category_path": ["Food", "Bakery", "Bread"],
        "price": 1.40,
        "attributes": food_attrs(
            800, "GRM", "Cupboard", ["Vegan"], ["Wheat", "Gluten", "Sesame"], "Malted Seeds"
        ),
        "drawing": drawing("loaf", "solid", "#b9773d", label="Bread"),
    },
    {
        "title": "Iced Rich Fruit Christmas Cake 900g",
        "brand": "Crofter's Bakehouse",
        "collections": ["christmas", "gifts"],
        "category_path": ["Food", "Bakery", "Cakes", "Celebration Cakes"],
        "price": 12.00,
        "attributes": food_attrs(
            900,
            "GRM",
            "Cupboard",
            ["Vegetarian"],
            ["Wheat", "Egg", "Milk", "Almonds"],
            "Fruit & Brandy",
            16,
        ),
        "drawing": drawing("cake", "solid", "#c8312e", label="Cake"),
    },
    {
        "title": "Easy Peeler Clementines 600g",
        "brand": "Goldfield Farms",
        "collections": ["christmas"],
        "category_path": ["Food", "Fresh Produce", "Fruit", "Citrus"],
        "price": 1.80,
        "attributes": food_attrs(600, "GRM", "Fresh", ["Vegan", "Gluten Free"], [], "Sweet Citrus"),
        "drawing": drawing("round_produce", "solid", "#ef8a1f", label="Clementines"),
    },
]


def records() -> list[dict]:
    """Every sample record, with IDs and the food department filled in."""
    out = []
    for i, rec in enumerate(CLOTHING + FOOD, 1):
        rec = dict(rec)
        rec.setdefault("department", ["food"])
        rec.setdefault("collections", [])
        prefix = "APP" if rec["department"][0] in ("clothing", "footwear") else "FOD"
        rec = {
            "product_id": f"{prefix}-PEEK-{i:04d}",
            "sku": f"{prefix}{i:06d}",
            **rec,
            "currency": "GBP",
        }
        out.append(rec)
    return out
