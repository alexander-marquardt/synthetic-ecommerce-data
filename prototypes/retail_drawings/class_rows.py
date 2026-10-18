"""The failure-class rows of gen#125 and their styles, as data.

Each block is one query shape: the targets a shopper meant and the distractors
that win without a policy (every name invented). The model is
:mod:`class_model`; the corpus, the Elasticsearch bodies and the proof read
these through :mod:`real_classes`.
"""

from __future__ import annotations

from collections.abc import Callable

import kit_suits  # noqa: F401 -- registers suit_jacket, which the check suit jacket is drawn as
from class_model import (
    BED_SIZE_DIMS,
    INSIDE_LEGS,
    LEGS3,
    PATH_SEPARATOR,
    ClassRow,
    Control,
    Policy,
    Style,
    on_sale,
    one,
)
from variants import Color, cw

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
           (*COATS, "Car Coats"), 99.0,
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
          "A light, buildable foundation with a natural finish.",
          "Foundation", "bottle",
          ((cw("Porcelain", "#f1dcc8"), 1), (cw("Caramel", "#c48a5c"), 2),
           (cw("Toffee", "#9a6440"), 1), (cw("Espresso", "#5a3a28"), 1)),
          volumes=((15.0, 20.0), (30.0, 32.0), (50.0, 46.0))),
)  # fmt: skip


def pack(base: str, sold: int) -> tuple[tuple[Color, int], ...]:
    """A colorless product's one doc: the color only fills its drawing."""
    return one(cw("Pack", base), sold)


# --------------------------------------------------------------------------
# 10. "beer" (food): a compound noun (ginger beer, root beer) and a modifier
# ("beer battered", "beer bread") share the word; ABV is an attribute, in
# only some titles. Each size is its own product, so no swatches.
# --------------------------------------------------------------------------

FOOD = "Food & Drink"
DRINKS = ("Food & Drink", "Drinks")
BEER_NODE = (FOOD, "Beer, Wine & Spirits", "Beer")
BEERS = (
    Style("BRTROP", "4.8% Tropical Pineapple Sour Beer", "Lanternby", FOOD,
          (*BEER_NODE, "Sour Beer"), 2.6,
          "A tart sour beer brewed with pineapple and passion fruit.",
          "Beer", "tin", pack("#f2c14e", 30), unit=(440.0, "ml"), abv=4.8,
          multibuy=True, colorless=True),
    Style("BRTABL", "Golden Table Beer", "Lanternby", FOOD, (*BEER_NODE, "Lager"), 2.2,
          "A light, low strength table beer brewed with English hops.",
          "Beer", "tin", pack("#d9a441", 25), unit=(330.0, "ml"), abv=2.8, colorless=True),
    Style("BRWHET", "5.5% Hazy Wheat Beer", "Lanternby", FOOD, (*BEER_NODE, "Wheat Beer"), 2.8,
          "An unfiltered wheat beer with notes of banana and clove.",
          "Beer", "bottle", pack("#e8b04a", 20),
          volumes=((500.0, 2.8), (330.0, 2.1), (750.0, 3.9)), abv=5.5, colorless=True),
)  # fmt: skip

_ROUTE_BEER = "route: Beer node boosted; a soft drink or a battered food is outside it"
NOT_BEER = (
    (Style("GNGBER", "Fiery Ginger Beer", "Pantry Mill", FOOD,
           (*DRINKS, "Soft Drinks", "Mixers"), 1.1,
           "An alcohol-free ginger beer brewed with root ginger and a little chilli.",
           "Ginger Beer", "bottle", pack("#c98b2b", 640),
           volumes=((330.0, 1.1), (200.0, 0.8), (1000.0, 2.2)), trending=True,
           colorless=True), _ROUTE_BEER),
    (Style("RTBEER", "Cloudy Root Beer", "Pantry Mill", FOOD,
           (*DRINKS, "Soft Drinks", "Fizzy Drinks"), 1.0,
           "An old fashioned root beer with vanilla and sarsaparilla.",
           "Root Beer", "tin", pack("#5a3020", 420),
           volumes=((330.0, 1.0), (500.0, 1.4), (1500.0, 2.6)), colorless=True),
     _ROUTE_BEER),
    (Style("BBHADD", "Beer Battered Haddock Fillets", "Saltmarsh", FOOD,
           ("Food & Drink", "Frozen", "Battered Fish"), 4.5,
           "Two haddock fillets in a crisp beer batter. Oven bake from frozen.",
           "Battered Fish", "box", pack("#d8a548", 600), unit=(280.0, "g"), colorless=True),
     _ROUTE_BEER),
    (Style("BBCHIP", "Beer Battered Chunky Chips", "Hearth & Table", FOOD,
           ("Food & Drink", "Frozen Food", "Chips & Potatoes"), 2.0,
           "Thick cut chips in a light beer batter, crisp from the oven.",
           "Chips", "box", pack("#e6b85c", 520), unit=(900.0, "g"), colorless=True),
     _ROUTE_BEER),
    (Style("BRBRED", "Malted Beer Bread", "Crofter's Bakehouse", FOOD,
           ("Food & Drink", "Bakery", "Bread"), 1.6,
           "A soft malted loaf baked with a dark beer.",
           "Bread", "loaf", pack("#8a5a30", 300), unit=(400.0, "g"), colorless=True),
     _ROUTE_BEER),
)  # fmt: skip

