"""Home accessories and decor templates for the scaled retail catalog (gen#217): data only.

The catalog had photo frames, candles, cushions and Christmas decorations but no clocks,
artificial flowers, decorative trays, wallpaper, greeting cards or diaries, so a search for a
clock or for artificial stems returned a watch or a real bouquet on the word alone. Nine types
are added, each a leaf of its own with its own drawing (:mod:`kit_decor`), its shopper
attributes as structured entries, and SKUs over its color and its own axis:

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
Greeting Card    Gifts > Cards & Stationery  design           occasion, card size
Diary            Gifts > Cards & Stationery  (color)          year, page layout, paper size
Picnic Blanket   Sports & Outdoors > Camping dimensions       waterproof backing
===============  ==========================  ===============  =====================================

Every type holds at least three styles from at least three brands, all invented. A colored type
offers the six main colors across its styles (gen#275); a greeting card is sold by design, not
by color, so it carries none. A measured axis is on the SKUs alone, which the export states with
its unit (``export.OPTIONS``). A card's SKU ``design`` is also its drawing's ``design`` param, so
each design draws its own picture.

:data:`DECOYS` are the gen#294 text-match decoys of these types: other products whose title holds
the type's word ("Clockwork Robot", "Wallpaper Print Cushion") while their fields tell the truth
(a toy, a cushion). Titles are five words or fewer, so the word sits where the text score weights
it most. Rows are templates only: :func:`scale.derivable` leaves them out, as it does the sports
and household rows, so the home department grows by authored rows.
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

import kit_decor  # noqa: F401 -- registers clock, ornament, stems, trinket_tray, ...
from breadth_rows import Row
from variants import cw

from synthetic_ecommerce_data.core.entry import canonical

_HOME, _GIFTS, _SO = "Home", "Gifts", "Sports & Outdoors"
_ACC = (_HOME, "Home Accessories")
CLOCKS = (*_ACC, "Clocks")
WALL = (*CLOCKS, "Wall Clocks")
MANTEL = (*CLOCKS, "Mantel Clocks")
ALARM = (*CLOCKS, "Alarm Clocks")
ORNAMENTS = (*_ACC, "Ornaments")
STEMS = (*_ACC, "Artificial Flowers")
TRAYS = (*_ACC, "Decorative Trays")
STOPS = (*_ACC, "Door Stops")
WALLPAPER = (_HOME, "Decorating", "Wallpaper")
CARDS = (_GIFTS, "Cards & Stationery", "Greeting Cards")
DIARIES = (_GIFTS, "Cards & Stationery", "Diaries")
BLANKETS = (_SO, "Camping", "Picnic Blankets")

_BM, _LN, _CK, _CL, _EH, _LW, _HP, _TW = (
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


def _a(key: str, name: str, v: str) -> tuple[str, str, str]:
    return (key, name, v)


def _cm(key: str, name: str, cm: int) -> tuple[str, str, str, str, float]:
    return (key, name, str(cm), "CMT", cm * 10.0)


def _kg(key: str, name: str, kg: float) -> tuple[str, str, str, str, float]:
    """A weight in kilograms: the canonical value is in grams, as the core's ``KGM`` says."""
    return (key, name, f"{kg:g}", "KGM", float(canonical(f"{kg:g}", "KGM")))


def _yes(key: str, name: str) -> tuple[str, str, str]:
    return (key, name, "Yes")


def _axis(*pairs: tuple[float, float]) -> tuple[tuple[str, float], ...]:
    return tuple((f"{v:g}", p) for v, p in pairs)


def _row(code: str, title: str, brand: str, path: tuple[str, ...], ptype: str, price: float,
         shape: str, description: str, colors: tuple, attrs: tuple, sizes: tuple = (),
         size_key: str = "size", params: tuple = (), colorless: bool = False,
         audience: str = "adult") -> Row:  # fmt: skip
    return Row(code, title, brand, path[0], path, ptype, price, shape, description, colors,
               attrs, sizes, audience=audience, size_key=size_key, params=params,
               colorless=colorless)  # fmt: skip


# --------------------------------------------------------------------------
# Clocks: wall, mantel and alarm; color x dial diameter
# --------------------------------------------------------------------------

_SIL = _yes("silent_movement", "Silent movement")
_TICK = _a("silent_movement", "Silent movement", "No")

