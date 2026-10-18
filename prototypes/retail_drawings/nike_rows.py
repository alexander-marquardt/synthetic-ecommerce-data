"""Nike products and the decoys that name Nike (gen#341): data only.

Nike is the second real-brand exception beside Apple, iPhone and iPad (maintainer ruling
2026-10-15, :mod:`real_brands`): a shopper who types ``nike air max`` finds products. The name is
text, in the title, the ``brand`` field and the description; no drawing carries a logo, a swoosh,
a wordmark or a trade dress (``house_styles.HOUSE_STYLES["Nike"]`` has the mark ``none``).

- **Trainers and running shoes** in the existing leaves of Mens, Womens and Kids, eight of them
  Air Max (:data:`STYLES`, drawn by the footwear kit), each in at least three of the six main
  colors as plain color words.
- **Sportswear**: joggers (Mens, Womens), sweatshirts and tees (Mens, Kids) and a sports bra.
  The kit has a crew-neck sweatshirt and no hooded one, so there is no hoodie here.
- **Text-match decoys** (:data:`DECOYS`, gen#294): products of other brands and types whose
  DESCRIPTION names Nike ("for Nike and other trainers") while the title does not: a close call
  a ``nike`` query has to rank below a Nike product. They keep their own brands (all invented).

The rows are templates only: :func:`scale.derivable` leaves them out (``scale.NIKE_IDS``) and
:func:`main_colors.complete` gives none of them a color. Every other name is invented.
"""

# ruff: noqa: E501 -- data rows read better whole (prototype only).

from __future__ import annotations

import breadth_rows
import footwear_rows as fw
from breadth_rows import Row
from class_model import BRAND_OWNER
from footwear_rows import FootwearStyle, sh
from lowerbody_rows import LRow, _jg, _jgp, _jrow, _sizes
from prints import KIDS_SIZES
from real_classes import badges
from scale_rows import Bra
from variants import cw, style_docs

BRAND = "Nike"
breadth_rows.OWNERS[BRAND] = "third_party"
#: The brands the decoys keep (all invented), owned as the rest of the catalog states.
breadth_rows.OWNERS.update({b: BRAND_OWNER[b] for b in (
    "Calderby & Lune", "Stridewell", "Little Fernby", "Pewley Table", "Hearth & Table",
    "Saltmarsh", "Larkmoor")})  # fmt: skip

_C = "Clothing"
BLACK, WHITE = cw("Black", "#2a2a2e"), cw("White", "#f4f1ea", "solid", "#9a9ca0")
RED, BLUE = cw("Red", "#c8312e"), cw("Blue", "#2f6db5")
GREEN, YELLOW = cw("Green", "#3c8d4f"), cw("Yellow", "#f2c230")

_W, _M, _K = "women", "men", "kids"
_KIDS_RUN = fw.run("10 Infant", "6 Junior", chart="kids")


def _shades(*names: str, material: str) -> tuple:
    """The colors named (the six main ones and Orange), each a plain color word with its own hex and family."""
    hexes = {"Black": "#24262b", "White": "#fbfaf6", "Red": "#c8312e", "Blue": "#2b56b5",
             "Green": "#3c8d4f", "Yellow": "#f2c230", "Orange": "#e8742a"}  # fmt: skip
    return tuple(sh(n, hexes[n], n.lower(), material) for n in names)


def _shoe(code, title, gender, kind, price, desc, colors, sizes, line=None, **kw) -> FootwearStyle:
    return FootwearStyle(
        f"NK{code}", title, BRAND, gender, kind, price, desc, colors, sizes, "Lace-Up", "Rubber",
        product_line=line, junior_price=(price + 6 if gender == _K else None), **kw)  # fmt: skip