# --------------------------------------------------------------------------
# 11. "oranges": the fruit word names a flavour in bakery, sweets and drinks,
# and a color in clothing and flowers; one true hit has no "orange" in it
# --------------------------------------------------------------------------

CITRUS = ("Food & Drink", "Fruit & Vegetables", "Fresh Fruit", "Citrus Fruit")
ORANGES = (
    Style("ORBLOD", "Blood Oranges", "Goldfield Farms", FOOD, (*CITRUS, "Oranges"), 2.0,
          "Ruby fleshed blood oranges, sweet with a berry note. A short season.",
          "Oranges", "produce_pile", pack("#c8432e", 40), unit=(860.0, "g"),
          colorless=True, params=(("fruit", "orange"),)),
    Style("ORNAVL", "Navel Oranges", "Goldfield Farms", FOOD, (*CITRUS, "Oranges"), 1.8,
          "Large, juicy navel oranges that are easy to segment.",
          "Oranges", "produce_pile", pack("#f08a24", 30), unit=(1000.0, "g"), colorless=True,
          params=(("fruit", "orange"),)),
    # A type match only: neither the title nor the description names the fruit.
    Style("OREASY", "Seedless Easy Peelers", "Goldfield Farms", FOOD, (*CITRUS, "Oranges"), 2.2,
          "Small, sweet and seedless, with a loose skin that comes away in one go.",
          "Easy Peelers", "produce_pile", pack("#f39c33", 260), unit=(1200.0, "g"),
          colorless=True, params=(("fruit", "clementine"), ("pack", "net"))),
)  # fmt: skip

_ROUTE_ORANGE = "route: Oranges node boosted and recalled"
NOT_ORANGES = (
    (Style("PANCRO", "Cranberry & Orange Panettone", "Crofter's Bakehouse", FOOD,
           ("Food & Drink", "Bakery", "Panettone"), 8.0,
           "A tall, light panettone with cranberries and candied orange peel.",
           "Panettone", "panettone", pack("#d9a35a", 610), unit=(750.0, "g"),
           colorless=True), _ROUTE_ORANGE),
    (Style("CKCORA", "Chocolate & Orange Cookies", "Crofter's Bakehouse", FOOD,
           ("Food & Drink", "Biscuits & Snacks", "Cookies"), 2.5,
           "Chunky cookies with dark chocolate and orange oil.",
           "Cookies", "box", pack("#6b3a20", 560), unit=(200.0, "g"), colorless=True),
     _ROUTE_ORANGE),
    (Style("HCORNG", "Orange Hot Chocolate", "Pantry Mill", FOOD,
           (*DRINKS, "Hot Chocolate"), 3.5,
           "A rich hot chocolate flavoured with orange.",
           "Hot Chocolate", "tub", pack("#5a3020", 480), unit=(250.0, "g"),
           colorless=True), _ROUTE_ORANGE),
    (Style("XPCHOR", "Cherry & Orange Christmas Pudding", "Hearth & Table", FOOD,
           ("Food & Drink", "Desserts", "Christmas Puddings"), 9.0,
           "A rich fruit pudding with cherries and orange zest, matured for a month.",
           "Christmas Pudding", "pudding", pack("#5a2a1a", 450), unit=(800.0, "g"),
           colorless=True), _ROUTE_ORANGE),
    (Style("JMPCBL", "Chunky Cable Knit Jumper", "Harbour & Pine", "Clothing",
           ("Womens", "Knitwear", "Jumpers"), 45.0,
           "A chunky cable knit jumper in a burnt orange wool blend.",
           "Jumper", "top", one(cw("Burnt Orange", "#c4622d"), 690), pattern="plain",
           params=(("neckline", "crew"), ("sleeve", "long"), ("kind", "jumper"))), _ROUTE_ORANGE),
    (Style("BQORNG", "Orange Rose Bouquet", "Goldfield Farms", "Garden",
           ("Garden", "Flowers", "Bouquets"), 30.0,
           "Orange roses and gerberas, hand tied with eucalyptus.",
           "Bouquet", "bouquet", one(cw("Orange", "#f08a24"), 380)), _ROUTE_ORANGE),
)  # fmt: skip

# --------------------------------------------------------------------------
# 12. "face cream": cream is a color (sofas, bedding, knitwear), a near type
# (powder, tint, oil, SPF) and part of a line name on an oil
# --------------------------------------------------------------------------

