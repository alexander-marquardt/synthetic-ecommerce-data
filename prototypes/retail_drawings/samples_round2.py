"""Round 2 sample records: leg fits, tops, home and beauty (prototype).

Same output shape as :mod:`samples`. Every brand, shade and fragrance name
here is invented. Garments carry the structured attributes of
:data:`samples.GARMENT_KEYS`; home and beauty records carry their own
(bed size, tog, pieces, photo size; shade, finish, volume, scent).
"""

from __future__ import annotations

from samples import LETTER, WOMENS, attr, clothing_attrs, drawing, garment, sizes

# --------------------------------------------------------------------------
# More size charts: one row per size, (UK, EU, US)
# --------------------------------------------------------------------------

MENS_WAIST = [(str(w), str(w + 16), str(w)) for w in range(28, 40, 2)]  # W28-38 / EU 44-54
KIDS = [
    ("3-4Y", "104", "4"),
    ("5-6Y", "116", "6"),
    ("7-8Y", "128", "8"),
    ("9-10Y", "140", "10"),
    ("11-12Y", "152", "12"),
    ("13-14Y", "164", "14"),
]
BABY = [
    ("0-3M", "62", "0-3M"),
    ("3-6M", "68", "3-6M"),
    ("6-12M", "80", "6-12M"),
    ("12-18M", "86", "12-18M"),
    ("18-24M", "92", "18-24M"),
]

INK_BLUE = "#34466e"


def wear(title, brand, path, price, size_rows, attrs, draw, dept=("clothing",), coll=()):
    """One garment record."""
    return {
        "title": title,
        "brand": brand,
        "department": list(dept),
        "collections": list(coll),
        "category_path": path,
        "price": price,
        **size_rows,
        "attributes": attrs,
        "drawing": draw,
    }


def item(title, brand, dept, path, price, attrs, draw, coll=()):
    """One home, beauty or gift record (no apparel sizes)."""
    return {
        "title": title,
        "brand": brand,
        "department": list(dept),
        "collections": list(coll),
        "category_path": path,
        "price": price,
        "attributes": attrs,
        "drawing": draw,
    }


def legs(color, pattern, who, fabric, rise, leg_fit, length="Regular", waist="Standard"):
    return clothing_attrs(
        color, pattern, None, who, fabric, rise=rise, leg_fit=leg_fit, length=length, waist=waist
    )


def tops(color, pattern, fit, who, fabric, neckline, sleeve):
    return clothing_attrs(
        color, pattern, fit, who, fabric, neckline=neckline, sleeve_length=sleeve
    )


def trouser_drawing(
    base, fit, rise, style="jeans", waist="standard", pattern="solid", accent="#333333"
):
    return drawing("trousers", pattern, base, accent, fit=fit, rise=rise, style=style, waist=waist)


def top_drawing(base, neckline, sleeve, kind="tee", pattern="solid", accent="#333333"):
    return drawing("top", pattern, base, accent, neckline=neckline, sleeve=sleeve, kind=kind)


# --------------------------------------------------------------------------
# Jeans and trousers: one record per leg fit, rises low to high
# --------------------------------------------------------------------------

DENIM = "98% Cotton, 2% Elastane"

