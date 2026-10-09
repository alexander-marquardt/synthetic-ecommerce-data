"""The distractors three failure classes need at catalog scale (gen#125): data only.

:func:`scale.templates` builds these after :mod:`breadth_rows`. On the 76K-SKU build
three of the retailer's failure classes did not reproduce, because the catalog lacked
the products that win a query without a policy:

- **"mattress topper"** (class 2). :data:`MORE_TOPPERS` are the true answers, with weak
  sales. :data:`PROTECTORS` (six titled "Mattress Topper Protector", so the text ties),
  :data:`MATTRESSES` and :data:`PILLOW_PROTECTORS` share the words and out-sell every
  topper, in sales and in reviews.
- **"balloon jeans"** (class 3). :data:`BARRELS` are bestselling barrel-leg jeans (some
  kids', some trousers) whose text says "balloon-shaped barrel leg": the search-time
  synonym (``balloon => balloon, barrel``) and the popularity boost lift them over
  :data:`MORE_BALLOONS`, the true balloon-leg jeans with weaker signals.
- **"petite sale"** (classes 6 and 7). :data:`PETITE` is a substantial set, cut in
  petite lengths or sizes, of which only every fifth is discounted; :data:`SALE` are
  discounted regular-range items that say "petite" nowhere.

Every row is a :class:`class_model.Style`, ``reviews`` pinned where a row must out-sell
another. Names and codes are invented; a row's numbers come from its position, never from
chance, so the build is deterministic.
"""

from __future__ import annotations

from class_model import LEGS3, Style, one
from variants import cw

BED = ("Home", "Bedding")
WJEANS = ("Women", "Jeans")
DENIM, MID, LIGHT, BLACK, NAVY = "#4a6a94", "#5b7aa6", "#9fb4cf", "#2a2a2e", "#26365c"
WHITE, STONE, OLIVE = "#ffffff", "#d9d3c7", "#6b6b3a"


def _price(n: int, low: float, span: int, step: float = 0.5) -> float:
    """A price that differs by row: ``low`` plus ``n`` steps, wrapping after ``span``."""
    return low + (n * 7 % span) * step


# --------------------------------------------------------------------------
# "mattress topper"
# --------------------------------------------------------------------------

_FILLS = ("Gel Infused Memory Foam", "Bamboo Fibre", "Goose Feather", "Microfibre",
          "Egg Box Foam", "Cooling Gel", "Duck Feather", "Pure Latex",
          "Cotton Quilted")  # fmt: skip
MORE_TOPPERS = tuple(
    Style(f"DTP{n:02d}", f"{fill} Mattress Topper",
          ("Quillon Sleep", "Brackenmere Home")[n % 2], "Home",
          (*BED, "Mattress Toppers"), _price(n, 30.0, 40, 2.0),
          f"{fill} topper that lifts a tired mattress. Corner straps hold it in place.",
          "Mattress Topper", "mattress_topper", one(cw("White", WHITE), 2 + n * 2),
          bed_sized=True, reviews=40 + n * 60, params=(("depth", f"{3 + n % 5}cm"),))
    for n, fill in enumerate(_FILLS)
)

_PROTECTOR_KINDS = ("Quilted", "Waterproof", "Cotton Terry", "Cool Touch", "Bamboo",
                    "Anti Allergy", "Fitted", "Hypoallergenic", "Breathable", "Smooth Top",
                    "Zipped", "Deep Fit")  # fmt: skip
#: Eighteen plain protectors, then six whose title also says "Topper": the text ties with
#: the toppers, so only the sales decide.
PROTECTORS = tuple(
    Style(f"DPR{n:02d}",
          f"{kind} Mattress {'Topper ' if n >= 18 else ''}Protector",
          ("Quillon Sleep", "Brackenmere Home")[n % 2], "Home",
          (*BED, "Mattress Protectors"), _price(n, 14.0, 20),
          f"{kind} mattress protector that guards the mattress. "
          + ("Padded like a mattress topper, it keeps the bed fresh."
             if n >= 18 else "Fits over a mattress topper or under one."),
          "Mattress Protector", "mattress_protector",
          one(cw(("White", "Ice", "Stone")[n % 3], (WHITE, "#e6eef2", STONE)[n % 3]),
              1400 - n * 30),
          bed_sized=True, reviews=3400 - n * 40)
    for n, kind in enumerate((*_PROTECTOR_KINDS, *_PROTECTOR_KINDS))
)

_MATTRESS_KINDS = ("Open Coil", "Memory Foam", "Pocket Sprung 1000", "Orthopaedic",
                   "Hybrid", "Rolled", "Firm Pocket", "Cool Gel")  # fmt: skip
MATTRESSES = tuple(
    Style(f"DMA{n:02d}", f"{kind} Mattress", "Quillon Sleep", "Home", (*BED, "Mattresses"),
          _price(n, 150.0, 30, 10.0),
          f"{kind} mattress with a built-in comfort topper layer.",
          "Mattress", "mattress", one(cw("Stone", STONE), 800 - n * 40),
          bed_sized=True, reviews=2600 - n * 50, params=(("depth", f"{20 + n}cm"),))
    for n, kind in enumerate(_MATTRESS_KINDS)
)

