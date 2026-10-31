"""The failure-class styles of the clothing, bedding and beauty rows (:mod:`class_rows`)."""

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.class_model import (
    INSIDE_LEGS,
    LEGS3,
    Style,
    one,
)
from synthetic_ecommerce_data.domains.retail.variants import cw, shade

DENIM, MID, LIGHT, ECRU, BLACK = "#4a6a94", "#5b7aa6", "#9fb4cf", "#e8dfcc", "#2a2a2e"
WHITE, NAVY, CAMEL, OLIVE, RUST = "#ffffff", "#26365c", "#c19a6b", "#6b6b3a", "#a8502e"

# --------------------------------------------------------------------------
# 2. "mattress topper": protectors share the head word and sell more
# --------------------------------------------------------------------------

BED = ("Home", "Bedding")
TOPPERS = (
    Style("MTTMEM", "Memory Foam Mattress Topper", "Quillon Sleep", "Home",
          (*BED, "Mattress Toppers"), 60.0,
          "A 5cm layer of memory foam that softens a firm bed, with corner straps.",
          "Mattress Topper", "mattress_topper", one(cw("White", WHITE), 6),
          bed_sized=True, params=(("depth", "5cm"),)),
    Style("MTTFIB", "Hollowfibre Mattress Topper", "Quillon Sleep", "Home",
          (*BED, "Mattress Toppers"), 35.0,
          "A deep hollowfibre topper that adds a soft, springy layer. Machine washable.",
          "Mattress Topper", "mattress_topper", one(cw("White", WHITE), 4),
          bed_sized=True, params=(("depth", "7cm"),)),
    Style("MTTWOL", "Wool Mattress Topper", "Brackenmere Home", "Home",
          (*BED, "Mattress Toppers"), 85.0,
          "A breathable wool-filled topper, quilted in cotton, for a cooler night.",
          "Mattress Topper", "mattress_topper", one(cw("Natural", "#efe8d8"), 3),
          bed_sized=True, params=(("depth", "4cm"),)),
)  # fmt: skip

_BURY_BED = "type boost: Mattress Topper; Mattress Protector buried"
MATTRESS = (
    (Style("MTPQLT", "Quilted Mattress Protector", "Quillon Sleep", "Home",
           (*BED, "Mattress Protectors"), 20.0,
           "A quilted mattress protector with deep skirts. Keeps the mattress and any "
           "mattress topper fresh.",
           "Mattress Protector", "mattress_protector", one(cw("White", WHITE), 880),
           bed_sized=True), _BURY_BED),
    (Style("MTPWTP", "Waterproof Mattress Protector", "Quillon Sleep", "Home",
           (*BED, "Mattress Protectors"), 18.0,
           "A waterproof mattress protector that guards the mattress against spills. Fits "
           "over a mattress topper.",
           "Mattress Protector", "mattress_protector", one(cw("White", WHITE), 760),
           bed_sized=True), _BURY_BED),
    (Style("MTPTOP", "Deep Fill Mattress Topper Protector", "Brackenmere Home", "Home",
           (*BED, "Mattress Protectors"), 28.0,
           "A protector with a padded top: protects the mattress with a topper-soft feel.",
           "Mattress Protector", "mattress_protector", one(cw("White", WHITE), 540),
           bed_sized=True), _BURY_BED),
    (Style("MTPCOL", "Cool Touch Mattress Protector", "Quillon Sleep", "Home",
           (*BED, "Mattress Protectors"), 24.0,
           "A cooling mattress protector for the mattress you have. Goes under a topper too.",
           "Mattress Protector", "mattress_protector", one(cw("Ice", "#e6eef2"), 610),
           bed_sized=True), _BURY_BED),
    (Style("MTRPKT", "Pocket Sprung Mattress", "Quillon Sleep", "Home",
           (*BED, "Mattresses"), 320.0,
           "A medium firm pocket sprung mattress with a built-in comfort topper layer.",
           "Mattress", "mattress", one(cw("Stone", "#d9d3c7"), 190),
           bed_sized=True, params=(("depth", "25cm"),)), "type boost: Mattress buried"),
    (Style("PILPRT", "Pillow Protectors, Pair", "Quillon Sleep", "Home",
           (*BED, "Pillow Protectors"), 9.0,
           "Zipped pillow protectors to match your mattress protector.",
           "Pillow Protector", "pillow", one(cw("White", WHITE), 650)),
     "type boost: Pillow Protector buried"),
)  # fmt: skip

