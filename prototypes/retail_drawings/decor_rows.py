"""The shared parts of the home accessories and decor types, and their text-match decoys (gen#217).

The catalog had photo frames, candles, cushions and Christmas decorations but no clocks,
artificial flowers, decorative trays, wallpaper or diaries, so a search for a clock or for
artificial stems returned a watch or a real bouquet on the word alone. Eight types are added, each
a spec of its own under ``type_specs/`` (gen#351) with its own drawing (:mod:`kit_decor`), its
shopper attributes as structured entries, and SKUs over its color and its own axis:

===============  ==========================  ===============  =====================================
type             path                        SKU axis         key attributes
===============  ==========================  ===============  =====================================
Clock            Home > Home Accessories     diameter_cm      clock type, finish, silent movement
Ornament         Home > Home Accessories     (color)          material, occasion, form
Artificial       Home > Home Accessories     height_cm        flower, holder (vase or loose)
Flowers
Decorative Tray  Home > Home Accessories     size (cm)        material, tray shape
Door Stop        Home > Home Accessories     (color)          material, weight
Wallpaper        Home > Decorating           roll_length_m    pattern, finish, roll width
Diary            Gifts > Stationery          (color)          year, page layout, paper size
Picnic Blanket   Sports & Outdoors > Camping dimensions       waterproof backing
===============  ==========================  ===============  =====================================

Greeting cards (``type_specs/greeting_card.py``) came with the Gifts types of gen#425; this issue
adds the decoys that name a card. Every type holds at least three styles from at least three
brands, all invented. A measured axis is on the SKUs alone, which the export states with its unit
(``export.OPTIONS``).

:data:`DECOYS` are the gen#294 text-match decoys of these types: other products whose title holds
the type's word ("Clockwork Robot", "Wallpaper Print Cushion") while their fields tell the truth
(a toy, a cushion). They sit in other departments, so they are not a spec's decoys (a spec's share
its department and type); :mod:`garden_rows` is the precedent. Titles are five words or fewer, so
the word sits where the text score weights it most. The rows are templates only: the derivation
leaves them out and the home department grows by authored rows.
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

import kit_decor  # noqa: F401 -- registers clock, ornament, stems, trinket_tray, ...
from breadth_rows import Row
from variants import cw

from synthetic_ecommerce_data.core.entry import canonical

HOME, GIFTS, SO = "Home", "Gifts", "Sports & Outdoors"
ACC = (HOME, "Home Accessories")
CLOCKS = (*ACC, "Clocks")
WALL = (*CLOCKS, "Wall Clocks")
MANTEL = (*CLOCKS, "Mantel Clocks")
ALARM = (*CLOCKS, "Alarm Clocks")
ORNAMENTS = (*ACC, "Ornaments")
STEMS = (*ACC, "Artificial Flowers")
TRAYS = (*ACC, "Decorative Trays")
STOPS = (*ACC, "Door Stops")
WALLPAPER = (HOME, "Decorating", "Wallpaper")
DIARIES = (GIFTS, "Stationery", "Diaries")
BLANKETS = (SO, "Camping", "Picnic Blankets")

BRACKENMERE, LANTERNBY, COBBLE, CALDERBY, EMBERLY, LARCHWOOD, HARBOUR, THISTLE = (
    "Brackenmere Home", "Lanternby", "Cobble & Kiln", "Calderby & Lune", "Emberly Home",
    "Larchwood Living", "Harbour & Pine", "Thistle & Wren",
)  # fmt: skip

RED, BLUE = cw("Red", "#c8312e"), cw("Blue", "#3f6fb5")
GREEN, YELLOW = cw("Green", "#4f8a3a"), cw("Yellow", "#f2c230")
BLACK, WHITE = cw("Black", "#2d2d33"), cw("White", "#f4f1ea", "solid", "#9a9ca0")
NATURAL, CREAM, GOLD = cw("Natural", "#e3d6bb"), cw("Cream", "#efe6cf"), cw("Gold", "#c9a227")
SILVER, GREY, PINK = cw("Silver", "#c3c7cc"), cw("Grey", "#9a9ca0"), cw("Pink", "#e8b9b3")
BROWN, TEAL, NAVY = cw("Brown", "#7a5a3c"), cw("Teal", "#1c7c7d"), cw("Navy", "#26365c")
COPPER, TAN = cw("Copper", "#c06a3c"), cw("Tan", "#c8a87a")


def a(key: str, name: str, v: str) -> tuple[str, str, str]:
    return (key, name, v)


def cm(key: str, name: str, value: int) -> tuple[str, str, str, str, float]:
    return (key, name, str(value), "CMT", value * 10.0)


def kg(key: str, name: str, value: float) -> tuple[str, str, str, str, float]:
    """A weight in kilograms: the canonical value is in grams, as the core's ``KGM`` says."""
    return (key, name, f"{value:g}", "KGM", float(canonical(f"{value:g}", "KGM")))


