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

- **"steak"** (gen#264). A food noun used as the modifier of a tool or serving item: the
  steak knives (:data:`STEAK_KNIVES`), a steak plate, a steak board and a cast-iron steak
  weight (:data:`STEAK_WARE`) win the text match, and a tin of tuna steaks shares the word. The
  true answers are beef steaks in the grocery build (``grocery_rows``, families ``SKS`` to
  ``SKW`` and ``TUS``): their titles name the cut and run to five words or more, the knives' lead
  with "Steak Knife" and two are two or four words long, so BM25's length norm puts a knife first.
  Their sales are modest (every knife sells more than the median beef steak, not more than
  every steak): the short title decides, nothing is stuffed.

Every row is a :class:`class_model.Style`, ``reviews`` pinned where a row must out-sell
another. Names and codes are invented; a row's numbers come from its position, never from
chance, so the build is deterministic.
"""

from __future__ import annotations

from class_model import LEGS3, Style, one
from variants import cw

BED = ("Home", "Bedding")
WJEANS = ("Womens", "Jeans")
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
                "Distressed", "Wide", "Loose", "Slouchy", "Rigid", "Vintage")  # fmt: skip
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
          ("Womens", "Trousers", "Barrel Trousers"), _price(n, 24.0, 12),
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
            ("Wide Leg Trousers", ("Womens", "Trousers", "Wide Leg Trousers"), "wide", "wide_leg"),
            ("Tapered Trousers", ("Womens", "Trousers", "Tapered Trousers"), "tapered", "slim"),
            ("Straight Trousers", ("Womens", "Trousers", "Straight Trousers"), "straight",
             "straight"),
            ("Slim Trousers", ("Womens", "Trousers", "Slim Trousers"), "slim", "slim"))
#: (noun, path, shape) of the petite garments sized by number.
_GARMENTS = (("Wrap Midi Dress", ("Womens", "Dresses", "Wrap Dresses"), "dress"),
             ("Shirt Dress", ("Womens", "Dresses", "Shirt Dresses"), "dress"),
             ("Maxi Dress", ("Womens", "Dresses", "Maxi Dresses"), "dress"),
             ("Jersey Top", ("Womens", "Tops", "Jersey Tops"), "top"),
             ("Long Sleeve Top", ("Womens", "Tops", "Long Sleeve Tops"), "top"))
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

# --------------------------------------------------------------------------
# "steak"
# --------------------------------------------------------------------------

KD = ("Home", "Kitchen & Dining")
STEEL = cw("Silver", "#cfd5da", "solid", "#8f989f")
CAST = cw("Black", "#2f2f35", "solid", "#8f989f")
WOODEN = cw("Natural", "#c9a46a", "solid", "#7d5634")


def _cutlery(code: str, title: str, count: int, handle: str, edge: str, color, sold: int,
             price: float, desc: str, piece: str = "steak knife") -> Style:  # fmt: skip
    """A steak-knife row: ``count`` pieces, a blade ``edge`` and a ``handle``."""
    kind = "Steak Knife and Fork" if "fork" in piece else "Steak Knife"
    return Style(code, title, "Lanternby" if handle == "wooden" else "Hearth & Table", "Home",
                 (*KD, "Cutlery"), price, desc, "Cutlery", "cutlery_piece", one(color, sold),
                 units_per_pack=count, colorless=False,
                 extra=(("cutlery_type", "Cutlery type", kind),
                        ("material", "Material", "Stainless Steel"),
                        ("handle", "Handle", handle.title()), ("edge", "Edge", edge.title())),
                 params=(("piece", piece), ("handle", handle), ("count", str(count)),
                         ("edge", edge)))  # fmt: skip


#: The steak knives. Two titles are short ("Steak Knife", "Steak Knife Set of 6"), the rest
#: longer. Sales are modest: a knife sells 60 to 120 in five days, a beef steak 6 to 89 with a
#: median of 46, so a knife out-sells the typical steak but not every steak (the test pins the
#: median bound). The title's length, not popularity, decides.
STEAK_KNIVES = (
    _cutlery("DSK01", "Steak Knife", 1, "wooden", "serrated", STEEL, 90, 5.5,
             "A single steak knife with a pointed serrated blade and a riveted wooden handle, "
             "to replace one from a set. It cuts a sirloin or a ribeye without tearing it. "
             "Hand wash."),
    _cutlery("DSK02", "Steak Knives Set of 6", 6, "wooden", "serrated", STEEL, 120, 24.0,
             "Six steak knives with a pointed serrated blade and a riveted wooden handle, "
             "for cutting a rump or a fillet steak at the table. Hand wash."),
    _cutlery("DSK03", "Steak Knife Set of 4 with Wooden Handles", 4, "wooden", "serrated", STEEL,
             110, 18.0, "Four steak knives with serrated blades that stay sharp through a "
             "steak dinner for two, and riveted wooden handles. Hand wash."),
    _cutlery("DSK04", "Steak Knife Set of 6 with Straight Edge Blades", 6, "wooden", "straight",
             STEEL, 80, 28.0, "Six steak knives with a plain straight edge that slices a "
             "steak cleanly and can be sharpened, and wooden handles. Hand wash."),
    _cutlery("DSK05", "Steak Knife Set of 12 with Black Handles", 12, "black", "serrated", CAST,
             60, 42.0, "Twelve steak knives with serrated blades and black handles, enough "
             "for a table of guests all eating steak. Dishwasher safe."),
    _cutlery("DSK06", "Steak Knife and Fork Set of 8", 8, "wooden", "serrated", STEEL, 100, 26.0,
             "Four steak knives and four forks with wooden handles: a full steak dinner for "
             "four. Hand wash.", "steak knife and fork"),
    _cutlery("DSK07", "Steak Knife Set of 6 with Black Straight Edge Blades", 6, "black",
             "straight", CAST, 70, 30.0, "Six steak knives with black handles and a straight "
             "edge, for cutting steak cooked rare. Dishwasher safe."),
)

#: Steak ware outside cutlery: a plate, a board and a cast-iron weight.
STEAK_WARE = (
    Style("DSK08", "Steak Plate Cast Iron Sizzler with Wooden Stand", "Calderby & Lune", "Home",
          (*KD, "Plates"), 16.0, "A cast-iron plate that keeps a steak sizzling at the table, "
          "on a wooden stand. Heat it first, then season it with oil after washing by hand.",
          "Plate", "plate", one(CAST, 60),
          extra=(("plate_type", "Plate type", "Serving Platter"),
                 ("material", "Material", "Cast Iron")),
          params=(("kind", "serving platter"), ("diameter", "30"), ("finish", "cast iron"))),
    Style("DSK09", "Steak Serving Board with Juice Groove", "Lanternby", "Home",
          (*KD, "Chopping Boards"), 19.0, "An acacia wood board for carving and serving a "
          "steak, with a groove round the edge that catches the juices. Hand wash.",
          "Chopping Board", "chopping_board", one(WOODEN, 50),
          extra=(("material", "Material", "Wood"),),
          params=(("material", "wood"),)),
    Style("DSK10", "Cast Iron Steak Weight", "Calderby & Lune", "Home", (*KD, "Kitchen Utensils"),
          14.0, "A ribbed cast-iron grill press that keeps a steak flat in the pan so it sears "
          "evenly, with a wooden handle that stays cool. Hand wash and oil after use.",
          "Kitchen Utensil", "grill_press", one(CAST, 40),
          extra=(("utensil_type", "Utensil type", "Grill Press"),
                 ("material", "Material", "Cast Iron"))),
)

STYLES = (*MORE_TOPPERS, *PROTECTORS, *MATTRESSES, *PILLOW_PROTECTORS, *BARRELS,
          *KIDS_BARRELS, *BARREL_TROUSERS, *MORE_BALLOONS, *PETITE, *SALE,
          *STEAK_KNIVES, *STEAK_WARE)


def docs() -> list[dict]:
    """Every row's catalog document, in the order of :data:`STYLES`."""
    return [s.doc() for s in STYLES]