CLOCK_ROWS = (
    _row("CLKWBR", "Brushed Brass Wall Clock", _BM, WALL, "Clock", 24.0, "clock",
         "A round wall clock in a brushed brass frame with a sweep movement that does not tick.",
         (GOLD, BLACK, WHITE),
         (_a("clock_type", "Clock type", "Wall"), _a("finish", "Finish", "Brushed Brass"), _SIL),
         _axis((30, 24.0), (40, 32.0), (50, 44.0)), "diameter_cm", (("type", "wall"),)),
    _row("CLKWWN", "Walnut Wall Clock", _LN, WALL, "Clock", 29.0, "clock",
         "A wall clock in a walnut frame with a plain dial and a quiet quartz sweep movement.",
         (BROWN, RED, BLUE),
         (_a("clock_type", "Clock type", "Wall"), _a("finish", "Finish", "Walnut"), _SIL),
         _axis((30, 29.0), (40, 38.0)), "diameter_cm", (("type", "wall"),)),
    _row("CLKWPT", "Painted Metal Wall Clock", _CK, WALL, "Clock", 19.0, "clock",
         "A metal wall clock in a gloss painted frame, with a ticking quartz movement.",
         (RED, YELLOW, GREEN, BLUE),
         (_a("clock_type", "Clock type", "Wall"), _a("finish", "Finish", "Gloss Painted"), _TICK),
         _axis((25, 19.0), (35, 25.0)), "diameter_cm", (("type", "wall"),)),
    _row("CLKMOK", "Oak Mantel Clock", _CL, MANTEL, "Clock", 39.0, "clock",
         "An arched mantel clock in a solid oak case on four small feet, with a silent sweep movement.",
         (NATURAL, BLACK, WHITE),
         (_a("clock_type", "Clock type", "Mantel"), _a("finish", "Finish", "Oak"), _SIL),
         _axis((12, 39.0), (16, 49.0)), "diameter_cm", (("type", "mantel"),)),
    _row("CLKMBZ", "Antique Bronze Mantel Clock", _EH, MANTEL, "Clock", 45.0, "clock",
         "A mantel clock in an arched case with an antique bronze finish and a ticking movement.",
         (COPPER, GREEN, BLUE),
         (_a("clock_type", "Clock type", "Mantel"), _a("finish", "Finish", "Antique Bronze"), _TICK),
         _axis((12, 45.0), (16, 55.0)), "diameter_cm", (("type", "mantel"),)),
    _row("CLKABL", "Twin Bell Alarm Clock", _HP, ALARM, "Clock", 12.0, "clock",
         "A twin bell alarm clock with a loud hammer alarm and a ticking movement, in a gloss painted case.",
         (RED, YELLOW, BLACK, WHITE),
         (_a("clock_type", "Clock type", "Alarm"), _a("finish", "Finish", "Gloss Painted"), _TICK),
         _axis((10, 12.0), (12, 15.0)), "diameter_cm", (("type", "alarm"),)),
    _row("CLKASL", "Silent Sweep Alarm Clock", _LN, ALARM, "Clock", 16.0, "clock",
         "A bedside alarm clock with a silent sweep movement and a gentle rising alarm tone, in a chrome case.",
         (SILVER, BLUE, GREEN),
         (_a("clock_type", "Clock type", "Alarm"), _a("finish", "Finish", "Chrome"), _SIL),
         _axis((10, 16.0), (12, 19.0)), "diameter_cm", (("type", "alarm"),)),
)

# --------------------------------------------------------------------------
# Ornaments and decorative objects: color only
# --------------------------------------------------------------------------

