"""About two dozen sample retail records in the #125 output shape (prototype).

Each record carries the standard top-level fields (``title``, ``brand``,
``department``, ``collections``, ``category_path``, ``price``), the nested
``attributes`` list of ``{key, name, value[, unit_code, value_canonical]}``
and, for clothing and footwear, ``size_uk``, ``size_eu`` and ``size_us``
derived from ONE size chart per type, so the three systems never disagree.

Every brand name is invented. ``drawing`` holds the kit inputs the preview
renders the picture from. Every record names its ``department`` from the
closed list :data:`DEPARTMENTS`; garments carry the structured attributes of
:data:`GARMENT_KEYS` (neckline, sleeve length, rise, leg fit, length, waist,
audience). Round 2's records live in ``samples_round2``.
"""

from __future__ import annotations

from kit_produce import pile_params

#: The closed list a record's ``department`` values come from.
DEPARTMENTS = ("clothing", "footwear", "lingerie", "home", "food", "beauty", "gifts")

#: Structured garment attributes: key -> (display name, closed list of values).
GARMENT_KEYS = {
    "neckline": (
        "Neckline",
        ("Crew", "V-Neck", "Boat Neck", "Scoop", "Square", "Roll Neck", "Collared"),
    ),
    "sleeve_length": ("Sleeve length", ("Sleeveless", "Short", "Three-Quarter", "Long")),
    "rise": ("Rise", ("Low", "Mid", "High")),
    "leg_fit": (
        "Leg fit",
        (
            "Skinny",
            "Slim",
            "Straight",
            "Bootcut",
            "Flared",
            "Wide Leg",
            "Barrel",
            "Balloon",
            "Carrot",
            "Cigarette",
        ),
    ),
    "length": ("Length", ("Petite", "Regular", "Long")),
    "waist": ("Waist", ("Standard", "Elasticated", "Drawstring", "Paperbag")),
    "audience": ("Audience", ("Womens", "Mens", "Girls", "Boys", "Baby")),
}


def garment(**values: str) -> list[dict]:
    """The garment attributes, in :data:`GARMENT_KEYS` order, each from its closed list."""
    out = []
    for key, (name, allowed) in GARMENT_KEYS.items():
        if key in values:
            if values[key] not in allowed:
                raise ValueError(f"{key}={values[key]!r} is not one of {allowed}")
            out.append(attr(key, name, values[key]))
    unknown = set(values) - set(GARMENT_KEYS)
    if unknown:
        raise ValueError(f"unknown garment attributes {sorted(unknown)}")
    return out


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