_AIR = "Air Max"
_MESH = ("Black", "White", "Red", "Blue")
STYLES = (
    _shoe("MAM90", "Nike Air Max 90 Trainers", _M, "trainer", 124.0,
          "Cushioned trainers with a visible air unit in the heel, a leather and mesh upper and a waffle outsole.",
          _shades(*_MESH, "Orange", material="leather"), fw.M_RUN, _AIR, trending=True),
    _shoe("MAM27", "Nike Air Max 270 Trainers", _M, "trainer", 144.0,
          "Everyday trainers with a tall air unit under the heel and a soft mesh upper.",
          _shades("Black", "White", "Green", "Blue", "Orange", material="mesh"), fw.M_RUN, _AIR),
    _shoe("MCTV1", "Nike Court Vision Low Trainers", _M, "trainer", 64.0,
          "Low-top court style trainers in smooth synthetic leather with a cupsole.",
          _shades("White", "Black", "Red", material="synthetic"), fw.M_RUN),
    _shoe("MPEG1", "Nike Pegasus Road Running Shoes", _M, "running", 109.0,
          "Neutral road running shoes with a responsive foam midsole and a breathable mesh upper.",
          _shades("Black", "White", "Blue", "Yellow", "Orange", material="mesh"), fw.M_RUN, "Pegasus"),
    _shoe("MAMRN", "Nike Air Max Run Running Shoes", _M, "running", 119.0,
          "Cushioned running shoes with an air unit in the heel for easy miles.",
          _shades("Black", "Red", "Green", material="mesh"), fw.M_RUN, _AIR),
    _shoe("WAM90", "Nike Air Max 90 Trainers", _W, "trainer", 124.0,
          "Cushioned trainers with a visible air unit in the heel, a leather and mesh upper and a waffle outsole.",
          _shades("White", "Black", "Red", "Blue", "Orange", material="leather"), fw.W_RUN, _AIR),
    _shoe("WAMDW", "Nike Air Max Dawn Trainers", _W, "trainer", 119.0,
          "Lightweight trainers with a visible air unit and a knit-look upper.",
          _shades("White", "Black", "Green", "Yellow", material="mesh"), fw.W_RUN, _AIR, trending=True),
    _shoe("WCTV1", "Nike Court Vision Low Trainers", _W, "trainer", 64.0,
          "Low-top court style trainers in smooth synthetic leather with a cupsole.",
          _shades("White", "Black", "Blue", material="synthetic"), fw.W_RUN),
    _shoe("WPEG1", "Nike Pegasus Road Running Shoes", _W, "running", 109.0,
          "Neutral road running shoes with a responsive foam midsole and a breathable mesh upper.",
          _shades("Black", "White", "Red", "Yellow", "Orange", material="mesh"), fw.W_RUN, "Pegasus"),
    _shoe("WAMRN", "Nike Air Max Run Running Shoes", _W, "running", 119.0,
          "Cushioned running shoes with an air unit in the heel for easy miles.",
          _shades("Black", "Blue", "Green", material="mesh"), fw.W_RUN, _AIR),
    _shoe("KAM90", "Kids' Nike Air Max 90 Trainers", _K, "trainer", 54.0,
          "Cushioned trainers for kids with an air unit in the heel and a padded tongue.",
          _shades("White", "Black", "Red", "Blue", "Orange", material="synthetic"), _KIDS_RUN, _AIR),
    _shoe("KAMEX", "Kids' Nike Air Max Excee Trainers", _K, "trainer", 49.0,
          "Chunky kids trainers with a visible air unit and a padded collar.",
          _shades("White", "Black", "Green", material="synthetic"), _KIDS_RUN, _AIR),
    _shoe("KRUN1", "Kids' Nike Revolution Running Shoes", _K, "running", 42.0,
          "Lightweight running shoes for kids with a foam midsole and a mesh upper.",
          _shades("Black", "Blue", "Yellow", "Red", "Orange", material="mesh"), _KIDS_RUN, "Revolution"),
    _shoe("KFLEX", "Kids' Nike Flex Runner Running Shoes", _K, "running", 38.0,
          "Slip-on style kids running shoes with a stretch bootie and a flexible sole.",
          _shades("Black", "White", "Green", material="mesh"), _KIDS_RUN, "Flex Runner"),
)  # fmt: skip


def _mat(v: str) -> tuple:
    return (("material", "Material", v),)


_PLAIN = (("pattern", "plain"),)
_MJ, _WJ = ("Mens", "Joggers"), ("Womens", "Joggers")
_SW, _TEE = "Sweatshirts", "T-Shirts"


