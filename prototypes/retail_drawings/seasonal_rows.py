"""Seasonal collections, colors typed before a category, and invented characters (gen#195).

Three things a shopper types that the build lacked, kept as data:

- **Color values** that are also a food, a stone or a fabric: champagne, duck egg, navy blue,
  rust, caramel, oatmeal, stone, aubergine, berry, raspberry, mint, olive, amber,
  tortoiseshell and the two-word rose quartz. Each is one plain color value
  (:mod:`colorwords` no longer folds it into a plainer one), like Rose Gold. These rows put
  them on the product types a shopper types them before: a dress, a jumper, a candle, a
  lipstick, a frame. There is no shade-name field; the value is the ``color`` facet's.
- **Collections**: the ``collections`` field, empty on every record until now, holds
  Christmas, Halloween, Advent, Summer, Autumn, Wedding or Going Out on the products that
  belong to one.
- **Characters**: invented ranges (never licensed ones) as a ``line`` attribute on cakes,
  sweets, pyjamas and soft toys, the same four ranges :mod:`toys_rows` sells as jigsaws and
  building sets, so a range name alone finds a toy, a pyjama set and a cake. A pyjama set's
  drawing carries the range's mark (a motif of :mod:`motifs`).

These rows are templates only: :func:`scale.derivable` leaves them out, as it does the toys,
so the seeded derivation is what it was. Prices are plausible shop prices and no query
depends on them.
"""

# ruff: noqa: E501 -- data rows read better whole (prototype only).

from __future__ import annotations

from dataclasses import dataclass

from breadth_rows import Row
from toys_rows import RANGES
from variants import cw

XMAS, HALLOWEEN, ADVENT = "Christmas", "Halloween", "Advent"
SUMMER, AUTUMN, WEDDING, GOING_OUT = "Summer", "Autumn", "Wedding", "Going Out"
#: Every collection value the rows carry (the generator test pins the set).
COLLECTIONS = (XMAS, HALLOWEEN, ADVENT, SUMMER, AUTUMN, WEDDING, GOING_OUT)


@dataclass(frozen=True)
class SRow(Row):
    """A row with ``collections`` and, for a printed garment, the drawing's motif fields."""

    collections: tuple[str, ...] = ()
    motif_print: tuple[tuple[str, object], ...] = ()

    def doc(self) -> dict:
        out = super().doc()
        out["collections"] = list(self.collections)
        out["drawing"].update(dict(self.motif_print))
        return out


def _a(key: str, name: str, v: str) -> tuple[str, str, str]:
    return (key, name, v)


def _line(name: str) -> tuple[str, str, str]:
    if name not in RANGES:
        raise ValueError(f"{name!r} is not one of the invented ranges")
    return _a("line", "Line", name)


#: The drawing fields of a flower print, scattered all over the garment (gen#408).
_FLOWERS = (("motif", "daisy"), ("placement", "all-over"), ("scale", 0.1), ("spacing", 96),
            ("count", 2))  # fmt: skip


def _mark(name: str) -> tuple[tuple[str, object], ...]:
    """The drawing fields of the range's motif, scattered small (as :mod:`prints` does)."""
    return (("motif", RANGES[name][1]), ("placement", "all-over"), ("scale", 0.1),
            ("spacing", 96), ("count", 2))  # fmt: skip