# --------------------------------------------------------------------------
# 3. "balloon jeans": an over-broad synonym (balloon -> barrel) and a
# bestseller boost
# --------------------------------------------------------------------------

WJEANS = ("Womens", "Jeans")
BALLOON = (
    Style("BLNLEG", "Balloon Leg Jeans", "Ferrowick Denim", "Clothing",
          (*WJEANS, "Balloon Jeans"), 45.0,
          "Full through the thigh and knee, curving back in at a cropped ankle.",
          "Jeans", "trousers", ((cw("Mid Wash", MID), 30), (cw("Ecru", ECRU), 21)),
          leg_style="balloon", pattern="plain", lengths=LEGS3,
          params=(("fit", "balloon"), ("rise", "high"))),
    Style("BLNHIW", "High Waisted Balloon Jeans", "Ottery Denim", "Clothing",
          (*WJEANS, "Balloon Jeans"), 42.0,
          "A high waist and a rounded leg that tapers to the hem, in rigid denim.",
          "Jeans", "trousers", one(cw("Light Wash", LIGHT), 25),
          leg_style="balloon", pattern="plain", lengths=LEGS3,
          params=(("fit", "balloon"), ("rise", "high"))),
    Style("BLNCRP", "Cropped Balloon Jeans", "Harbour & Pine", "Clothing",
          (*WJEANS, "Balloon Jeans"), 39.0,
          "A volume leg cut to just above the ankle, with a curved side seam.",
          "Jeans", "trousers", one(cw("Black", BLACK), 18),
          leg_style="balloon", pattern="plain", lengths=LEGS3,
          params=(("fit", "balloon"), ("rise", "mid"))),
)  # fmt: skip

_EXACT = "exact style first: leg_style balloon"
BARREL = (
    (Style("BRLMID", "Mid Rise Barrel Jeans", "Ottery Denim", "Clothing",
           (*WJEANS, "Barrel Jeans"), 36.0,
           "Our bestselling barrel jeans: a curved leg that narrows at the ankle.",
           "Jeans", "trousers",
           ((cw("Mid Wash", MID), 940), (cw("Light Wash", LIGHT), 820), (cw("Black", BLACK), 700),
            (cw("Ecru", ECRU), 610), (cw("Vintage Blue", DENIM), 540)),
           leg_style="barrel", pattern="plain", lengths=INSIDE_LEGS,
           params=(("fit", "barrel"), ("rise", "mid"))), _EXACT),
    (Style("BRLHIG", "High Rise Barrel Jeans", "Ferrowick Denim", "Clothing",
           (*WJEANS, "Barrel Jeans"), 40.0,
           "Barrel jeans with a high rise and a soft curve through the knee.",
           "Jeans", "trousers", ((cw("Rinse", NAVY), 640), (cw("Washed Black", BLACK), 460)),
           leg_style="barrel", pattern="plain", lengths=LEGS3,
           params=(("fit", "barrel"), ("rise", "high"))), _EXACT),
    (Style("BRLKID", "Girls' Barrel Jeans (6-16 Yrs)", "Little Fernby", "Clothing",
           ("Kids", "Girls", "Jeans"), 18.0,
           "Barrel jeans for girls with an adjustable waist.",
           "Jeans", "trousers", one(cw("Mid Wash", MID), 520), audience="kids",
           leg_style="barrel", pattern="plain", lengths=("Regular",),
           params=(("fit", "barrel"), ("rise", "mid"))), _EXACT),
    (Style("BRLTRS", "Barrel Leg Trousers", "Larkmoor", "Clothing",
           ("Womens", "Trousers", "Barrel Trousers"), 32.0,
           "Twill barrel trousers that wear like jeans, with a pressed crease.",
           "Trousers", "trousers", one(cw("Khaki", OLIVE), 480),
           leg_style="barrel", pattern="plain", lengths=LEGS3,
           params=(("fit", "barrel"), ("rise", "high"))), _EXACT),
)  # fmt: skip

