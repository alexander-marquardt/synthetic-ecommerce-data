"""Text-match decoys: products whose words match a demo query and whose fields do not (gen#294).

"red sofa", "red shirt" and "red bra" give good results with no interpretation when every word
of the query is on the right products and on nothing else. A real catalogue also holds products
whose words match while the product does not, and no text tuning separates them, because the
words are really there. The color, category and audience policies separate them, because they
read the structured fields. Each row of :data:`TABLE` is one such decoy, with its class and the
query it targets, so the proof (``tests/test_retail_text_match_decoys_294.py``) and the docs table
(``docs/retail-catalog-batch-1.md``) are generated from this table, never kept by hand.

The classes (the numbers follow the issue):

1. **part**: the color word names a part (a trim, a sole, a collar), not the product.
2. **type**: the type word names an accessory or a sibling product ("Red Sofa Cushion").
3. **audience**: the audience word names a sibling version ("a smaller version of our men's
   puffer"), or an adult product shares the title of the boys' one.
4. **sense**: a color word that is also a product, a material or a shade (cream, gold, wine).
5. **guard**: no decoy; a real product whose name holds a color word ("green tea"), so a color
   filter that wrongly fires shows as an empty or wrong page.

Every decoy's structured fields tell the truth: its color, category path and audience are its
own, and only the title and description carry the misleading word. Titles are short and the
sales and reviews above typical, so the plain text score and the popularity boost put them in the
top 10. Names and codes are invented. :data:`IDS` is the set of product ids that
:func:`scale.derivable` leaves out and :mod:`main_colors` leaves out of its color completion (a
completion would give a decoy the query's color).
"""

from __future__ import annotations

from dataclasses import dataclass

from class_model import Style, one
from variants import cw

RED, BLUE, BLACK, WHITE, GREY = ("#c8322b", "#2f6db5", "#2a2a2e", "#ffffff", "#8a8a8e")
NAVY, CREAM, GOLD, GREEN, BROWN, PINK, NUDE = ("#26365c", "#efe8d8", "#c9a34a", "#3c8d4f",
                                               "#6b4a2e", "#e8b9b3", "#e3c1a5")  # fmt: skip
COLORS = {"Red": RED, "Blue": BLUE, "Black": BLACK, "White": WHITE, "Grey": GREY, "Navy": NAVY,
          "Cream": CREAM, "Gold": GOLD, "Green": GREEN, "Brown": BROWN, "Pink": PINK,
          "Nude": NUDE}  # fmt: skip


@dataclass(frozen=True)
class Kind:
    """What a product type needs to be a :class:`Style`: its place, shape and defaults."""

    department: str
    path: tuple[str, ...]
    product_type: str
    shape: str
    brand: str
    price: float
    audience: str = "adult"
    params: tuple[tuple[str, str], ...] = ()
    extra: tuple[tuple[str, str, str], ...] = ()
    sizes: tuple[str, ...] = ()
    size_range: str | None = None
    colorless: bool = False
    units_per_pack: int | None = None
    pattern: str | None = None