def yes(key: str, name: str) -> tuple[str, str, str]:
    return (key, name, "Yes")


def axis(*pairs: tuple[float, float]) -> tuple[tuple[str, float], ...]:
    return tuple((f"{v:g}", p) for v, p in pairs)


def row(code: str, title: str, brand: str, path: tuple[str, ...], ptype: str, price: float,
         shape: str, description: str, colors: tuple, attrs: tuple, sizes: tuple = (),
         size_key: str = "size", params: tuple = (), colorless: bool = False,
         audience: str = "adult") -> Row:  # fmt: skip
    return Row(code, title, brand, path[0], path, ptype, price, shape, description, colors,
               attrs, sizes, audience=audience, size_key=size_key, params=params,
               colorless=colorless)  # fmt: skip


# --------------------------------------------------------------------------
# Text-match decoys (gen#294): another product that holds the type's word
# --------------------------------------------------------------------------

_TOY = ("Toys", "Baby & Toddler", "Wooden Toys")
_CUSH = (HOME, "Soft Furnishings", "Cushions")
_BOX = (HOME, "Storage", "Storage Boxes")
_MUG = (HOME, "Kitchen & Dining", "Drinkware", "Mugs")
_TOWEL = (HOME, "Kitchen & Dining", "Tea Towels")
_BOUQ = ("Garden", "Flowers", "Bouquets")
_GLASS = (HOME, "Kitchen & Dining", "Glassware")
_UTEN = (HOME, "Kitchen & Dining", "Kitchen Utensils")


def _decoy(code: str, title: str, brand: str, path: tuple[str, ...], ptype: str, price: float,
           shape: str, description: str, color, material: str, audience: str = "adult") -> Row:
    return row(code, title, brand, path, ptype, price, shape, description, (color,),
                (a("material", "Material", material),), audience=audience)