# --------------------------------------------------------------------------
# 4. "womens boat neck top": the word "neck" matched as a keyword
# --------------------------------------------------------------------------

TOPS = ("Womens", "Tops")
BOAT = (
    Style("BNTSTR", "Striped Boat Neck Top", "Harbour & Pine", "Clothing",
          (*TOPS, "Long Sleeve Tops"), 24.0,
          "A wide, shallow neckline that runs shoulder to shoulder, in striped cotton.",
          "Top", "top", one(cw("Navy Stripe", WHITE, "stripe", NAVY), 40),
          neckline="boat", pattern="stripe", size_range="regular",
          params=(("neckline", "boat"), ("sleeve", "long"))),
    Style("BNTJER", "Boat Neck Jersey Top", "Larkmoor", "Clothing",
          (*TOPS, "Jersey Tops"), 20.0,
          "Soft jersey with a wide boat neckline and three quarter sleeves.",
          "Top", "top", one(cw("Ecru", ECRU), 22),
          neckline="boat", pattern="plain", size_range="regular",
          params=(("neckline", "boat"), ("sleeve", "three_quarter"))),
    Style("SNTLNG", "Slash Neck Long Sleeve Top", "Wrenfield", "Clothing",
          (*TOPS, "Long Sleeve Tops"), 26.0,
          "A straight slash neckline across the collarbone, in a fine rib.",
          "Top", "top", one(cw("Black", BLACK), 35),
          neckline="slash", pattern="plain", size_range="regular",
          params=(("neckline", "boat"), ("sleeve", "long"))),
)  # fmt: skip

_NECK = "type = Top; neckline boat or slash boosted"
NECK = (
    (Style("HNRIBT", "Womens High Neck Ribbed Top", "Larkmoor", "Clothing",
           (*TOPS, "Jersey Tops"), 22.0,
           "A ribbed high neck top for women. The neck sits close; a neat neck finish.",
           "Top", "top", one(cw("Oat", "#d8cbb2"), 950),
           neckline="high", pattern="plain", size_range="regular",
           params=(("neckline", "roll_neck"), ("sleeve", "long"))), _NECK),
    (Style("CNCOTT", "Womens Crew Neck Cotton Top", "Harbour & Pine", "Clothing",
           (*TOPS, "T-Shirts"), 14.0,
           "A crew neck cotton top for women with a ribbed neck trim.",
           "Top", "top", one(cw("White", WHITE), 820),
           neckline="crew", pattern="plain", size_range="regular",
           params=(("neckline", "crew"), ("sleeve", "short"))), _NECK),
    (Style("RNJERS", "Womens Round Neck Jersey Top", "Wrenfield", "Clothing",
           (*TOPS, "Jersey Tops"), 16.0,
           "A round neck jersey top for women, the neck bound in self fabric.",
           "Top", "top", one(cw("Rust", RUST), 700),
           neckline="round", pattern="plain", size_range="regular",
           params=(("neckline", "crew"), ("sleeve", "long"))), _NECK),
    (Style("COLTOP", "Womens Collared Jersey Top", "Hollinwray Knits", "Clothing",
           (*TOPS, "Jersey Tops"), 26.0,
           "A womens jersey top with a neat collar at the neck and a button placket.",
           "Top", "top", one(cw("Navy", NAVY), 610),
           neckline="collared", pattern="plain", size_range="regular",
           params=(("neckline", "crew"), ("sleeve", "long"))), _NECK),
    (Style("SQBODY", "Womens Square Neck Bodysuit", "Larkmoor", "Clothing",
           (*TOPS, "Bodysuits"), 18.0,
           "A womens bodysuit with a square neck, worn as a top. Popper fastening.",
           "Bodysuit", "bodysuit", one(cw("Black", BLACK), 650),
           neckline="square", pattern="plain", size_range="regular",
           params=(("neckline", "square"), ("sleeve", "sleeveless"))), "type = Top"),
    (Style("NTSETS", "Womens Tie Neck Top and Trousers Set", "Wrenfield", "Clothing",
           ("Womens", "Co-ords", "Sets"), 48.0,
           "A womens co-ord: a tie neck top and matching wide trousers.",
           "Co-ord Set", "outfit_set", one(cw("Sage", "#9bb08f"), 430),
           pattern="plain", size_range="regular", params=(("tee", "#9bb08f"),)), "type = Top"),
)  # fmt: skip

