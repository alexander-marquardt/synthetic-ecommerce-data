"""The phone range (gen#1117): more invented handsets, and cases and screen protectors for every one.

Data only, beside ``electronics_rows`` (gen#332), whose rows stay as they were. The spec files
``smartphone``, ``phone_case``, ``screen_protector``, ``charger`` and ``cable`` add these lists to
theirs.

* A new smartphone is sold in storage tiers, colors and ``network_lock`` (Unlocked or
  Carrier-locked), the third SKU axis; its screen size is an attribute.
* Every smartphone, old or new, has a clear, a rugged and a wallet case and a clear, a matte and a
  privacy screen protector. A row is added only where none of that style exists yet.
* An accessory's ``compatible_with`` is the phone's ``model_line``, our own model id, so the two
  join exactly, and its title ends ``for <model line>``. The search demo is "case for <model
  line>": only the cases with that ``compatible_with`` are right, and the cases of the next model
  in the family ("Halvern Arc 6 Pro" beside "Halvern Arc 6") are the near misses.
* Each new phone has a charger of its own (wall, wireless or car, in turn); six more cables carry
  no model.
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.electronics_rows import (
    _A,
    _CONN,
    _FORM_TEXT,
    _OS,
    _P,
    _STORAGE,
    BLACK,
    BLUE,
    BOLTWICK,
    CINDREL,
    CLEAR,
    DASKEL,
    DEPARTMENT,
    GOLD,
    GREEN,
    GREY,
    HALVERN,
    MERVANE,
    NAVY,
    NIMBREL,
    ORANGE,
    PELLIMAR,
    PHONE_CASES,
    PINK,
    PURPLE,
    QUORRIN,
    RED,
    SCREEN_PROTECTORS,
    SILVER,
    SINGINGSAM,
    TEAL,
    TORVANE,
    WEXMOOR,
    WHITE,
    YELLOW,
    _a,
    _in,
    _row,
)
from synthetic_ecommerce_data.domains.retail.electronics_rows import SMARTPHONES as OLD_SMARTPHONES
from synthetic_ecommerce_data.domains.retail.lowerbody_rows import LRow

#: The ``network_lock`` SKU axis: ``(value, price factor)``; a carrier-locked phone costs less.
NETWORK_LOCK = (("Unlocked", 1.0), ("Carrier-locked", 0.9))

# --- New smartphones: brand, line, form, screen, connectivity, price, colors, what it is for ----
_PHONES = (
    (HALVERN, "Halvern Arc 6", "flagship", "6.4", "5G", 799, (BLACK, SILVER, TEAL, PINK), "a flat display and a camera that keeps up with children and pets"),
    (HALVERN, "Halvern Arc 6 Pro", "flagship", "6.8", "5G", 999, (BLACK, SILVER, NAVY), "a periscope zoom, a ceramic back and a charge that fills in twenty minutes"),
    (HALVERN, "Halvern Arc 4", "midrange", "6.3", "5G", 429, (BLACK, WHITE, GREEN), "a light body and a battery that lasts a long day"),
    (TORVANE, "Torvane T11", "flagship", "6.8", "5G", 949, (BLACK, WHITE, GOLD, BLUE), "a bright display and a lens set tuned for portraits at night"),
    (TORVANE, "Torvane T5", "midrange", "6.4", "5G", 329, (BLACK, BLUE, GREEN, PINK), "a sharp display and stereo speakers"),
    (TORVANE, "Torvane T2", "budget", "6.1", "4G", 129, (BLACK, GREY, RED), "a toughened screen and a battery for two days of calls"),
    (NIMBREL, "Nimbrel Sky 14", "flagship", "6.9", "5G", 1099, (BLACK, SILVER, PURPLE), "a stylus that docks inside and a display made for notes and sketches"),
    (NIMBREL, "Nimbrel Sky 6", "budget", "6.3", "4G", 159, (BLACK, WHITE, BLUE), "a big screen and a headphone socket"),
    (NIMBREL, "Nimbrel Sky Flip", "foldable", "6.7", "5G", 899, (BLACK, PINK, GREEN), "a clamshell that folds to fit a jacket pocket"),
    (QUORRIN, "Quorrin Q 60", "midrange", "6.6", "5G", 399, (BLACK, WHITE, ORANGE, TEAL), "a smooth display for games and a large battery"),
    (QUORRIN, "Quorrin Q 20", "budget", "6.4", "4G", 139, (BLACK, BLUE, YELLOW), "a large screen and a battery that charges over a cable or a pad"),
    (QUORRIN, "Quorrin Q Max 2", "flagship", "6.8", "5G", 1029, (BLACK, GOLD, GREEN), "a fast processor and a cooling chamber for long games"),
    (DASKEL, "Daskel D70", "flagship", "6.7", "5G", 699, (BLACK, SILVER, NAVY, RED), "a bright display and a camera with a true zoom"),
    (DASKEL, "Daskel D30", "budget", "6.4", "4G", 149, (BLACK, WHITE, TEAL), "calls, maps and messages on a screen that is easy to read"),
    (MERVANE, "Mervane M8", "midrange", "6.5", "5G", 379, (BLACK, WHITE, PURPLE, GREEN), "a camera that shoots steady video and a fast charge"),
    (MERVANE, "Mervane M4", "budget", "6.5", "4G", 119, (BLACK, BLUE, PINK), "a large battery and a fingerprint key on the side"),
    (PELLIMAR, "Pellimar P13", "flagship", "6.7", "5G", 949, (BLACK, WHITE, SILVER, BLUE), "a glass back and a camera that keeps skin tones natural in any light"),
    (PELLIMAR, "Pellimar P7", "midrange", "6.3", "5G", 449, (BLACK, WHITE, PINK), "a light body, a flat screen and a fast chip"),
    (PELLIMAR, "Pellimar P Fold", "foldable", "7.4", "5G", 1399, (BLACK, SILVER, GREEN), "a tablet-size screen that folds shut like a book"),
    (BOLTWICK, "Boltwick Ridge R2", "midrange", "6.5", "5G", 479, (BLACK, ORANGE, YELLOW), "a sealed body that survives drops, rain and dust"),
    (BOLTWICK, "Boltwick Ridge R3", "flagship", "6.6", "5G", 649, (BLACK, ORANGE, GREEN), "a rugged frame, a thermal camera and a battery for a week outdoors"),
    (SINGINGSAM, "SingingSam Aria 11", "flagship", "6.8", "5G", 999, (BLACK, SILVER, NAVY, PURPLE), "stereo speakers tuned for music and a bright curved display"),
    (SINGINGSAM, "SingingSam Aria 7", "midrange", "6.5", "5G", 499, (BLACK, WHITE, BLUE, PINK), "a loud speaker pair and a display for streaming"),
    (SINGINGSAM, "SingingSam Aria 3", "budget", "6.4", "4G", 169, (BLACK, WHITE, GREEN), "a big battery and a speaker loud enough for a kitchen"),
)  # fmt: skip


def _phone(n: int, brand, line, form, screen, conn, price, colors, note) -> LRow:
    tiers = _STORAGE[form]
    os_ = _OS.get(brand, "Open Mobile OS")
    return LRow(
        f"EPR{n:03d}", f"{line} Smartphone", brand, DEPARTMENT, (*_P, "Smartphones"), "Smartphone",
        price, "smartphone", f"A {_FORM_TEXT[form]} {conn} smartphone with {note}. It runs {os_}, "
        f"comes in {len(tiers)} storage sizes and is sold unlocked or locked to a carrier.", colors,
        (_a("model_line", "Model line", line), _a("operating_system", "Operating system", os_),
         _a("connectivity", "Connectivity", conn), _in("screen_size", "Screen size", screen)),
        tuple((str(g), price + 60.0 * i) for i, g in enumerate(tiers)), size_key="storage_gb",
        params=(("form", form),), axis_key="network_lock", axis=NETWORK_LOCK,
    )  # fmt: skip


SMARTPHONES = tuple(_phone(i + 1, *p) for i, p in enumerate(_PHONES))


def _attr(row, key: str) -> str:
    return next(v for k, _, v, *_ in row.attrs if k == key)


#: Every smartphone's model line, the gen#332 rows' first.
MODEL_LINES = tuple(_attr(r, "model_line") for r in (*OLD_SMARTPHONES, *SMARTPHONES))

# --- A clear, a rugged and a wallet case for every phone ----------------------------------------
_CASE = {
    "clear": (CINDREL, "Clear Case", 14, (CLEAR, BLACK, PINK, BLUE),
              "A slim see-through case that shows the color of the phone and guards the back and edges."),
    "rugged": (BOLTWICK, "Rugged Case", 24, (BLACK, ORANGE, GREEN, NAVY),
               "A two-layer case with raised corners that absorbs a drop from head height."),
    "wallet": (WEXMOOR, "Wallet Case", 22, (BLACK, NAVY, RED, GREY),
               "A folding case with slots for three cards and a stand fold for watching video."),
}  # fmt: skip
_HAVE_CASE = {(_attr(r, "compatible_with"), dict(r.params)["style"]) for r in PHONE_CASES}
PHONE_CASES_NEW = tuple(
    _row(f"ECR{i + 1:03d}", f"{name} for {line}", brand, (*_A, "Phone Cases"), "Phone Case", price,
         "phone_case", f"{text} Made to fit the {line} exactly, with cut-outs for the camera and "
         "every port.", colors,
         (_a("compatible_with", "Compatible with", line), _a("case_style", "Case style", style.title())),
         params=(("style", style),))
    for i, (line, style, (brand, name, price, colors, text)) in enumerate(
        (line, style, _CASE[style]) for line in MODEL_LINES for style in _CASE
        if (line, style) not in _HAVE_CASE)
)  # fmt: skip

# --- A clear, a matte and a privacy screen protector for every phone ----------------------------
_PROTECTOR = {
    "clear": (CINDREL, "Tempered Glass Screen Protector", 9,
              "a clear tempered glass sheet that resists scratches and keeps touch sharp"),
    "matte": (WEXMOOR, "Matte Screen Protector", 9, "a matte film that cuts glare and fingerprints"),
    "privacy": (WEXMOOR, "Privacy Screen Protector", 12, "a privacy film that goes dark when viewed from the side"),
}  # fmt: skip
_HAVE_PROTECTOR = {
    (_attr(r, "compatible_with"), dict(r.params)["finish"]) for r in SCREEN_PROTECTORS
}
SCREEN_PROTECTORS_NEW = tuple(
    _row(f"ESR{i + 1:03d}", f"{name} for {line}", brand, (*_A, "Screen Protectors"), "Screen Protector",
         price, "screen_protector", f"A screen protector for the {line}: {text}. Two in a pack, "
         "with a tray that lines it up.", (CLEAR,),
         (_a("compatible_with", "Compatible with", line), _a("finish", "Finish", finish.title())),
         params=(("finish", finish),))
    for i, (line, finish, (brand, name, price, text)) in enumerate(
        (line, finish, _PROTECTOR[finish]) for line in MODEL_LINES for finish in _PROTECTOR
        if (line, finish) not in _HAVE_PROTECTOR)
)  # fmt: skip

# --- A charger for every new phone: wall, wireless and car in turn ------------------------------
_CHARGER = (
    (BOLTWICK, "25W USB-C Wall Charger", "wall", 17, "25", (WHITE, BLACK)),
    (WEXMOOR, "Fast Wireless Charger", "wireless", 24, "15", (WHITE, BLACK, PINK)),
    (BOLTWICK, "Dual Port Car Charger", "car", 15, "30", (BLACK, SILVER)),
)  # fmt: skip
CHARGERS_NEW = tuple(
    _row(f"ECG{i + 1:03d}", f"{n} for {line}", b, (*_A, "Chargers"), "Charger", p, "charger",
         f"A {k} charger that tops up the {line} at up to {w} watts, with short-circuit and "
         "overheat protection.", c,
         (_a("compatible_with", "Compatible with", line), _a("charger_type", "Charger type", k.title()),
          _a("power_output", "Power output (W)", w)), params=(("kind", k),))
    for i, (line, (b, n, k, p, w, c)) in enumerate(
        (_attr(r, "model_line"), _CHARGER[j % len(_CHARGER)]) for j, r in enumerate(SMARTPHONES))
)  # fmt: skip

# --- Cables that fit any phone with the connector -------------------------------------------------
_CABLES = (
    (WEXMOOR, "Braided USB-C to USB-C Cable", "usb_c", 10, (GREY, NAVY, PINK)),
    (CINDREL, "Right-Angle USB-C Cable", "usb_c", 9, (BLACK, WHITE, TEAL)),
    (BOLTWICK, "Heavy Duty USB-C Cable", "usb_c", 15, (BLACK, ORANGE, GREEN)),
    (CINDREL, "Fast Charge USB-C to USB-A Cable", "usb_c", 8, (WHITE, BLACK, PURPLE)),
    (WEXMOOR, "Flat Micro USB Cable", "micro", 6, (BLACK, WHITE, RED)),
    (BOLTWICK, "Braided Multi Charging Cable", "multi", 14, (BLACK, SILVER, BLUE)),
)  # fmt: skip
CABLES_NEW = tuple(
    _row(f"ECL{i + 1:03d}", n, b, (*_A, "Cables"), "Cable", p, "cable",
         f"A charging and data cable with {_CONN[e]} ends, in three lengths, with a reinforced neck "
         "that survives daily bending.", c,
         (_a("connector", "Connector", _CONN[e].split(",")[0]),),
         tuple((f"{m:g}", p + 2.0 * k) for k, m in enumerate((1, 2, 3))), "length_m", (("end", e),))
    for i, (b, n, e, p, c) in enumerate(_CABLES)
)  # fmt: skip