PILLOW_PROTECTORS = tuple(
    Style(f"DPP{n:02d}", f"{kind} Pillow Protectors, Pair", "Quillon Sleep", "Home",
          (*BED, "Pillow Protectors"), _price(n, 6.0, 10),
          f"{kind} pillow protectors to match your mattress protector and mattress topper.",
          "Pillow Protector", "pillow", one(cw("White", WHITE), 900 - n * 50),
          reviews=2400 - n * 60)
    for n, kind in enumerate(("Zipped", "Quilted", "Waterproof", "Cotton", "Bamboo", "Cool"))
)

# --------------------------------------------------------------------------
# "balloon jeans"
# --------------------------------------------------------------------------

_BARREL_CUTS = ("Mid Rise", "High Rise", "Low Rise", "Cropped", "Stretch", "Raw Hem",
                "Washed", "Wide", "Loose", "Slouchy", "Rigid", "Vintage")  # fmt: skip
_WASHES = (("Mid Wash", MID), ("Light Wash", LIGHT), ("Black", BLACK), ("Indigo", DENIM))
#: Bestselling barrel-leg jeans; their text calls the leg "balloon-shaped" or "balloon".
BARRELS = tuple(
    Style(f"DBR{n:02d}", f"{cut} Barrel Leg Jeans", ("Ottery Denim", "Ferrowick Denim")[n % 2],
          "Clothing", (*WJEANS, "Barrel Jeans"), _price(n, 28.0, 24),
          ("Our bestselling barrel leg jeans: a balloon-shaped leg, full at the knee and "
           "narrow at the ankle." if n % 2 else
           "Barrel leg jeans cut in a rounded balloon shape through the thigh and knee."),
          "Jeans", "trousers", ((cw(*_WASHES[n % 4]), 2400 - n * 110),),
          leg_style="barrel", pattern="plain", lengths=LEGS3, reviews=3000 - n * 50,
          params=(("fit", "barrel"), ("rise", ("mid", "high", "low")[n % 3])))
    for n, cut in enumerate(_BARREL_CUTS)
)
KIDS_BARRELS = tuple(
    Style(f"DBK{n:02d}", f"{who}' Barrel Leg Jeans ({age} Yrs)", "Little Fernby", "Clothing",
          ("Kids", who, "Jeans"), _price(n, 12.0, 8),
          "Barrel leg jeans for kids with a balloon-shaped leg and an adjustable waist.",
          "Jeans", "trousers", ((cw(*_WASHES[n % 4]), 1500 - n * 150),), audience="kids",
          leg_style="barrel", pattern="plain", lengths=("Regular",), reviews=2800 - n * 90,
          params=(("fit", "barrel"), ("rise", "mid")))
    for n, (who, age) in enumerate((("Girls", "6-16"), ("Boys", "6-16"),
                                    ("Girls", "9-16"), ("Boys", "9-16")))
)
BARREL_TROUSERS = tuple(
    Style(f"DBT{n:02d}", f"{fab} Barrel Leg Trousers", "Larkmoor", "Clothing",
          ("Women", "Trousers", "Barrel Trousers"), _price(n, 24.0, 12),
          f"{fab} barrel leg trousers with a balloon-shaped leg and a pressed crease.",
          "Trousers", "trousers", ((cw(*(("Khaki", OLIVE), ("Black", BLACK), ("Stone", STONE))[n]),
                                    1100 - n * 120),),
          leg_style="barrel", pattern="plain", lengths=LEGS3, reviews=2700 - n * 70,
          params=(("fit", "barrel"), ("rise", "high")))
    for n, fab in enumerate(("Twill", "Cord", "Linen Blend"))
)
#: The true balloon-leg jeans of the new rows: fewer than the barrels, weaker signals.
MORE_BALLOONS = tuple(
    Style(f"DBL{n:02d}", f"{cut} Balloon Leg Jeans", ("Ottery Denim", "Ferrowick Denim")[n % 2],
          "Clothing", (*WJEANS, "Balloon Jeans"), _price(n, 36.0, 10),
          "Full through the thigh and knee, curving back in at the ankle.",
          "Jeans", "trousers", ((cw(*_WASHES[n % 4]), 12 + n * 8),),
          leg_style="balloon", pattern="plain", lengths=LEGS3, reviews=60 + n * 90,
          params=(("fit", "balloon"), ("rise", "high")))
    for n, cut in enumerate(("Slouchy", "Relaxed", "Curved"))
)

# --------------------------------------------------------------------------
# "petite sale"
# --------------------------------------------------------------------------

_BRANDS = ("Larkmoor", "Wrenfield", "Harbour & Pine", "Ottery Denim")
_PALETTE = (("Black", BLACK), ("Navy", NAVY), ("Stone", STONE), ("Khaki", OLIVE),
            ("Mid Wash", MID), ("Grey", "#8a8a8e"))  # fmt: skip