COLORS = {
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


def clothing_attrs(color, pattern, fit, who, fabric, extra=(), **garment_values) -> list[dict]:
    """Color, pattern, fit and fabric, then the structured garment attributes.

    ``who`` is the audience; ``fit`` may be ``None`` where ``leg_fit`` says it.
    """
    return [
        attr("color", "Color", color),
        attr("pattern", "Pattern", pattern),
        *([attr("fit", "Fit / Cut", fit)] if fit else []),
        attr("fabric", "Fabric", fabric),
        *extra,
        *garment(audience=who, **garment_values),
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
    shape, pattern="solid", base="#cccccc", accent="#333333", label=None, third="#f2d14b", **params
) -> dict:
    out = {
        "shape": shape,
        "pattern": pattern,
        "base": base,
        "accent": accent,
        "third": third,
        "label": label,
    }
    if params:
        out["params"] = params
    return out


C = COLORS

# --------------------------------------------------------------------------
# The records
# --------------------------------------------------------------------------

CLOTHING = [
    {
        "title": "Breton Stripe Cotton T-Shirt",
        "brand": "Harbour & Pine",
        "department": ["clothing"],
        "collections": ["summer", "new"],
        "category_path": ["Womens", "Tops", "T-Shirts"],
        "price": 14.00,
        **sizes(WOMENS, "6", "20"),
        "attributes": clothing_attrs(
            "Navy / Ecru",
            "Stripe",
            "Regular",
            "Womens",
            "100% Cotton",
            neckline="Crew",
            sleeve_length="Short",
        ),
        "drawing": drawing("tshirt", "stripe", C["Ecru"], C["Navy"]),
    },
    {
        "title": "Organic Cotton Crew Neck T-Shirt",
        "brand": "Wrenfield",
        "department": ["clothing"],
        "collections": [],
        "category_path": ["Mens", "Tops", "T-Shirts"],
        "price": 9.50,
        **sizes(LETTER, "S", "XXL"),
        "attributes": clothing_attrs(
            "Olive",
            "Plain",
            "Relaxed",
            "Mens",
            "100% Organic Cotton",
            neckline="Crew",
            sleeve_length="Short",
        ),
        "drawing": drawing("top", "solid", C["Olive"], neckline="crew", sleeve="short"),
    },
    {
        "title": "Pinstripe Button-Through Blouse",
        "brand": "Larkmoor",
        "department": ["clothing"],
        "collections": [],
        "category_path": ["Womens", "Tops", "Blouses & Shirts"],
        "price": 26.00,
        **sizes(WOMENS, "8", "18"),
        "attributes": clothing_attrs(
            "Sky Blue / White",
            "Stripe",
            "Regular",
            "Womens",
            "Cotton Poplin",
            neckline="Collared",
            sleeve_length="Long",
        ),
        "drawing": drawing("blouse", "stripe", C["White"], C["Sky Blue"]),
    },
    {
        "title": "Leopard Print Tiered Sundress",
        "brand": "Larkmoor",
        "department": ["clothing"],
        "collections": ["summer"],
        "category_path": ["Womens", "Dresses", "Sundresses"],
        "price": 35.00,
        **sizes(WOMENS, "6", "20"),
        "attributes": clothing_attrs(
            "Tan / Black",
            "Leopard",
            "Fit and Flare",
            "Womens",
            "Viscose",
            [attr("hem_length", "Hem length", "Midi")],
            neckline="Scoop",
            sleeve_length="Sleeveless",
            length="Regular",
        ),
        "drawing": drawing("dress", "leopard", C["Leopard"], C["Black"]),
    },
    {
        "title": "Gingham Paperbag Waist Shorts",
        "brand": "Harbour & Pine",
        "department": ["clothing"],
        "collections": ["summer", "sale"],
        "category_path": ["Womens", "Shorts"],
        "price": 16.00,
        **sizes(WOMENS, "6", "18"),
        "attributes": clothing_attrs(
            "Red / White",
            "Gingham",
            "Relaxed",
            "Womens",
            "Cotton Seersucker",
            rise="High",
            waist="Paperbag",
        ),
        "drawing": drawing("shorts", "gingham", C["White"], C["Red"]),
    },
    {
        "title": "Bootcut Stretch Jeans",
        "brand": "Ottery Denim",
        "department": ["clothing"],
        "collections": [],
        "category_path": ["Womens", "Jeans", "Bootcut Jeans"],
        "price": 30.00,
        **sizes(WOMENS, "6", "20"),
        "attributes": clothing_attrs(
            "Indigo",
            "Plain",
            None,
            "Womens",
            "98% Cotton, 2% Elastane",
            rise="Mid",
            leg_fit="Bootcut",
            length="Regular",
            waist="Standard",
        ),
        "drawing": drawing("jeans_bootcut", "solid", C["Indigo"], rise="mid"),
    },
    {
        "title": "Straight Leg Jeans",
        "brand": "Ottery Denim",
        "department": ["clothing"],
        "collections": ["new"],
        "category_path": ["Womens", "Jeans", "Straight Jeans"],
        "price": 30.00,
        **sizes(WOMENS, "6", "18"),
        "attributes": clothing_attrs(
            "Black",
            "Plain",
            None,
            "Womens",
            "100% Cotton Denim",
            rise="High",
            leg_fit="Straight",
            length="Long",
            waist="Standard",
        ),
        "drawing": drawing("jeans_straight", "solid", C["Black"], rise="high"),
    },
    {
        "title": "Tartan Pleated Mini Skirt",
        "brand": "Thistle & Wren",
        "department": ["clothing"],
        "collections": ["christmas"],
        "category_path": ["Womens", "Skirts", "Mini Skirts"],
        "price": 22.00,
        **sizes(WOMENS, "6", "16"),
        "attributes": clothing_attrs(
            "Red / Green", "Tartan", "A-Line", "Womens", "Brushed Twill", waist="Standard"
        ),
        "drawing": drawing("skirt", "tartan", C["Red"], C["Green"], third="#f2d14b"),
    },
    {
        "title": "Belted Double-Breasted Trench Coat",
        "brand": "Wrenfield",
        "department": ["clothing"],
        "collections": [],
        "category_path": ["Womens", "Coats & Jackets", "Trench Coats"],
        "price": 79.00,
        **sizes(WOMENS, "6", "20"),
        "attributes": clothing_attrs(
            "Stone",
            "Plain",
            "Regular",
            "Womens",
            "Cotton Gabardine",
            [attr("hem_length", "Hem length", "Knee")],
            sleeve_length="Long",
            length="Regular",
        ),
        "drawing": drawing("coat", "solid", C["Stone"]),
    },
    {
        "title": "Lace-Up Running Trainers",
        "brand": "Stridewell",
        "department": ["footwear"],
        "collections": ["new"],
        "category_path": ["Womens", "Shoes", "Trainers"],
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
        "category_path": ["Womens", "Shoes", "Sandals"],
        "price": 24.00,
        **sizes(SHOES, "3", "8"),
        "attributes": clothing_attrs("Tan", "Plain", "Wide Fit", "Womens", "Leather Upper"),
        "drawing": drawing("sandal", "solid", C["Tan"]),
    },
    {
        "title": "Polka Dot Non-Wired Bra",
        "brand": "Bramblewood",
        "department": ["lingerie"],
        "collections": [],
        "category_path": ["Womens", "Lingerie", "Bras"],
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

CLEMENTINE_GRAMS = 600

FOOD = [
    {
        "title": "Semi-Skimmed Milk 2 Litres",
        "brand": "Meadowgate Dairy",
        "department": ["food"],
        "category_path": ["Food & Drink", "Dairy", "Milk"],
        "price": 1.65,
        "attributes": food_attrs(2, "LTR", "Chilled", ["Vegetarian"], ["Milk"], "Plain"),
        "drawing": drawing("carton", "solid", "#3f8fd2", label="Milk"),
    },
    {
        "title": "Smooth Spanish Red Wine 75cl",
        "brand": "Vine & Valley",
        "department": ["food"],
        "category_path": ["Food & Drink", "Drinks", "Wine", "Red Wine"],
        "price": 7.50,
        "attributes": food_attrs(
            750, "MLT", "Cupboard", ["Vegan"], ["Sulphites"], "Cherry & Spice"
        ),
        "drawing": drawing("bottle", "solid", "#5a1f2e", label="Wine"),
    },
    {
        "title": "Extra Virgin Olive Oil 500ml",
        "brand": "Olivar Grove",
        "department": ["food"],
        "category_path": ["Food & Drink", "Cupboard", "Oils & Vinegars"],
        "price": 5.25,
        "attributes": food_attrs(500, "MLT", "Cupboard", ["Vegan", "Gluten Free"], [], "Fruity"),
        "drawing": drawing("bottle", "solid", "#8a9a2c", label="Oil"),
    },
    {
        "title": "Strawberry Conserve 340g",
        "brand": "Copper Hill Preserves",
        "department": ["food"],
        "category_path": ["Food & Drink", "Cupboard", "Jams & Spreads"],
        "price": 2.10,
        "attributes": food_attrs(340, "GRM", "Cupboard", ["Vegetarian", "Vegan"], [], "Strawberry"),
        "drawing": drawing("jar", "solid", "#b8242f", "#e6e1d8", label="Jam"),
    },
    {
        "title": "Baked Beans in Tomato Sauce 415g",
        "brand": "Pantry Mill",
        "department": ["food"],
        "category_path": ["Food & Drink", "Cupboard", "Tinned Food"],
        "price": 0.85,
        "attributes": food_attrs(415, "GRM", "Cupboard", ["Vegan", "Gluten Free"], [], "Tomato", 2),
        "drawing": drawing("tin", "solid", "#2f7fb5", label="Beans"),
    },
    {
        "title": "Honey Oat Crunch Cereal 500g",
        "brand": "Goldfield Farms",
        "department": ["food"],
        "category_path": ["Food & Drink", "Cupboard", "Cereals"],
        "price": 2.75,
        "attributes": food_attrs(
            500, "GRM", "Cupboard", ["Vegetarian"], ["Oats", "Gluten"], "Honey"
        ),
        "drawing": drawing("box", "solid", "#e7a42b", label="Cereal"),
    },
    {
        "title": "All Butter Shortbread Fingers Gift Tin 300g",
        "brand": "Thistle & Wren",
        "department": ["food", "gifts"],
        "collections": ["christmas", "gifts"],
        "category_path": ["Food & Drink", "Biscuits & Sweets", "Biscuits"],
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
        "department": ["food"],
        "category_path": ["Food & Drink", "Cupboard", "Crisps & Snacks"],
        "price": 1.90,
        "attributes": food_attrs(150, "GRM", "Cupboard", ["Vegan"], [], "Salt & Vinegar"),
        "drawing": drawing("crisps_bag", "solid", "#3aa3a0", label="Crisps"),
    },
    {
        "title": "Beef Lasagne Ready Meal 400g",
        "brand": "Hearth & Table",
        "department": ["food"],
        "category_path": ["Food & Drink", "Ready Meals", "Italian"],
        "price": 3.50,
        "attributes": food_attrs(
            400, "GRM", "Chilled", [], ["Wheat", "Milk", "Egg", "Celery"], "Beef & Tomato", 1
        ),
        "drawing": drawing("tray", "solid", "#c9472d", label="Lasagne"),
    },
    {
        "title": "Sweet Strawberries 400g",
        "brand": "Goldfield Farms",
        "department": ["food"],
        "collections": ["summer"],
        "category_path": ["Food & Drink", "Fresh Produce", "Fruit", "Berries"],
        "price": 2.50,
        "attributes": food_attrs(400, "GRM", "Chilled", ["Vegan", "Gluten Free"], [], "Strawberry"),
        "drawing": drawing("punnet", "solid", "#2f6b3c", label="Strawberries"),
    },
    {
        "title": "Greek Style Natural Yogurt 500g",
        "brand": "Meadowgate Dairy",
        "department": ["food"],
        "category_path": ["Food & Drink", "Dairy", "Yogurts"],
        "price": 1.45,
        "attributes": food_attrs(
            500, "GRM", "Chilled", ["Vegetarian", "Gluten Free"], ["Milk"], "Natural"
        ),
        "drawing": drawing("tub", "solid", "#e9eef4", label="Yogurt"),
    },
    {
        "title": "Seeded Wholemeal Loaf 800g",
        "brand": "Crofter's Bakehouse",
        "department": ["food"],
        "category_path": ["Food & Drink", "Bakery", "Bread"],
        "price": 1.40,
        "attributes": food_attrs(
            800, "GRM", "Cupboard", ["Vegan"], ["Wheat", "Gluten", "Sesame"], "Malted Seeds"
        ),
        "drawing": drawing("loaf", "solid", "#b9773d", label="Bread"),
    },
    {
        "title": "Iced Rich Fruit Christmas Cake 900g",
        "brand": "Crofter's Bakehouse",
        "department": ["food"],
        "collections": ["christmas", "gifts"],
        "category_path": ["Food & Drink", "Bakery", "Cakes", "Celebration Cakes"],
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
        "department": ["food"],
        "collections": ["christmas"],
        "category_path": ["Food & Drink", "Fresh Produce", "Fruit", "Citrus"],
        "price": 1.80,
        "attributes": food_attrs(
            CLEMENTINE_GRAMS, "GRM", "Fresh", ["Vegan", "Gluten Free"], [], "Sweet Citrus"
        ),
        # The fruit count drawn comes from the same pack weight the record states.
        "drawing": drawing("produce_pile", "solid", "#ef8a1f", label="Clementines",
                           **pile_params("clementine", "Easy Peeler Clementines", "net",
                                         grams=CLEMENTINE_GRAMS)),
    },
]


PREFIX = {
    "clothing": "APP",
    "footwear": "APP",
    "lingerie": "APP",
    "food": "FOD",
    "home": "HOM",
    "beauty": "BTY",
    "gifts": "GFT",
}


def records() -> list[dict]:
    """Every sample record (round 1, then round 2), with IDs filled in."""
    from samples_round2 import ROUND2

    out = []
    for i, rec in enumerate(CLOTHING + FOOD + ROUND2, 1):
        rec = dict(rec)
        rec.setdefault("collections", [])
        bad = [d for d in rec["department"] if d not in DEPARTMENTS]
        if bad:
            raise ValueError(f"{rec['title']}: department {bad} is not in {DEPARTMENTS}")
        prefix = PREFIX[rec["department"][0]]
        rec = {
            "product_id": f"{prefix}-PEEK-{i:04d}",
            "sku": f"{prefix}{i:06d}",
            **rec,
            "currency": "GBP",
        }
        out.append(rec)
    return out