_SOFAS = ("Home", "Furniture", "Sofas")
UK = ("6", "8", "10", "12", "14", "16")
KINDS = {
    "sofa": Kind("Home", _SOFAS, "Sofa", "sofa_seats", "Brackenmere Home", 549.0,
                 params=(("seats", "3"), ("arms", "rolled"), ("legs", "walnut")),
                 extra=(("material", "Material", "Velvet"),)),
    "corner": Kind("Home", (*_SOFAS, "Corner Sofas"), "Corner Sofa", "corner_sofa",
                   "Brackenmere Home", 899.0, extra=(("material", "Material", "Velvet"),),
                   params=(("seats", "3"), ("side", "left"), ("arms", "track"),
                           ("legs", "black_metal"))),
    "cushion": Kind("Home", ("Home", "Soft Furnishings", "Cushions"), "Cushion", "cushion",
                    "Hearth & Table", 12.0, extra=(("fabric", "Fabric", "Velvet"),)),
    "doll": Kind("Toys", ("Toys", "Dolls & Accessories", "Dolls"), "Doll", "doll",
                 "Little Fernby", 14.0, "kids", (("kind", "fashion"), ("accessories", "4")),
                 extra=(("toy_type", "Toy type", "Fashion Doll"),)),
    "bra": Kind("Lingerie & Nightwear", ("Womens", "Lingerie", "Bras", "T-Shirt Bras"), "Bra",
                "bra", "Saltmarsh", 18.0, audience="adult"),
    "shirt": Kind("Clothing", ("Womens", "Tops", "Shirts", "Oxford Shirts"), "Shirt", "blouse",
                  "Wrenfield", 26.0, sizes=UK, size_range="regular"),
    "shirt_dress": Kind("Clothing", ("Womens", "Dresses", "Shirt Dresses"), "Dress", "dress",
                        "Harbour & Pine", 28.0, sizes=UK, size_range="regular"),
    "hanger": Kind("Home", ("Home", "Storage", "Hangers"), "Hanger", "hanger",
                   "Brackenmere Home", 7.0, extra=(("pack_size", "Pack size", "10 pack"),)),
    "trainers": Kind("Footwear", ("Mens", "Shoes", "Trainers"), "Trainers", "shoe", "Stridewell",
                     38.0, params=(("kind", "trainer"), ("material", "canvas"),
                                   ("closure", "Lace-Up"))),
    "shoe_care": Kind("Footwear", ("Mens", "Shoes", "Shoe Care"), "Shoe Care Kit", "tin",
                      "Calderby & Lune", 9.0),
    "puffer_m": Kind("Clothing", ("Mens", "Coats & Jackets", "Puffer Jackets"), "Puffer Jacket",
                     "coat", "Stridewell", 70.0, sizes=("S", "M", "L", "XL"),
                     size_range="regular"),
    "puffer_w": Kind("Clothing", ("Womens", "Coats & Jackets", "Puffer Jackets"), "Puffer Jacket",
                     "coat", "Larkmoor", 62.0, sizes=UK, size_range="regular"),
    "puffer_k": Kind("Clothing", ("Kids", "Boys", "Coats & Jackets"), "Puffer Jacket", "coat",
                     "Little Fernby", 32.0, "kids", sizes=("2-3 Yrs", "4-5 Yrs", "6-7 Yrs"),
                     size_range="regular"),
    "socks_m": Kind("Clothing", ("Mens", "Socks", "Ankle Socks"), "Socks", "socks",
                    "Harbour & Pine", 9.0, params=(("pairs", "5"),), units_per_pack=5),
    "socks_w": Kind("Clothing", ("Womens", "Socks", "Boot Socks"), "Boot Socks", "boot_sock",
                    "Hollinwray Knits", 8.0),
    "socks_k": Kind("Clothing", ("Kids", "Boys", "Socks"), "Socks", "socks", "Little Fernby",
                    6.0, "kids", (("pairs", "5"),), units_per_pack=5),
    "face_cream": Kind("Beauty", ("Beauty", "Skincare", "Creams", "Face Creams"), "Face Cream",
                       "moisturiser_jar", "Velling Apothecary", 18.0),
    "face_cloth": Kind("Home", ("Home", "Bathroom", "Bath Towels"), "Towel", "bath_towel",
                       "Hearth & Table", 6.0),
    "top": Kind("Clothing", ("Womens", "Tops", "Jersey Tops"), "Top", "top", "Larkmoor", 20.0,
                sizes=UK, size_range="regular"),
    "handbag": Kind("Clothing", ("Womens", "Accessories", "Bags", "Handbags"), "Handbag", "handbag",
                    "Larkmoor", 34.0, params=(("style", "shoulder"), ("flap", "flap"),
                                                ("strap", "leather")),
                    extra=(("audience", "Audience", "Womens"),)),
    "glassware": Kind("Home", ("Home", "Kitchen & Dining", "Glassware"), "Glassware", "bottle",
                      "Lanternby", 14.0),
    "candle": Kind("Gifts", ("Gifts", "Home Fragrance", "Scented Candles"), "Scented Candle",
                   "jar", "Lanternby", 16.0, extra=(("fragrance", "Fragrance", "Wine"),)),
    "cleaner": Kind("Cleaning & Janitorial",
                    ("Cleaning", "Kitchen & Surfaces", "Cleaners", "Glass Cleaners"),
                    "Glass Cleaner", "bottle", "Calderby & Lune", 4.0),
    "tea": Kind("Food & Drink", ("Food & Drink", "Drinks", "Tea"), "Tea", "box",
                "Pantry Mill", 3.2, colorless=True),
    "spice": Kind("Food & Drink", ("Food & Drink", "Food Cupboard", "Herbs & Spices"),
                  "Seasoning", "jar", "Copper Hill Preserves", 2.4, colorless=True),
    "cake": Kind("Food & Drink", ("Food & Drink", "Bakery", "Cakes"), "Cake", "cake",
                 "Crofter's Bakehouse", 4.5, colorless=True),
    "apples": Kind("Food & Drink", ("Food & Drink", "Fruit & Vegetables", "Fresh Fruit",
                                    "Apples & Pears", "Apples"), "Fruit", "produce_pile",
                   "Pantry Mill", 2.2, params=(("fruit", "apple"),), colorless=True,
                   units_per_pack=4),
    "yoghurt": Kind("Food & Drink", ("Food & Drink", "Dairy & Alternatives", "Yogurt"), "Yogurt",
                    "tub", "Pantry Mill", 2.0, colorless=True),
    "cereal_bar": Kind("Food & Drink", ("Food & Drink", "Biscuits & Snacks", "Snack Bars"),
                       "Snack Bar", "box", "Copper Hill Preserves", 2.6, colorless=True),
    "curry": Kind("Food & Drink", ("Food & Drink", "Chilled", "Ready Meals"), "Ready Meal",
                  "tray", "Crofter's Bakehouse", 4.0, colorless=True),
    "fish": Kind("Food & Drink", ("Food & Drink", "Meat & Fish", "Fish"), "Fish", "tray",
                 "Crofter's Bakehouse", 5.0, colorless=True),
    "biscuit": Kind("Food & Drink", ("Food & Drink", "Biscuits & Snacks", "Biscuits"), "Biscuit",
                    "box", "Pantry Mill", 2.4, colorless=True),
    "sauce": Kind("Food & Drink", ("Food & Drink", "Food Cupboard", "Sauces & Condiments"),
                  "Sauce", "bottle", "Copper Hill Preserves", 2.1, colorless=True),
    "lav_candle": Kind("Gifts", ("Gifts", "Home Fragrance", "Scented Candles"), "Scented Candle",
                       "jar", "Lanternby", 16.0, extra=(("fragrance", "Fragrance", "Lavender"),)),
    "lotion": Kind("Beauty", ("Beauty", "Body Care", "Body Lotion"), "Body Lotion", "bottle",
                   "Velling Apothecary", 8.0, colorless=True),
    "bath_salts": Kind("Beauty", ("Beauty", "Bath & Body", "Bath Salts"), "Bath Salts", "jar",
                       "Velling Apothecary", 6.0, colorless=True),
    "surface_spray": Kind("Cleaning & Janitorial",
                          ("Cleaning", "Kitchen & Surfaces", "Cleaners", "Surface Sprays"),
                          "Surface Spray", "bottle", "Calderby & Lune", 3.0, colorless=True),
}