CHAMPAGNE = cw("Champagne", "#e8d5a8")
NAVY_BLUE = cw("Navy Blue", "#1f3a68")
DUCK_EGG = cw("Duck Egg", "#a9cfc8")
RUST = cw("Rust", "#b5532a")
CARAMEL = cw("Caramel", "#c68642")
OATMEAL = cw("Oatmeal", "#d9ccb4")
STONE = cw("Stone", "#bdb5a6")
AUBERGINE = cw("Aubergine", "#4b2a4f")
BERRY = cw("Berry", "#8c2f52")
RASPBERRY = cw("Raspberry", "#c2185b")
MINT = cw("Mint", "#a8dcc0")
OLIVE = cw("Olive", "#6b6b2f")
AMBER = cw("Amber", "#e0a030")
TORTOISESHELL = cw("Tortoiseshell", "#8a5a2b", "solid", "#2a1a0e")
ROSE_QUARTZ = cw("Rose Quartz", "#f0c8cf")
#: The jersey midi dress's first colorway: a flower print, so "floral dress" finds it (gen#408).
PINK_FLORAL = cw("Pink Floral", "#f3c6cf", "print", "#c8312e")
NATURAL = cw("Natural", "#d9b98a")
RED = cw("Red", "#c8312e")
GREEN = cw("Green", "#3f7d4a")
ORANGE = cw("Orange", "#e07a1f")
BLACK = cw("Black", "#2a2a2e")
WHITE = cw("White", "#f4f1ea")
PINK = cw("Pink", "#f2a1b8")
NAVY = cw("Navy", "#26365c")

_ADULT = (("S", 0.0), ("M", 0.0), ("L", 0.0))
_KID_AGES = (("3-4 Yrs", 0.0), ("5-6 Yrs", 0.0), ("7-8 Yrs", 0.0))


def _sz(price: float, sizes=_ADULT) -> tuple[tuple[str, float], ...]:
    return tuple((s, price) for s, _ in sizes)


def _mat(v: str) -> tuple[tuple[str, str, str], ...]:
    return (_a("material", "Material", v),)


_SLIP, _MIDI = ("Womens", "Dresses", "Slip Dresses"), ("Womens", "Dresses", "Midi Dresses")
_JUMP, _CARDI, _EAR = ("Womens", "Knitwear", "Jumpers"), ("Womens", "Knitwear", "Cardigans"), ("Womens", "Jewellery", "Earrings")
_CANDLE = ("Gifts", "Home Fragrance", "Scented Candles")
_FRAME = ("Gifts", "Keepsakes", "Photo Frames")
_WRAPPAPER = ("Gifts", "Gift Wrap", "Wrapping Paper")
_GIFTBAG = ("Gifts", "Gift Wrap", "Gift Bags")
_WALLET = ("Gifts", "Gifts for Him", "Wallet Gift Sets")
_LIPS = ("Beauty", "Make-Up", "Lips", "Lipstick")
_MAKEUP_SET = ("Beauty", "Gift Sets", "Make-Up Gift Sets")
_CAKES = ("Food & Drink", "Bakery", "Cakes")
_SWEETS = ("Food & Drink", "Chocolate & Sweets", "Sweets")
_BOXES = ("Food & Drink", "Chocolate & Sweets", "Chocolate Boxes")
_PJ_K = ("Kids", "Nightwear", "Pyjamas")
_SOFT = ("Toys", "Soft Toys", "Cuddly Animals")
_C, _L, _H = "Clothing", "Lingerie & Nightwear", "Gifts"
_FOOD = "Food & Drink"