ORNAMENT_ROWS = (
    _row("ORNCVS", "Ceramic Table Vase Ornament", _CK, ORNAMENTS, "Ornament", 18.0, "ornament",
         "A glazed ceramic vase for the shelf or the table, a decorative object that holds a few dried stems.",
         (WHITE, BLUE, YELLOW, GREEN),
         (_a("material", "Material", "Ceramic"), _a("occasion", "Occasion", "Everyday"),
          _a("form", "Form", "Vase")),
         params=(("form", "vase"),)),
    _row("ORNWBD", "Carved Wooden Bird Ornament", _TW, ORNAMENTS, "Ornament", 14.0, "ornament",
         "A bird carved from mango wood and finished by hand, to stand on a shelf or a window sill.",
         (BROWN, BLACK, RED),
         (_a("material", "Material", "Wood"), _a("occasion", "Occasion", "Everyday"),
          _a("form", "Form", "Bird")),
         params=(("form", "bird"),)),
    _row("ORNGOR", "Glass Orb Christmas Ornament", _LW, ORNAMENTS, "Ornament", 12.0, "ornament",
         "A clear glass orb on a small stand, a winter ornament that catches the light of a candle.",
         (RED, GREEN, WHITE),
         (_a("material", "Material", "Glass"), _a("occasion", "Occasion", "Christmas"),
          _a("form", "Form", "Orb")),
         params=(("form", "orb"),)),
    _row("ORNHBD", "Hand Painted Ceramic Bird Ornament", _BM, ORNAMENTS, "Ornament", 16.0, "ornament",
         "A small ceramic bird, hand painted, for a shelf or a mantel.",
         (YELLOW, BLACK, BLUE),
         (_a("material", "Material", "Ceramic"), _a("occasion", "Occasion", "Spring"),
          _a("form", "Form", "Bird")),
         params=(("form", "bird"),)),
)

# --------------------------------------------------------------------------
# Artificial flowers and stems: color x stem height
# --------------------------------------------------------------------------

_LOOSE = _a("holder", "Holder", "Loose")
_VASE = _a("holder", "Holder", "In a Vase")

STEM_ROWS = (
    _row("STMEUC", "Artificial Eucalyptus Stems", _TW, STEMS, "Artificial Flowers", 9.0, "stems",
         "Artificial eucalyptus stems with soft leaves, sold loose, for a vase or a wreath.",
         (GREEN, GREY, WHITE),
         (_a("flower", "Flower", "Eucalyptus"), _LOOSE, _a("material", "Material", "Polyester")),
         _axis((45, 9.0), (60, 11.0), (80, 14.0)), "height_cm", (("flower", "eucalyptus"), ("holder", "loose"))),
    _row("STMPNY", "Artificial Peony Stems", _BM, STEMS, "Artificial Flowers", 12.0, "stems",
         "Artificial peony stems with full layered blooms, sold loose, for a table or a mantel.",
         (PINK, WHITE, RED, YELLOW),
         (_a("flower", "Flower", "Peony"), _LOOSE, _a("material", "Material", "Silk")),
         _axis((45, 12.0), (60, 15.0)), "height_cm", (("flower", "peony"), ("holder", "loose"))),
    _row("STMROV", "Artificial Rose Stems in Vase", _CK, STEMS, "Artificial Flowers", 28.0, "stems",
         "Artificial rose stems arranged in a glass vase, ready to stand on a table.",
         (RED, BLUE, BLACK, YELLOW),
         (_a("flower", "Flower", "Rose"), _VASE, _a("material", "Material", "Silk")),
         _axis((30, 28.0), (40, 34.0)), "height_cm", (("flower", "rose"), ("holder", "vase"))),
    _row("STMPMP", "Artificial Pampas Grass Stems", _LW, STEMS, "Artificial Flowers", 15.0, "stems",
         "Artificial pampas grass stems with tall feathery plumes, sold loose.",
         (NATURAL, CREAM, WHITE),
         (_a("flower", "Flower", "Pampas"), _LOOSE, _a("material", "Material", "Dried-Look Polyester")),
         _axis((70, 15.0), (90, 19.0), (110, 24.0)), "height_cm", (("flower", "pampas"), ("holder", "loose"))),
    _row("STMPVS", "Artificial Pampas Stems in Vase", _EH, STEMS, "Artificial Flowers", 35.0, "stems",
         "Artificial pampas stems in a ceramic vase, a tall floor arrangement.",
         (NATURAL, BLACK),
         (_a("flower", "Flower", "Pampas"), _VASE, _a("material", "Material", "Dried-Look Polyester")),
         _axis((90, 35.0), (110, 42.0)), "height_cm", (("flower", "pampas"), ("holder", "vase"))),
)

# --------------------------------------------------------------------------
# Decorative and trinket trays: color x size
# --------------------------------------------------------------------------

