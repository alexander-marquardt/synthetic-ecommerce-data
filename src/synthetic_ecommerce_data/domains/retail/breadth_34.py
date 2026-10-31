"""The breadth rows of gen#34 (:mod:`breadth_rows`): the leaves shopper queries land on."""

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.breadth_cleaning import _CJ, _spray
from synthetic_ecommerce_data.domains.retail.breadth_food import _FD, _flavor
from synthetic_ecommerce_data.domains.retail.breadth_row import Row, _fab, _mat
from synthetic_ecommerce_data.domains.retail.breadth_toys import _KIDS
from synthetic_ecommerce_data.domains.retail.variants import Color, cw

# --------------------------------------------------------------------------
# gen#34, first increment: one or two plain products in each of 20 new leaves, so more
# shopper queries (cutlery, dinner set, claw hammer, cherries, oven cleaner) land on a
# category at all. Each leaf has no derived styles unless its two rows differ in a value.
# --------------------------------------------------------------------------


def _a1(key: str, name: str, v: str) -> tuple[tuple[str, str, str], ...]:
    return ((key, name, v),)


def _volts(v: int) -> tuple[tuple[str, str, str, str, float], ...]:
    """A tool's battery voltage: the unit is in the key (``_v``), the canonical value in volts."""
    return (("voltage_v", "Voltage", str(v), "VLT", float(v)),)


def _pieces(n: int) -> tuple[tuple[str, str, str, str], ...]:
    """How many pieces a set holds: a count (unit code C62), so a facet can range over it."""
    return (("piece_count", "Piece count", str(n), "C62"),)


class Contents(tuple):
    """What a set holds, as ``(quantity, name)`` pairs: the one source of its piece count,
    the "N Piece" in its title and the first sentence of its description."""

    __slots__ = ()

    def __new__(cls, *items: tuple[int, str]) -> Contents:
        return super().__new__(cls, items)

    @property
    def n(self) -> int:
        return sum(q for q, _ in self)

    @property
    def sentence(self) -> str:
        parts = [f"{q} {name}" for q, name in self]
        head = ", ".join(parts[:-1])
        return f"Includes {head + ' and ' if head else ''}{parts[-1]}."

    def title(self, name: str) -> str:
        return f"{name}, {self.n} Piece"

    def text(self, rest: str) -> str:
        return f"{self.sentence} {rest}"

    @property
    def attrs(self) -> tuple[tuple[str, str, str, str], ...]:
        return _pieces(self.n)


_CUT16 = Contents((4, "knives"), (4, "forks"), (4, "dessert spoons"), (4, "teaspoons"))
_CUT24 = Contents((6, "knives"), (6, "forks"), (6, "dessert spoons"), (6, "teaspoons"))
_DIN12 = Contents((4, "dinner plates"), (4, "side plates"), (4, "bowls"))
_DIN16 = Contents((4, "dinner plates"), (4, "side plates"), (4, "bowls"), (4, "mugs"))
_SCR6 = Contents((3, "slotted screwdrivers"), (3, "Phillips screwdrivers"))
_BIT32 = Contents((8, "slotted bits"), (8, "Phillips bits"), (8, "Torx bits"), (8, "hex bits"))
_BIT100 = Contents(
    (24, "slotted bits"),
    (24, "Phillips bits"),
    (24, "Torx bits"),
    (24, "hex bits"),
    (2, "holders"),
    (1, "bit extender"),
    (1, "case"),
)
_SKT40 = Contents((38, "metric sockets"), (1, "ratchet"), (1, "extension bar"))
_SKT94 = Contents(
    (44, "metric sockets"),
    (44, "imperial sockets"),
    (2, "ratchets"),
    (2, "extension bars"),
    (2, "bit adaptors"),
)
_DINO6 = Contents((6, "dinosaurs"))


def _in(hex_: str, accent: str = "#2a2a2e", name: str = "Grey") -> tuple[Color, ...]:
    return (cw(name, hex_, "solid", accent),)


_HW = "Home"
_KD = ("Home", "Kitchen & Dining")
_DIY = ("Home", "DIY & Tools")
_FRUIT = ("Food & Drink", "Fruit & Vegetables", "Fresh Fruit")