#: Color values on the product types a shopper types them before, some in a collection.
COLORS = (
    SRow("CLRSLP", "Satin Slip Dress", "Larkmoor", _C, _SLIP, "Dress", 38.0, "dress",
         "A satin slip dress with fine straps and a flared skirt, for an evening out.",
         (CHAMPAGNE, NAVY_BLUE, BLACK), _mat("Satin"), _sz(38.0), collections=(GOING_OUT, WEDDING)),
    SRow("CLRWRP", "Jersey Midi Dress", "Harbour & Pine", _C, _MIDI, "Dress", 34.0, "dress",
         "A soft jersey midi dress with fine straps and a flared skirt.",
         (PINK_FLORAL, NAVY_BLUE, OLIVE), _mat("Jersey"), _sz(34.0), collections=(WEDDING,),
         motif_print=_FLOWERS),
    SRow("CLRSHD", "Linen Blend Midi Dress", "Harbour & Pine", _C, _MIDI, "Dress", 36.0, "dress",
         "A light midi dress in a linen blend with fine straps and a flared skirt, easy for hot days.",
         (MINT, STONE, DUCK_EGG), _mat("Linen blend"), _sz(36.0), collections=(SUMMER,)),
    SRow("CLRCRD", "Needlecord Midi Dress", "Larkmoor", _C, _MIDI, "Dress", 42.0, "dress",
         "A needlecord midi dress with fine straps and a flared skirt, to wear over a tee in the cooler months.",
         (OLIVE, CARAMEL, AUBERGINE), _mat("Cotton"), _sz(42.0), collections=(AUTUMN,)),
    SRow("CLRJMP", "Crew Neck Knit Jumper", "Harbour & Pine", _C, _JUMP, "Jumper", 32.0, "sweatshirt",
         "A knit jumper with a crew neck, ribbed cuffs and hem, and a relaxed fit.",
         (AUBERGINE, RUST, OATMEAL, STONE), _mat("Wool blend"), _sz(32.0), collections=(AUTUMN,)),
    SRow("CLRCDG", "Brushed Knit Cardigan", "Larkmoor", _C, _CARDI, "Cardigan", 30.0, "cardigan",
         "A brushed knit cardigan with a button front and patch pockets.",
         (RASPBERRY, CARAMEL, OATMEAL), _mat("Acrylic blend"), _sz(30.0), collections=(AUTUMN,)),
    SRow("CLRXMP", "Festive Crew Neck Jumper", "Harbour & Pine", _C, _JUMP, "Jumper", 28.0, "sweatshirt",
         "A cosy crew neck jumper for the festive season, for the office party and the day itself.",
         (BERRY, OLIVE, NAVY_BLUE), _mat("Acrylic blend"), _sz(28.0), collections=(XMAS,)),
    SRow("CLREAR", "Resin Stud Earrings", "Wrenfield", _C, _EAR, "Earrings", 12.0, "earrings",
         "Round stud earrings in a mottled resin, light enough to wear all night.",
         (TORTOISESHELL, CHAMPAGNE), _mat("Resin"), collections=(GOING_OUT,)),
    SRow("CLRFRM", "Resin Photo Frame, 5 x 7", "Lanternby", _H, _FRAME, "Photo Frame", 14.0, "photo_frame",
         "A slim photo frame in a mottled resin with a glass front, for a wedding photo.",
         (TORTOISESHELL, STONE), _mat("Resin"), collections=(WEDDING,)),
    SRow("CLRLIP", "Satin Finish Lipstick", "Kestlewood Cosmetics", "Beauty", _LIPS, "Lipstick", 9.0, "lipstick",
         "A comfortable satin lipstick with a creamy glide, in shades from soft to deep.",
         (ROSE_QUARTZ, BERRY, RASPBERRY), collections=(GOING_OUT,)),
    SRow("CLRCNA", "Amber and Oak Scented Candle", "Calderby & Lune", _H, _CANDLE, "Scented Candle", 16.0, "tin",
         "A warm candle of amber, oak and smoked cedar, poured in a tin that burns for 40 hours.",
         (AMBER, RUST), _mat("Soy wax"), collections=(AUTUMN,)),
    SRow("CLRCNB", "Cranberry and Clove Scented Candle", "Lanternby", _H, _CANDLE, "Scented Candle", 14.0, "tin",
         "A festive candle of cranberry, clove and cinnamon, poured in a tin that burns for 35 hours.",
         (BERRY, CHAMPAGNE), _mat("Soy wax"), collections=(XMAS,)),
    SRow("CLRCNC", "Sea Salt and Mint Scented Candle", "Lanternby", _H, _CANDLE, "Scented Candle", 12.0, "tin",
         "A fresh candle of sea salt, mint and driftwood, poured in a tin that burns for 30 hours.",
         (MINT, DUCK_EGG), _mat("Soy wax"), collections=(SUMMER,)),
    SRow("CLRWLT", "Leather Wallet Gift Set", "Calderby & Lune", _H, _WALLET, "Gift Set", 30.0, "gift_set",
         "A grained leather wallet with a matching card holder, boxed for giving.",
         (CARAMEL, NAVY_BLUE), _mat("Leather"), collections=(XMAS,)),
)