SKINCARE = ("Beauty", "Skincare")
CREAMS = (*SKINCARE, "Creams")
FACE_CREAMS = (
    Style("FCDAYC", "Daily Hydrating Face Cream", "Velling Apothecary", "Beauty",
          (*CREAMS, "Face Creams"), 18.0,
          "A light daily face cream that hydrates without shine.",
          "Face Cream", "moisturiser_jar", pack("#f4efe6", 5),
          volumes=((50.0, 18.0), (30.0, 12.0), (100.0, 28.0)), colorless=True),
    Style("FCNGHT", "Rich Night Cream", "Velling Apothecary", "Beauty",
          (*CREAMS, "Face Creams"), 22.0,
          "A rich overnight face cream for dry skin.",
          "Face Cream", "moisturiser_jar", pack("#efe4d6", 4), unit=(50.0, "ml"), colorless=True),
    Style("FCCALM", "Calming Face Cream", "Velling Apothecary", "Beauty",
          (*CREAMS, "Face Creams"), 16.0,
          "A fragrance free face cream for sensitive skin.",
          "Face Cream", "moisturiser_jar", pack("#eef1ea", 3), unit=(50.0, "ml"), colorless=True),
)  # fmt: skip

_ROUTE_FACE = "route: Face Creams node boosted"
_DEPT = "route: Face Creams node boosted (a department policy alone removes it)"
NOT_FACE_CREAM = (
    (Style("SOFCRN", "Four Seater Corner Sofa", "Brackenmere Home", "Home",
           ("Home", "Furniture", "Sofas", "Corner Sofas"), 2795.0,
           "A deep corner sofa in a soft boucle weave. Shown in cream.",
           # Popularity is summed per style: 680 keeps it out of the bestseller top 15.
           "Corner Sofa", "sofa", ((cw("Cream", "#efe6d2"), 420), (cw("Sage", "#9bb08f"), 260))),
     _DEPT),
    (Style("PWDLSE", "Loose Face Powder", "Kestlewood Cosmetics", "Beauty",
           ("Beauty", "Make-Up", "Face", "Face Powder"), 24.0,
           "A silky loose powder that sets cream and liquid foundation.",
           "Face Powder", "compact", pack("#e8d2bd", 650), unit=(20.0, "g"),
           colorless=True, params=(("form", "loose"),)), _ROUTE_FACE),
    (Style("TNTGEL", "Tinted Face Gel", "Kestlewood Cosmetics", "Beauty",
           ("Beauty", "Make-Up", "Face", "Skin Tints"), 21.0,
           "A sheer tinted gel that wears like a light cream.",
           "Skin Tint", "bottle", pack("#d9b08c", 560),
           volumes=((30.0, 21.0), (15.0, 14.0), (50.0, 30.0)), colorless=True), _ROUTE_FACE),
    (Style("FCEOIL", "Nourishing Face Oil", "Velling Apothecary", "Beauty",
           (*SKINCARE, "Face Oils"), 26.0,
           "A lightweight face oil to wear under your cream.",
           "Face Oil", "bottle", pack("#e3b448", 500),
           volumes=((30.0, 26.0), (15.0, 17.0), (50.0, 38.0)), trending=True,
           colorless=True), _ROUTE_FACE),
    (Style("SPFFCE", "SPF 50 Face Sun Cream", "Velling Apothecary", "Beauty",
           ("Beauty", "Suncare", "Face Sun Cream"), 15.0,
           "A high protection sun cream for the face, with no white cast.",
           "Sun Cream", "bottle", pack("#f6f1e4", 470),
           volumes=((50.0, 15.0), (100.0, 22.0), (200.0, 34.0)), colorless=True),
     _ROUTE_FACE),
    (Style("VLCOIL", "Velvetmere Cream Body Oil Spray", "Kestlewood Cosmetics", "Beauty",
           ("Beauty", "Bath & Body", "Body Oils"), 30.0,
           "An all over dry oil spray from our Velvetmere Cream line.",
           "Body Oil", "fragrance", pack("#f3e3c3", 540),
           volumes=((100.0, 30.0), (50.0, 19.0), (200.0, 48.0)),
           product_line="Velvetmere Cream", colorless=True), _ROUTE_FACE),
    (Style("DCSATN", "400 Thread Count Sateen Duvet Cover", "Quillon Sleep", "Home",
           (*BED, "Duvet Covers"), 45.0,
           "Smooth cotton sateen with a soft sheen, in white or cream.",
           "Duvet Cover", "duvet", ((cw("White", WHITE), 300), (cw("Cream", "#efe6d2"), 260)),
           bed_sized=True, extra=(("thread_count", "Thread Count", "400"),)), _DEPT),
    (Style("CRDRIB", "Ribbed Cardigan", "Larkmoor", "Clothing",
           ("Womens", "Knitwear", "Cardigans"), 32.0,
           "A soft ribbed cardigan in cream or oat, with horn effect buttons.",
           "Cardigan", "cardigan",
           ((cw("Cream", "#efe6d2"), 420), (cw("Oat", "#d8cbb2"), 200)), pattern="plain",
           params=(("neckline", "crew"), ("sleeve", "long"))), _DEPT),
)  # fmt: skip

# --------------------------------------------------------------------------
# 13. "single bed" (mild): the size word is not applied, so big beds with no
# single and a chairbed that literally says "single" lead
# --------------------------------------------------------------------------