DECOYS = (
    _decoy("DCYCLW", "Clockwork Robot", CALDERBY, _TOY, "Wooden Toy", 9.0, "wooden_toy",
           "A wooden robot that walks when its key is wound, a toy for ages 3 and up, not a clock.",
           NATURAL, "Wood", "kids"),
    _decoy("DCYCLC", "Grandfather Clock Print Cushion", BRACKENMERE, _CUSH, "Cushion", 12.0, "cushion",
           "A cushion printed with a picture of a grandfather clock, which tells no time.",
           CREAM, "Cotton"),
    _decoy("DCYORS", "Ornament Storage Box", HARBOUR, _BOX, "Storage Box", 11.0, "storage_box",
           "A padded storage box with dividers that keeps glass ornaments safe between seasons.",
           GREY, "Fabric"),
    _decoy("DCYORM", "Cat Ornament Mug", THISTLE, _MUG, "Mug", 7.0, "mug",
           "A ceramic mug printed with a cat on a shelf of ornaments.",
           WHITE, "Ceramic"),
    _decoy("DCYSTB", "Fresh Rose Stems Bouquet", THISTLE, _BOUQ, "Bouquet", 22.0, "bouquet",
           "A bouquet of fresh cut rose stems, delivered in water. These are real flowers, not artificial ones.",
           PINK, "Fresh Flowers"),
    _decoy("DCYSTG", "Long Stem Wine Glass", COBBLE, _GLASS, "Glassware", 6.0, "drinking_glass",
           "A wine glass on a long stem, sold singly. It holds a drink, not flowers.",
           cw("Clear", "#dfe8ea"), "Glass"),
    _decoy("DCYTRB", "Tray Bake Spatula", LANTERNBY, _UTEN, "Kitchen Utensil", 5.0, "kitchen_utensil",
           "A flat spatula with a thin edge for lifting a tray bake from its tin.",
           BLACK, "Silicone"),
    _decoy("DCYTRT", "Tray Print Tea Towel", CALDERBY, _TOWEL, "Tea Towels", 5.0, "tea_towel",
           "A cotton tea towel printed with a tea tray and cups.",
           WHITE, "Cotton"),
    _decoy("DCYWLC", "Wallpaper Print Cushion", EMBERLY, _CUSH, "Cushion", 14.0, "cushion",
           "A cushion cut from fabric in a wallpaper design of leaves.",
           GREEN, "Cotton"),
    _decoy("DCYWLB", "Wallpaper Stripe Tea Towel", LARCHWOOD, _TOWEL, "Tea Towels", 5.0, "tea_towel",
           "A cotton tea towel printed in the stripes of a wallpaper. It is a tea towel, not a roll.",
           CREAM, "Cotton"),
    _decoy("DCYCRD", "Birthday Card Tea Towel", CALDERBY, _TOWEL, "Tea Towels", 5.0, "tea_towel",
           "A cotton tea towel printed with a birthday card. It is a tea towel, not a greeting.",
           RED, "Cotton"),
    _decoy("DCYCRM", "Thank You Card Mug", BRACKENMERE, _MUG, "Mug", 7.0, "mug",
           "A ceramic mug printed with a thank you card, a gift for a teacher.",
           BLUE, "Ceramic"),
    _decoy("DCYDRC", "Diary Print Cushion", COBBLE, _CUSH, "Cushion", 13.0, "cushion",
           "A cushion printed with the cover of an old diary.",
           BROWN, "Cotton"),
    _decoy("DCYDRB", "Diary Lock Storage Box", HARBOUR, _BOX, "Storage Box", 15.0, "storage_box",
           "A small storage box with a key lock, for keeping a diary private.",
           BLACK, "Metal"),
    _decoy("DCYPCC", "Picnic Blanket Print Cushion", LARCHWOOD, _CUSH, "Cushion", 12.0, "cushion",
           "A cushion in the red check of a picnic blanket.",
           RED, "Cotton"),
    _decoy("DCYPCT", "Picnic Blanket Check Tea Towel", THISTLE, _TOWEL, "Tea Towels", 5.0, "tea_towel",
           "A cotton tea towel in the check of a picnic blanket. It is a tea towel, not a blanket.",
           YELLOW, "Cotton"),
    _decoy("DCYDSC", "Door Stop Cat Cushion", EMBERLY, _CUSH, "Cushion", 12.0, "cushion",
           "A heavy cat shaped cushion that some people lean on a door; it is not a door stop.",
           GREY, "Cotton"),
    _decoy("DCYDSB", "Door Stop Print Tea Towel", HARBOUR, _TOWEL, "Tea Towels", 5.0, "tea_towel",
           "A cotton tea towel printed with a wedge door stop. It is a tea towel, not a door stop.",
           WHITE, "Cotton"),
)

def docs() -> list[dict]:
    """Every row's catalog document."""
    return [r.doc() for r in DECOYS]


def decoy_ids() -> frozenset[str]:
    """The decoys' product ids: ``main_colors.complete`` leaves them as authored."""
    return frozenset(f"BRD-{r.code}" for r in DECOYS)