def _top(code, title, root, leaf, ptype, shape, price, desc, colors, fabric, kids=False) -> LRow:
    sizes = _sizes(price, KIDS_SIZES) if kids else _sizes(price)
    return LRow(f"NK{code}", title, BRAND, _C, (root, "Tops", leaf), ptype, price, shape, desc,
                colors, (("fabric", "Fabric", fabric),), sizes,
                audience="kids" if kids else "adult", facts=_PLAIN)  # fmt: skip


SPORTSWEAR = (
    _jrow("NKJGM1", "Nike Club Fleece Joggers", BRAND, _MJ, 49.0,
          "Brushed fleece joggers with a ribbed cuff and a drawstring waist.",
          (BLACK, BLUE, RED, GREEN), _jg("Regular", "Elasticated", "Fleece", "Yes", "No"),
          _jgp("regular", "elastic", "Mid", "yes", "no"), "Mid"),
    _jrow("NKJGW1", "Nike Sportswear Phoenix Fleece Joggers", BRAND, _WJ, 52.0,
          "High-rise fleece joggers with a relaxed leg and a cuffed hem.",
          (BLACK, WHITE, BLUE, YELLOW), _jg("Relaxed", "Elasticated", "Fleece", "Yes", "No"),
          _jgp("relaxed", "elastic", "High", "yes", "no"), "High"),
    _top("SWM1", "Nike Club Crew Sweatshirt", "Mens", _SW, "Sweatshirt", "sweatshirt", 44.0,
         "A soft brushed-back cotton sweatshirt with ribbed cuffs and hem.",
         (BLACK, BLUE, RED, GREEN), "Cotton"),
    _top("SWK1", "Kids' Nike Crew Sweatshirt", "Kids", _SW, "Sweatshirt", "sweatshirt", 28.0,
         "A cosy fleece-back kids sweatshirt with a ribbed neck and cuffs.",
         (BLACK, BLUE, RED, WHITE), "Cotton", kids=True),
    _top("TEM1", "Nike Dri-FIT Training T-Shirt", "Mens", _TEE, "Tee", "tshirt", 27.0,
         "A sweat-wicking training t-shirt in a light stretch knit.",
         (BLACK, WHITE, BLUE, RED, GREEN), "Polyester"),
    _top("TEM2", "Nike Essentials Cotton T-Shirt", "Mens", _TEE, "Tee", "tshirt", 22.0,
         "A soft cotton jersey t-shirt with a ribbed crew neck.",
         (WHITE, BLACK, YELLOW, BLUE), "Cotton"),
    _top("TEK1", "Kids' Nike Dri-FIT Sports T-Shirt", "Kids", _TEE, "Tee", "tshirt", 19.0,
         "A light, quick-drying kids t-shirt for games and training.",
         (BLUE, RED, BLACK, WHITE), "Polyester", kids=True),
)  # fmt: skip

BRA = Bra("NKBRA1", "Nike Dri-FIT", BRAND, "Sports", (32, 38), ("A", "D"),
          (BLACK, WHITE, RED, BLUE), 34.0, wired=False, fabric="Recycled Polyester, Elastane")


# -- text-match decoys: another brand's product whose description names Nike -----------------------

_G = cw("Grey", "#9a9ca0")
_NAVY = cw("Navy", "#26365c")


def _decoy(code, title, brand, dept, path, ptype, price, shape, desc, colors, attrs=(), params=(),
           label=None, audience="adult", colorless=False) -> Row:
    return Row(f"NKD{code}", title, brand, dept, path, ptype, price, shape, desc, colors, attrs,
               (), label, audience, colorless, params)  # fmt: skip