#: Festive and seasonal products that are not about a color word.
SEASONS = (
    SRow("SEAWRP", "Christmas Wrapping Paper, 3 m Roll", "Lanternby", _H, _WRAPPAPER, "Wrapping Paper", 4.0, "wrapping_paper",
         "A 3 m roll of heavy gift wrap in a deep, solid shade.",
         (RUST, CHAMPAGNE), collections=(XMAS,)),
    SRow("SEAADV", "Chocolate Advent Calendar", "Pantry Mill", _FOOD, _BOXES, "Chocolate Box", 6.0, "box",
         "A window a day to Christmas, each with a milk chocolate shape. 24 windows, 100g.",
         (NATURAL,), collections=(ADVENT, XMAS), colorless=True, label="Calendar"),
    SRow("SEABAD", "Beauty Advent Calendar", "Kestlewood Cosmetics", "Beauty", _MAKEUP_SET, "Gift Set", 45.0, "gift_set",
         "Twenty four make-up and skincare minis, one behind each door, from the first of December.",
         (RED,), collections=(ADVENT, XMAS), colorless=True),
    SRow("SEAXMC", "Iced Christmas Cake", "Hearth & Table", _FOOD, _CAKES, "Cake", 9.0, "cake",
         "A rich fruit cake under marzipan and white icing, ready for Christmas.",
         (WHITE,), collections=(XMAS,), colorless=True, label="Cake"),
    SRow("SEAHBG", "Trick or Treat Bucket Bag", "Lanternby", _H, _GIFTBAG, "Gift Bag", 5.0, "gift_bag",
         "A sturdy treat bag with a pumpkin face and a handle, for collecting sweets.",
         (ORANGE, BLACK), collections=(HALLOWEEN,)),
    SRow("SEAHCK", "Halloween Cupcakes", "Hearth & Table", _FOOD, _CAKES, "Cake", 5.0, "cupcake",
         "Six vanilla cupcakes with swirled orange buttercream, for a Halloween party.",
         (ORANGE,), collections=(HALLOWEEN,), colorless=True, label="Cupcakes"),
    SRow("SEAHSW", "Halloween Treat Sweets, 250g", "Pantry Mill", _FOOD, _SWEETS, "Sweets", 3.0, "bag",
         "A mixed bag of fruit chews and fizzy shapes for trick or treaters.",
         (ORANGE,), collections=(HALLOWEEN,), colorless=True, label="Sweets"),
    SRow("SEASMC", "Summer Berry Celebration Cake, 800g", "Hearth & Table", _FOOD, _CAKES, "Cake", 14.0, "cake",
         "A vanilla sponge layered with raspberry jam and cream, finished with fresh berries.",
         (PINK,), collections=(SUMMER,), colorless=True, label="Cake"),
    SRow("SEAWDC", "Two Tier Wedding Cake, Serves 40", "Hearth & Table", _FOOD, _CAKES, "Cake", 85.0, "cake",
         "Two tiers of lemon sponge under white icing. Serves 40.",
         (WHITE,), collections=(WEDDING,), colorless=True, label="Cake"),
)