# --------------------------------------------------------------------------
# 5. "check contrast bomber jacket": type not enforced, "contrast" ignored,
# audience not defaulted
# --------------------------------------------------------------------------

COATS = ("Womens", "Coats & Jackets")
CHECK = (
    Style("CKBCON", "Check Bomber Jacket with Contrast Collar", "Calderby & Lune", "Clothing",
          (*COATS, "Bomber Jackets"), 69.0,
          "A wool-blend check bomber with a contrast rib collar and cuffs.",
          "Bomber Jacket", "coat", one(cw("Brown Check", CAMEL, "gingham", "#5a3426"), 14),
          pattern="check", size_range="regular"),
    Style("CKBWOL", "Wool Check Bomber Jacket", "Bramblewood", "Clothing",
          (*COATS, "Bomber Jackets"), 75.0,
          "A bomber in a soft check wool with contrast ribbing.",
          "Bomber Jacket", "coat", one(cw("Grey Check", "#9a9a9a", "gingham", BLACK), 11),
          pattern="check", size_range="regular"),
    Style("CKBPAD", "Padded Check Bomber", "Harbour & Pine", "Clothing",
          (*COATS, "Bomber Jackets"), 59.0,
          "A lightly padded bomber in a checked twill, zip front, contrast lining.",
          "Bomber Jacket", "coat", one(cw("Navy Check", NAVY, "gingham", "#c8312e"), 9),
          pattern="check", size_range="regular"),
)  # fmt: skip

_TYPE = "type = Bomber Jacket (hard); pattern check boosted"
BOMBER = (
    (Style("BMBCRD", "Cord Bomber Jacket", "Wrenfield", "Clothing",
           (*COATS, "Bomber Jackets"), 55.0,
           "A plain cord bomber jacket with a zip front. The bomber jacket of the season.",
           "Bomber Jacket", "coat", one(cw("Tobacco", "#7a4a2a"), 900),
           pattern="plain", size_range="regular"), "pattern check boosted"),
    (Style("BMBWOL", "Wool Blend Bomber Jacket", "Larkmoor", "Clothing",
           (*COATS, "Bomber Jackets"), 65.0,
           "A plain wool blend bomber jacket with ribbed trims. A bomber jacket for every day.",
           "Bomber Jacket", "coat", one(cw("Charcoal", "#4a4a50"), 720),
           pattern="plain", size_range="regular"), "pattern check boosted"),
    (Style("SUITCK", "Check Suit Jacket", "Calderby & Lune", "Clothing",
           (*COATS, "Blazers"), 80.0,
           "A single breasted check suit jacket, the check jacket that matches our trousers.",
           "Suit Jacket", "suit_jacket", one(cw("Grey Check", "#9a9a9a", "gingham", BLACK), 650),
           pattern="check", size_range="regular",
           params=(("fit", "regular"), ("lapel", "notch"), ("buttons", "2"))), _TYPE),
    (Style("CARCHK", "Checked Car Coat", "Bramblewood", "Clothing",
           (*COATS, "Coats", "Car Coats"), 99.0,
           "A checked car coat, jacket length, with a contrast collar.",
           "Coat", "coat", one(cw("Camel Check", CAMEL, "gingham", NAVY), 500),
           pattern="check", size_range="regular"), _TYPE),
    (Style("KIDBMB", "Boys' Bomber Jacket (2-8 Yrs)", "Little Fernby", "Clothing",
           ("Kids", "Boys", "Coats & Jackets"), 24.0,
           "A bomber jacket for boys with contrast stripe cuffs.",
           "Bomber Jacket", "coat", one(cw("Navy", NAVY), 600), audience="kids",
           pattern="plain", size_range="regular"), "audience adult by default"),
    (Style("BABBMB", "Baby Bomber Jacket (3-36 Mths)", "Little Fernby", "Clothing",
           ("Kids", "Baby", "Coats & Jackets", "Bomber Jackets"), 20.0,
           "A soft padded bomber jacket for babies, with contrast ribbing.",
           "Bomber Jacket", "coat", one(cw("Olive", OLIVE), 420), audience="baby",
           pattern="plain"), "audience adult by default"),
)  # fmt: skip