BEDS_NODE = ("Home", "Furniture", "Beds")
SIZES5 = tuple(BED_SIZE_DIMS)
BEDS = (
    Style("BDSHKR", "Shaker Wooden Bed Frame", "Brackenmere Home", "Home", BEDS_NODE, 299.0,
          "A solid wood bed frame, made in every size from single to super king.",
          "Bed", "bed_frame", pack("#b08a5a", 40), bed_frame=SIZES5, colorless=True,
          params=(("head", "shaker"),)),
    Style("BDMETL", "Metal Spindle Bed", "Brackenmere Home", "Home", BEDS_NODE, 189.0,
          "A painted metal bed with a spindle head end, in single, small double and double.",
          "Bed", "bed_frame", pack("#3a3a3a", 30), bed_frame=SIZES5[:3], colorless=True,
          params=(("head", "spindle"),)),
    Style("BDUPHL", "Upholstered Bed Frame", "Brackenmere Home", "Home", BEDS_NODE, 349.0,
          "A padded bed frame in a soft weave, from single to king size.",
          "Bed", "bed_frame", pack("#9a9a9a", 25), bed_frame=SIZES5[:4], colorless=True,
          params=(("head", "upholstered"),)),
)  # fmt: skip

_SIZE = "single to a size filter on the nested bed-size SKUs"
NOT_SINGLE = (
    (Style("BDOTTO", "Ottoman Storage Bed", "Brackenmere Home", "Home", BEDS_NODE, 999.0,
           "A lift up ottoman bed with deep storage, in double, king and super king.",
           "Bed", "bed_frame", pack("#7a6a5a", 600), bed_frame=SIZES5[2:], colorless=True,
           params=(("head", "ottoman"),)),
     _SIZE),
    (Style("BDSLGH", "Upholstered Sleigh Bed", "Brackenmere Home", "Home", BEDS_NODE, 1099.0,
           "A scrolled sleigh bed in soft velvet, in king and super king.",
           "Bed", "bed_frame", pack("#4a4a5a", 500), bed_frame=SIZES5[3:], colorless=True,
           params=(("head", "sleigh"),)),
     _SIZE),
    (Style("BDPANL", "Panelled Wooden Bed", "Brackenmere Home", "Home", BEDS_NODE, 899.0,
           "A panelled oak bed with a tall head end, in double, king and super king.",
           "Bed", "bed_frame", pack("#a07a4a", 450), bed_frame=SIZES5[2:], colorless=True,
           params=(("head", "panel"),)),
     _SIZE),
    # A sibling type that matches both words; it may rank below the beds.
    (Style("CHRCUB", "Single Cube Chairbed", "Brackenmere Home", "Home",
           ("Home", "Furniture", "Chairbeds"), 90.0,
           "A cube seat that unfolds into a single bed for guests.",
           "Chairbed", "chairbed", pack("#5a5a6a", 550), bed_frame=SIZES5[:1], trending=True,
           colorless=True), "type boost: Bed above Chairbed"),
    (Style("SOFBED", "Two Seater Sofa Bed", "Brackenmere Home", "Home",
           ("Home", "Furniture", "Sofas", "Sofa Beds"), 499.0,
           "A two seater sofa that pulls out into a double bed.",
           "Sofa Bed", "sofa", pack("#6a7a8a", 300), bed_frame=(SIZES5[2],), colorless=True),
     _SIZE),
)  # fmt: skip

# --------------------------------------------------------------------------
# 14. "rose gold": a two-word color split into words. "Rose Gold" is one
# structured color value (and, on metal goods, the finish), yet the words
# match rose bouquets with gold foliage and gold-plated rose quartz apart
# --------------------------------------------------------------------------

ROSE_GOLD = "Rose Gold"
JEWELLERY = ("Womens", "Jewellery", "Earrings")
BOUQUETS = ("Garden", "Flowers", "Bouquets")
ROSE_GOLDS = (
    Style("RGSTUD", "Cubic Zirconia Stud Earrings", "Wrenfield", "Clothing", JEWELLERY, 18.0,
          "Sparkling cubic zirconia studs set in rose gold plated sterling silver.",
          "Earrings", "earrings", one(cw(ROSE_GOLD, "#d8a28f"), 40), metal=True,
          params=(("kind", "stud"),)),
    Style("RGMESH", "Slim Mesh Strap Watch", "Calderby & Lune", "Clothing",
          ("Womens", "Watches", "Bracelet Watches"), 69.0,
          "A slim watch with a fine mesh strap and a rose gold tone case.",
          "Watch", "watch", one(cw(ROSE_GOLD, "#d8a28f"), 30), metal=True,
          params=(("strap", "mesh"),)),
    Style("RGLAMP", "Touch Dimmable Table Lamp", "Brackenmere Home", "Home",
          ("Home", "Lighting", "Lamps", "Table Lamps"), 35.0,
          "A touch dimmable lamp with a rose gold metal base and a white linen shade.",
          "Table Lamp", "table_lamp", one(cw(ROSE_GOLD, "#d8a28f"), 25), metal=True,
          params=(("shade", "#f7f3ea"),)),  # the white linen shade; the base is the rose gold
    Style("RGCHRG", "Wireless Charging Pad", "Harbour & Pine", "Home",
          ("Home", "Electricals", "Phone Accessories", "Wireless Chargers"), 22.0,
          "A slim wireless charging pad with a rose gold metal rim.",
          "Wireless Charger", "charging_pad", one(cw(ROSE_GOLD, "#d8a28f"), 20), metal=True),
    Style("RGHLIT", "Glow Powder Highlighter", "Velling Apothecary", "Beauty",
          ("Beauty", "Make-Up", "Face", "Highlighter"), 19.0,
          "A silky powder highlighter with a rose gold shimmer.",
          "Highlighter", "compact", one(cw(ROSE_GOLD, "#d8a28f"), 15), unit=(8.0, "g")),
)  # fmt: skip