@dataclass(frozen=True)
class Decoy:
    code: str
    kind: str
    title: str
    description: str
    color: str
    cls: int
    query: str
    sold: int = 500
    brand: str | None = None
    #: A true hit or a guard product, not a decoy (class 0).
    true_hit: bool = False
    #: Class 7: the label list, where the query word appears and the title does not name it.
    ingredients: tuple[str, ...] = ()

    def style(self) -> Style:
        k = KINDS[self.kind]
        color = cw(self.color, COLORS.get(self.color, GREY))
        # A review count above the typical (a digest of the code gives a few hundred).
        return Style(
            f"D{self.code}", self.title, self.brand or k.brand, k.department, k.path, k.price,
            self.description, k.product_type, k.shape, one(color, self.sold), audience=k.audience,
            params=k.params, extra=k.extra, sizes=k.sizes, size_range=k.size_range,
            colorless=k.colorless, units_per_pack=k.units_per_pack, pattern=k.pattern,
            reviews=900 + self.sold,
        )


def _d(code, kind, title, desc, color, cls, query, sold=500, **kw) -> Decoy:
    return Decoy(code, kind, title, desc, color, cls, query, sold, **kw)


TABLE = (
    # -- red sofa / blue sofa: the color names a trim (1), the type names a part or a toy (2)
    _d("XS01", "sofa", "Blue 3 Seater Sofa with Red Piping",
       "A blue velvet sofa finished with red piping along the seams.", "Blue", 1, "red sofa", 720),
    _d("XS02", "sofa", "Grey Sofa with Red Scatter Cushions",
       "A grey sofa sold with two red scatter cushions.", "Grey", 1, "red sofa", 680),
    _d("XS03", "corner", "Navy Corner Sofa, Contrast Red Stitching",
       "A navy corner sofa with contrast red stitching.", "Navy", 1, "red sofa", 640),
    _d("XS04", "sofa", "Grey Sofa with Red Legs",
       "A grey sofa on red lacquered legs.", "Grey", 1, "red sofa", 600),
    _d("XS05", "cushion", "Red Sofa Cushion",
       "A red velvet cushion made to sit on a sofa.", "Red", 2, "red sofa", 760),
    _d("XS06", "cushion", "Red Sofa Cushion Cover, Set of 2",
       "Two red covers for sofa cushions.", "Red", 2, "red sofa", 700),
    _d("XS07", "doll", "Dolls House Red Sofa",
       "A red sofa for a dolls house, for ages 3 and up.", "Red", 2, "red sofa", 660),
    _d("XS11", "sofa", "Red 3 Seater Sofa with Blue Piping",
       "A red velvet sofa finished with blue piping along the seams.", "Red", 1, "blue sofa", 720),
    _d("XS12", "sofa", "Cream Sofa with Blue Scatter Cushions",
       "A cream sofa sold with two blue scatter cushions.", "Cream", 1, "blue sofa", 680),
    _d("XS13", "corner", "Grey Corner Sofa, Contrast Blue Stitching",
       "A grey corner sofa with contrast blue stitching.", "Grey", 1, "blue sofa", 640),
    _d("XS14", "cushion", "Blue Sofa Cushion",
       "A blue velvet cushion made to sit on a sofa.", "Blue", 2, "blue sofa", 760),
    _d("XS15", "doll", "Dolls House Blue Sofa",
       "A blue sofa for a dolls house, for ages 3 and up.", "Blue", 2, "blue sofa", 660),
    # -- red bra, blue shirt, black trainers
    _d("XB01", "bra", "Black Bra with Red Lace Trim",
       "A black t-shirt bra edged with red lace trim.", "Black", 1, "red bra", 700),
    _d("XB02", "bra", "White Bra with Red Bow",
       "A white t-shirt bra with a small red bow.", "White", 1, "red bra", 660),
    _d("XB03", "bra", "Pink Bra with Red Straps",
       "A pink t-shirt bra with red straps.", "Pink", 1, "red bra", 640),
    _d("XB04", "bra", "Navy Bra with Red Stitching",
       "A navy t-shirt bra with red stitching.", "Navy", 1, "red bra", 620),
    _d("XH01", "shirt", "White Shirt with Blue Collar and Cuffs",
       "A white cotton shirt with a blue collar and blue cuffs.", "White", 1, "blue shirt", 820),
    _d("XH02", "shirt", "Black Shirt with Blue Buttons",
       "A black shirt with blue buttons.", "Black", 1, "blue shirt", 760),
    _d("XH03", "shirt", "Grey Shirt with Blue Check Pocket",
       "A grey shirt with a blue pocket.", "Grey", 1, "blue shirt", 700),
    _d("XH04", "hanger", "Blue Shirt Hangers, Pack of 10",
       "Ten blue hangers shaped for a shirt.", "Blue", 2, "blue shirt", 840),
    _d("XH05", "shirt_dress", "Blue Shirt Dress",
       "A blue cotton shirt dress with a self belt.", "Blue", 2, "blue shirt", 780),
    _d("XT01", "trainers", "White Trainers with Black Sole",
       "White canvas trainers on a black sole.", "White", 1, "black trainers", 900),
    _d("XT02", "trainers", "Grey Trainers with Black Laces",
       "Grey canvas trainers with black laces.", "Grey", 1, "black trainers", 860),
    _d("XT03", "trainers", "Red Trainers with Black Stripe",
       "Red canvas trainers with a black stripe.", "Red", 1, "black trainers", 820),
    _d("XT04", "shoe_care", "Black Trainer Cleaning Kit",
       "A cleaning kit for trainers, in a black tin.", "Black", 2, "black trainers", 800),
    # -- mens puffer jacket: the true hits first, then the audience decoys (3)
    _d("XP01", "puffer_m", "Mens Puffer Jacket",
       "A quilted puffer jacket for men.", "Navy", 0, "mens puffer jacket", 120, true_hit=True),
    _d("XP02", "puffer_m", "Mens Hooded Puffer Jacket",
       "A quilted hooded puffer jacket for men.", "Black", 0, "mens puffer jacket", 110,
       true_hit=True),
    _d("XP03", "puffer_k", "Kids Mini-Me Puffer Jacket",
       "A smaller version of our mens puffer jacket, cut for children.", "Navy", 3,
       "mens puffer jacket", 760),
    _d("XP04", "puffer_k", "Boys Mini-Me Mens Puffer Jacket",
       "The mens puffer jacket in boys sizes.", "Black", 3, "mens puffer jacket", 740),
    _d("XP05", "puffer_w", "Womens Puffer Jacket, Mens-Style Fit",
       "A womens puffer jacket cut like our mens puffer jacket.", "Black", 3,
       "mens puffer jacket", 720),
    _d("XP06", "puffer_w", "Womens Boyfriend Puffer Jacket",
       "A roomy womens puffer jacket in the cut of the mens puffer jacket.", "Green", 3,
       "mens puffer jacket", 700),
    # -- boys grey socks: adult socks titled without an audience word (3)
    _d("XK01", "socks_m", "Grey Socks 5 Pack",
       "Five pairs of grey socks, the same sock as our boys range, cut for men.", "Grey", 3,
       "boys grey socks", 900),
    _d("XK02", "socks_m", "Grey Ankle Socks 5 Pack",
       "Five pairs of grey ankle socks in the boys style, in adult sizes.", "Grey", 3,
       "boys grey socks", 860),
    _d("XK03", "socks_w", "Grey Boot Socks, Boys Style",
       "Grey socks knitted like the boys range, in womens sizes.", "Grey", 3,
       "boys grey socks", 820),
    _d("XK04", "socks_k", "Boys Grey Socks 5 Pack",
       "Five pairs of grey socks for boys.", "Grey", 0, "boys grey socks", 150, true_hit=True),
    # -- face cream: cream the color (4)
    _d("XF01", "face_cloth", "Cream Face Cloths 4 Pack",
       "Four cream cotton face cloths.", "Cream", 4, "face cream", 900),
    _d("XF02", "face_cloth", "Cream Face Towel",
       "A cream cotton face towel.", "Cream", 4, "face cream", 880),
    _d("XF04", "cushion", "Cream Cushion Cover with Face Print",
       "A cream cushion cover printed with a face.", "Cream", 4, "face cream", 760),
    # -- gold top: gold the shade, top the part of a bag (4)
    _d("XG01", "handbag", "Gold Top Handle Bag",
       "A gold bag with a rigid top handle.", "Gold", 4, "gold top", 900),
    _d("XG02", "handbag", "Gold Top Zip Clutch Bag",
       "A gold clutch bag with a top zip.", "Gold", 4, "gold top", 860),
    _d("XG03", "handbag", "Brown Top Handle Bag with Gold Hardware",
       "A brown bag with a top handle and gold hardware.", "Brown", 1, "gold top", 820),
    _d("XG04", "top", "Gold Sequin Top",
       "A gold sequin top with a boat neckline.", "Gold", 0, "gold top", 130, true_hit=True),
    # -- red wine: the wine the color and the glass, the candle, the stain remover (2, 4)
    _d("XW01", "glassware", "Red Wine Glasses, Set of 4",
       "Four glasses made for red wine.", "Red", 2, "red wine", 900),
    _d("XW02", "candle", "Red Wine Scented Candle",
       "A candle scented like red wine.", "Red", 4, "red wine", 880),
    _d("XW03", "cleaner", "Red Wine Stain Remover",
       "A spray that lifts red wine from a carpet.", "Red", 2, "red wine", 840),
    _d("XW04", "glassware", "Red Wine Carafe",
       "A glass carafe for red wine.", "Red", 2, "red wine", 800),
    # -- guards: a real product whose name holds a color word (5)
    _d("XU01", "tea", "Green Tea, 40 Bags", "Sencha green tea in round bags, 40 to a box.",
       "Green", 5, "green tea", 900, true_hit=True),
    _d("XU02", "spice", "Black Pepper, Whole Peppercorns",
       "Whole black peppercorns for a grinder.", "Black", 5, "black pepper", 90, true_hit=True),
    _d("XU03", "cake", "Red Velvet Cake", "A red velvet sponge with cream cheese icing. Serves 8.",
       "Red", 5, "red velvet cake", 90, true_hit=True),
    # -- pink lady apples: the guard holds the pink and the apple together (5)
    _d("XU04", "apples", "Pink Lady Apples", "Crisp pink lady apples, sold loose by the kilo.",
       "Red", 5, "pink lady apples", 90, true_hit=True),
    # -- class 7: the query word is only an ingredient (title names a different product)
    _d("XI01", "tea", "Earl Grey Tea, 40 Bags",
       "Black tea scented with bergamot and dried orange peel, orange peel in every bag.",
       "Black", 7, "oranges", 950,
       ingredients=("black tea", "orange peel (6%)", "bergamot flavoring")),
    _d("XI02", "tea", "Afternoon Blend Tea",
       "Black tea with orange peel and cornflower petals; the orange peel is dried in strips.",
       "Black", 7, "oranges", 920, ingredients=("black tea", "orange peel", "cornflower petals")),
    _d("XI03", "cake", "Rich Fruit Cake",
       "A moist fruit cake with orange peel, sultanas and cherries. Orange peel throughout.",
       "Brown", 7, "oranges", 900, ingredients=("sultanas", "orange peel (5%)", "wheat flour")),
    _d("XI04", "sauce", "Cranberry Sauce",
       "A tart cranberry sauce with orange zest and a little orange juice.", "Red", 7, "oranges",
       880, ingredients=("cranberries", "sugar", "orange zest", "orange juice")),
    _d("XI05", "surface_spray", "Kitchen Surface Spray",
       "A lemon scented spray for worktops; lemon fragrance, lemon oil and lemon extract.",
       "Yellow", 7, "lemons", 940, ingredients=("water", "lemon oil", "lemon extract")),
    _d("XI06", "fish", "Baked Cod Fillets",
       "Cod fillets baked with lemon juice and herbs, lemon zest and a squeeze of lemon.",
       "White", 7, "lemons", 900, ingredients=("cod", "lemon juice", "lemon zest", "parsley")),
    _d("XI07", "cake", "Sponge Cake",
       "A light sponge with lemon zest and lemon juice in the batter and a lemon glaze.",
       "Yellow", 7, "lemons", 860, ingredients=("wheat flour", "lemon zest", "lemon juice",
                                 "sugar")),
    _d("XI08", "yoghurt", "Fruit Yogurt, 4 Pack",
       "Yoghurt pots with strawberry puree and real strawberries: strawberry in every pot.",
       "Pink", 7, "strawberries", 950, ingredients=("yoghurt", "strawberry puree", "sugar")),
    _d("XI09", "cereal_bar", "Oat Bar Multipack",
       "Oat bars with dried strawberries and strawberry flavour, a strawberry bar for lunchboxes.",
       "Pink", 7, "strawberries", 920, ingredients=("oats", "strawberry pieces", "honey")),
    _d("XI10", "biscuit", "Cream Biscuits",
       "Sandwich biscuits with a strawberry cream filling, strawberry jam and dried strawberries.",
       "Pink", 7, "strawberries", 880, ingredients=("wheat flour", "strawberry jam", "sugar")),
    _d("XI11", "curry", "Thai Green Curry",
       "A green curry with chicken, coconut milk and lime leaf: coconut milk in a creamy sauce.",
       "Green", 7, "coconut", 950, ingredients=("chicken", "coconut milk", "green curry paste")),
    _d("XI12", "lotion", "Nourishing Body Lotion",
       "A rich body lotion made with coconut oil, shea butter and coconut extract.",
       "White", 7, "coconut", 920, ingredients=("water", "coconut oil", "shea butter")),
    _d("XI13", "curry", "Chickpea Dhal",
       "Lentils and chickpeas simmered in coconut milk with turmeric, coconut cream to finish.",
       "Yellow", 7, "coconut", 880, ingredients=("lentils", "coconut milk", "turmeric")),
    _d("XI14", "biscuit", "All Butter Shortbread",
       "Crumbly shortbread baked with dried lavender, lavender flowers and lavender sugar.",
       "Cream", 7, "lavender", 950, ingredients=("wheat flour", "butter", "lavender flowers")),
    _d("XI15", "bath_salts", "Relaxing Bath Salts",
       "Mineral bath salts with lavender oil and dried lavender buds to soak in.", "Purple", 7,
       "lavender", 920, ingredients=("sea salt", "lavender oil", "lavender buds")),
    _d("XI16", "lav_candle", "Soy Wax Candle",
       "A soy wax candle poured with lavender essential oil, a calming lavender scent.", "Cream", 7,
       "lavender", 880, ingredients=("soy wax", "lavender essential oil")),
)

