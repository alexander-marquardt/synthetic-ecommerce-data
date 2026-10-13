"""Small appliance templates for the scaled retail catalog (gen#202): data only.

The catalog had no fans, heaters, kettles or toasters, so a search for a fan found nothing
and the fan-type, blade-size, power and noise filters could not be shown. Each type here is
a leaf with its own drawing (:mod:`kit_appliances`), its shopper attributes as structured
entries, and SKUs over the issue's axes: a desk fan's color and blade size, a ceiling fan's
finish and blade span, a heater's wattage, a kettle's color and capacity, a toaster's color
and slot count.

A measured axis (``blade_size_in``, ``blade_span_cm``, ``capacity_l``) is on the SKUs alone,
which the export states with its unit (``export.OPTIONS``); a fixed one is a product entry.
A wattage or a noise level is a plain number whose name carries its unit ("Wattage (W)"),
as an oven-safe temperature's does: prism spells no watt or decibel unit. A drawn count
that varies by SKU (a toaster's ``slots``, an oil-filled radiator's ``fin_count``) is a
drawing param the SKU carries, so each SKU's image draws its own count
(``export.drawing_spec``). These styles are templates only: :func:`scale.derivable` leaves
them out, as it does the shirts, so the seeded derivation is what it was.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction

import kit_appliances  # noqa: F401 -- registers desk_fan, pedestal_fan, tower_fan, ...
from breadth_rows import Row
from variants import cw

_HW = "Home"
_HC = ("Home", "Heating & Cooling")
_SA = ("Home", "Small Appliances")
_H, _L, _C = "Hearth & Table", "Lanternby", "Calderby & Lune"
_E, _W, _K = "Emberly Home", "Larchwood Living", "Cobble & Kiln"
YES, NO = "Yes", "No"


@dataclass(frozen=True)
class ARow(Row):
    """A row whose SKUs carry more than their color and size: ``extra`` maps a size to the
    other fields that SKU holds (a 2500 W radiator's 11 fins), ``per_color`` maps a color to
    them (a ceiling fan's Black is its Matte Black finish)."""

    extra: tuple[tuple[str, tuple[tuple[str, str], ...]], ...] = ()
    per_color: tuple[tuple[str, tuple[tuple[str, str], ...]], ...] = ()

    def skus(self) -> list[dict]:
        by_size = {s: dict(kv) for s, kv in self.extra}
        by_color = {c: dict(kv) for c, kv in self.per_color}
        out = super().skus()
        for sku in out:
            sku.update(by_color.get(sku.get("color", ""), {}))
            sku.update(by_size.get(sku.get(self.size_key, ""), {}))
        return out


def _a(key: str, name: str, v: str) -> tuple[str, str, str]:
    return (key, name, v)


def _yn(key: str, name: str, on: bool) -> tuple[str, str, str]:
    return (key, name, YES if on else NO)


def _count(key: str, name: str, n: int) -> tuple[str, str, str, str, float]:
    return (key, name, str(n), "C62", float(n))


def _inch(key: str, name: str, v: int) -> tuple[str, str, str, str, float]:
    return (key, name, str(v), "INH", float(Fraction(v) * Fraction(127, 5)))


def _cm(key: str, name: str, v: int) -> tuple[str, str, str, str, float]:
    return (key, name, str(v), "CMT", float(v * 10))


def _watts(v: int) -> tuple[str, str, str]:
    return ("wattage", "Wattage (W)", str(v))


def _noise(db: int) -> tuple[str, str, str]:
    return ("noise_level", "Noise level (dB)", str(db))


def _power(v: str) -> tuple[str, str, str]:
    """The power source, in the night lights' words: Plug-In, USB-Powered, Rechargeable or
    Battery-Powered (breadth_rows.TOYS)."""
    return ("power", "Power", v)


def _sizes(*pairs: tuple[object, float]) -> tuple[tuple[str, float], ...]:
    return tuple((f"{v:g}" if isinstance(v, float) else str(v), p) for v, p in pairs)


WHITE = cw("White", "#f4f1ea", "solid", "#8f989f")
BLACK = cw("Black", "#2f2f35", "solid", "#8f989f")
GREY = cw("Grey", "#9a9ca0", "solid", "#2f2f35")
SILVER = cw("Brushed Silver", "#cfd5da", "solid", "#2f2f35")
COPPER = cw("Copper", "#c27a4a", "solid", "#2f2f35")
CREAM = cw("Cream", "#efe8d8", "solid", "#2f2f35")
MINT = cw("Mint", "#a8d8c2", "solid", "#2f2f35")
RED = cw("Red", "#c8312e", "solid", "#2f2f35")
BLUE = cw("Blue", "#3f6fb5", "solid", "#2f2f35")
PINK = cw("Pink", "#f2a1b8", "solid", "#2f2f35")
YELLOW = cw("Yellow", "#f2d14b", "solid", "#2f2f35")
DUCK_EGG = cw("Duck Egg", "#b7d3cf", "solid", "#2f2f35")
MUSTARD = cw("Mustard", "#d1a03c", "solid", "#2f2f35")
NAVY = cw("Navy", "#26365c", "solid", "#8f989f")

# --------------------------------------------------------------------------
# Desk fans: color x blade size; the head draws its blade count.
# --------------------------------------------------------------------------

_DF = (*_HC, "Desk Fans")


def _df(power: str, speeds: int, osc: bool, db: int, blades: int, watts: int,
        remote: bool = False) -> tuple:
    return (_power(power), _count("speed_settings", "Speed settings", speeds),
            _yn("oscillating", "Oscillating", osc), _noise(db),
            _yn("remote_control", "Remote control", remote),
            _count("blade_count", "Blade count", blades), _watts(watts))  # fmt: skip


def _dfp(kind: str, blades: int) -> tuple[tuple[str, str], ...]:
    return (("kind", kind), ("blades", str(blades)))


DESK_FANS = (
    Row("DFNMET", "Metal Oscillating Desk Fan, 3 Speeds", _C, _HW, _DF, "Desk Fan", 35.0,
        "desk_fan", "A powder-coated steel fan with a chrome grille that sweeps side to side "
        "and tilts up to 30 degrees. Plugs into the mains on a 1.8 m cable.",
        (BLACK, WHITE, COPPER), _df("Plug-In", 3, True, 48, 3, 40),
        _sizes((12, 35.0), (16, 45.0)), params=_dfp("stand", 3), size_key="blade_size_in"),
    Row("DFNUSB", "Quiet USB Desk Fan", _L, _HW, _DF, "Desk Fan", 14.0, "desk_fan",
        "A small fan for a home office that runs from a laptop's USB port, at a whisper-quiet "
        "32 dB on its low setting. The head tilts on its stand.",
        (WHITE, PINK, BLUE), _df("USB-Powered", 2, False, 32, 5, 4),
        _sizes((6, 14.0), (8, 17.0)), params=_dfp("stand", 5), size_key="blade_size_in"),
    Row("DFNCLP", "Rechargeable Clip-On Desk Fan", _H, _HW, _DF, "Desk Fan", 22.0, "desk_fan",
        "A clip-on fan that grips a desk edge, a shelf or a buggy, with a built-in battery "
        "that runs up to 10 hours on its lowest of 4 speeds.",
        (WHITE, MINT), _df("Rechargeable", 4, False, 36, 4, 5),
        _sizes((6, 22.0), (8, 26.0)), params=_dfp("clip", 4), size_key="blade_size_in"),
    Row("DFNRET", "Retro Oscillating Desk Fan", _E, _HW, _DF, "Desk Fan", 39.0, "desk_fan",
        "A fan with a domed base and a brushed metal grille in a 1950s style, with 3 speeds "
        "and a wide side-to-side sweep.",
        (CREAM, MINT, MUSTARD), _df("Plug-In", 3, True, 45, 5, 35),
        _sizes((9, 39.0), (12, 45.0)), params=_dfp("stand", 5), size_key="blade_size_in"),
    Row("DFNDCQ", "Quiet DC Desk Fan with Remote", _W, _HW, _DF, "Desk Fan", 69.0, "desk_fan",
        "A low-energy DC motor fan with 12 speeds, a sleep setting and a remote, at 26 dB on "
        "its lowest speed. It turns side to side and tilts.",
        (WHITE, GREY), _df("Plug-In", 12, True, 26, 7, 20, True),
        _sizes((10, 69.0), (12, 79.0)), params=_dfp("stand", 7), size_key="blade_size_in"),
)  # fmt: skip

# --------------------------------------------------------------------------
# Pedestal fans: color only; the blade size and height range are product entries.
# --------------------------------------------------------------------------

_PF = (*_HC, "Pedestal Fans")


def _pf(size: int, lo: int, hi: int, remote: bool, timer: bool, speeds: int, watts: int,
        blades: int) -> tuple:
    return (_inch("blade_size", "Blade size", size), _cm("min_height", "Minimum height", lo),
            _cm("max_height", "Maximum height", hi),
            _yn("remote_control", "Remote control", remote),
            _yn("timer", "Timer", timer), _count("speed_settings", "Speed settings", speeds),
            _watts(watts), _yn("oscillating", "Oscillating", True),
            _count("blade_count", "Blade count", blades))  # fmt: skip


PEDESTAL_FANS = (
    Row("PFNREM", "16 Inch Pedestal Fan with Remote and Timer", _H, _HW, _PF, "Pedestal Fan",
        45.0, "pedestal_fan", "A stand fan that turns side to side, with 3 speeds, a 7.5 hour "
        "timer and a remote that stows in the control panel. Its height sets from 95 to 125 cm.",
        (WHITE, BLACK), _pf(16, 95, 125, True, True, 3, 45, 5),
        params=(("base", "round"), ("blades", "5"))),
    Row("PFNMET", "18 Inch Metal Pedestal Fan", _C, _HW, _PF, "Pedestal Fan", 65.0,
        "pedestal_fan", "A high-velocity fan with steel blades and a cross base, for a "
        "workshop, a gym or a large room. 3 speeds, from 105 to 135 cm tall.",
        (BLACK, SILVER), _pf(18, 105, 135, False, False, 3, 100, 3),
        params=(("base", "cross"), ("blades", "3"))),
    Row("PFNDCQ", "Quiet DC Pedestal Fan with Remote", _W, _HW, _PF, "Pedestal Fan", 95.0,
        "pedestal_fan", "A DC motor fan with 26 speeds and a breeze setting, quiet enough "
        "for a bedroom at 24 dB, with a 12 hour timer and a remote. From 80 to 115 cm tall.",
        (WHITE, GREY), _pf(14, 80, 115, True, True, 26, 24, 7),
        params=(("base", "round"), ("blades", "7"))),
    Row("PFNTMR", "16 Inch Stand Fan with Timer", _E, _HW, _PF, "Pedestal Fan", 39.0,
        "pedestal_fan", "A stand fan with 3 speeds and a 2 hour timer on its push-button "
        "panel. It turns side to side and sets from 90 to 120 cm tall.",
        (BLACK, CREAM), _pf(16, 90, 120, False, True, 3, 50, 5),
        params=(("base", "cross"), ("blades", "5"))),
)  # fmt: skip

# --------------------------------------------------------------------------
# Tower fans: color only; the column draws to its height, a bladeless fan as an open loop.
# --------------------------------------------------------------------------

_TF = (*_HC, "Tower Fans")


def _tf(height: int, remote: bool, timer: bool, modes: tuple[str, ...], bladeless: bool,
        speeds: int, watts: int) -> tuple:
    return (_cm("item_height", "Item height", height), _yn("oscillating", "Oscillating", True),
            _yn("remote_control", "Remote control", remote), _yn("timer", "Timer", timer),
            *(_a("mode", "Mode", m) for m in modes), _yn("bladeless", "Bladeless", bladeless),
            _count("speed_settings", "Speed settings", speeds), _watts(watts))  # fmt: skip


def _tfp(kind: str, height: int) -> tuple[tuple[str, str], ...]:
    return (("kind", kind), ("height", str(height)))


_ALL_MODES = ("Normal", "Sleep", "Natural")

TOWER_FANS = (
    Row("TWRREM", "Oscillating Tower Fan with Remote, 80 cm", _H, _HW, _TF, "Tower Fan", 39.0,
        "tower_fan", "A slim column fan with 3 speeds, Normal, Sleep and Natural modes, an "
        "8 hour timer and a remote. It turns side to side through 70 degrees.",
        (WHITE, BLACK), _tf(80, True, True, _ALL_MODES, False, 3, 45),
        params=_tfp("column", 80)),
    Row("TWRQUI", "Quiet Tower Fan, 107 cm", _L, _HW, _TF, "Tower Fan", 59.0, "tower_fan",
        "A tall tower fan with 12 speeds, a Sleep mode that dims its display, a 12 hour timer "
        "and a remote, at 32 dB on its lowest speed.",
        (GREY, WHITE), _tf(107, True, True, ("Normal", "Sleep"), False, 12, 40),
        params=_tfp("column", 107)),
    Row("TWRBLD", "Bladeless Tower Fan with Remote", _E, _HW, _TF, "Tower Fan", 99.0,
        "tower_fan", "A bladeless fan that draws air through its base and pushes it out of "
        "an open loop, with 10 speeds, Normal, Sleep and Natural modes and a remote.",
        (WHITE, SILVER), _tf(100, True, True, _ALL_MODES, True, 10, 40),
        params=_tfp("bladeless", 100)),
    Row("TWRMIN", "Desktop Tower Fan, 60 cm", _K, _HW, _TF, "Tower Fan", 25.0, "tower_fan",
        "A short tower fan for a desk or a bedside table, with 3 speeds on a simple dial, "
        "turning side to side.",
        (WHITE, PINK), _tf(60, False, False, ("Normal",), False, 3, 25),
        params=_tfp("column", 60)),
)  # fmt: skip

# --------------------------------------------------------------------------
# Ceiling fans: finish x blade span; the finish is the SKU's color in a fan's words.
# --------------------------------------------------------------------------

_CF = (*_HC, "Ceiling Fans")


def _cf(blades: int, light: bool, reversible: bool, remote: bool, cord: bool,
        speeds: int) -> tuple:
    return (_count("blade_count", "Blade count", blades), _yn("light_kit", "Light kit", light),
            _yn("reversible", "Reversible", reversible),
            _yn("remote_control", "Remote control", remote), _yn("pull_cord", "Pull cord", cord),
            _count("speed_settings", "Speed settings", speeds))  # fmt: skip


def _finish(*pairs: tuple[str, str]) -> tuple:
    return tuple((color, (("finish", finish),)) for color, finish in pairs)


def _cfp(blades: int, light: bool, wood: bool = False) -> tuple[tuple[str, str], ...]:
    return (("blades", str(blades)), ("light", "yes" if light else "no"),
            ("wood", "yes" if wood else "no"))  # fmt: skip


CEILING_FANS = (
    ARow("CFNLGT", "Ceiling Fan with Light and Remote", _H, _HW, _CF, "Ceiling Fan", 129.0,
         "ceiling_fan", "A 5 blade fan with an opal glass LED light, 3 speeds and a remote. "
         "It runs in reverse in winter to push warm air down.",
         (WHITE, SILVER), _cf(5, True, True, True, False, 3),
         _sizes((107, 129.0), (132, 149.0)), params=_cfp(5, True), size_key="blade_span_cm",
         per_color=_finish(("White", "Matte White"), ("Brushed Silver", "Brushed Nickel"))),
    ARow("CFNIND", "Industrial 3 Blade Ceiling Fan with Pull Cord", _C, _HW, _CF, "Ceiling Fan",
         159.0, "ceiling_fan", "A metal fan for a high ceiling, with 3 broad steel blades on a "
         "45 cm downrod and 3 speeds on a pull cord. It runs in reverse in winter.",
         (BLACK, COPPER), _cf(3, False, True, False, True, 3),
         _sizes((122, 159.0), (142, 189.0)), params=_cfp(3, False), size_key="blade_span_cm",
         per_color=_finish(("Black", "Matte Black"), ("Copper", "Brushed Copper"))),
    ARow("CFNLOW", "Low Profile Ceiling Fan with LED Light", _W, _HW, _CF, "Ceiling Fan", 119.0,
         "ceiling_fan", "A flush-mount fan for a low ceiling, with 4 blades, a dimmable LED "
         "light, a remote and a DC motor with 6 speeds.",
         (WHITE, BLACK), _cf(4, True, True, True, False, 6),
         _sizes((91, 119.0), (107, 135.0)), params=_cfp(4, True), size_key="blade_span_cm",
         per_color=_finish(("White", "Matte White"), ("Black", "Matte Black"))),
    ARow("CFNWOD", "Wooden Blade Ceiling Fan with Light", _E, _HW, _CF, "Ceiling Fan", 179.0,
         "ceiling_fan", "A traditional fan with 4 walnut-finish wooden blades, a frosted glass "
         "bowl light and a pull cord for its 3 speeds.",
         (cw("Brass", "#c8a14a", "solid", "#2f2f35"), cw("Walnut", "#5a3a26", "solid", "#2f2f35")),
         _cf(4, True, False, False, True, 3),
         _sizes((132, 179.0),), params=_cfp(4, True, True), size_key="blade_span_cm",
         per_color=_finish(("Gold", "Antique Brass"), ("Dark Brown", "Oil-Rubbed Bronze"))),
)  # fmt: skip

# --------------------------------------------------------------------------
# Handheld fans: color only; a neck fan draws as its band, with no blades.
# --------------------------------------------------------------------------

_HF = (*_HC, "Handheld Fans")


def _hf(power: str, foldable: bool, neck: bool, speeds: int, blades: int = 0) -> tuple:
    return (_power(power), _yn("foldable", "Foldable", foldable), _yn("neck_fan", "Neck fan", neck),
            _count("speed_settings", "Speed settings", speeds),
            *((_count("blade_count", "Blade count", blades),) if blades else ()))  # fmt: skip


HANDHELD_FANS = (
    Row("HFNREC", "Rechargeable Handheld Fan with Desk Stand", _L, _HW, _HF, "Handheld Fan", 12.0,
        "handheld_fan", "A pocket fan with 3 speeds and a battery that runs up to 8 hours, "
        "charged over USB-C. It stands on its base on a desk.",
        (PINK, WHITE, DUCK_EGG), _hf("Rechargeable", False, False, 3, 5),
        params=(("kind", "handheld"), ("blades", "5"))),
    Row("HFNFLD", "Foldable Rechargeable Handheld Fan", _H, _HW, _HF, "Handheld Fan", 15.0,
        "handheld_fan", "A fan whose head folds flat against its handle to fit a bag, with "
        "4 speeds and a battery that charges over USB-C.",
        (MINT, CREAM, NAVY), _hf("Rechargeable", True, False, 4, 4),
        params=(("kind", "handheld"), ("blades", "4"), ("fold", "yes"))),
    Row("HFNBAT", "Battery Mini Handheld Fan", _K, _HW, _HF, "Handheld Fan", 5.0,
        "handheld_fan", "A light fan with soft foam blades that are safe for small fingers, "
        "running on 2 AA batteries.",
        (YELLOW, BLUE, PINK), _hf("Battery-Powered", False, False, 1, 3),
        params=(("kind", "handheld"), ("blades", "3"))),
    Row("HFNNCK", "Bladeless Rechargeable Neck Fan", _E, _HW, _HF, "Handheld Fan", 25.0,
        "handheld_fan", "A hands-free fan worn round the neck, blowing air up through vents "
        "along both arms, with 3 speeds and up to 12 hours a charge.",
        (WHITE, BLACK, PINK), _hf("Rechargeable", False, True, 3),
        params=(("kind", "neck"),)),
)  # fmt: skip

# --------------------------------------------------------------------------
# Heaters: wattage; an oil-filled radiator's fin count follows its wattage on each SKU.
# --------------------------------------------------------------------------

_HT = (*_HC, "Heaters")


def _ht(kind: str, thermostat: bool, timer: bool, settings: int) -> tuple:
    return (_a("heater_type", "Heater type", kind), _yn("thermostat", "Thermostat", thermostat),
            _yn("timer", "Timer", timer),
            _count("heat_settings", "Heat settings", settings))  # fmt: skip


def _fins(*pairs: tuple[int, int]) -> tuple:
    return tuple((str(w), (("fin_count", str(n)),)) for w, n in pairs)


HEATERS = (
    Row("HTRFAN", "Fan Heater with Thermostat", _H, _HW, _HT, "Heater", 25.0, "heater",
        "A compact fan heater with 2 heat settings, a cool blow setting for summer and an "
        "adjustable thermostat. Cuts out if it tips over or overheats.",
        (WHITE,), _ht("Fan Heater", True, False, 2), _sizes((2000, 25.0), (3000, 32.0)),
        params=(("kind", "fan"),), size_key="wattage"),
    ARow("HTROIL", "Oil-Filled Radiator with Thermostat", _E, _HW, _HT, "Heater", 55.0, "heater",
         "A sealed oil-filled radiator that keeps a room warm long after it is switched off, "
         "with 3 heat settings and an adjustable thermostat, on castors. 7 fins at 1500 W, "
         "9 at 2000 W and 11 at 2500 W.",
         (WHITE,), _ht("Oil-Filled Radiator", True, False, 3),
         _sizes((1500, 55.0), (2000, 65.0), (2500, 75.0)), params=(("kind", "oil"),
                                                                   ("fin_count", "9")),
         size_key="wattage", extra=_fins((1500, 7), (2000, 9), (2500, 11))),
    ARow("HTROTM", "Oil-Filled Radiator with Thermostat and Timer", _C, _HW, _HT, "Heater", 79.0,
         "heater", "A slim oil-filled radiator with a 24 hour timer, a digital thermostat and "
         "3 heat settings, on castors. 9 fins at 2000 W and 11 at 2500 W.",
         (GREY,), _ht("Oil-Filled Radiator", True, True, 3), _sizes((2000, 79.0), (2500, 89.0)),
         params=(("kind", "oil"), ("fin_count", "11")), size_key="wattage",
         extra=_fins((2000, 9), (2500, 11))),
    Row("HTRCNV", "Convector Heater with Thermostat and Timer", _W, _HW, _HT, "Heater", 39.0,
        "heater", "A low convector heater that warms the air rising through it, with 3 heat "
        "settings, a 24 hour timer and an adjustable thermostat. Free standing or wall mounted.",
        (WHITE,), _ht("Convector", True, True, 3), _sizes((2000, 39.0), (2500, 45.0)),
        params=(("kind", "convector"),), size_key="wattage"),
    Row("HTRHAL", "Halogen Heater with 3 Tubes", _K, _HW, _HT, "Heater", 29.0, "heater",
        "A halogen heater that gives instant warmth from 3 glowing tubes, 400 W each, on 3 "
        "heat settings. Cuts out if it tips over.",
        (BLACK,), _ht("Halogen", False, False, 3), _sizes((1200, 29.0),),
        params=(("kind", "halogen"), ("tubes", "3")), size_key="wattage"),
    Row("HTRCER", "Ceramic Heater with Thermostat and Timer", _L, _HW, _HT, "Heater", 45.0,
        "heater", "A small ceramic heater that warms fast through its honeycomb grille, with "
        "2 heat settings, an 8 hour timer and an adjustable thermostat.",
        (GREY,), _ht("Ceramic", True, True, 2), _sizes((1500, 45.0), (2000, 52.0)),
        params=(("kind", "ceramic"),), size_key="wattage"),
)  # fmt: skip

# --------------------------------------------------------------------------
# Kettles: color x capacity; the kind sets the drawn form, a glass body shows its water.
# --------------------------------------------------------------------------

_KT = (*_SA, "Kettles")


def _kt(kind: str, material: str, finish: str, watts: int) -> tuple:
    return (_a("kettle_type", "Kettle type", kind), _a("material", "Material", material),
            _a("finish", "Finish", finish), _watts(watts))  # fmt: skip


def _ktp(kind: str, material: str) -> tuple[tuple[str, str], ...]:
    return (("kind", kind), ("material", material))


KETTLES = (
    Row("KTLJUG", "Rapid Boil Jug Kettle", _H, _HW, _KT, "Kettle", 25.0, "kettle",
        "A 3 kW jug kettle that boils a cup in under a minute, with a water window on each "
        "side and a limescale filter. In a gloss plastic body.",
        (WHITE, BLACK, RED), _kt("Standard", "Plastic", "Gloss", 3000),
        _sizes((1.5, 25.0), (1.7, 28.0)), params=_ktp("jug", "plastic"), size_key="capacity_l"),
    Row("KTLQUI", "Quiet Boil Stainless Steel Kettle", _C, _HW, _KT, "Kettle", 49.0, "kettle",
        "A quiet boil kettle in brushed stainless steel, with a soft-opening lid and a "
        "removable limescale filter.",
        (SILVER, COPPER), _kt("Quiet Boil", "Stainless Steel", "Brushed", 3000),
        _sizes((1.5, 49.0), (1.7, 55.0)), params=_ktp("jug", "steel"), size_key="capacity_l"),
    Row("KTLDOM", "Retro Dome Kettle", _E, _HW, _KT, "Kettle", 59.0, "kettle",
        "A round stainless steel kettle with an arched handle, a matte enamel finish and "
        "a chrome base, in a 1950s style.",
        (CREAM, MINT, RED, BLACK), _kt("Standard", "Stainless Steel", "Matte", 2200),
        _sizes((1.7, 59.0),), params=_ktp("dome", "steel"), size_key="capacity_l"),
    Row("KTLGLS", "Glass Kettle with LED Light", _L, _HW, _KT, "Kettle", 35.0, "kettle",
        "A clear borosilicate glass kettle whose LED lights the water as it boils, with a gloss "
        "trim "
        "on its handle and lid.",
        (BLACK, WHITE), _kt("Standard", "Glass", "Gloss", 3000),
        _sizes((1.7, 35.0),), params=_ktp("jug", "glass"), size_key="capacity_l"),
    Row("KTLTMP", "Temperature Control Gooseneck Kettle", _W, _HW, _KT, "Kettle", 89.0, "kettle",
        "A pour-over kettle with a slim gooseneck spout and a temperature control from 40 to "
        "100 degrees, held for an hour. In a matte stainless steel body.",
        (BLACK, WHITE), _kt("Temperature Control", "Stainless Steel", "Matte", 1200),
        _sizes((0.8, 89.0), (1.0, 99.0)), params=_ktp("gooseneck", "steel"),
        size_key="capacity_l"),
    Row("KTLTRV", "Travel Kettle, Dual Voltage", _K, _HW, _KT, "Kettle", 22.0, "kettle",
        "A small travel kettle that switches between 120 V and 230 V, with 2 cups that stow "
        "inside. In a gloss plastic body.",
        (WHITE, BLUE), _kt("Travel", "Plastic", "Gloss", 1000),
        _sizes((0.5, 22.0),), params=_ktp("travel", "plastic"), size_key="capacity_l"),
)  # fmt: skip

# --------------------------------------------------------------------------
# Toasters: color x slots; each SKU's image draws its own slots.
# --------------------------------------------------------------------------

_TS = (*_SA, "Toasters")


def _ts(long: bool, finish: str, browning: int, defrost: bool = True) -> tuple:
    return (_yn("long_slot", "Long slot", long), _a("finish", "Finish", finish),
            _count("browning_settings", "Browning settings", browning),
            _yn("defrost", "Defrost", defrost), _yn("reheat", "Reheat", True))  # fmt: skip


TOASTERS = (
    Row("TSTGLS", "Toaster with Defrost and Reheat", _H, _HW, _TS, "Toaster", 25.0, "toaster",
        "A 2 slice or 4 slice toaster in a gloss finish, with 6 browning settings, a cancel "
        "button and a pull-out crumb tray.",
        (WHITE, BLACK, RED), _ts(False, "Gloss", 6), _sizes((2, 25.0), (4, 35.0)),
        params=(("slots", "2"),), size_key="slots"),
    Row("TSTSTL", "Brushed Stainless Steel Toaster", _C, _HW, _TS, "Toaster", 45.0, "toaster",
        "A 2 slice or 4 slice toaster in a brushed finish, with wide slots for bagels, 7 "
        "browning settings and a high-lift lever.",
        (SILVER, COPPER), _ts(False, "Brushed", 7), _sizes((2, 45.0), (4, 59.0)),
        params=(("slots", "2"),), size_key="slots"),
    Row("TSTRET", "Retro Toaster", _E, _HW, _TS, "Toaster", 49.0, "toaster",
        "A 2 slice or 4 slice toaster in a matte finish and a 1950s style, with 6 browning "
        "settings and a chrome lever.",
        (CREAM, MINT, DUCK_EGG, RED), _ts(False, "Matte", 6), _sizes((2, 49.0), (4, 65.0)),
        params=(("slots", "2"),), size_key="slots"),
    Row("TSTLNG", "Long Slot Toaster", _W, _HW, _TS, "Toaster", 39.0, "toaster",
        "A toaster whose slots run its whole length, for sourdough and long loaves, in a "
        "matte finish with 7 browning settings. Each long slot takes one long slice or two "
        "small ones.",
        (BLACK, GREY), _ts(True, "Matte", 7), _sizes((2, 39.0), (4, 55.0)),
        params=(("slots", "2"), ("long", "yes")), size_key="slots"),
)  # fmt: skip

ROWS = (*DESK_FANS, *PEDESTAL_FANS, *TOWER_FANS, *CEILING_FANS, *HANDHELD_FANS, *HEATERS,
        *KETTLES, *TOASTERS)  # fmt: skip


def docs() -> list[dict]:
    """Every appliance row's catalog document, type by type."""
    return [r.doc() for r in ROWS]