_FABRICS = ("Stretch", "Linen Blend", "Cotton Twill", "Pleated", "Pull-On", "Belted",
            "Ponte", "Pinstripe", "Crinkle", "Cord", "Satin", "Woven", "Cropped",
            "Seamed")  # fmt: skip
#: (noun, path, leg style, fit) of the petite-length legwear.
_LEGWEAR = (("Straight Jeans", (*WJEANS, "Straight Jeans"), "straight", "straight"),
            ("Slim Jeans", (*WJEANS, "Slim Jeans"), "slim", "slim"),
            ("Wide Leg Trousers", ("Women", "Trousers", "Wide Leg Trousers"), "wide", "wide_leg"),
            ("Tapered Trousers", ("Women", "Trousers", "Tapered Trousers"), "tapered", "slim"),
            ("Straight Trousers", ("Women", "Trousers", "Straight Trousers"), "straight",
             "straight"), ("Slim Trousers", ("Women", "Trousers", "Slim Trousers"), "slim", "slim"))
#: (noun, path, shape) of the petite garments sized by number.
_GARMENTS = (("Wrap Midi Dress", ("Women", "Dresses", "Wrap Dresses"), "dress"),
             ("Shirt Dress", ("Women", "Dresses", "Shirt Dresses"), "dress"),
             ("Maxi Dress", ("Women", "Dresses", "Maxi Dresses"), "dress"),
             ("Jersey Top", ("Women", "Tops", "Jersey Tops"), "top"),
             ("Long Sleeve Top", ("Women", "Tops", "Long Sleeve Tops"), "top"))
UK_SIZES = ("6", "8", "10", "12", "14", "16")


def _petite(n: int) -> Style:
    """The ``n``th petite style: legwear in the petite lengths, then numbered garments.

    Every fifth is discounted (a was-price over the price); the rest are full price.
    """
    legwear = n < 90
    fabric = _FABRICS[n % len(_FABRICS)]
    price = 18.0 + n * 0.5
    was = float(round(price * 1.4)) if n % 5 == 0 else None
    color = cw(*_PALETTE[n // 3 % len(_PALETTE)])
    common = {"was_price": was, "reviews": None}
    if legwear:
        noun, path, leg, fit = _LEGWEAR[n % len(_LEGWEAR)]
        return Style(f"DPT{n:03d}", f"Petite {fabric} {noun}", _BRANDS[n % 4], "Clothing", path,
                     price, f"{fabric} {noun.lower()} with a shorter inside leg, made for petite "
                     "heights.", "Jeans" if "Jeans" in noun else "Trousers", "trousers",
                     one(color, 10 + n % 40), lengths=("Extra Short", "Short/Petite"),
                     leg_style=leg, pattern="plain", **common,
                     params=(("fit", fit), ("rise", ("mid", "high")[n % 2])))
    noun, path, shape = _GARMENTS[n % len(_GARMENTS)]
    return Style(f"DPT{n:03d}", f"Petite {fabric} {noun}", _BRANDS[n % 4], "Clothing", path,
                 price, f"{fabric} {noun.lower()} cut shorter in the body and hem for "
                 "petite frames.", noun.split()[-1], shape, one(color, 10 + n % 40),
                 sizes=UK_SIZES, size_range="petite", pattern="plain", **common)


PETITE = tuple(_petite(n) for n in range(150))


def _sale(n: int) -> Style:
    """The ``n``th discounted regular-range style: no word "petite" in it."""
    fabric = _FABRICS[(n + 5) % len(_FABRICS)]
    price = 16.0 + n * 0.5 + 0.25 * (n % 2)
    was = float(round(price * 1.5))
    color = cw(*_PALETTE[n // 2 % len(_PALETTE)])
    if n % 2:
        noun, path, shape = _GARMENTS[n % len(_GARMENTS)]
        return Style(f"DSL{n:03d}", f"Womens {fabric} {noun}", _BRANDS[n % 4], "Clothing", path,
                     price, f"{fabric} {noun.lower()} for women.",
                     noun.split()[-1], shape, one(color, 60 + n * 3), sizes=UK_SIZES,
                     size_range="regular", pattern="plain", was_price=was)
    noun, path, leg, fit = _LEGWEAR[n % len(_LEGWEAR)]
    return Style(f"DSL{n:03d}", f"{fabric} {noun}", _BRANDS[n % 4], "Clothing", path, price,
                 f"{fabric} {noun.lower()} in a regular and long length.",
                 "Jeans" if "Jeans" in noun else "Trousers", "trousers", one(color, 60 + n * 3),
                 lengths=("Regular", "Long"), leg_style=leg, pattern="plain", was_price=was,
                 params=(("fit", fit), ("rise", ("mid", "high")[n % 2])))


SALE = tuple(_sale(n) for n in range(60))

STYLES = (*MORE_TOPPERS, *PROTECTORS, *MATTRESSES, *PILLOW_PROTECTORS, *BARRELS,
          *KIDS_BARRELS, *BARREL_TROUSERS, *MORE_BALLOONS, *PETITE, *SALE)


def docs() -> list[dict]:
    """Every row's catalog document, in the order of :data:`STYLES`."""
    return [s.doc() for s in STYLES]