LEGWEAR = [
    wear(
        "High Rise Skinny Jeans",
        "Ottery Denim",
        ["Womens", "Jeans", "Skinny Jeans"],
        28.00,
        sizes(WOMENS, "6", "18"),
        legs("Indigo", "Plain", "Womens", DENIM, "High", "Skinny", "Petite"),
        trouser_drawing(INK_BLUE, "skinny", "high"),
    ),
    wear(
        "Slim Fit Stretch Jeans",
        "Ferrowick Denim",
        ["Mens", "Jeans", "Slim Jeans"],
        35.00,
        sizes(MENS_WAIST, "30", "38"),
        legs("Black", "Plain", "Mens", DENIM, "Mid", "Slim"),
        trouser_drawing("#2a2a2e", "slim", "mid"),
    ),
    wear(
        "Low Rise Straight Leg Jeans",
        "Ottery Denim",
        ["Womens", "Jeans", "Straight Jeans"],
        30.00,
        sizes(WOMENS, "6", "16"),
        legs("Mid Blue", "Plain", "Womens", "100% Cotton Denim", "Low", "Straight"),
        trouser_drawing("#5f7fae", "straight", "low"),
        coll=("new",),
    ),
    wear(
        "High Rise Flared Jeans",
        "Ottery Denim",
        ["Womens", "Jeans", "Flared Jeans"],
        32.00,
        sizes(WOMENS, "6", "20"),
        legs("Light Blue", "Plain", "Womens", DENIM, "High", "Flared", "Long"),
        trouser_drawing("#86a6cc", "flared", "high"),
    ),
    wear(
        "Barrel Leg Jeans",
        "Ferrowick Denim",
        ["Womens", "Jeans", "Barrel Jeans"],
        36.00,
        sizes(WOMENS, "6", "18"),
        legs("Ecru", "Plain", "Womens", "100% Cotton Denim", "Mid", "Barrel"),
        trouser_drawing("#e6dcc4", "barrel", "mid"),
        coll=("new",),
    ),
    wear(
        "Wide Leg Tailored Trousers",
        "Calderby & Lune",
        ["Womens", "Trousers", "Wide Leg Trousers"],
        39.00,
        sizes(WOMENS, "6", "20"),
        legs("Stone", "Plain", "Womens", "Polyester, Viscose, Elastane", "High", "Wide Leg"),
        trouser_drawing("#cdbb98", "wide_leg", "high", "tailored"),
    ),
    wear(
        "Balloon Leg Trousers with Elasticated Waist",
        "Larkmoor",
        ["Womens", "Trousers", "Balloon Trousers"],
        32.00,
        sizes(WOMENS, "6", "18"),
        legs("Olive", "Plain", "Womens", "Lyocell", "High", "Balloon", waist="Elasticated"),
        trouser_drawing("#6b7240", "balloon", "high", "tailored", "elasticated"),
        coll=("new",),
    ),
    wear(
        "Pleat Front Carrot Leg Trousers",
        "Calderby & Lune",
        ["Womens", "Trousers", "Tapered Trousers"],
        35.00,
        sizes(WOMENS, "6", "18"),
        legs("Navy", "Plain", "Womens", "Wool Blend", "High", "Carrot"),
        trouser_drawing("#26365c", "carrot", "high", "tailored"),
    ),
    wear(
        "Check Cropped Cigarette Trousers",
        "Calderby & Lune",
        ["Womens", "Trousers", "Cigarette Trousers"],
        29.00,
        sizes(WOMENS, "6", "18"),
        legs("Black / Grey", "Check", "Womens", "Polyester, Viscose", "Mid", "Cigarette", "Petite"),
        trouser_drawing(
            "#9aa0a6", "cigarette", "mid", "tailored", pattern="tartan", accent="#2a2a2e"
        ),
    ),
    wear(
        "Straight Leg Cotton Chinos",
        "Wrenfield",
        ["Mens", "Trousers", "Chinos"],
        30.00,
        sizes(MENS_WAIST, "28", "38"),
        legs("Olive", "Plain", "Mens", "98% Cotton, 2% Elastane", "Mid", "Straight", "Long"),
        trouser_drawing("#6b7240", "straight", "mid", "tailored"),
    ),
    wear(
        "Girls Pink Flared Jeans with Adjustable Waist",
        "Little Fernby",
        ["Kids", "Girls", "Jeans"],
        16.00,
        sizes(KIDS, "3-4Y", "13-14Y"),
        legs("Pink", "Plain", "Girls", DENIM, "Mid", "Flared", waist="Elasticated"),
        trouser_drawing("#e7a1b8", "flared", "mid", waist="elasticated"),
    ),
    wear(
        "Boys Slim Fit Jeans",
        "Little Fernby",
        ["Kids", "Boys", "Jeans"],
        15.00,
        sizes(KIDS, "3-4Y", "13-14Y"),
        legs("Indigo", "Plain", "Boys", DENIM, "Mid", "Slim"),
        trouser_drawing(INK_BLUE, "slim", "mid"),
    ),
    wear(
        "Boys Pull-On Carrot Leg Trousers",
        "Little Fernby",
        ["Kids", "Boys", "Trousers"],
        13.00,
        sizes(KIDS, "3-4Y", "11-12Y"),
        legs("Sand", "Plain", "Boys", "100% Cotton Twill", "Mid", "Carrot", waist="Elasticated"),
        trouser_drawing("#d8c39a", "carrot", "mid", "tailored", "elasticated"),
    ),
]