_COLOR = "color filter: Rose Gold is one color value; a bouquet's color is its flower's"
#: Gold sprayed eucalyptus or ruscus: a bouquet drawing's foliage, not its color.
GOLD_LEAF = "#d4af37"
NOT_ROSE_GOLD = (
    (Style("BQBLSH", "Blush Rose & Gold Eucalyptus Bouquet", "Goldfield Farms", "Garden",
           BOUQUETS, 35.0,
           "Blush pink roses with gold sprayed eucalyptus, hand tied.",
           "Bouquet", "bouquet", one(cw("Pink", "#f3c6cf"), 560),
           params=(("foliage", GOLD_LEAF),)), _COLOR),
    (Style("BQREDR", "Classic Red Rose Bouquet", "Goldfield Farms", "Garden", BOUQUETS, 40.0,
           "Twelve long stem red roses wrapped in kraft paper with a gold ribbon.",
           "Bouquet", "bouquet", one(cw("Red", "#b0182f"), 520)), _COLOR),
    (Style("BQWHGF", "White Rose Bouquet with Gold Foliage", "Goldfield Farms", "Garden",
           BOUQUETS, 32.0,
           "White roses and gold painted ruscus in a gift box.",
           "Bouquet", "bouquet", one(cw("White", WHITE), 410),
           params=(("foliage", GOLD_LEAF),)), _COLOR),
    (Style("RQHOOP", "Gold Plated Rose Quartz Hoop Earrings", "Wrenfield", "Clothing",
           (*JEWELLERY, "Hoop Earrings"), 24.0,  # its title names the node (gen#423, gen#283)
           "Rose quartz drops on gold plated hoops.",
           "Earrings", "earrings", one(cw("Yellow Gold", "#d4af37"), 300), metal=True,
           params=(("kind", "hoop"), ("stone", "#f3c6cf")),
           extra=(("stone", "Stone", "rose quartz"),)), _COLOR),
    # The other finishes of a metal good: the color filter keeps them out.
    (Style("LKWTCH", "Link Bracelet Watch", "Larkmoor", "Clothing",
           ("Womens", "Watches", "Bracelet Watches"), 79.0,
           "A link bracelet watch with a sunray dial, in yellow gold, white gold or silver tone.",
           "Watch", "watch",
           ((cw("Yellow Gold", "#d4af37"), 90), (cw("White Gold", "#e5e4e2"), 60),
            (cw("Silver", "#c0c0c0"), 50)), metal=True, params=(("strap", "link"),)), _COLOR),
)  # fmt: skip

# --------------------------------------------------------------------------
# 15. "cups": one word, a sense in two departments. In Home a cup is
# drinkware; in Lingerie it is the cup of a bra or a cup size (A to E). Bras
# titled "... Cup Bra" outsell the drinkware, and most drinkware says "Mug" or
# "Tumbler", so a bare "cups" fills the page with bras.
# --------------------------------------------------------------------------

DRINKWARE = ("Home", "Kitchen & Dining", "Drinkware")
BRAS = ("Womens", "Lingerie", "Bras")
LINGERIE = "Lingerie & Nightwear"


def bra_sizes(cups: str) -> tuple[str, ...]:
    """Band x cup, 32 to 38 in every cup letter of ``cups``."""
    return tuple(f"{band}{cup}" for band in (32, 34, 36, 38) for cup in cups)