STYLES = tuple(d.style() for d in TABLE)
#: The product ids left out of the derivation and of the color completion.
IDS = frozenset(f"PLT-{s.code}" for s in STYLES)
#: product id -> its row: the class and the query the proof reads.
BY_ID = {f"PLT-D{d.code}": d for d in TABLE}


def docs() -> list[dict]:
    """Every row's catalog document, in the order of :data:`TABLE`."""
    out = []
    for style, row in zip(STYLES, TABLE, strict=True):
        doc = style.doc()
        if row.ingredients:
            doc["ingredients"] = list(row.ingredients)
        out.append(doc)
    return out


CLASSES = {
    0: "a true hit, kept for the proof",
    1: "color names a part",
    2: "type names an accessory or a toy",
    3: "audience names a sibling version",
    4: "color word is also a product or a shade",
    5: "guard: a real product whose name holds a color word",
    7: "word only in the ingredients",
}


def table_markdown() -> str:
    """The docs table: one line per row, generated from :data:`TABLE`."""
    lines = ["| Query | Class | Product id | Title | Kind |", "|---|---|---|---|---|"]
    for pid, d in BY_ID.items():
        role = "true hit" if d.true_hit else "decoy"
        lines.append(f"| {d.query} | {d.cls} {CLASSES[d.cls]} | {pid} | {d.title} | {role} |")
    return "\n".join(lines)