# --------------------------------------------------------------------------
# Tops: every neckline and sleeve length, plus knits
# --------------------------------------------------------------------------

TOPS = [
    wear(
        "V-Neck Long Sleeve T-Shirt",
        "Wrenfield",
        ["Mens", "Tops", "T-Shirts"],
        12.00,
        sizes(LETTER, "S", "XXL"),
        tops("Grey Marl", "Plain", "Regular", "Mens", "100% Cotton", "V-Neck", "Long"),
        top_drawing("#9aa0a6", "v_neck", "long"),
    ),
    wear(
        "Crew Neck Sleeveless Running Vest",
        "Stridewell",
        ["Mens", "Sportswear", "Tops"],
        14.00,
        sizes(LETTER, "S", "XXL"),
        tops("Navy", "Plain", "Regular", "Mens", "Recycled Polyester", "Crew", "Sleeveless"),
        top_drawing("#26365c", "crew", "sleeveless"),
    ),
    wear(
        "Breton Stripe Boat Neck Top",
        "Harbour & Pine",
        ["Womens", "Tops", "Long Sleeve Tops"],
        19.00,
        sizes(WOMENS, "6", "20"),
        tops(
            "White / Red",
            "Stripe",
            "Regular",
            "Womens",
            "100% Cotton",
            "Boat Neck",
            "Three-Quarter",
        ),
        top_drawing("#ffffff", "boat", "three_quarter", pattern="stripe", accent="#c8312e"),
    ),
    wear(
        "Scoop Neck Vest Top",
        "Larkmoor",
        ["Womens", "Tops", "Vests & Camis"],
        8.00,
        sizes(WOMENS, "6", "20"),
        tops("Blush", "Plain", "Slim", "Womens", "Cotton, Elastane", "Scoop", "Sleeveless"),
        top_drawing("#e8b4b0", "scoop", "sleeveless"),
        coll=("summer",),
    ),
    wear(
        "Leopard Print Scoop Neck Top",
        "Larkmoor",
        ["Womens", "Tops", "Long Sleeve Tops"],
        17.00,
        sizes(WOMENS, "6", "18"),
        tops(
            "Tan / Black",
            "Leopard",
            "Regular",
            "Womens",
            "Viscose Jersey",
            "Scoop",
            "Three-Quarter",
        ),
        top_drawing("#d9a95b", "scoop", "three_quarter", pattern="leopard", accent="#2a2a2e"),
    ),
    wear(
        "Polka Dot Square Neck Top",
        "Harbour & Pine",
        ["Womens", "Tops", "Blouses & Shirts"],
        22.00,
        sizes(WOMENS, "6", "18"),
        tops("Black / White", "Polka Dot", "Regular", "Womens", "Crepe", "Square", "Short"),
        top_drawing("#2a2a2e", "square", "short", pattern="polka", accent="#ffffff"),
        coll=("summer", "new"),
    ),
    wear(
        "Boys Striped Crew Neck T-Shirt",
        "Little Fernby",
        ["Kids", "Boys", "T-Shirts"],
        6.00,
        sizes(KIDS, "3-4Y", "13-14Y"),
        tops("Green / White", "Stripe", "Regular", "Boys", "100% Cotton", "Crew", "Short"),
        top_drawing("#ffffff", "crew", "short", pattern="stripe", accent="#2f6b3c"),
    ),
    wear(
        "Ribbed Roll Neck Jumper",
        "Hollinwray Knits",
        ["Womens", "Knitwear", "Jumpers"],
        29.00,
        sizes(WOMENS, "6", "20"),
        tops("Burgundy", "Plain", "Relaxed", "Womens", "Merino Wool Blend", "Roll Neck", "Long"),
        top_drawing("#7a2338", "roll_neck", "long", "jumper"),
        coll=("christmas",),
    ),
    wear(
        "Lambswool Crew Neck Jumper",
        "Hollinwray Knits",
        ["Mens", "Knitwear", "Jumpers"],
        39.00,
        sizes(LETTER, "S", "XXL"),
        tops("Green", "Plain", "Regular", "Mens", "100% Lambswool", "Crew", "Long"),
        top_drawing("#2f6b3c", "crew", "long", "jumper"),
    ),
    wear(
        "Button Through V-Neck Cardigan",
        "Hollinwray Knits",
        ["Womens", "Knitwear", "Cardigans"],
        27.00,
        sizes(WOMENS, "6", "20"),
        tops("Oatmeal", "Plain", "Regular", "Womens", "Cotton Blend", "V-Neck", "Long"),
        top_drawing("#d9ccb0", "v_neck", "long", "cardigan", accent="#8a6f4a"),
    ),
    wear(
        "Girls Polka Dot Crew Neck Cardigan",
        "Little Fernby",
        ["Kids", "Girls", "Cardigans"],
        12.00,
        sizes(KIDS, "3-4Y", "11-12Y"),
        tops("Pink / White", "Polka Dot", "Regular", "Girls", "100% Cotton", "Crew", "Long"),
        top_drawing("#e7a1b8", "crew", "long", "cardigan", "polka", "#ffffff"),
    ),
    wear(
        "Baby Knitted Crew Neck Cardigan",
        "Little Fernby",
        ["Kids", "Baby", "Knitwear"],
        10.00,
        sizes(BABY, "0-3M", "18-24M"),
        tops("Sky Blue", "Plain", "Regular", "Baby", "100% Cotton", "Crew", "Long"),
        top_drawing("#9cc3e6", "crew", "long", "cardigan", accent="#ffffff"),
    ),
]