TRAY_ROWS = (
    _row("TRYMBL", "Marble Effect Trinket Tray", _CL, TRAYS, "Decorative Tray", 14.0, "trinket_tray",
         "A round trinket tray with a marble effect finish, for rings, keys and small things.",
         (WHITE, BLACK, GREEN),
         (_a("material", "Material", "Marble Effect"), _a("tray_shape", "Tray shape", "Round")),
         _axis((15, 14.0), (20, 18.0)), "diameter_cm", (("outline", "round"),)),
    _row("TRYWDR", "Wooden Rectangular Decorative Tray", _LN, TRAYS, "Decorative Tray", 22.0, "trinket_tray",
         "A rectangular tray made of acacia wood with two cut-out handles, for the coffee table.",
         (BROWN, BLACK, WHITE),
         (_a("material", "Material", "Wood"), _a("tray_shape", "Tray shape", "Rectangular")),
         _axis((30, 22.0), (40, 28.0), (50, 36.0)), "length_cm", (("outline", "rectangular"),)),
    _row("TRYMTL", "Gold Metal Trinket Tray", _EH, TRAYS, "Decorative Tray", 16.0, "trinket_tray",
         "A round metal trinket tray with a raised rim and a gold finish.",
         (GOLD, RED, BLUE, YELLOW),
         (_a("material", "Material", "Metal"), _a("tray_shape", "Tray shape", "Round")),
         _axis((15, 16.0), (20, 21.0)), "diameter_cm", (("outline", "round"),)),
    _row("TRYMRT", "Mirrored Rectangular Decorative Tray", _BM, TRAYS, "Decorative Tray", 26.0, "trinket_tray",
         "A rectangular tray with a mirrored base and a metal rim, for perfume and candles.",
         (SILVER, BLACK, GREEN),
         (_a("material", "Material", "Metal"), _a("tray_shape", "Tray shape", "Rectangular")),
         _axis((25, 26.0), (35, 34.0)), "length_cm", (("outline", "rectangular"),)),
)

# --------------------------------------------------------------------------
# Door stops: color only
# --------------------------------------------------------------------------

STOP_ROWS = (
    _row("DRSWDG", "Rubber Wedge Door Stop", _HP, STOPS, "Door Stop", 3.0, "door_stop",
         "A rubber wedge that grips the floor and holds a door open.",
         (BLACK, WHITE, RED, BLUE),
         (_a("material", "Material", "Rubber"), _kg("weight", "Weight", 0.2),
          _a("stop_type", "Stop type", "Wedge")),
         params=(("kind", "wedge"),)),
    _row("DRSCST", "Cast Iron Weighted Door Stop", _CK, STOPS, "Door Stop", 14.0, "door_stop",
         "A heavy cast iron door stop with a carrying handle, for a door that swings shut.",
         (BLACK, GREEN, YELLOW),
         (_a("material", "Material", "Cast Iron"), _kg("weight", "Weight", 1.8),
          _a("stop_type", "Stop type", "Weighted")),
         params=(("kind", "weighted"),)),
    _row("DRSFBR", "Fabric Weighted Door Stop", _TW, STOPS, "Door Stop", 9.0, "door_stop",
         "A cotton door stop filled with sand, which sits behind a door and holds it open.",
         (BLUE, RED, WHITE),
         (_a("material", "Material", "Cotton"), _kg("weight", "Weight", 1.2),
          _a("stop_type", "Stop type", "Weighted")),
         params=(("kind", "weighted"),)),
)

# --------------------------------------------------------------------------
# Wallpaper: color x roll length
# --------------------------------------------------------------------------

_STRIPE = cw("Blue", "#f4f1ea", "stripe", "#3f6fb5")
_SPOT = cw("Yellow", "#f4f1ea", "polka", "#f2c230")
_CHECK = cw("Green", "#f4f1ea", "gingham", "#4f8a3a")