#: Character cakes, sweets, pyjamas and soft toys: the invented ranges as a ``line``.
_PJ_DESC = "A long sleeve top and bottoms in soft cotton, with the {line} mark all over."
_PJ_FOR = {  # the ground, printed with the range's mark in a pale ink
    "Moonmoth Rangers": cw("Navy", "#26365c", "print", "#f2d14b"),
    "Rumblesaur Ridge": cw("Green", "#5f9a4a", "print", "#f4f1ea"),
    "Bramblewood Owls": cw("Pink", "#f2a1b8", "print", "#7a4a5a"),
    "Driftwhistle Bay": cw("Blue", "#3f6fb5", "print", "#f4f1ea"),
}
_PLUSH = {"Moonmoth Rangers": ("star", "Star Plush", "A soft, squashy star, the Moonmoth Rangers' mascot."),
          "Rumblesaur Ridge": ("dinosaur", "Dinosaur Soft Toy", "A floppy long necked dinosaur, the Rumblesaur Ridge favorite."),
          "Bramblewood Owls": ("bird", "Owl Soft Toy", "A round little owl with felt wings, from the Bramblewood Owls."),
          "Driftwhistle Bay": ("whale", "Whale Soft Toy", "A long squashy whale, the Driftwhistle Bay mascot.")}  # fmt: skip

CHARACTERS = (
    *(SRow(f"CHP{i}", f"{name} Kids' Pyjamas", "Little Fernby", _L, _PJ_K, "Pyjamas", 14.0, "pyjamas",
           _PJ_DESC.format(line=name), (_PJ_FOR[name],), (_mat("Cotton")[0], _line(name)), _sz(14.0, _KID_AGES),
           audience="kids", motif_print=_mark(name),
           collections=(XMAS,) if name == "Moonmoth Rangers" else ())
      for i, name in enumerate(RANGES)),
    *(SRow(f"CHT{i}", f"{name} {title}", "Little Fernby", "Toys", _SOFT, "Soft Toy", 12.0, shape, desc,
           (cw("Grey", "#9a9ca0"),), (_mat("Plush")[0], _line(name)), audience="kids")
      for i, (name, (shape, title, desc)) in enumerate(_PLUSH.items())),
    SRow("CHKMOO", "Moonmoth Rangers Birthday Cake, 900g", "Hearth & Table", _FOOD, _CAKES, "Cake", 11.0, "cake",
         "A two tier vanilla sponge with blue buttercream, for a Moonmoth Rangers birthday.",
         (NAVY,), (_line("Moonmoth Rangers"),), colorless=True, label="Cake"),
    SRow("CHKRUM", "Rumblesaur Ridge Dinosaur Cake, 900g", "Hearth & Table", _FOOD, _CAKES, "Cake", 11.0, "cake",
         "A two tier chocolate sponge with green buttercream, for a Rumblesaur Ridge birthday.",
         (GREEN,), (_line("Rumblesaur Ridge"),), colorless=True, label="Cake"),
    SRow("CHKDRI", "Driftwhistle Bay Cupcakes", "Hearth & Table", _FOOD, _CAKES, "Cake", 5.0, "cupcake",
         "Six vanilla cupcakes with swirled blue icing and a cherry on top, from Driftwhistle Bay.",
         (cw("Blue", "#3f6fb5"),), (_line("Driftwhistle Bay"),), colorless=True, label="Cupcakes"),
    SRow("CHSOWL", "Bramblewood Owls Fruit Sweets, 180g", "Pantry Mill", _FOOD, _SWEETS, "Sweets", 2.0, "bag",
         "Soft fruit chews in the shape of the Bramblewood Owls.",
         (PINK,), (_line("Bramblewood Owls"),), colorless=True, label="Sweets"),
    SRow("CHSMOO", "Moonmoth Rangers Star Sweets, 180g", "Pantry Mill", _FOOD, _SWEETS, "Sweets", 2.0, "bag",
         "Fizzy star shaped sweets from the Moonmoth Rangers.",
         (NAVY,), (_line("Moonmoth Rangers"),), colorless=True, label="Sweets"),
)

ROWS = (*COLORS, *SEASONS, *CHARACTERS)


def docs() -> list[dict]:
    """Every row's catalog document."""
    return [r.doc() for r in ROWS]