# --------------------------------------------------------------------------
# 6. "petite sale": the size range and the sale state are not extracted
# --------------------------------------------------------------------------

PETITE = (
    Style("PETDRS", "Petite Wrap Midi Dress", "Larkmoor", "Clothing",
          ("Womens", "Dresses", "Wrap Dresses"), 28.0,
          "A wrap midi dress cut shorter in the body and hem for petite frames.",
          "Dress", "dress", one(cw("Navy Print", NAVY, "polka", WHITE), 4), was_price=40.0,
          size_range="petite", pattern="print"),
    Style("PETTRS", "Petite Wide Leg Trousers", "Wrenfield", "Clothing",
          ("Womens", "Trousers", "Wide Leg Trousers"), 22.0,
          "Wide leg trousers with a shorter inside leg for petite heights.",
          "Trousers", "trousers", one(cw("Black", BLACK), 3), was_price=32.0,
          lengths=("Extra Short", "Short/Petite"), pattern="plain", leg_style="wide",
          params=(("fit", "wide_leg"), ("rise", "high"))),
    Style("PETJNS", "Petite Straight Jeans", "Ottery Denim", "Clothing",
          (*WJEANS, "Straight Jeans"), 25.0,
          "Straight jeans with a 28 inch inside leg, made for petite heights.",
          "Jeans", "trousers", one(cw("Mid Wash", MID), 5), was_price=35.0,
          lengths=("Extra Short", "Short/Petite"), pattern="plain", leg_style="straight",
          params=(("fit", "straight"), ("rise", "mid"))),
)  # fmt: skip

_SALE = "size range petite and on sale, as filters"
BESTSELLERS = (
    (Style("TAPTRS", "Tapered Trousers", "Wrenfield", "Clothing",
           ("Womens", "Trousers", "Tapered Trousers"), 30.0,
           "Our bestselling tapered trousers. Also cut in petite and tall.",
           "Trousers", "trousers", one(cw("Navy", NAVY), 960),
           lengths=LEGS3, pattern="plain", leg_style="tapered",
           params=(("fit", "slim"), ("rise", "high"))), _SALE),
    (Style("STRJNS", "Straight Leg Jeans", "Ottery Denim", "Clothing",
           (*WJEANS, "Straight Jeans"), 32.0,
           "Straight leg jeans in a regular length. Also cut in petite and long.",
           "Jeans", "trousers", one(cw("Indigo", DENIM), 910),
           lengths=LEGS3, pattern="plain", leg_style="straight",
           params=(("fit", "straight"), ("rise", "high"))), _SALE),
    (Style("WIDTRS", "Wide Leg Trousers", "Larkmoor", "Clothing",
           ("Womens", "Trousers", "Wide Leg Trousers"), 34.0,
           "Fluid wide leg trousers with a pressed crease. Also cut in petite.",
           "Trousers", "trousers", one(cw("Black", BLACK), 800),
           lengths=("Short/Petite", "Regular"), pattern="plain", leg_style="wide",
           params=(("fit", "wide_leg"), ("rise", "high"))), _SALE),
    (Style("SLMJNS", "Slim Jeans", "Ferrowick Denim", "Clothing",
           (*WJEANS, "Slim Jeans"), 30.0,
           "Slim jeans with stretch. Also cut in petite and tall lengths.",
           "Jeans", "trousers", one(cw("Black", BLACK), 690),
           # Cut in petite, but the petite lengths are sold out.
           lengths=LEGS3, sold_out=("Short/Petite",), pattern="plain", leg_style="slim",
           params=(("fit", "slim"), ("rise", "mid"))), _SALE),
)  # fmt: skip