WALLPAPER_ROWS = (
    _row("WLPPLN", "Plain Matt Wallpaper", _LW, WALLPAPER, "Wallpaper", 16.0, "wallpaper",
         "A plain matt wallpaper that is easy to paste and hides a lightly uneven wall.",
         (WHITE, GREY, GREEN, BLACK, RED, BLUE, YELLOW),
         (_a("pattern", "Pattern", "Plain"), _a("finish", "Finish", "Matt"), _cm("roll_width", "Roll width", 53)),
         _axis((5, 16.0), (10, 28.0)), "roll_length_m", (("finish", "matt"),)),
    _row("WLPSTR", "Striped Wallpaper", _EH, WALLPAPER, "Wallpaper", 18.0, "wallpaper",
         "A wallpaper with a wide stripe running down the roll, matched across the join.",
         (_STRIPE, cw("Red", "#f4f1ea", "stripe", "#c8312e")),
         (_a("pattern", "Pattern", "Striped"), _a("finish", "Finish", "Matt"), _cm("roll_width", "Roll width", 53)),
         _axis((10, 18.0), (15, 26.0)), "roll_length_m", (("finish", "matt"),)),
    _row("WLPSPT", "Spotted Metallic Wallpaper", _BM, WALLPAPER, "Wallpaper", 24.0, "wallpaper",
         "A spotted wallpaper with a metallic sheen that catches the light.",
         (_SPOT, cw("Black", "#f4f1ea", "polka", "#2d2d33")),
         (_a("pattern", "Pattern", "Spotted"), _a("finish", "Finish", "Metallic"), _cm("roll_width", "Roll width", 53)),
         _axis((10, 24.0), (15, 34.0)), "roll_length_m", (("finish", "metallic"),)),
    _row("WLPCHK", "Checked Wallpaper", _TW, WALLPAPER, "Wallpaper", 20.0, "wallpaper",
         "A checked wallpaper with a soft gingham weave look, for a kitchen or a hall.",
         (_CHECK, cw("Blue", "#f4f1ea", "gingham", "#3f6fb5")),
         (_a("pattern", "Pattern", "Checked"), _a("finish", "Finish", "Matt"), _cm("roll_width", "Roll width", 53)),
         _axis((10, 20.0),), "roll_length_m", (("finish", "matt"),)),
)

# --------------------------------------------------------------------------
# Greeting cards (by design) and diaries (by color)
# --------------------------------------------------------------------------

_DESIGNS = ("Balloons", "Cake", "Tree", "Heart")


def _designs(price: float, *names: str) -> tuple[tuple[str, float], ...]:
    return tuple((n, price) for n in names)


CARD_ROWS = (
    _row("GRCBDY", "Birthday Greeting Card", _TW, CARDS, "Greeting Card", 2.5, "greeting_card",
         "A blank inside birthday card with an envelope, in a choice of designs.",
         (WHITE,),
         (_a("occasion", "Occasion", "Birthday"), _a("card_size", "Card size", "Standard")),
         _designs(2.5, "Balloons", "Cake"), "design", (("design", "balloons"),), colorless=True),
    _row("GRCXMS", "Christmas Greeting Card", _LW, CARDS, "Greeting Card", 2.0, "greeting_card",
         "A Christmas card with a festive picture on the front and a blank inside, with an envelope.",
         (WHITE,),
         (_a("occasion", "Occasion", "Christmas"), _a("card_size", "Card size", "Standard")),
         _designs(2.0, "Tree", "Heart"), "design", (("design", "tree"),), colorless=True),
    _row("GRCTHX", "Thank You Greeting Card", _EH, CARDS, "Greeting Card", 2.5, "greeting_card",
         "A thank you card with a heart on the front, a blank inside and an envelope.",
         (WHITE,),
         (_a("occasion", "Occasion", "Thank You"), _a("card_size", "Card size", "Large")),
         _designs(2.5, "Heart"), "design", (("design", "heart"),), colorless=True),
    _row("GRCANV", "Anniversary Greeting Card", _CL, CARDS, "Greeting Card", 3.5, "greeting_card",
         "An anniversary card with a heart on the front and a message inside, with an envelope.",
         (WHITE,),
         (_a("occasion", "Occasion", "Anniversary"), _a("card_size", "Card size", "Large")),
         _designs(3.5, "Heart", "Balloons"), "design", (("design", "heart"),), colorless=True),
)

DIARY_ROWS = (
    _row("DRYWTV", "Week to View Diary", _CL, DIARIES, "Diary", 9.0, "diary",
         "A hardback diary with a week on every spread and a ribbon marker.",
         (RED, BLUE, GREEN, YELLOW, BLACK, WHITE),
         (_a("diary_year", "Year", "2027"), _a("page_layout", "Page layout", "Week to View"),
          _a("paper_size", "Paper size", "A5")),
         params=(("band", "no"),)),
    _row("DRYDPG", "Day a Page Diary with Elastic Band", _HP, DIARIES, "Diary", 12.0, "diary",
         "A hardback diary with a full page for every day, an elastic band to keep it closed and a ribbon marker.",
         (BLACK, BLUE, RED),
         (_a("diary_year", "Year", "2027"), _a("page_layout", "Page layout", "Day a Page"),
          _a("paper_size", "Paper size", "A5")),
         params=(("band", "yes"),)),
    _row("DRYPKT", "Pocket Diary", _BM, DIARIES, "Diary", 6.0, "diary",
         "A small diary with a week to view that fits in a coat pocket.",
         (GREEN, WHITE, YELLOW),
         (_a("diary_year", "Year", "2027"), _a("page_layout", "Page layout", "Week to View"),
          _a("paper_size", "Paper size", "A6")),
         params=(("band", "no"),)),
)