# --------------------------------------------------------------------------
# Home
# --------------------------------------------------------------------------


def home_attrs(color, pattern, material, *extra) -> list[dict]:
    return [
        attr("color", "Color", color),
        attr("pattern", "Pattern", pattern),
        attr("material", "Material", material),
        *extra,
    ]


BED = attr("bed_size", "Bed size", "Double")

HOME = [
    item(
        "Deep Quilted Memory Foam Mattress Topper",
        "Quillon Sleep",
        ["home"],
        ["Home", "Bedding", "Mattress Toppers"],
        65.00,
        home_attrs(
            "White",
            "Plain",
            "Memory Foam, Polyester Cover",
            BED,
            attr("mattress_depth", "Mattress depth", 5, "CMT", 50.0),
        ),
        drawing("mattress_topper", "solid", "#f4f2ec", depth="5 cm"),
    ),
    item(
        "Waterproof Fitted Mattress Protector",
        "Quillon Sleep",
        ["home"],
        ["Home", "Bedding", "Mattress Protectors"],
        22.00,
        home_attrs(
            "White",
            "Plain",
            "Cotton Terry, Polyurethane Backing",
            BED,
            attr("skirt_depth", "Fits mattress depth up to", 30, "CMT"),
            attr("feature", "Feature", "Waterproof"),
        ),
        drawing("mattress_protector", "solid", "#eef3f6"),
    ),
    item(
        "Gingham Cotton Pillowcase Pair",
        "Brackenmere Home",
        ["home"],
        ["Home", "Bedding", "Pillowcases"],
        12.00,
        home_attrs("Sage / White", "Gingham", "100% Cotton", attr("pieces", "Pieces", 2, "C62")),
        drawing("pillow", "gingham", "#ffffff", "#8fae8b"),
    ),
    item(
        "All Seasons Duvet 13.5 Tog",
        "Quillon Sleep",
        ["home"],
        ["Home", "Bedding", "Duvets"],
        45.00,
        home_attrs("White", "Plain", "Hollowfibre, Cotton Cover", BED, attr("tog", "Tog", "13.5")),
        drawing("duvet", "solid", "#f7f6f1", label="13.5 tog"),
    ),
    item(
        "Egyptian Cotton Bath Towel",
        "Brackenmere Home",
        ["home"],
        ["Home", "Bathroom", "Towels"],
        16.00,
        home_attrs(
            "Teal",
            "Plain",
            "100% Egyptian Cotton",
            attr("towel_size", "Towel size", "Bath Towel"),
            attr("weight", "Weight", 600, "GM2"),
        ),
        drawing("bath_towel", "solid", "#2f8f8a"),
    ),
    item(
        "Striped Fringed Beach Towel",
        "Saltmarsh",
        ["home"],
        ["Home", "Bathroom", "Beach Towels"],
        18.00,
        home_attrs(
            "Yellow / Navy",
            "Stripe",
            "Cotton Velour",
            attr("towel_size", "Towel size", "Beach Towel"),
        ),
        drawing("beach_towel", "stripe", "#f2c84b", "#26365c"),
        coll=("summer",),
    ),
    item(
        "12 Piece Stoneware Dinner Set",
        "Pewley Table",
        ["home"],
        ["Home", "Dining", "Dinner Sets"],
        49.00,
        home_attrs(
            "Speckled Blue",
            "Plain",
            "Stoneware",
            attr("pieces", "Pieces", 12, "C62"),
            attr("contents", "Contents", "4 Plates, 4 Bowls, 4 Mugs"),
        ),
        drawing("dinner_set", "solid", "#5b7fa6"),
    ),
    item(
        "16 Piece Black Handled Cutlery Set",
        "Pewley Table",
        ["home"],
        ["Home", "Dining", "Cutlery"],
        30.00,
        home_attrs(
            "Black / Silver", "Plain", "Stainless Steel", attr("pieces", "Pieces", 16, "C62")
        ),
        drawing("cutlery_set", "solid", "#2a2a2e"),
    ),
    item(
        "Ceramic Gourd Table Lamp",
        "Lanternby",
        ["home"],
        ["Home", "Lighting", "Lamps", "Table Lamps"],
        42.00,
        home_attrs(
            "Ochre / Linen",
            "Plain",
            "Ceramic, Linen Shade",
            attr("item_height", "Item height", 46, "CMT", 460.0),
        ),
        drawing("table_lamp", "solid", "#ece3cf", "#c9873a"),
    ),
    item(
        "Three Seater Velvet Sofa",
        "Brackenmere Home",
        ["home"],
        ["Home", "Furniture", "Sofas"],
        699.00,
        home_attrs(
            "Bottle Green",
            "Plain",
            "Velvet",
            attr("seats", "Seats", 3, "C62"),
            attr("width", "Width", 210, "CMT"),
        ),
        drawing("sofa", "solid", "#2f5b46", "#d9a95b"),
    ),
    item(
        "Oak Photo Frame 5x7",
        "Lanternby",
        ["home", "gifts"],
        ["Home", "Home Accessories", "Photo Frames"],
        10.00,
        home_attrs("Natural Oak", "Plain", "Oak Veneer", attr("photo_size", "Photo size", "5x7")),
        drawing("photo_frame", "solid", "#c49a63", size="5x7"),
    ),
    item(
        "Black Photo Frame 8x10",
        "Lanternby",
        ["home", "gifts"],
        ["Home", "Home Accessories", "Photo Frames"],
        14.00,
        home_attrs("Black", "Plain", "Wood", attr("photo_size", "Photo size", "8x10")),
        drawing("photo_frame", "solid", "#2a2a2e", size="8x10"),
    ),
]