BREADTH_34 = (
    Row("CUTSET", _CUT16.title("Stainless Steel Cutlery Set"), "Hearth & Table", _HW,
        (*_KD, "Cutlery Sets"), "Cutlery Set", 18.0, "cutlery_set",
        _CUT16.text("A plain polished handle. Dishwasher safe."),
        _in("#b9bcc0", "#7a7d82", "Silver"),
        (*_a1("material", "Material", "Stainless Steel"), *_CUT16.attrs)),
    Row("CUTBAM", _CUT24.title("Bamboo Handle Cutlery Set"), "Lanternby", _HW,
        (*_KD, "Cutlery Sets"), "Cutlery Set", 32.0, "cutlery_set",
        _CUT24.text("A bamboo handle and a satin steel head. Hand wash."),
        _in("#c9a46a", "#7a7d82", "Brown"),
        (*_a1("material", "Material", "Bamboo"), *_CUT24.attrs)),
    Row("DINPOR", _DIN12.title("White Porcelain Dinner Set"), "Hearth & Table", _HW,
        (*_KD, "Dinner Sets"), "Dinner Set", 38.0, "dinner_set",
        _DIN12.text("A rolled rim. Oven and microwave safe."),
        _in("#f4f1ea", "#b9b4a6", "White"),
        (*_a1("material", "Material", "Porcelain"), *_DIN12.attrs)),
    Row("DINSTO", _DIN16.title("Speckled Stoneware Dinner Set"), "Calderby & Lune", _HW,
        (*_KD, "Dinner Sets"), "Dinner Set", 56.0, "dinner_set",
        _DIN16.text("Glazed by hand so no two speckle alike."),
        _in("#d8cdb8", "#6b5b45", "Cream"),
        (*_a1("material", "Material", "Stoneware"), *_DIN16.attrs)),
    Row("STRJAR", "Glass Storage Jar with Lid", "Lanternby", _HW,
        (*_KD, "Storage Jars"), "Storage Jar", 6.0, "jar",
        "A clear jar with an airtight clip lid, for flour, pasta or biscuits.",
        _in("#cfe3e6", "#7a7d82", "Clear"), _a1("material", "Material", "Glass"),
        (("0.5 L", 6.0), ("1 L", 8.0), ("2 L", 11.0))),
    Row("LNCBOX", "Leakproof Lunch Box", "Hearth & Table", _HW,
        (*_KD, "Lunch Boxes"), "Lunch Box", 9.0, "box",
        "A lunch box with three compartments and a locking lid. Dishwasher safe.",
        (cw("Green", "#4f7a3a", "solid", "#efe8d8"), cw("Navy", "#26365c", "solid", "#efe8d8")),
        _a1("material", "Material", "Recycled Plastic")),
    Row("APRCTN", "Cotton Kitchen Apron with Pocket", "Hearth & Table", _HW,
        (*_KD, "Aprons"), "Apron", 12.0, "apron",
        "An adjustable neck strap, a wide front pocket and ties that wrap around twice.",
        (cw("Sage", "#9bb08f"), cw("Navy", "#26365c"), cw("Rust", "#a4502a")),
        _fab("Cotton")),
    Row("SCRDSET", _SCR6.title("Slotted and Phillips Screwdriver Set"), "Calderby & Lune", _HW,
        (*_DIY, "Tool Sets", "Screwdriver Sets"), "Screwdriver Set", 13.0, "screwdriver",
        _SCR6.text("Magnetic tips and a soft grip handle, in a roll-up pouch."),
        _in("#c8312e", "#2a2a2e", "Red"),
        (*_a1("tip_type", "Tip type", "Slotted and Phillips"), *_SCR6.attrs)),
    Row("BITSML", _BIT32.title("Screwdriver Bit Set"), "Calderby & Lune", _HW,
        (*_DIY, "Tool Sets", "Bit Sets"), "Bit Set", 9.0, "screwdriver",
        _BIT32.text("A magnetic holder, in a snap-shut case."),
        _in("#2a2a2e", "#c8312e", "Black"),
        (*_a1("drive_type", "Drive type", "Mixed"), *_BIT32.attrs)),
    Row("BITLRG", _BIT100.title("Screwdriver Bit Set"), "Calderby & Lune", _HW,
        (*_DIY, "Tool Sets", "Bit Sets"), "Bit Set", 19.0, "screwdriver",
        _BIT100.text("Stored in a snap-shut case."),
        _in("#2a2a2e", "#c8312e", "Black"),
        (*_a1("drive_type", "Drive type", "Mixed"), *_BIT100.attrs)),
    Row("SKTSML", _SKT40.title("Socket Set"), "Calderby & Lune", _HW,
        (*_DIY, "Tool Sets", "Socket Sets"), "Socket Set", 22.0, "box",
        _SKT40.text("In a molded case."),
        _in("#7a7d82", "#c8312e", "Silver"),
        (*_a1("material", "Material", "Chrome Vanadium"), *_SKT40.attrs)),
    Row("SKTLRG", _SKT94.title("Socket Set"), "Calderby & Lune", _HW,
        (*_DIY, "Tool Sets", "Socket Sets"), "Socket Set", 45.0, "box",
        _SKT94.text("In a molded case."),
        _in("#7a7d82", "#c8312e", "Silver"),
        (*_a1("material", "Material", "Chrome Vanadium"), *_SKT94.attrs)),
    Row("PERJAS", "Midnight Jasmine Eau de Parfum", "Mirefield Naturals", "Beauty",
        ("Beauty", "Fragrance", "Perfume"), "Perfume", 28.0, "fragrance",
        "A warm floral with jasmine and a trace of vanilla, in a glass bottle with a cap.",
        _in("#d9c2e8", "#2a2a2e", "Purple"), _a1("fragrance_family", "Fragrance family", "Floral"),
        ((30.0, 28.0), (50.0, 38.0), (100.0, 55.0)), size_key="net_volume_ml"),
    Row("PERCIT", "Citrus Grove Eau de Toilette", "Mirefield Naturals", "Beauty",
        ("Beauty", "Fragrance", "Perfume"), "Perfume", 22.0, "fragrance",
        "A bright citrus with bergamot and neroli, in a clear glass bottle with a cap.",
        _in("#f2e29b", "#2a2a2e", "Yellow"), _a1("fragrance_family", "Fragrance family", "Citrus"),
        ((30.0, 22.0), (50.0, 30.0), (100.0, 44.0)), size_key="net_volume_ml"),
    Row("EYLBLK", "Waterproof Eyeliner Pencil", "Hollin Hair", "Beauty",
        ("Beauty", "Make-Up", "Eyes", "Eyeliners"), "Eyeliner", 5.0, "eyeliner",
        "A soft pencil that glides on and stays put all day. Twist up, no sharpening.",
        (cw("Black", "#2a2a2e"), cw("Brown", "#5a3a26"), cw("Navy", "#26365c")),
        _a1("finish", "Finish", "Matte")),
    Row("DINOFG", _DINO6.title("Plastic Dinosaur Figure Set"), "Puddlecombe Toys", "Toys",
        ("Toys", "Figures & Playsets", "Dinosaur Figures"), "Toy Figure", 8.0, "dinosaur",
        _DINO6.text("Chunky, with painted detail, sized for small hands. For ages 3 and up."),
        (cw("Green", "#6f8f4a"),), (*_mat("Plastic"), *_DINO6.attrs), audience=_KIDS),
    Row("DAISYP", "Marguerite Daisy Plant", "Fenwold Nursery", "Garden",
        ("Garden", "Plants", "Daisies"), "Bedding Plant", 5.0, "daisy",
        "A compact plant covered in white flowers from spring to autumn, in a 12 cm pot.",
        (cw("White", "#ffffff", "solid", "#f2d14b"),), _a1("variety", "Variety", "Marguerite"),
        colorless=True),
    Row("SEEDPM", "Giant Pumpkin Seeds", "Fenwold Nursery", "Garden",
        ("Garden", "Seeds", "Pumpkin Seeds"), "Seeds", 2.5, "pumpkin",
        "A packet of ten seeds for large orange pumpkins. Sow indoors in spring.",
        (cw("Orange", "#e07a1f", "solid", "#4f7a3a"),), _a1("variety", "Variety", "Atlantic Giant"),
        colorless=True),
    Row("SEEDCR", "Nantes Carrot Seeds", "Fenwold Nursery", "Garden",
        ("Garden", "Seeds", "Carrot Seeds"), "Seeds", 2.0, "carrot",
        "A packet of about 500 seeds for sweet, blunt roots. Sow straight into the ground.",
        (cw("Orange", "#e07a1f", "solid", "#4f7a3a"),), _a1("variety", "Variety", "Nantes"),
        colorless=True),
    Row("DNUTSG", "Sugar Ring Doughnuts, Pack of 4", "Pantry Mill", _FD,
        ("Food & Drink", "Bakery", "Doughnuts"), "Doughnut", 2.0, "doughnut",
        "Light ring doughnuts rolled in sugar, baked in store each morning.",
        (cw("Tan", "#d9a05b", "solid", "#ffffff"),), _flavor("Sugar"), colorless=True),
    Row("STRBRY", "Fresh British Strawberries", "Freshfold", _FD,
        (*_FRUIT, "Berries", "Strawberry Punnets"), "Fresh Fruit", 2.5,
        "strawberry",
        "Sweet, juicy strawberries picked at the height of summer, packed in a recyclable punnet.",
        (cw("Red", "#c8312e", "solid", "#4f7a3a"),), _a1("variety", "Variety", "Elsanta"),
        (("400 g", 2.5), ("800 g", 4.5)), colorless=True),
    Row("OVNSPR", "Heavy Duty Oven Cleaner Spray", "Pantry Mill", _CJ,
        ("Cleaning", "Kitchen & Surfaces", "Cleaners", "Oven Cleaners"), "Oven Cleaner", 3.5,
        "trigger_spray",
        "A foaming spray that loosens baked-on grease from oven walls, racks and hobs.",
        _spray("Yellow"), _a1("form", "Form", "Foam Spray"), colorless=True,
        sizes=((300.0, 2.5), (500.0, 3.5), (750.0, 4.8)), size_key="net_volume_ml"),
    Row("LMSSPR", "Limescale Remover Spray", "Freshfold", _CJ,
        ("Cleaning", "Bathroom", "Limescale Removers"), "Limescale Remover", 3.0,
        "trigger_spray",
        "A fast spray for kettles, taps and shower heads: leave a few minutes, then rinse.",
        _spray("Aqua"), _a1("form", "Form", "Spray"), colorless=True,
        sizes=((250.0, 2.0), (500.0, 3.0), (750.0, 4.0)), size_key="net_volume_ml"),
)  # fmt: skip