# --------------------------------------------------------------------------
# 7. "womens sale dresses": "sale" ignored, so the full-price bestsellers win
# --------------------------------------------------------------------------

DRESSES = ("Womens", "Dresses")
SALE_DRESSES = (
    Style("SDWRAP", "Womens Wrap Dress", "Larkmoor", "Clothing",
          (*DRESSES, "Wrap Dresses"), 27.0,
          "A jersey wrap dress for women with a tie waist.",
          "Dress", "dress", one(cw("Green Print", "#2f6b3c", "polka", WHITE), 5), was_price=45.0,
          size_range="regular", pattern="print"),
    Style("SDSHRT", "Womens Shirt Dress", "Harbour & Pine", "Clothing",
          (*DRESSES, "Shirt Dresses"), 23.0,
          "A cotton shirt dress for women with a self belt.",
          "Dress", "dress", one(cw("Blue Stripe", WHITE, "stripe", "#5b84b8"), 4), was_price=38.0,
          size_range="regular", pattern="stripe"),
    Style("SDMAXI", "Womens Tiered Maxi Dress", "Wrenfield", "Clothing",
          (*DRESSES, "Maxi Dresses"), 33.0,
          "A tiered maxi dress for women in cotton voile.",
          "Dress", "dress", one(cw("Terracotta", RUST), 6), was_price=55.0,
          size_range="regular", pattern="plain"),
)  # fmt: skip

_ONSALE = "on sale (price < was_price), as a filter"
FULL_PRICE = (
    (Style("FPLINN", "Womens Linen Midi Dress", "Harbour & Pine", "Clothing",
           (*DRESSES, "Midi Dresses"), 45.0,
           "A linen midi dress for women. Our most loved dress of the season.",
           "Dress", "dress", one(cw("White", WHITE), 950),
           size_range="regular", pattern="plain"), _ONSALE),
    (Style("FPTEES", "Womens Jersey T-Shirt Dress", "Larkmoor", "Clothing",
           (*DRESSES, "T-Shirt Dresses"), 22.0,
           "An easy jersey t-shirt dress for women.",
           "Dress", "dress", one(cw("Navy", NAVY), 870),
           size_range="regular", pattern="plain"), _ONSALE),
    (Style("FPSMOK", "Womens Smocked Mini Dress", "Wrenfield", "Clothing",
           (*DRESSES, "Mini Dresses"), 35.0,
           "A smocked mini dress for women with puff sleeves.",
           "Dress", "dress", one(cw("Gingham", WHITE, "gingham", "#c8312e"), 720),
           size_range="regular", pattern="check"), _ONSALE),
    (Style("FPSLIP", "Womens Satin Slip Dress", "Larkmoor", "Clothing",
           (*DRESSES, "Slip Dresses"), 39.0,
           "A bias cut satin slip dress for women.",
           "Dress", "dress", one(cw("Champagne", "#e8d6b0"), 640),
           size_range="regular", pattern="plain"), _ONSALE),
    (Style("KIDDRS", "Girls' Party Dress (2-8 Yrs)", "Little Fernby", "Clothing",
           ("Kids", "Girls", "Dresses"), 20.0,
           "A tulle party dress for girls. Dresses for every party.",
           "Dress", "dress", one(cw("Pink", "#f3c6cf"), 560), audience="kids",
           size_range="regular", pattern="plain"), "audience adult by default; on sale filter"),
)  # fmt: skip


# --------------------------------------------------------------------------
# 9. "5 pack socks" (an on-stage demo case): the count lives in title
# spellings ("5 Pack", "5pk", "Pack of 5"), so "5pk" misses and the
# bestselling 7 pack and a single pair win
# --------------------------------------------------------------------------