# --------------------------------------------------------------------------
# Beauty and gifts
# --------------------------------------------------------------------------

BEAUTY = [
    item(
        "Quince Eau de Parfum 50ml",
        "Velling Apothecary",
        ["beauty"],
        ["Beauty", "Fragrance", "Womens Fragrance"],
        28.00,
        [
            attr("scent", "Scent", "Quince"),
            attr("scent_family", "Scent family", "Fruity"),
            attr("volume", "Volume", 50, "MLT"),
            *garment(audience="Womens"),
        ],
        drawing("fragrance", "solid", "#e9c46a", "#b08a3e", label="Quince"),
    ),
    item(
        "Damson Eau de Parfum 100ml",
        "Velling Apothecary",
        ["beauty"],
        ["Beauty", "Fragrance", "Unisex Fragrance"],
        42.00,
        [
            attr("scent", "Scent", "Damson"),
            attr("scent_family", "Scent family", "Woody"),
            attr("volume", "Volume", 100, "MLT"),
        ],
        drawing("fragrance", "solid", "#6a3f6e", "#2a2a2e", label="Damson"),
        coll=("christmas",),
    ),
    item(
        "Satin Lipstick in Rosehip",
        "Kestlewood Cosmetics",
        ["beauty"],
        ["Beauty", "Make-Up", "Lips"],
        9.00,
        [attr("shade", "Shade", "Rosehip"), attr("finish", "Finish", "Satin")],
        drawing("lipstick", "solid", "#c2475a", "#2a2a2e"),
    ),
    item(
        "Matte Lipstick in Brick Dust",
        "Kestlewood Cosmetics",
        ["beauty"],
        ["Beauty", "Make-Up", "Lips"],
        9.00,
        [attr("shade", "Shade", "Brick Dust"), attr("finish", "Finish", "Matte")],
        drawing("lipstick", "solid", "#a4442c", "#e8b4b0"),
    ),
    item(
        "Hydrating Day Moisturiser 50ml",
        "Velling Apothecary",
        ["beauty"],
        ["Beauty", "Skincare", "Moisturisers"],
        14.00,
        [
            attr("skin_type", "Skin type", "Dry"),
            attr("volume", "Volume", 50, "MLT"),
            attr("spf", "SPF", "15"),
        ],
        drawing("moisturiser_jar", "solid", "#f2e6da", "#c9a54a", label="Day Cream"),
    ),
    item(
        "Kohl Eyeliner Pencil in Coal",
        "Kestlewood Cosmetics",
        ["beauty"],
        ["Beauty", "Make-Up", "Eyes"],
        6.00,
        [attr("shade", "Shade", "Coal"), attr("finish", "Finish", "Matte")],
        drawing("eyeliner", "solid", "#2a2a2e", "#c9a54a"),
    ),
    item(
        "Pamper Night Bath & Body Gift Set",
        "Velling Apothecary",
        ["beauty", "gifts"],
        ["Gifts", "Gift Sets", "Beauty Gift Sets"],
        25.00,
        [
            attr("scent", "Scent", "Quince"),
            attr("pieces", "Pieces", 4, "C62"),
            attr("contents", "Contents", "Bath Soak, Body Wash, Hand Cream, Candle"),
        ],
        drawing("gift_set", "solid", "#2f5b46", "#d6b56a", label="Gift Set"),
        coll=("christmas", "gifts"),
    ),
]

ROUND2 = LEGWEAR + TOPS + HOME + BEAUTY