CUPS = (
    Style("DRKMUG", "Speckled Stoneware Mug", "Brackenmere Home", "Home", (*DRINKWARE, "Mugs"),
          8.0, "A glazed stoneware mug with a speckled finish. Holds 350ml.",
          "Mug", "mug", ((cw("Cream", ECRU), 40), (cw("Sage", "#9caf88"), 25))),
    Style("DRKLAT", "Large Latte Mug", "Pewley Table", "Home", (*DRINKWARE, "Mugs"), 10.0,
          "A wide, tall porcelain mug for lattes and hot chocolate.",
          "Mug", "mug", one(cw("White", WHITE), 45)),
    Style("DRKTMB", "Double Walled Tumbler", "Pewley Table", "Home",
          (*DRINKWARE, "Tumblers"), 14.0,
          "An insulated steel tumbler with a sliding lid. Keeps drinks hot for 6 hours.",
          "Tumbler", "mug", ((cw("Black", BLACK), 50), (cw("Navy", NAVY), 30))),
    Style("DRKSAU", "Fine Bone China Cup and Saucer", "Pewley Table", "Home",
          (*DRINKWARE, "Cups & Saucers"), 12.0,
          "A fine bone china tea cup with a matching saucer.",
          "Cup", "mug", one(cw("White", WHITE), 35)),
    Style("DRKTRV", "Leakproof Travel Cup", "Brackenmere Home", "Home",
          (*DRINKWARE, "Travel Cups"), 16.0,
          "A reusable travel cup with a leakproof lid that fits most car holders.",
          "Travel Cup", "mug", ((cw("Charcoal", "#4a4a4a"), 60), (cw("Pink", "#f3c6cf"), 20))),
    Style("DRKSET", "Set of 4 Espresso Cups", "Brackenmere Home", "Home",
          (*DRINKWARE, "Cups & Saucers"), 18.0,
          "Four small porcelain espresso cups in a gift box.",
          "Cup Set", "mug", one(cw("Stone", "#c8bfae"), 30)),
)  # fmt: skip

_BRA = "route: a bare cup goes to Drinkware; a bra word in the query switches the route off"
_TAIL = "route: outside the Drinkware node"
NOT_CUPS = (
    (Style("CUPDEM", "Lace Demi Cup Bra A-E", "Thistle & Wren", LINGERIE, (*BRAS, "Demi Bras"),
           22.0, "A lace demi cup bra with underwired cups and adjustable straps.",
           "Bra", "bra", ((cw("Black", BLACK), 380), (cw("Pink", "#f3c6cf"), 300)),
           pattern="plain", sizes=bra_sizes("ABCDE")), _BRA),
    (Style("CUPFUL", "Smooth Full Cup Bra B-G", "Thistle & Wren", LINGERIE,
           (*BRAS, "Full Cup Bras"), 20.0,
           "A non padded full cup bra with smooth cups for everyday support.",
           "Bra", "bra", ((cw("White", WHITE), 340), (cw("Black", BLACK), 310)),
           pattern="plain", sizes=bra_sizes("BCDEFG")), _BRA),
    (Style("CUPMLD", "Moulded Cup T-Shirt Bra", "Thistle & Wren", LINGERIE,
           (*BRAS, "T-Shirt Bras"), 18.0,
           "A seamless t-shirt bra with lightly padded moulded cups.",
           "Bra", "bra", one(cw("Champagne", "#e8d3b0"), 620),
           pattern="plain", sizes=bra_sizes("ABCDE")), _BRA),
    (Style("CUPBAL", "Padded Balcony Bra", "Thistle & Wren", LINGERIE,
           (*BRAS, "Balcony Bras"), 20.0,
           "A balcony bra with padded half cups and a low, wide neckline.",
           "Bra", "bra", one(cw("Black", BLACK), 600),
           pattern="plain", sizes=bra_sizes("ABCDE")), _BRA),
    (Style("CUPCAK", "Foil Cupcake Cases", "Brackenmere Home", "Home",
           ("Home", "Kitchen & Dining", "Bakeware", "Cake Cases"), 3.0,
           "Fifty foil baking cups for cupcakes and muffins.",
           "Cupcake Cases", "cupcake", one(cw("Silver", "#c0c0c0"), 90)), _TAIL),
    (Style("CUPHLD", "Car Cup Holder Organiser", "Harbour & Pine", "Home",
           ("Home", "Electricals", "Car Accessories", "Cup Holders"), 9.0,
           "A cup holder insert that holds two cups and a phone.",
           "Cup Holder", "tray", one(cw("Black", BLACK), 70)), _TAIL),
    (Style("CUPTRO", "Engraved Trophy Cup", "Wrenfield", "Gifts",
           ("Gifts", "Personalised Gifts", "Trophies"), 25.0,
           "A silver plated trophy cup with two handles, engraved with your message.",
           "Trophy", "trophy", one(cw("Silver", "#c0c0c0"), 40), metal=True), _TAIL),
)  # fmt: skip

#: Words that put "cup" in a bra's sense: the cups policy is off when one is in the query.
BRA_WORDS = (r"\bbras?\b", r"\bdemi\b", r"\bbalcon(y|ette)\b", r"\bplunge\b",
             r"\b([a-k]|dd|ff|gg|hh|jj)\s?cups?\b", r"\b\d\d([a-k]|dd|ff|gg)\b",
             r"\b[a-k]\s?-\s?[a-k]\b")  # fmt: skip


def _is_bra(d: dict) -> bool:
    return d.get("product_type") == "Bra" or "Bras" in d.get("category_path", ())


# --------------------------------------------------------------------------
# Offers (not a query row): third-party brands lead, online only, with a
# sub-collection label; one own-brand line on a was-price
# --------------------------------------------------------------------------