# --------------------------------------------------------------------------
# Picnic blankets: color x dimensions
# --------------------------------------------------------------------------

BLANKET_ROWS = (
    _row("PCBWTP", "Waterproof Picnic Blanket", _HP, BLANKETS, "Picnic Blanket", 18.0, "picnic_blanket",
         "A picnic blanket with a waterproof backing that keeps out damp grass, folding to a carry bag.",
         (RED, BLUE, GREEN, YELLOW),
         (_yes("waterproof_backing", "Waterproof backing"), _a("material", "Material", "Fleece")),
         (("130 x 150 cm", 18.0), ("150 x 200 cm", 24.0)), "dimensions", (("backing", "waterproof"),)),
    _row("PCBWLN", "Wool Picnic Blanket", _TW, BLANKETS, "Picnic Blanket", 32.0, "picnic_blanket",
         "A thick wool picnic blanket with a fringed edge and a leather carry strap.",
         (NAVY, TAN, BLACK),
         (_a("waterproof_backing", "Waterproof backing", "No"), _a("material", "Material", "Wool")),
         (("140 x 170 cm", 32.0),), "dimensions", (("backing", "plain"),)),
    _row("PCBXLG", "Extra Large Waterproof Picnic Blanket", _LW, BLANKETS, "Picnic Blanket", 28.0, "picnic_blanket",
         "A big picnic blanket with a waterproof backing, wide enough for a family and a basket.",
         (WHITE, BLACK, GREEN),
         (_yes("waterproof_backing", "Waterproof backing"), _a("material", "Material", "Polyester")),
         (("200 x 200 cm", 28.0), ("200 x 230 cm", 34.0)), "dimensions", (("backing", "waterproof"),)),
)

TYPE_ROWS = (*CLOCK_ROWS, *ORNAMENT_ROWS, *STEM_ROWS, *TRAY_ROWS, *STOP_ROWS, *WALLPAPER_ROWS,
             *CARD_ROWS, *DIARY_ROWS, *BLANKET_ROWS)  # fmt: skip

# --------------------------------------------------------------------------
# Text-match decoys (gen#294): another product that holds the type's word
# --------------------------------------------------------------------------

_TOY = ("Toys", "Baby & Toddler", "Wooden Toys")
_CUSH = (_HOME, "Soft Furnishings", "Cushions")
_BOX = (_HOME, "Storage", "Storage Boxes")
_MUG = (_HOME, "Kitchen & Dining", "Drinkware", "Mugs")
_TOWEL = (_HOME, "Kitchen & Dining", "Tea Towels")
_BOUQ = ("Garden", "Flowers", "Bouquets")
_GLASS = (_HOME, "Kitchen & Dining", "Glassware")
_UTEN = (_HOME, "Kitchen & Dining", "Kitchen Utensils")
_BAG = (_GIFTS, "Gift Wrap", "Gift Bags")


def _decoy(code: str, title: str, brand: str, path: tuple[str, ...], ptype: str, price: float,
           shape: str, description: str, color, material: str, audience: str = "adult") -> Row:
    return _row(code, title, brand, path, ptype, price, shape, description, (color,),
                (_a("material", "Material", material),), audience=audience)


