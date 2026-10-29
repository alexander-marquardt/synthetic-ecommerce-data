"""The Electronics department's rows (gen#332): phones, computers, tablets and their accessories.

Data only. The fifteen spec files of ``type_specs/`` (``smartphone.py`` ... ``monitor.py``) each take
one list from here, so a spec stays a few lines and the department reads in one place.

Real names: Apple, iPhone and iPad only, as text (``real_brands.ALLOWED``; no logo, no trade
dress, the drawings carry none). Every other brand is invented (``electronics_brand_styles``). An
accessory keeps an invented brand and names the phone it fits ("Clear Case for iPhone 15"): that
is true and it is the model-word decoy, a query for the phone also finds its cases. A phone's
operating system is named ``Apple OS`` or ``Open Mobile OS``: no real system name appears.
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.core.entry import canonical
from synthetic_ecommerce_data.domains.retail import (
    kit_electronics,  # noqa: F401 -- registers smartphone, laptop, tablet, phone_case, ...
)
from synthetic_ecommerce_data.domains.retail.breadth_rows import Row
from synthetic_ecommerce_data.domains.retail.furniture_rows import FurnitureRow
from synthetic_ecommerce_data.domains.retail.variants import cw

DEPARTMENT = "Electronics"
APPLE = "Apple"
HALVERN, TORVANE, NIMBREL, QUORRIN = "Halvern", "Torvane", "Nimbrel", "Quorrin"
DASKEL, MERVANE, PELLIMAR = "Daskel", "Mervane", "Pellimar"
CINDREL, BOLTWICK, WEXMOOR, DUNVALE, ARDMOOR, MARRICK = (
    "Cindrel", "Boltwick", "Wexmoor", "Dunvale", "Ardmoor", "Marrick")  # fmt: skip

#: Every brand of the department. Apple is a real name used as text; the rest are invented.
ELECTRONICS_OWNERS = tuple(
    (b, "third_party")
    for b in (APPLE, HALVERN, TORVANE, NIMBREL, QUORRIN, DASKEL, MERVANE, PELLIMAR, CINDREL,
              BOLTWICK, WEXMOOR, DUNVALE, ARDMOOR, MARRICK)
)  # fmt: skip

RED = cw("Red", "#c8312e")
BLUE = cw("Blue", "#3f6fb5")
GREEN = cw("Green", "#4f8a3a")
YELLOW = cw("Yellow", "#f2c230")
BLACK = cw("Black", "#2d2d33")
WHITE = cw("White", "#f4f1ea", "solid", "#9a9ca0")
SILVER = cw("Silver", "#c4c7cc")
GOLD = cw("Gold", "#d8b56a")
GREY = cw("Grey", "#9a9ca0")
PINK = cw("Pink", "#e59ab0")
PURPLE = cw("Purple", "#7b5aa6")
NAVY = cw("Navy", "#25365e")
TEAL = cw("Teal", "#2f8f8a")
ORANGE = cw("Orange", "#e07a1f")
CLEAR = cw("Clear", "#e8f1f7")
CHARCOAL = cw("Charcoal", "#44464d")

_OS = {APPLE: "Apple OS", PELLIMAR: "Pellimar OS"}
_P = (DEPARTMENT, "Phones")
_C = (DEPARTMENT, "Computers")
_T = (DEPARTMENT, "Tablets")
_A = (DEPARTMENT, "Accessories")


def _a(key: str, name: str, v: str) -> tuple[str, str, str]:
    return (key, name, v)


def _in(key: str, name: str, inches: str) -> tuple[str, str, str, str, float]:
    """A length in inches (a screen): the canonical value is in millimetres, as ``INH`` says."""
    return (key, name, inches, "INH", float(canonical(inches, "INH")))


def _row(code, title, brand, path, ptype, price, shape, description, colors, attrs, sizes=(),
         size_key="size", params=(), cls=Row) -> Row:  # fmt: skip
    return cls(code, title, brand, DEPARTMENT, path, ptype, price, shape, description, colors,
               attrs, sizes, size_key=size_key, params=params)  # fmt: skip


# --- Smartphones: line, brand, form, screen, connectivity, price, colors, what it is for -------
_STORAGE = {
    "flagship": (128, 256, 512), "midrange": (128, 256), "budget": (64, 128),
    "foldable": (256, 512), "compact": (128, 256, 512),
}  # fmt: skip
_FORM_TEXT = {
    "flagship": "flagship", "midrange": "mid-range", "budget": "budget",
    "foldable": "folding", "compact": "compact",
}  # fmt: skip
_PHONES = (
    (APPLE, "iPhone 15", "flagship", "6.1", "5G", 799, (BLACK, PINK, BLUE, GOLD), "a bright display and a camera that handles low light well"),
    (APPLE, "iPhone 15 Plus", "flagship", "6.7", "5G", 899, (BLACK, PINK, BLUE, GREEN), "the larger screen of the family and a battery that lasts two days"),
    (APPLE, "iPhone 15 Pro", "flagship", "6.1", "5G", 999, (SILVER, BLACK, GREY, BLUE), "a brushed metal frame, a fast chip and a three-lens camera"),
    (APPLE, "iPhone 14", "midrange", "6.1", "5G", 649, (BLACK, WHITE, BLUE, RED), "a dependable camera and a screen that stays readable in sun"),
    (APPLE, "iPhone 13", "midrange", "6.1", "5G", 549, (BLACK, PINK, BLUE, GREEN), "a long battery life and a camera that copes with fast action"),
    (APPLE, "iPhone SE", "compact", "4.7", "5G", 429, (BLACK, WHITE, RED), "a small body and a home button, for one-handed use"),
    (HALVERN, "Halvern Arc 5", "flagship", "6.4", "5G", 749, (BLACK, SILVER, TEAL, PURPLE), "a curved display and a fast charge that fills the battery in thirty minutes"),
    (HALVERN, "Halvern Arc 5 Pro", "flagship", "6.8", "5G", 949, (BLACK, SILVER, GOLD), "a large display, a periscope zoom lens and a glass back"),
    (HALVERN, "Halvern Arc Fold", "foldable", "7.6", "5G", 1349, (BLACK, SILVER, NAVY), "a tablet-size screen that folds flat to fit a pocket"),
    (HALVERN, "Halvern Arc Lite", "midrange", "6.5", "5G", 329, (BLACK, WHITE, GREEN, ORANGE), "a smooth display and a battery built for a day of streaming"),
    (TORVANE, "Torvane T9", "flagship", "6.7", "5G", 899, (BLACK, WHITE, NAVY, GOLD), "a bright display and a camera tuned for portraits"),
    (TORVANE, "Torvane T7", "midrange", "6.5", "5G", 399, (BLACK, WHITE, BLUE, GREEN), "a sharp display and a camera that does well after dark"),
    (TORVANE, "Torvane T3", "budget", "6.2", "4G", 149, (BLACK, BLUE, RED, GREY), "a big battery and a screen that survives a drop to the pavement"),
    (NIMBREL, "Nimbrel Sky 12", "flagship", "6.9", "5G", 1049, (BLACK, SILVER, BLUE), "the biggest screen the maker has built and a stylus that docks inside"),
    (NIMBREL, "Nimbrel Sky 8", "midrange", "6.4", "5G", 449, (BLACK, WHITE, GREEN, PINK), "a balanced phone with a steady camera and two days of battery"),
    (NIMBREL, "Nimbrel Sky Mini", "compact", "5.8", "5G", 479, (BLACK, WHITE, PURPLE), "a small phone with a flat edge that fits a back pocket"),
    (QUORRIN, "Quorrin Q Max", "flagship", "6.8", "5G", 979, (BLACK, GOLD, GREEN, YELLOW), "a fast processor, a smooth display and a lens set for sports"),
    (QUORRIN, "Quorrin Q Fold", "foldable", "6.7", "5G", 799, (BLACK, PINK, TEAL), "a clamshell that folds to the size of a coaster"),
    (QUORRIN, "Quorrin Q 40", "budget", "6.6", "4G", 179, (BLACK, WHITE, ORANGE, BLUE), "a large display and a battery that charges over a cable or a pad"),
    (DASKEL, "Daskel D50", "midrange", "6.5", "5G", 379, (BLACK, SILVER, RED, TEAL), "a fast display and a camera with night mode"),
    (DASKEL, "Daskel D20", "budget", "6.1", "4G", 119, (BLACK, WHITE, BLUE), "everyday calls, messages and maps on a screen that is easy to read"),
    (MERVANE, "Mervane M6", "midrange", "6.4", "5G", 349, (BLACK, WHITE, GREEN, PURPLE), "a bright display and a camera that shoots clean video"),
    (MERVANE, "Mervane M2", "budget", "6.3", "4G", 99, (BLACK, BLUE, YELLOW), "a simple phone with a large battery and a headphone socket"),
    (PELLIMAR, "Pellimar P11", "flagship", "6.6", "5G", 849, (BLACK, WHITE, SILVER, PINK), "a glass back and a camera that keeps skin tones natural"),
    (PELLIMAR, "Pellimar P5", "compact", "5.9", "5G", 399, (BLACK, WHITE, GOLD), "a light phone with a fast chip and a flat screen"),
    (BOLTWICK, "Boltwick Ridge R1", "midrange", "6.3", "5G", 429, (BLACK, ORANGE, YELLOW, GREEN), "a rubber-sealed body that shrugs off drops, water and dust"),
)  # fmt: skip


def _phone(n: int, brand, line, form, screen, conn, price, colors, note) -> Row:
    tiers = _STORAGE[form]
    sizes = tuple((str(g), price + 60.0 * i) for i, g in enumerate(tiers))
    os_ = _OS.get(brand, "Open Mobile OS")
    return _row(
        f"EPH{n:03d}", f"{line} Smartphone", brand, (*_P, "Smartphones"), "Smartphone", price,
        "smartphone", f"A {_FORM_TEXT[form]} {conn} smartphone with {note}. It runs {os_} and "
        f"comes in {len(tiers)} storage sizes.", colors,
        (_a("model_line", "Model line", line), _a("operating_system", "Operating system", os_),
         _a("connectivity", "Connectivity", conn), _in("screen_size", "Screen size", screen)),
        sizes, "storage_gb", (("form", form),),
    )  # fmt: skip


SMARTPHONES = tuple(_phone(i + 1, *p) for i, p in enumerate(_PHONES))

# --- Basic phones --------------------------------------------------------------------------
_BASIC = (
    (DASKEL, "Daskel Easy Bar", "bar", 29, (BLACK, SILVER, BLUE), "a keypad, a two-week battery and a loud speaker"),
    (QUORRIN, "Quorrin Snap Flip", "flip", 39, (BLACK, RED, PINK), "a hinged lid that ends a call when it closes"),
    (MERVANE, "Mervane Big Button", "bigbutton", 45, (WHITE, BLACK, GREEN), "large keys, a bright screen and a button that calls a saved number"),
    (BOLTWICK, "Boltwick Ridge Basic", "bar", 59, (BLACK, ORANGE, YELLOW), "a sealed body, a torch and a battery that lasts for weeks"),
)  # fmt: skip
BASIC_PHONES = tuple(
    _row(f"EBP{i + 1:03d}", f"{n} Basic Phone", b, (*_P, "Basic Phones"), "Basic Phone", p,
         "basic_phone", f"A basic phone with {note}. It makes calls and sends messages, with no apps.",
         c, (_a("model_line", "Model line", n), _a("operating_system", "Operating system", "Basic OS"),
             _a("connectivity", "Connectivity", "4G")), params=(("form", f),))
    for i, (b, n, f, p, c, note) in enumerate(_BASIC)
)  # fmt: skip

# --- Laptops and desktops: RAM, storage (and a screen) ride on each SKU -------------------
_LAPTOPS = (
    (HALVERN, "Halvern Slate 14", "clamshell", 649, "14", (8, 16), (256, 512), (SILVER, GREY, BLUE), "Integrated", "a thin metal body and a keyboard with deep keys"),
    (HALVERN, "Halvern Slate Flip 13", "two_in_one", 799, "13.3", (8, 16), (256, 512), (SILVER, NAVY, GREEN), "Integrated", "a screen that folds back into a tablet and takes pen input"),
    (TORVANE, "Torvane Book 15", "clamshell", 549, "15.6", (8, 16), (256, 512), (SILVER, BLACK, RED), "Integrated", "a full-size keyboard with a number pad and a bright screen"),
    (TORVANE, "Torvane Fury 16", "gaming", 1199, "16", (16, 32), (512, 1024), (BLACK, RED, BLUE), "Dedicated", "a fast graphics card, a high refresh screen and a cooled base"),
    (NIMBREL, "Nimbrel Air 13", "clamshell", 899, "13.3", (8, 16), (256, 512), (SILVER, WHITE, GOLD), "Integrated", "a light body that weighs just over a kilo and runs a full day"),
    (NIMBREL, "Nimbrel Studio 15", "workstation", 1599, "15.6", (16, 32), (512, 1024), (GREY, BLACK), "Dedicated", "a color-accurate screen and a graphics card for design and video"),
    (QUORRIN, "Quorrin Raider 17", "gaming", 1399, "17.3", (16, 32), (512, 1024), (BLACK, GREEN, PURPLE), "Dedicated", "a large high refresh screen and per-key lighting"),
    (DASKEL, "Daskel Pro 15", "workstation", 1499, "15.6", (16, 32), (512, 1024), (GREY, BLACK, SILVER), "Dedicated", "a certified graphics card and a screen for engineering and simulation"),
    (MERVANE, "Mervane Flex 13", "two_in_one", 699, "13.3", (8, 16), (256, 512), (SILVER, TEAL, PINK, WHITE), "Integrated", "a touch screen that turns through three hundred and sixty degrees"),
    (PELLIMAR, "Pellimar Go 14", "clamshell", 499, "14", (4, 8), (128, 256), (SILVER, BLUE, GREY, WHITE), "Integrated", "an everyday laptop for study and browsing with a battery that lasts the day"),
    (BOLTWICK, "Boltwick Ridge Book 14", "clamshell", 949, "14", (8, 16), (256, 512), (BLACK, ORANGE, GREEN), "Integrated", "a rubber-edged case and a sealed keyboard for building sites and workshops"),
)  # fmt: skip


def _laptop(i, brand, name, form, price, screen, rams, stor, colors, gfx, note) -> Row:
    sizes = tuple(
        (str(s), price + 120.0 * k, (("ram_gb", str(r)), ("screen_size_in", screen)))
        for k, (r, s) in enumerate(zip(rams, stor, strict=True))
    )
    return _row(
        f"ELP{i + 1:03d}", f"{name} Laptop", brand, (*_C, "Laptops"), "Laptop", price, "laptop",
        f"A {screen} inch laptop with {note}. It runs Open Desktop OS.", colors,
        (_a("model_line", "Model line", name), _a("operating_system", "Operating system", "Open Desktop OS"),
         _a("graphics", "Graphics", gfx)),
        sizes, "storage_gb", (("form", form),), FurnitureRow,
    )  # fmt: skip


LAPTOPS = tuple(_laptop(i, *r) for i, r in enumerate(_LAPTOPS))

_DESKTOPS = (
    (HALVERN, "Halvern Tower 5", "tower", 599, (8, 16), (256, 512), (BLACK, WHITE, SILVER), "a tower with room for two drives and a quiet fan"),
    (TORVANE, "Torvane Forge", "tower", 1299, (16, 32), (512, 1024), (BLACK, RED, BLUE), "a glass side panel, a dedicated graphics card and lit fans"),
    (NIMBREL, "Nimbrel Hub One", "all_in_one", 849, (8, 16), (256, 512), (WHITE, SILVER, GREY), "a 24 inch screen and the computer built into its stand"),
    (QUORRIN, "Quorrin Arena", "tower", 1799, (16, 32), (512, 1024), (BLACK, GREEN, PURPLE), "a liquid-cooled gaming build with a fast graphics card"),
    (DASKEL, "Daskel Station", "tower", 1099, (16, 32), (512, 1024), (BLACK, GREY), "a workstation with an error-correcting memory slot and a quiet case"),
    (MERVANE, "Mervane Canvas", "all_in_one", 1099, (8, 16), (256, 512), (WHITE, SILVER, TEAL, PINK), "a 27 inch touch screen on a tilting stand"),
    (PELLIMAR, "Pellimar Cube", "mini", 349, (4, 8), (128, 256), (BLACK, SILVER, WHITE), "a mini computer small enough to fit behind a monitor"),
    (MARRICK, "Marrick Mini Pro", "mini", 549, (8, 16), (256, 512), (SILVER, BLACK, GREY), "a palm-size computer with four screen outputs"),
    (BOLTWICK, "Boltwick Ridge Desk", "tower", 749, (8, 16), (256, 512), (BLACK, ORANGE, GREY), "a dust-filtered case for a workshop or a shop floor"),
)  # fmt: skip


def _desktop(i, brand, name, form, price, rams, stor, colors, note) -> Row:
    sizes = tuple(
        (str(s), price + 130.0 * k, (("ram_gb", str(r)),))
        for k, (r, s) in enumerate(zip(rams, stor, strict=True))
    )
    return _row(
        f"EDK{i + 1:03d}", f"{name} Desktop Computer", brand, (*_C, "Desktops"),
        "Desktop Computer", price, "desktop", f"A desktop computer with {note}. It runs Open Desktop OS.",
        colors, (_a("model_line", "Model line", name),
                 _a("operating_system", "Operating system", "Open Desktop OS")),
        sizes, "storage_gb", (("form", form),), FurnitureRow,
    )  # fmt: skip


DESKTOPS = tuple(_desktop(i, *r) for i, r in enumerate(_DESKTOPS))

# --- Tablets and e-readers -----------------------------------------------------------------
_TABLETS = (
    (APPLE, "iPad", "standard", "10.9", 349, (SILVER, BLUE, PINK, YELLOW), "a bright screen, a front camera on the long edge and a day of battery"),
    (APPLE, "iPad Air", "standard", "10.9", 599, (GREY, BLUE, PURPLE, GOLD), "a thin body, a fast chip and support for a pencil"),
    (APPLE, "iPad Pro", "pro", "12.9", 1099, (SILVER, BLACK), "a large screen with a high refresh rate and a keyboard connector"),
    (APPLE, "iPad mini", "standard", "8.3", 499, (GREY, PURPLE, PINK, GOLD), "a small screen that fits in one hand"),
    (HALVERN, "Halvern Tab 10", "standard", "10.1", 229, (GREY, BLUE, SILVER), "a sharp screen, four speakers and two days of battery"),
    (TORVANE, "Torvane Slate Pro", "pro", "11", 549, (GREY, BLACK, NAVY), "a stylus that clips to the side and a keyboard cover"),
    (NIMBREL, "Nimbrel Glide 11", "standard", "11", 329, (SILVER, GREEN, PINK), "a thin body, a fast screen and a kickstand cover"),
    (QUORRIN, "Quorrin Pad 8", "standard", "8", 149, (BLACK, BLUE, RED), "a compact screen for reading and video"),
    (DASKEL, "Daskel Kids Tab", "kids", "8", 119, (BLUE, PINK, GREEN, YELLOW), "a thick foam case, a parental control mode and a screen guard"),
    (MERVANE, "Mervane Tab 12", "pro", "12.4", 699, (GREY, SILVER, GREEN), "a large screen for drawing, with a stylus in the box"),
    (PELLIMAR, "Pellimar Lite 10", "standard", "10.4", 179, (GREY, SILVER, BLUE, GOLD), "a plain tablet for streaming and video calls"),
    (BOLTWICK, "Boltwick Ridge Tab", "standard", "8", 349, (BLACK, ORANGE, YELLOW), "a sealed rubber body with a screen that works with gloves on"),
)  # fmt: skip


def _tablet(i, brand, line, form, screen, price, colors, note) -> Row:
    tiers = (64, 128, 256) if form != "kids" else (32, 64)
    os_ = _OS.get(brand, "Open Mobile OS")
    return _row(
        f"ETB{i + 1:03d}", f"{line} Tablet", brand, (*_T, "Tablets"), "Tablet", price, "tablet",
        f"A {screen} inch tablet with {note}. It runs {os_}.", colors,
        (_a("model_line", "Model line", line), _a("operating_system", "Operating system", os_),
         _in("screen_size", "Screen size", screen)),
        tuple((str(g), price + 70.0 * k) for k, g in enumerate(tiers)), "storage_gb",
        (("form", form),),
    )  # fmt: skip


TABLETS = tuple(_tablet(i, *t) for i, t in enumerate(_TABLETS))

_READERS = (
    (NIMBREL, "Nimbrel Page", 99, (BLACK, WHITE, TEAL), "a glare-free screen that reads like paper and a battery that lasts for weeks"),
    (PELLIMAR, "Pellimar Leaf", 129, (BLACK, GREEN, NAVY), "a warm light for the evening and a waterproof body"),
    (TORVANE, "Torvane Ink 7", 149, (WHITE, GREY, PINK), "a seven inch screen with page buttons, for reading in the bath"),
    (MERVANE, "Mervane Folio", 179, (BLACK, SILVER), "a large screen that shows a full page of a magazine or a comic"),
)  # fmt: skip
E_READERS = tuple(
    _row(f"ERD{i + 1:03d}", f"{n} E-reader", b, (*_T, "E-readers"), "E-reader", p, "e_reader",
         f"An e-reader with {note}.", c,
         (_a("model_line", "Model line", n), _a("operating_system", "Operating system", "Basic OS")),
         (("8", p), ("32", p + 30.0)), "storage_gb")
    for i, (b, n, p, c, note) in enumerate(_READERS)
)  # fmt: skip

# --- Accessories ---------------------------------------------------------------------------
_CASES = (
    (CINDREL, "Clear Case", "clear", "iPhone 15", 14, (CLEAR, BLACK, PINK)),
    (BOLTWICK, "Rugged Case", "rugged", "iPhone 15", 24, (BLACK, ORANGE, GREEN)),
    (CINDREL, "Wallet Case", "wallet", "iPhone 15 Pro", 22, (BLACK, NAVY, RED)),
    (CINDREL, "Clear Case", "clear", "iPhone 15 Pro", 15, (CLEAR, BLACK, BLUE)),
    (WEXMOOR, "Wallet Case", "wallet", "iPhone 15 Plus", 23, (BLACK, GREEN, PINK)),
    (CINDREL, "Clear Case", "clear", "iPhone 14", 13, (CLEAR, BLACK, YELLOW)),
    (BOLTWICK, "Rugged Case", "rugged", "iPhone 13", 22, (BLACK, BLUE, RED)),
    (WEXMOOR, "Slim Case", "clear", "iPhone SE", 12, (CLEAR, WHITE, RED)),
    (CINDREL, "Clear Case", "clear", "Halvern Arc 5", 14, (CLEAR, BLACK)),
    (BOLTWICK, "Rugged Case", "rugged", "Halvern Arc 5 Pro", 25, (BLACK, ORANGE, GREEN)),
    (WEXMOOR, "Wallet Case", "wallet", "Torvane T9", 21, (BLACK, NAVY, TEAL)),
    (BOLTWICK, "Rugged Case", "rugged", "Nimbrel Sky 12", 26, (BLACK, YELLOW, BLUE)),
    (CINDREL, "Clear Case", "clear", "Quorrin Q Max", 14, (CLEAR, BLACK, PURPLE)),
    (WEXMOOR, "Wallet Case", "wallet", "Pellimar P11", 21, (BLACK, RED, GREEN, WHITE)),
)  # fmt: skip
_CASE_TEXT = {
    "clear": "A slim see-through case that shows the color of the phone and guards the back and edges.",
    "rugged": "A two-layer case with raised corners that absorbs a drop from head height.",
    "wallet": "A folding case with slots for three cards and a stand fold for watching video.",
}  # fmt: skip
PHONE_CASES = tuple(
    _row(f"ECS{i + 1:03d}", f"{n} for {fits}", b, (*_A, "Phone Cases"), "Phone Case", p,
         "phone_case", f"{_CASE_TEXT[st]} Made to fit the {fits} exactly, with cut-outs for the "
         "camera and every port.", c,
         (_a("compatible_with", "Compatible with", fits), _a("case_style", "Case style", st.title())),
         params=(("style", st),))
    for i, (b, n, st, fits, p, c) in enumerate(_CASES)
)  # fmt: skip

_PROTECTORS = (
    (CINDREL, "Tempered Glass Screen Protector", "clear", "iPhone 15", 9),
    (CINDREL, "Matte Screen Protector", "matte", "iPhone 15 Pro", 9),
    (WEXMOOR, "Privacy Screen Protector", "privacy", "iPhone 14", 12),
    (CINDREL, "Tempered Glass Screen Protector", "clear", "iPhone 13", 8),
    (CINDREL, "Tempered Glass Screen Protector", "clear", "Halvern Arc 5", 9),
    (WEXMOOR, "Matte Screen Protector", "matte", "Torvane T9", 9),
    (WEXMOOR, "Privacy Screen Protector", "privacy", "Nimbrel Sky 12", 13),
    (CINDREL, "Tempered Glass Screen Protector", "clear", "iPad Air", 14),
    (WEXMOOR, "Matte Screen Protector", "matte", "iPad", 12),
    (BOLTWICK, "Impact Screen Protector", "clear", "Boltwick Ridge R1", 10),
)  # fmt: skip
_PROT_TEXT = {
    "clear": "a clear tempered glass sheet that resists scratches and keeps touch sharp",
    "matte": "a matte film that cuts glare and fingerprints",
    "privacy": "a privacy film that goes dark when viewed from the side",
}  # fmt: skip
SCREEN_PROTECTORS = tuple(
    _row(f"ESP{i + 1:03d}", f"{n} for {fits}", b, (*_A, "Screen Protectors"), "Screen Protector",
         p, "screen_protector", f"A screen protector for the {fits}: {_PROT_TEXT[f]}. Two in a pack, "
         "with a tray that lines it up.", (CLEAR,),
         (_a("compatible_with", "Compatible with", fits), _a("finish", "Finish", f.title())),
         params=(("finish", f),))
    for i, (b, n, f, fits, p) in enumerate(_PROTECTORS)
)  # fmt: skip

_CHARGERS = (
    (BOLTWICK, "20W USB-C Wall Charger", "wall", "iPhone 15", 15, "20", (WHITE, BLACK)),
    (BOLTWICK, "30W Dual Port Wall Charger", "wall", "iPad Air", 24, "30", (WHITE, BLACK)),
    (WEXMOOR, "65W USB-C Wall Charger", "wall", "Halvern Arc 5", 34, "65", (BLACK, WHITE, GREY)),
    (WEXMOOR, "Fast Wireless Charger", "wireless", "iPhone 15", 22, "15", (WHITE, BLACK, PINK)),
    (WEXMOOR, "Wireless Charging Stand", "wireless", "iPhone 15 Pro", 29, "15", (BLACK, WHITE, NAVY)),
    (BOLTWICK, "Wireless Charging Pad", "wireless", "Torvane T9", 19, "10", (BLACK, GREY, GREEN)),
    (BOLTWICK, "10000 mAh Power Bank", "power_bank", "iPhone 15", 27, "22", (BLACK, BLUE, RED, WHITE)),
    (BOLTWICK, "20000 mAh Power Bank", "power_bank", "iPhone 14", 39, "30", (BLACK, ORANGE, GREEN)),
    (WEXMOOR, "5000 mAh Slim Power Bank", "power_bank", "Nimbrel Sky 12", 19, "15", (WHITE, PINK, BLUE)),
    (BOLTWICK, "Rugged 26800 mAh Power Bank", "power_bank", "Boltwick Ridge R1", 49, "45", (BLACK, YELLOW, ORANGE)),
    (BOLTWICK, "Dual Port Car Charger", "car", "iPhone 15", 14, "30", (BLACK, SILVER)),
    (WEXMOOR, "Fast Car Charger", "car", "Halvern Arc 5", 16, "36", (BLACK, GREY, RED)),
)  # fmt: skip
CHARGERS = tuple(
    _row(f"ECH{i + 1:03d}", f"{n} for {fits}", b, (*_A, "Chargers"), "Charger", p, "charger",
         f"A {k.replace('_', ' ')} charger that tops up the {fits} at up to {w} watts, with "
         "short-circuit and overheat protection.", c,
         (_a("compatible_with", "Compatible with", fits), _a("charger_type", "Charger type", k.replace("_", " ").title()),
          _a("power_output", "Power output (W)", w)), params=(("kind", k),))
    for i, (b, n, k, fits, p, w, c) in enumerate(_CHARGERS)
)  # fmt: skip

_CABLES = (
    (BOLTWICK, "Braided USB-C to USB-C Cable", "usb_c", 9, (BLACK, WHITE, RED)),
    (WEXMOOR, "Fast Charge USB-C Cable", "usb_c", 11, (WHITE, BLACK, BLUE)),
    (CINDREL, "Flat USB-C Cable", "usb_c", 8, (GREY, PINK, GREEN)),
    (BOLTWICK, "Rugged USB-C Cable", "usb_c", 14, (BLACK, ORANGE, YELLOW)),
    (WEXMOOR, "Micro USB Cable", "micro", 6, (BLACK, WHITE, BLUE)),
    (BOLTWICK, "Braided Micro USB Cable", "micro", 8, (BLACK, RED, GREEN)),
    (CINDREL, "Three-in-One Charging Cable", "multi", 12, (BLACK, WHITE, PINK)),
    (WEXMOOR, "Retractable Multi Cable", "multi", 13, (BLACK, SILVER, TEAL)),
    (BOLTWICK, "Coiled USB-C Cable", "usb_c", 12, (BLACK, GREY)),
    (CINDREL, "Right-Angle Micro USB Cable", "micro", 7, (BLACK, WHITE, PURPLE)),
)  # fmt: skip
_CONN = {"usb_c": "USB-C", "micro": "Micro USB", "multi": "USB-C, Micro USB and a spare tip"}
CABLES = tuple(
    _row(f"ECB{i + 1:03d}", n, b, (*_A, "Cables"), "Cable", p, "cable",
         f"A charging and data cable with {_CONN[e]} ends, in three lengths, with a reinforced neck "
         "that survives daily bending.", c,
         (_a("connector", "Connector", _CONN[e].split(",")[0]),),
         tuple((f"{m:g}", p + 2.0 * k) for k, m in enumerate((1, 2, 3))), "length_m", (("end", e),))
    for i, (b, n, e, p, c) in enumerate(_CABLES)
)  # fmt: skip

_EARBUDS = (
    (WEXMOOR, "Wexmoor Pulse Wireless Earbuds", "buds", 39, "Bluetooth", (WHITE, BLACK, BLUE), "a charging case and six hours of music per charge"),
    (WEXMOOR, "Wexmoor Pulse Pro Noise Cancelling Earbuds", "buds", 79, "Bluetooth", (BLACK, WHITE, GREEN), "active noise cancelling and a transparency mode"),
    (CINDREL, "Cindrel Sport Earbuds", "buds", 29, "Bluetooth", (BLACK, RED, YELLOW), "ear hooks that stay in during a run and a sweat-proof body"),
    (BOLTWICK, "Boltwick Rugged Earbuds", "buds", 45, "Bluetooth", (BLACK, ORANGE), "a sealed body and a case that holds three charges"),
    (ARDMOOR, "Ardmoor Wired Earbuds", "buds", 9, "Wired", (WHITE, BLACK, PINK), "a USB-C plug, an inline mic and a tangle-free cable"),
    (WEXMOOR, "Wexmoor Studio Over-Ear Headphones", "over_ear", 99, "Bluetooth", (BLACK, SILVER, NAVY), "soft ear cups and thirty hours of battery"),
    (ARDMOOR, "Ardmoor Gaming Headset", "over_ear", 59, "Wired", (BLACK, RED, GREEN), "a boom mic that flips up to mute and lit ear cups"),
    (MARRICK, "Marrick Quiet Noise Cancelling Headphones", "over_ear", 149, "Bluetooth", (BLACK, GREY, PURPLE), "adaptive noise cancelling and a folding frame"),
)  # fmt: skip
EARBUDS = tuple(
    _row(f"EEB{i + 1:03d}", n, b, (*_A, "Earbuds"), "Earbuds", p, "earbuds",
         f"{'Earbuds' if f == 'buds' else 'Headphones'} with {note}.", c,
         (_a("connection", "Connection", conn), _a("wearing_style", "Wearing style", "In-ear" if f == "buds" else "Over-ear")),
         params=(("form", f),))
    for i, (b, n, f, p, conn, c, note) in enumerate(_EARBUDS)
)  # fmt: skip

_SLEEVES = (
    (DUNVALE, "Neoprene Laptop Sleeve", 15, (BLACK, GREY, NAVY, RED), "soft neoprene that cushions the lid"),
    (DUNVALE, "Felt Laptop Sleeve", 19, (GREY, CHARCOAL, GREEN), "a thick felt shell with a magnetic flap"),
    (DUNVALE, "Waterproof Laptop Sleeve", 22, (BLACK, BLUE, ORANGE), "a zipped, water-repellent shell"),
    (CINDREL, "Slim Faux Leather Laptop Sleeve", 25, (BLACK, NAVY, CREAM := cw("Cream", "#efe6d0")), "a slim wipe-clean shell with a soft lining"),
    (BOLTWICK, "Padded Rugged Laptop Sleeve", 29, (BLACK, YELLOW), "thick foam padding and a drop-proof base"),
    (DUNVALE, "Sleeve with Accessory Pocket", 24, (GREY, BLACK, PURPLE, TEAL), "a front pocket for the charger and a mouse"),
)  # fmt: skip
LAPTOP_SLEEVES = tuple(
    _row(f"ELS{i + 1:03d}", n, b, (*_A, "Laptop Sleeves"), "Laptop Sleeve", p, "laptop_sleeve",
         f"A sleeve for a laptop, with {note}. It comes in three sizes.", c,
         (_a("material", "Material", "Neoprene" if "Neoprene" in n else "Felt" if "Felt" in n else "Fabric"),),
         tuple((s, p + 3.0 * k) for k, s in enumerate(("13", "14", "16"))), "screen_size_in")
    for i, (b, n, p, c, note) in enumerate(_SLEEVES)
)  # fmt: skip

_MICE = (
    (ARDMOOR, "Ardmoor Click Wireless Mouse", "wireless", 12, "Wireless", (BLACK, WHITE, BLUE, RED), "a quiet click and a battery that lasts a year"),
    (ARDMOOR, "Ardmoor Slim Wireless Mouse", "wireless", 16, "Wireless", (GREY, PINK, GREEN), "a thin body that fits a laptop sleeve"),
    (MARRICK, "Marrick Dual Mode Mouse", "wireless", 24, "Bluetooth", (BLACK, SILVER, NAVY), "a switch between three computers at one press"),
    (WEXMOOR, "Wexmoor Travel Mouse", "wireless", 10, "Wireless", (BLACK, WHITE, ORANGE, YELLOW), "a small body and a receiver that stores underneath"),
    (ARDMOOR, "Ardmoor Strike Gaming Mouse", "gaming", 39, "Wired", (BLACK, RED, GREEN), "a high precision sensor, eight buttons and lit panels"),
    (QUORRIN, "Quorrin Viper Wireless Gaming Mouse", "gaming", 59, "Wireless", (BLACK, BLUE, PURPLE), "a light shell and a low delay link"),
    (MARRICK, "Marrick Vertical Ergonomic Mouse", "ergonomic", 29, "Wireless", (BLACK, GREY, WHITE), "an upright grip that eases the wrist"),
    (ARDMOOR, "Ardmoor Trackball Ergonomic Mouse", "ergonomic", 35, "Wireless", (BLACK, SILVER, TEAL), "a thumb ball, so the hand stays still"),
)  # fmt: skip
MICE = tuple(
    _row(f"EMS{i + 1:03d}", n, b, (*_A, "Mice"), "Computer Mouse", p, "mouse",
         f"A computer mouse with {note}.", c,
         (_a("connection", "Connection", conn), _a("mouse_type", "Mouse type", f.title())),
         params=(("form", f),))
    for i, (b, n, f, p, conn, c, note) in enumerate(_MICE)
)  # fmt: skip

_KEYBOARDS = (
    (ARDMOOR, "Ardmoor Type Full-Size Keyboard", "full", 24, "Wireless", (BLACK, WHITE, GREY), "a number pad and keys with a short, quiet drop"),
    (ARDMOOR, "Ardmoor Mechanical Keyboard", "full", 69, "Wired", (BLACK, RED, BLUE), "mechanical switches and per-key lighting"),
    (MARRICK, "Marrick Office Full-Size Keyboard", "full", 32, "Bluetooth", (SILVER, BLACK, WHITE), "a slim metal plate and an adjustable stand"),
    (QUORRIN, "Quorrin Arena Gaming Keyboard", "full", 79, "Wired", (BLACK, GREEN, PURPLE), "fast switches and a wrist rest"),
    (WEXMOOR, "Wexmoor Compact Keyboard", "compact", 19, "Bluetooth", (WHITE, BLACK, PINK), "no number pad, so the mouse sits closer"),
    (ARDMOOR, "Ardmoor Compact Mechanical Keyboard", "compact", 59, "Wired", (BLACK, WHITE, ORANGE), "a seventy-five percent layout and hot-swap switches"),
    (MARRICK, "Marrick Slim Compact Keyboard", "compact", 27, "Wireless", (GREY, SILVER, TEAL), "low-profile keys that connect to three devices"),
    (DUNVALE, "Dunvale Folding Travel Keyboard", "compact", 35, "Bluetooth", (BLACK, NAVY), "a folding body that goes in a coat pocket"),
)  # fmt: skip
KEYBOARDS = tuple(
    _row(f"EKB{i + 1:03d}", n, b, (*_A, "Keyboards"), "Keyboard", p, "keyboard",
         f"A {'full-size' if f == 'full' else 'compact'} keyboard with {note}.", c,
         (_a("connection", "Connection", conn), _a("keyboard_layout", "Layout", f.title())),
         params=(("layout", f),))
    for i, (b, n, f, p, conn, c, note) in enumerate(_KEYBOARDS)
)  # fmt: skip

_MONITORS = (
    (MARRICK, "Marrick View Full HD Monitor", "standard", 119, ("24", "27"), (BLACK, WHITE), "a Full HD panel and a stand that tilts"),
    (MARRICK, "Marrick View 4K Monitor", "standard", 289, ("27", "32"), (BLACK, SILVER), "a 4K panel and a stand that rises and swivels"),
    (HALVERN, "Halvern Vision Monitor", "standard", 149, ("24", "27"), (BLACK, SILVER, WHITE), "slim edges and two HDMI inputs"),
    (TORVANE, "Torvane Pixel Gaming Monitor", "standard", 249, ("24", "27"), (BLACK, RED), "a fast refresh rate and a one millisecond response"),
    (MARRICK, "Marrick Wide Ultrawide Monitor", "ultrawide", 399, ("29", "34"), (BLACK, SILVER), "a wide panel that holds two documents side by side"),
    (QUORRIN, "Quorrin Panorama Ultrawide Monitor", "ultrawide", 449, ("34",), (BLACK, GREY), "a wide 34 inch panel with a speed that suits games"),
    (TORVANE, "Torvane Arc Curved Monitor", "curved", 279, ("27", "32"), (BLACK, BLUE), "a deep curve that wraps the view around you"),
    (DASKEL, "Daskel Studio Curved Monitor", "curved", 349, ("27", "32"), (BLACK, WHITE, GREY), "a curved panel with accurate color for editing"),
)  # fmt: skip
MONITORS = tuple(
    _row(f"EMN{i + 1:03d}", n, b, (*_A, "Monitors"), "Monitor", p, "monitor",
         f"A computer monitor with {note}.", c,
         (_a("panel_type", "Panel type", "Curved" if f == "curved" else "Flat"),),
         tuple((s, p + 60.0 * k) for k, s in enumerate(sz)), "screen_size_in", (("form", f),))
    for i, (b, n, f, p, sz, c, note) in enumerate(_MONITORS)
)  # fmt: skip

DEVICE_COUNT = len(SMARTPHONES + BASIC_PHONES + LAPTOPS + DESKTOPS + TABLETS + E_READERS)
ACCESSORY_COUNT = len(PHONE_CASES + SCREEN_PROTECTORS + CHARGERS + CABLES + EARBUDS
                      + LAPTOP_SLEEVES + MICE + KEYBOARDS + MONITORS)  # fmt: skip

# --- In-department text-match decoys (gen#294 classes 1-7); each tells the truth in its fields ----
DECOY_ROWS = {
    "keyboard": (
        (1, "blue keyboard", "color facet: Blue in a range name is not the keyboard color",
         _row("DCEKB1", "Blue Glow Keyboard", ARDMOOR, (*_A, "Keyboards"), "Keyboard", 21.0,
              "keyboard", "A white full-size keyboard with a soft glow behind its keys and a number pad.",
              (WHITE,), (_a("connection", "Connection", "Wired"), _a("keyboard_layout", "Layout", "Full")),
              params=(("layout", "full"),))),
    ),
    "phone_case": (
        (5, "red phone case", "color facet: a color named in the text is not the case color",
         _row("DCECS1", "Trim Edge Case for iPhone 14", CINDREL, (*_A, "Phone Cases"), "Phone Case", 13.0,
              "phone_case", "A black case for the iPhone 14 with a thin red trim around the camera ring.",
              (BLACK,), (_a("compatible_with", "Compatible with", "iPhone 14"), _a("case_style", "Case style", "Clear")),
              params=(("style", "clear"),))),
        (4, "iphone 15", "category facet: a bare model-line query returns the Smartphones first, then the cases",
         _row("DCECS2", "Pocket Wallet Case for iPhone 15", WEXMOOR, (*_A, "Phone Cases"), "Phone Case", 18.0,
              "phone_case", "A slim folding case for the iPhone 15 with a card slot, not a phone.",
              (BLACK, NAVY), (_a("compatible_with", "Compatible with", "iPhone 15"), _a("case_style", "Case style", "Wallet")),
              params=(("style", "wallet"),))),
    ),
    "charger": (
        (7, "apple charger", "brand facet: a brand named in the text is not the charger's brand",
         _row("DCECH1", "Compatible USB-C Wall Charger", BOLTWICK, (*_A, "Chargers"), "Charger", 12.0,
              "charger", "A 20 watt wall charger that works with the Apple iPhone and iPad, sold by Boltwick, not by Apple.",
              (WHITE,), (_a("compatible_with", "Compatible with", "iPhone 15"), _a("charger_type", "Charger type", "Wall"),
                         _a("power_output", "Power output (W)", "20")), params=(("kind", "wall"),))),
    ),
}  # fmt: skip