OFFERS = (
    Style("OFRTEE", "Active Training Tee", "Stridewell", "Clothing",
          ("Womens", "Sportswear", "Sports Tees"), 15.0,
          "A quick drying training tee with mesh panels.",
          "T-Shirt", "tshirt", one(cw("Black", BLACK), 210), was_price=25.0,
          size_range="regular", pattern="plain", online_only=True,
          sub_collection="The Active Edit"),
    Style("OFRBLS", "Pleated Crepe Blouse", "Calderby & Lune", "Clothing",
          ("Womens", "Shirts & Blouses", "Blouses"), 41.0,
          "A fluid crepe blouse with a pleated yoke.",
          "Blouse", "blouse", one(cw("Ecru", ECRU), 160), was_price=59.0,
          size_range="regular", pattern="plain", online_only=True,
          sub_collection="The Weekend Edit"),
    Style("OFRBRA", "Seamless Smoothing Bra", "Thistle & Wren", "Lingerie & Nightwear",
          ("Womens", "Lingerie", "Bras", "T-Shirt Bras"), 15.0,
          "A seamless non wired bra with smooth moulded cups.",
          "Bra", "bra", one(cw("Black", BLACK), 140), was_price=22.0, pattern="plain",
          online_only=True),
    Style("OFRPJS", "Cotton Pyjama Shorts", "Thistle & Wren", "Lingerie & Nightwear",
          ("Womens", "Nightwear", "Pyjama Bottoms"), 12.0,
          "Soft cotton jersey pyjama shorts with a drawstring waist.",
          "Pyjama Shorts", "shorts", one(cw("Pink", "#f3c6cf"), 120), was_price=18.0,
          pattern="plain", online_only=True),
)  # fmt: skip

#: Not a query row: the food sense of a word that is also a lipstick shade.
HONEY = Style("HONBLS", "Clear Blossom Honey", "Copper Hill Preserves", FOOD,
              ("Food & Drink", "Food Cupboard", "Honey"), 4.0,
              "A clear, mild blossom honey for tea and toast.",
              "Honey", "jar", pack("#e0a030", 120), unit=(340.0, "g"),
              colorless=True)  # fmt: skip

#: Not a query row: the gen#125 ruling's worked example, one product holding
#: 11 SKUs (navy and white in S-XL, heather grey in S-L). The color query of
#: :mod:`es_proof` ("navy tee") measures a nested color filter on it.
CREW_TEE = Style("CRWTEE", "Mens Crew Neck Cotton Tee", "Harbour & Pine", "Clothing",
                 ("Mens", "Tops", "T-Shirts"), 14.0,
                 "A regular fit tee in soft combed cotton jersey, with a ribbed collar.",
                 "T-Shirt", "top",
                 ((cw("Navy", NAVY), 12), (cw("White", WHITE), 9),
                  (cw("Heather Grey", "#9a9ca0"), 6)),
                 neckline="crew", pattern="plain", size_range="regular",
                 sizes=("S", "M", "L", "XL"), not_made=(("Heather Grey", "XL"),),
                 params=(("neckline", "crew"), ("sleeve", "short")))  # fmt: skip

#: A word whose senses live in different fields or domains, so a policy that
#: reads one field must not pool them.
COLLISIONS = (
    {"word": "thread",
     "senses": ["attributes.thread_count", "attributes.thread_size"],
     "retail_keys": ["thread_count"],
     "industrial_keys": ["thread_size", "thread_type", "thread_direction"],
     "note": "bedding threads per square inch (a unitless count) vs a screw thread's "
             "size (1/4-20: diameter and pitch) and its type; one key each, never merged"},
    {"word": "cup", "query": "cups",
     "senses": [PATH_SEPARATOR.join(DRINKWARE), PATH_SEPARATOR.join(BRAS)],
     "meanings": {"Home": "drinkware: a cup, a mug, a travel cup or a set of cups",
                  LINGERIE: "the cup of a bra, or a cup size (A to E)"},
     "personas": {"a home shopper buying drinkware": "Home",
                  "a lingerie shopper with a bra word in the query": LINGERIE},
     "note": "a bare cup(s) is drinkware; the bra sense needs a bra word (bra, demi, "
             "balcony, a cup size such as D cup or A-E) in the query (class 15)"},
)  # fmt: skip


def _type(*types: str) -> Callable[[dict], bool]:
    return lambda d: d.get("product_type") in types and d.get("audience") == "adult"