DECOYS = (
    _decoy("DCYCLW", "Clockwork Robot", _CL, _TOY, "Wooden Toy", 9.0, "wooden_toy",
           "A wooden robot that walks when its key is wound, a toy for ages 3 and up, not a clock.",
           NATURAL, "Wood", "kids"),
    _decoy("DCYCLC", "Grandfather Clock Print Cushion", _BM, _CUSH, "Cushion", 12.0, "cushion",
           "A cushion printed with a picture of a grandfather clock, which tells no time.",
           CREAM, "Cotton"),
    _decoy("DCYORS", "Ornament Storage Box", _HP, _BOX, "Storage Box", 11.0, "storage_box",
           "A padded storage box with dividers that keeps glass ornaments safe between seasons.",
           GREY, "Fabric"),
    _decoy("DCYORM", "Cat Ornament Mug", _TW, _MUG, "Mug", 7.0, "mug",
           "A ceramic mug printed with a cat on a shelf of ornaments.",
           WHITE, "Ceramic"),
    _decoy("DCYSTB", "Fresh Rose Stems Bouquet", _TW, _BOUQ, "Bouquet", 22.0, "bouquet",
           "A bouquet of fresh cut rose stems, delivered in water. These are real flowers, not artificial ones.",
           PINK, "Fresh Flowers"),
    _decoy("DCYSTG", "Long Stem Wine Glass", _CK, _GLASS, "Glassware", 6.0, "drinking_glass",
           "A wine glass on a long stem, sold singly. It holds a drink, not flowers.",
           cw("Clear", "#dfe8ea"), "Glass"),
    _decoy("DCYTRB", "Tray Bake Spatula", _LN, _UTEN, "Kitchen Utensil", 5.0, "kitchen_utensil",
           "A flat spatula with a thin edge for lifting a tray bake from its tin.",
           BLACK, "Silicone"),
    _decoy("DCYTRT", "Tray Print Tea Towel", _CL, _TOWEL, "Tea Towels", 5.0, "tea_towel",
           "A cotton tea towel printed with a tea tray and cups.",
           WHITE, "Cotton"),
    _decoy("DCYWLC", "Wallpaper Print Cushion", _EH, _CUSH, "Cushion", 14.0, "cushion",
           "A cushion cut from fabric in a wallpaper design of leaves.",
           GREEN, "Cotton"),
    _decoy("DCYWLB", "Wallpaper Stripe Gift Bag", _LW, _BAG, "Gift Bag", 3.0, "gift_bag",
           "A paper gift bag printed in the stripes of a wallpaper.",
           CREAM, "Paper"),
    _decoy("DCYCRD", "Birthday Card Tea Towel", _CL, _TOWEL, "Tea Towels", 5.0, "tea_towel",
           "A cotton tea towel printed with a birthday card. It is a tea towel, not a greeting.",
           RED, "Cotton"),
    _decoy("DCYCRM", "Thank You Card Mug", _BM, _MUG, "Mug", 7.0, "mug",
           "A ceramic mug printed with a thank you card, a gift for a teacher.",
           BLUE, "Ceramic"),
    _decoy("DCYDRC", "Diary Print Cushion", _CK, _CUSH, "Cushion", 13.0, "cushion",
           "A cushion printed with the cover of an old diary.",
           BROWN, "Cotton"),
    _decoy("DCYDRB", "Diary Lock Storage Box", _HP, _BOX, "Storage Box", 15.0, "storage_box",
           "A small storage box with a key lock, for keeping a diary private.",
           BLACK, "Metal"),
    _decoy("DCYPCC", "Picnic Blanket Print Cushion", _LW, _CUSH, "Cushion", 12.0, "cushion",
           "A cushion in the red check of a picnic blanket.",
           RED, "Cotton"),
    _decoy("DCYPCT", "Picnic Blanket Tote Gift Bag", _TW, _BAG, "Gift Bag", 4.0, "gift_bag",
           "A paper gift bag with a picnic blanket pattern, for a summer present.",
           YELLOW, "Paper"),
    _decoy("DCYDSC", "Door Stop Cat Cushion", _EH, _CUSH, "Cushion", 12.0, "cushion",
           "A heavy cat shaped cushion that some people lean on a door; it is not a door stop.",
           GREY, "Cotton"),
    _decoy("DCYDSB", "Door Stop Sign Gift Bag", _HP, _BAG, "Gift Bag", 3.0, "gift_bag",
           "A paper gift bag printed with a door sign.",
           WHITE, "Paper"),
)

ROWS = (*TYPE_ROWS, *DECOYS)


def docs() -> list[dict]:
    """Every row's catalog document."""
    return [r.doc() for r in ROWS]


def decoy_ids() -> frozenset[str]:
    """The decoys' product ids: ``main_colors.complete`` leaves them as authored."""
    return frozenset(f"BRD-{r.code}" for r in DECOYS)