SOCKS = ("Mens", "Socks")
FIVE_PACKS = (
    Style("SK5PKC", "Cotton Rich Ankle Socks 5pk", "Harbour & Pine", "Clothing",
          (*SOCKS, "Ankle Socks"), 10.0, "Cushioned ankle socks in soft cotton rich yarn.",
          "Socks", "socks", one(cw("Black", BLACK), 28), pattern="plain", units_per_pack=5,
          params=(("pairs", "5"),)),
    Style("SK5BMB", "Bamboo Socks, Pack of 5", "Wrenfield", "Clothing",
          (*SOCKS, "Everyday Socks"), 12.0, "Breathable bamboo socks with a comfort top.",
          "Socks", "socks", one(cw("Navy", NAVY), 24), pattern="plain", units_per_pack=5,
          params=(("pairs", "5"),)),
    Style("SK5SPT", "Sports Trainer Socks 5 Pack", "Stridewell", "Clothing",
          (*SOCKS, "Sports Socks"), 9.0, "Trainer liners with an arch grip.",
          "Socks", "socks", one(cw("White", WHITE), 9), pattern="plain", units_per_pack=5,
          params=(("pairs", "5"),)),
)  # fmt: skip

_PACK = "units_per_pack = 5, as a filter"
PACKS = (
    (Style("SK7PKC", "Cotton Rich Socks 7 Pack", "Harbour & Pine", "Clothing",
           (*SOCKS, "Everyday Socks"), 14.0,
           "Our bestselling socks: a pack of socks for every day of the week.",
           "Socks", "socks", one(cw("Black", BLACK), 960), pattern="plain", units_per_pack=7,
           params=(("pairs", "7"),)),
     _PACK),
    (Style("SK3PKS", "Striped Socks 3 Pack", "Wrenfield", "Clothing",
           (*SOCKS, "Everyday Socks"), 8.0, "A pack of striped cotton socks.",
           "Socks", "socks", one(cw("Stripe", WHITE, "stripe", RUST), 720), pattern="stripe",
           units_per_pack=3, params=(("pairs", "3"),)), _PACK),
    (Style("SK1WAL", "Wool Walking Socks", "Stridewell", "Clothing",
           (*SOCKS, "Walking Socks"), 9.0,
           "Cushioned wool walking socks, sold as a single pair. Socks for long days.",
           "Socks", "socks", one(cw("Grey", "#9a9a9a"), 690), pattern="plain", units_per_pack=1,
           params=(("pairs", "1"),)),
     _PACK),
    (Style("SK5KID", "Kids' School Socks 5 Pack (6-16 Yrs)", "Little Fernby", "Clothing",
           ("Kids", "School Uniform", "School Socks"), 7.0, "Five pairs of grey school socks.",
           "Socks", "socks", one(cw("Grey", "#9a9a9a"), 610), audience="kids", pattern="plain",
           units_per_pack=5, params=(("pairs", "5"),)), "audience adult by default"),
)  # fmt: skip


# --------------------------------------------------------------------------
# Beauty: a third-party brand; the variant axis is the shade (one doc each,
# food-word shade names), every shade the same unit size. Not a query row.
# --------------------------------------------------------------------------

MAKEUP = ("Beauty", "Make-Up")
BEAUTY = (
    Style("BTYLIP", "Satin Lipstick", "Kestlewood Cosmetics", "Beauty",
          (*MAKEUP, "Lips", "Lipstick"), 25.0,
          "A creamy satin lipstick with a soft sheen, in a slim bullet.",
          "Lipstick", "lipstick",
          ((cw("Wild Honey", "#b9774a"), 2), (cw("Mocha Kiss", "#7b4a3a"), 1),
           (cw("Cherry Pop", "#b0182f"), 1)), unit=(1.9, "g")),
    Style("BTYFND", "Soft Veil Foundation", "Kestlewood Cosmetics", "Beauty",
          (*MAKEUP, "Face", "Foundation"), 32.0,
          "A soft, buildable foundation with a natural finish.",
          "Foundation", "bottle",
          ((shade("Porcelain", "#f1dcc8"), 1), (shade("Caramel", "#c48a5c"), 2),
           (shade("Toffee", "#9a6440"), 1), (shade("Espresso", "#5a3a28"), 1)),
          volumes=((15.0, 20.0), (30.0, 32.0), (50.0, 46.0))),
)  # fmt: skip