ROWS = (
    ClassRow(2, "Sibling types share a head word", "mattress topper", "a mattress topper",
             _type("Mattress Topper"), "product-type boost: topper; protector and mattress buried",
             Policy(boosts=(("product_type", ("Mattress Topper",), 10.0),
                            ("product_type", ("Mattress Protector", "Mattress",
                                              "Pillow Protector"), 0.2))),
             TOPPERS, MATTRESS),
    ClassRow(3, "Over-broad style synonym plus a bestseller boost", "balloon jeans",
             "balloon leg jeans",
             lambda d: _type("Jeans")(d) and d.get("leg_style") == "balloon",
             "exact style term first, synonym second",
             Policy(boosts=(("leg_style", ("balloon",), 10.0),)),
             BALLOON, BARREL),
    ClassRow(4, "A neckline word matched as a keyword", "womens boat neck top",
             "a boat (or slash) neck top",
             lambda d: _type("Top")(d) and d.get("neckline") in ("boat", "slash"),
             "neckline attribute: boat = slash, others buried; type = top",
             Policy(filters=(("product_type", ("Top",)),),
                    boosts=(("neckline", ("boat", "slash"), 10.0),)),
             BOAT, NECK),
    ClassRow(5, "Product type, pattern and audience not enforced",
             "check contrast bomber jacket", "an adult check bomber jacket",
             lambda d: _type("Bomber Jacket")(d) and d.get("pattern") == "check",
             "type = bomber (hard), pattern = check (boost), audience adult by default",
             Policy(filters=(("product_type", ("Bomber Jacket",)), ("audience", ("adult",))),
                    boosts=(("pattern", ("check",), 5.0),)),
             CHECK, BOMBER),
    ClassRow(6, "Size range and sale state not extracted", "petite sale",
             "a petite item on sale",
             lambda d: "petite" in d.get("size_range", ()) and on_sale(d),
             "petite to a size-range filter; sale to an on-sale filter",
             Policy(filters=(("size_range", ("petite",)),), on_sale=True),
             PETITE, BESTSELLERS),
    ClassRow(7, "Sale word ignored", "womens sale dresses", "an adult dress on sale",
             lambda d: _type("Dress")(d) and on_sale(d),
             "sale to an on-sale filter (price below was-price)",
             Policy(filters=(("product_type", ("Dress",)), ("audience", ("adult",))),
                    on_sale=True),
             SALE_DRESSES, FULL_PRICE),
    ClassRow(9, "Pack count only in title spellings", "5 pack socks", "an adult 5 pack of socks",
             lambda d: _type("Socks")(d) and d.get("units_per_pack") == 5,
             "units_per_pack (a C62 count) as a filter; audience adult by default",
             Policy(filters=(("units_per_pack", ("5",)), ("audience", ("adult",)))),
             FIVE_PACKS, PACKS),
    ClassRow(10, "A food word inside compounds and modifiers", "beer", "a beer",
             lambda d: d.get("product_type") == "Beer",
             "route to the Beer node: ginger beer, root beer and beer-battered food are outside",
             Policy(route=PATH_SEPARATOR.join(BEER_NODE)),
             BEERS, NOT_BEER),
    ClassRow(11, "A fruit plural read as a flavour and a color", "oranges", "oranges (the fruit)",
             lambda d: d.get("category_leaf") == "Oranges",
             "route to the Oranges node: recalls an easy peeler that never says orange",
             Policy(route=PATH_SEPARATOR.join((*CITRUS, "Oranges"))),
             ORANGES, NOT_ORANGES),
    ClassRow(12, "A type word that is also a color and a line name", "face cream",
             "a face cream",
             lambda d: d.get("category_leaf") == "Face Creams",
             "route to the Face Creams node: a cream sofa, a powder and an oil are outside",
             Policy(route=PATH_SEPARATOR.join((*CREAMS, "Face Creams"))),
             FACE_CREAMS, NOT_FACE_CREAM),
    ClassRow(13, "A size word not applied (mild)", "single bed", "a bed made in single",
             lambda d: d.get("product_type") == "Bed" and any(
                 s.get("bed_size") == SIZES5[0] and s["in_stock"] for s in d["skus"]),
             "single to a nested in-stock bed-size filter; type Bed boosted over a chairbed",
             Policy(sku_filters=(("bed_size", (SIZES5[0],)),),
                    boosts=(("product_type", ("Bed",), 10.0),)),
             BEDS, NOT_SINGLE),
    ClassRow(14, "A two-word color split into words", "rose gold",
             "a product whose color is Rose Gold",
             lambda d: any(s.get("color") == ROSE_GOLD for s in d["skus"]),
             "color vocabulary (a terms aggregation over the color field) holds Rose Gold as "
             "one value: the phrase becomes a color filter",
             Policy(sku_filters=(("color", (ROSE_GOLD,)),)),
             ROSE_GOLDS, NOT_ROSE_GOLD),
    ClassRow(15, "One word, a sense in two departments", "cups", "drinkware (a cup or a mug)",
             lambda d: "/".join(d.get("category_path", ())).startswith(
                 PATH_SEPARATOR.join(DRINKWARE) + PATH_SEPARATOR),
             "a bare cup(s) routes to the Drinkware node; a bra word (bra, demi, balcony, "
             "a cup size) switches the route off, so the bra sense stays reachable",
             Policy(route=PATH_SEPARATOR.join(DRINKWARE), unless=BRA_WORDS,
                    unless_text="bra, demi, balcony or a cup size"),
             CUPS, NOT_CUPS,
             controls=(Control("d cup bra", "a bra", _is_bra),),
             # An espresso cup is a cup, so it may lead the bare baseline too: the claim is
             # that the bras are in the baseline top 3, not that no drinkware is.
             baseline_holds=Control("cups", "a bra", _is_bra)),
)  # fmt: skip