_CARE = ("Mens", "Accessories", "Shoe Care")
DECOYS = (
    _decoy("CLN", "Trainer Cleaning Kit with Brush", "Calderby & Lune", "Footwear", _CARE,
           "Shoe Care Kit", 9.0, "tin",
           "A foam cleaner and a soft brush for canvas and mesh uppers. Safe on Nike and other trainers.",
           (BLACK,), colorless=True),
    _decoy("WHT", "Sole and Midsole Whitening Kit", "Calderby & Lune", "Footwear", _CARE,
           "Shoe Care Kit", 8.0, "tin",
           "A whitening paste and a scrubbing pad that bring yellowed soles back, tested on Nike Air Max midsoles.",
           (WHITE,), colorless=True),
    _decoy("SKM", "Cushioned Sports Socks, 3 Pack", "Stridewell", _C, ("Mens", "Socks", "Sports Socks"),
           "Socks", 8.0, "socks",
           "Padded sports socks with an arch band that sit neatly inside Nike and other low-cut trainers.",
           (WHITE,), (("units_per_pack", "Units per pack", "3", "C62"),), (("pairs", "3"),)),
    _decoy("SKK", "Kids' Grippy Play Socks, 5 Pack", "Little Fernby", _C, ("Kids", "Boys", "Socks"),
           "Socks", 6.0, "socks",
           "Soft socks with grippy soles for the playground, sized to fit kids' Nike trainers.",
           (_G,), (("units_per_pack", "Units per pack", "5", "C62"),), (("pairs", "5"),), audience="kids"),
    _decoy("BPK", "Gym Backpack with Shoe Compartment", "Tallow Street", _C,
           ("Womens", "Accessories", "Bags", "Backpacks"), "Backpack", 24.0, "backpack",
           "A vented side compartment holds a pair of Nike or other trainers apart from your kit.",
           (_NAVY,), (("use", "Use", "School"), ("material", "Material", "Polyester")),
           (("use", "school"), ("pockets", "1"))),
    _decoy("TMB", "Insulated Sports Tumbler", "Pewley Table", "Home",
           ("Home", "Kitchen & Dining", "Drinkware", "Tumblers"), "Tumbler", 14.0, "mug",
           "Keeps drinks cold on the run and slips into the bottle pocket of most Nike running belts.",
           (_NAVY,)),
    _decoy("BOX", "Stackable Shoe Storage Box", "Hearth & Table", "Home",
           ("Home", "Storage", "Storage Boxes"), "Storage Box", 6.0, "storage_box",
           "A clear drop-front box that holds one pair of trainers, up to the size of a boxed Nike Air Max.",
           (cw("Clear", "#e3eef0", "solid", "#7a7d82"),),
           (("material", "Material", "Plastic"), ("lid_type", "Lid type", "Clip Lid")),
           (("form", "box"), ("lid", "yes"), ("clear", "yes"), ("material", "plastic"))),
    _decoy("WSH", "Gym Wash Bag", "Saltmarsh", "Beauty",
           ("Beauty", "Accessories", "Wash Bags"), "Wash Bag", 7.0, "pouch",
           "A wipe-clean wash bag that zips flat in a gym bag beside your Nike kit.", (_NAVY,)),
    _decoy("YGM", "Non-Slip Travel Yoga Mat", "Larkmoor", "Sports & Outdoors",
           ("Sports & Outdoors", "Yoga & Fitness", "Yoga", "Yoga Mats"), "Yoga Mat", 16.0,
           "yoga_mat", "A thin mat that rolls up small enough to carry with your Nike trainers.",
           (BLUE,)),
)  # fmt: skip


def _ranked(docs: list[dict]) -> list[dict]:
    """The footwear docs ranked by sales among the Nike footwear, and badged, as footwear_rows."""
    ranked = sorted(docs, key=lambda d: (-d["sold_last_5_days"], d["product_id"]))
    rank = {d["product_id"]: n for n, d in enumerate(ranked, 1)}
    docs = [{**d, "bestseller_rank": rank[d["product_id"]]} for d in docs]
    return [{**d, "badges": badges(d)} for d in docs]


def docs() -> list[dict]:
    """Every Nike product, then every decoy that names Nike."""
    shoes = _ranked([s.doc() for s in STYLES])
    bra = [{**d, "brand_owner": "third_party"} for d in style_docs("Bras", BRA)]
    return [*shoes, *(r.doc() for r in SPORTSWEAR), *bra, *(r.doc() for r in DECOYS)]


def decoy_ids() -> frozenset[str]:
    return frozenset(f"BRD-{r.code}" for r in DECOYS)


def product_ids() -> frozenset[str]:
    """Every id the module adds, for :func:`scale.derivable` and the color completion."""
    return frozenset(d["product_id"] for d in docs())
