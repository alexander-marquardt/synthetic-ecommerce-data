"""Lighting (gen#197): floor, table, desk, ceiling and wall lights, and lampshades (data only).

The catalog had one table lamp and no other light, so a lamp search showed no fixture type,
finish or power source to narrow on. Each type here is a leaf of its own under
``Home/Lighting``, typed by its name, with at least three styles from at least three brands,
and draws with its own shape in :mod:`kit_lighting` (a table lamp through
:func:`kit_home.table_lamp`).

A style's SKUs are its colors times one second axis, stored under the row's ``size_key``:

==============  ======================  ===================
type            color (the fill)        second axis
==============  ======================  ===================
Floor Lamp      the shade               ``finish``
Table Lamp      the base                ``shade_color``
Desk Lamp       the whole lamp          none
Ceiling Light   the shade               ``finish``
Wall Light      the shade (one color)   ``finish``
Lampshade       the fabric and pattern  ``diameter_cm``
==============  ======================  ===================

The second axis changes the picture (a brass frame, a navy shade, a 40 cm drum), so a SKU's
own value of a drawing param is drawn (:func:`export.drawing_spec`).

Each drawing param that a style attribute names (``style``, ``fixture_type`` as ``kind``,
``arm``, ``shape`` as ``form``, ``power``) is that attribute's value lowercased, so a derived
style that changes the value redraws it (:func:`scale.derive`). ``usb_port``, ``dimmable`` and
``wireless_charging`` are only ever "Yes", so a derived style never flips one; a wall light's
``ip_rating`` and a shade's ``fitting`` are in :data:`scale.FROZEN_KEYS`.

A light's color temperature is a measured entry (gen#232): ``color_temperature`` holds the
kelvin count with unit code ``KEL``, so a facet ranges over it and no value holds a unit. One fact
has one key (gen#498): a tunable lamp holds the two ends of its range as two entries under that
same key (2700 and 6500), so a filter for 2700-3300K finds it by its warm end and one for
6000-6500K by its cool end, and no "Minimum color temperature" key exists. The bulbs that
state a temperature are the Light Bulb type (``type_specs/light_bulb.py``).
"""

from __future__ import annotations

import re

import kit_lighting  # noqa: F401 -- registers the lighting shapes
from breadth_rows import Row
from variants import Color, cw

_LIGHT = ("Home", "Lighting")
_LAMPS = (*_LIGHT, "Lamps")
_LIGHTS = (*_LIGHT, "Lights")
FLOOR = (*_LAMPS, "Floor Lamps")
TABLE = (*_LAMPS, "Table Lamps")
DESK = (*_LAMPS, "Desk Lamps")
CEILING = (*_LIGHTS, "Ceiling Lights")
WALL = (*_LIGHTS, "Wall Lights")
SHADES = (*_LIGHT, "Lampshades")

def _a(key: str, name: str, value: str) -> tuple[str, str, str]:
    return (key, name, value)


def _cm(key: str, name: str, cm: int) -> tuple[str, str, str, str, float]:
    """A length in centimetres (unit code CMT; the canonical value is in millimetres)."""
    return (key, name, str(cm), "CMT", cm * 10.0)


def _kelvin(key: str, name: str, kelvin: int) -> tuple[str, str, str, str, float]:
    """A light's color temperature in kelvin (unit code KEL; the canonical value is the count)."""
    return (key, name, str(kelvin), "KEL", float(kelvin))


def _temp(kelvin: int) -> tuple[str, str, str, str, float]:
    return _kelvin("color_temperature", "Color temperature", kelvin)


def _temp_range(low: int, high: int) -> tuple[tuple[str, str, str, str, float], ...]:
    """A tunable lamp's range: its two ends, two entries under the one color temperature key."""
    return (_temp(low), _temp(high))


def _lights(n: int) -> tuple[str, str, str, str]:
    """How many bulbs or heads a fitting holds: a count (C62), so a facet can range over it."""
    return ("light_count", "Number of lights", str(n), "C62")


def _yes(key: str, name: str) -> tuple[str, str, str]:
    return (key, name, "Yes")


def _p(**params: str) -> tuple[tuple[str, str], ...]:
    return tuple(params.items())


def _each(price: float, *values: str) -> tuple[tuple[str, float], ...]:
    """One price for every value of the second axis."""
    return tuple((v, price) for v in values)


WHITE, BLACK, CREAM = cw("White", "#f6f3ea"), cw("Black", "#2f2f33"), cw("Cream", "#efe6cf")
NATURAL, GREY, NAVY = cw("Natural", "#e3d6bb"), cw("Grey", "#a3a7ab"), cw("Navy", "#26365c")
FOREST, SAGE, MUSTARD = cw("Forest", "#3f5f45"), cw("Sage", "#9bb08f"), cw("Mustard", "#d4a32a")
BLUSH, TEAL, CLEAR = cw("Blush", "#e8b9b3"), cw("Teal", "#1c7c7d"), cw("Clear", "#dfe8ea")
SMOKE, BRASS, COPPER = cw("Smoke", "#8f9296"), cw("Brass", "#c9a227"), cw("Copper", "#c06a3c")
SILVER, AMBER = cw("Silver", "#c3c7cc"), cw("Amber", "#e39b3b")


def _stripe(name: str, accent: str) -> Color:
    return cw(name, "#f6f3ea", "stripe", accent)


def _gingham(name: str, accent: str) -> Color:
    return cw(name, "#f6f3ea", "gingham", accent)


# --------------------------------------------------------------------------
# Floor lamps: shade color x frame finish
# --------------------------------------------------------------------------

FLOOR_LAMPS = (
    Row("LTFARC", "Arc Floor Lamp with Dome Shade", "Brackenmere Home", "Home", FLOOR,
        "Floor Lamp", 139.0, "floor_lamp",
        "An arc floor lamp with a metal shade. It takes an E27 bulb and a foot switch turns "
        "it on.",
        (BLACK, WHITE, FOREST),
        (_a("style", "Style", "Arc"), _cm("item_height", "Item height", 190),
         _a("shade_material", "Shade material", "Metal"), _a("switch", "Switch", "Foot"),
         _a("bulb_fitting", "Bulb fitting", "E27")),
        (("Brass", 149.0), ("Chrome", 149.0), ("Matte Black", 139.0)),
        params=_p(style="arc", finish="brass"), size_key="finish"),
    Row("LTFTRI", "Tripod Floor Lamp with Linen Drum Shade", "Lanternby", "Home", FLOOR,
        "Floor Lamp", 99.0, "floor_lamp",
        "A tripod floor lamp with a linen drum shade and an inline switch on the cable.",
        (NATURAL, WHITE, GREY),
        (_a("style", "Style", "Tripod"), _cm("item_height", "Item height", 155),
         _a("shade_material", "Shade material", "Linen"), _a("switch", "Switch", "Inline"),
         _a("bulb_fitting", "Bulb fitting", "E27")),
        _each(99.0, "Oak", "Walnut", "Matte Black"),
        params=_p(style="tripod", finish="oak"), size_key="finish"),
    Row("LTFUPL", "Dimmable Uplighter Floor Lamp", "Calderby & Lune", "Home", FLOOR,
        "Floor Lamp", 89.0, "floor_lamp",
        "An uplighter with a glass bowl shade. It takes an integrated LED bulb and is "
        "dimmable, with a dimmer switch on the cable.",
        (WHITE, CREAM),
        (_a("style", "Style", "Uplighter"), _cm("item_height", "Item height", 180),
         _a("shade_material", "Shade material", "Glass"), _a("switch", "Switch", "Dimmer"),
         _a("bulb_fitting", "Bulb fitting", "Integrated LED"),
         _yes("dimmable", "Dimmable")),
        _each(89.0, "Satin Nickel", "Antique Brass"),
        params=_p(style="uplighter", finish="satin nickel"), size_key="finish"),
    Row("LTFTSK", "Task Floor Lamp for Reading", "Harbour & Pine", "Home", FLOOR,
        "Floor Lamp", 69.0, "floor_lamp",
        "A task floor lamp with a metal shade. An inline switch sits on the cable; it takes "
        "an E14 bulb.",
        (BLACK, WHITE, MUSTARD),
        (_a("style", "Style", "Task"), _cm("item_height", "Item height", 140),
         _a("shade_material", "Shade material", "Metal"), _a("switch", "Switch", "Inline"),
         _a("bulb_fitting", "Bulb fitting", "E14")),
        _each(69.0, "Chrome", "Matte Black"),
        params=_p(style="task", finish="chrome"), size_key="finish"),
    Row("LTFMAC", "Mother-and-Child Floor Lamp", "Brackenmere Home", "Home", FLOOR,
        "Floor Lamp", 119.0, "floor_lamp",
        "A mother-and-child floor lamp with glass shades and a foot switch.",
        (WHITE, BLACK),
        (_a("style", "Style", "Mother-and-Child"), _cm("item_height", "Item height", 178),
         _a("shade_material", "Shade material", "Glass"), _a("switch", "Switch", "Foot"),
         _a("bulb_fitting", "Bulb fitting", "E27")),
        (("Brass", 129.0), ("Copper", 129.0), ("Satin Nickel", 119.0)),
        params=_p(style="mother-and-child", finish="brass"), size_key="finish"),
)

# --------------------------------------------------------------------------
# Table lamps: base color x shade color
# --------------------------------------------------------------------------

TABLE_LAMPS = (
    Row("LTTBED", "Bedside Table Lamp with Drum Shade", "Lanternby", "Home", TABLE,
        "Table Lamp", 39.0, "table_lamp",
        "A bedside table lamp on a metal base, with a drum shade that softens the bulb. It is "
        "plug-in.",
        (BRASS, BLACK, WHITE),
        (_a("style", "Style", "Bedside"), _cm("item_height", "Item height", 40),
         _a("base_material", "Base material", "Metal"), _a("power", "Power", "Plug-In")),
        _each(39.0, "White", "Natural", "Navy"),
        params=_p(style="bedside", shade_color="white", power="plug-in"),
        size_key="shade_color"),
    Row("LTTCER", "Ceramic Table Lamp with Linen Shade", "Brackenmere Home", "Home", TABLE,
        "Table Lamp", 65.0, "table_lamp",
        "A table lamp with a linen drum shade. It is plug-in.",
        (SAGE, TEAL, CREAM),
        (_a("style", "Style", "Ceramic"), _cm("item_height", "Item height", 56),
         _a("base_material", "Base material", "Ceramic"), _a("power", "Power", "Plug-In")),
        _each(65.0, "White", "Natural"),
        params=_p(style="ceramic", shade_color="white", power="plug-in"),
        size_key="shade_color"),
    Row("LTTTCH", "Touch Table Lamp with USB Port", "Calderby & Lune", "Home", TABLE,
        "Table Lamp", 45.0, "table_lamp",
        "A touch table lamp that dims. A USB port in the base charges a phone overnight.",
        (COPPER, BRASS, SILVER),
        (_a("style", "Style", "Touch"), _cm("item_height", "Item height", 38),
         _a("base_material", "Base material", "Metal"), _a("power", "Power", "Plug-In"),
         _yes("dimmable", "Dimmable"), ("usb_port", "USB port", "yes")),
        _each(45.0, "White", "Grey", "Black"),
        params=_p(style="touch", shade_color="white", power="plug-in"),
        size_key="shade_color"),
    Row("LTTMSH", "Rechargeable Mushroom Table Lamp", "Harbour & Pine", "Home", TABLE,
        "Table Lamp", 49.0, "table_lamp",
        "A mushroom table lamp with a glass base. It is rechargeable. Dimmable.",
        (BLUSH, SAGE, AMBER, WHITE),
        (_a("style", "Style", "Mushroom"), _cm("item_height", "Item height", 30),
         _a("base_material", "Base material", "Glass"), _a("power", "Power", "Rechargeable"),
         _yes("dimmable", "Dimmable")),
        _each(49.0, "White", "Cream"),
        params=_p(style="mushroom", shade_color="white", power="rechargeable"),
        size_key="shade_color"),
)

# --------------------------------------------------------------------------
# Desk lamps: color only
# --------------------------------------------------------------------------

DESK_LAMPS = (
    Row("LTDADJ", "Adjustable LED Desk Lamp with USB Port", "Brackenmere Home", "Home", DESK,
        "Desk Lamp", 39.0, "desk_lamp",
        "An adjustable desk lamp with a 2700-6500K LED light and a USB port that charges a "
        "phone.",
        (BLACK, WHITE, SAGE),
        (_a("arm", "Arm", "Adjustable"), *_temp_range(2700, 6500),
         _yes("dimmable", "Dimmable"), ("usb_port", "USB port", "yes")),
        params=_p(arm="adjustable", base="round")),
    Row("LTDGNK", "Gooseneck LED Desk Lamp", "Lanternby", "Home", DESK,
        "Desk Lamp", 25.0, "desk_lamp",
        "A gooseneck desk lamp with a 3000K LED light.",
        (BLACK, SILVER, NAVY),
        (_a("arm", "Arm", "Gooseneck"), _temp(3000)),
        params=_p(arm="gooseneck", base="round")),
    Row("LTDCLP", "Clamp-On LED Desk Lamp", "Calderby & Lune", "Home", DESK,
        "Desk Lamp", 29.0, "desk_lamp",
        "A clamp-on desk lamp with a 5000K LED light.",
        (WHITE, BLACK, MUSTARD),
        (_a("arm", "Arm", "Clamp-On"), _temp(5000),
         _yes("dimmable", "Dimmable")),
        params=_p(arm="clamp-on", base="round")),
    Row("LTDWCP", "LED Desk Lamp with Wireless Charging Pad", "Harbour & Pine", "Home", DESK,
        "Desk Lamp", 49.0, "desk_lamp",
        "A desk lamp whose wide base is a wireless charging pad for a phone, with a USB port "
        "beside it and a 2700-6500K LED light.",
        (BLACK, WHITE),
        (_a("arm", "Arm", "Adjustable"), *_temp_range(2700, 6500),
         _yes("dimmable", "Dimmable"), ("usb_port", "USB port", "yes"),
         _yes("wireless_charging", "Wireless charging")),
        params=_p(arm="adjustable", base="pad")),
)

# --------------------------------------------------------------------------
# Ceiling lights: shade color x finish
# --------------------------------------------------------------------------

CEILING_LIGHTS = (
    Row("LTCPND", "Glass Dome Pendant Light", "Brackenmere Home", "Home", CEILING,
        "Ceiling Light", 59.0, "ceiling_light",
        "A pendant, 1 light, with a glass shade. Takes an E27 bulb.",
        (CLEAR, SMOKE, FOREST),
        (_a("fixture_type", "Fixture type", "Pendant"), _lights(1), _cm("diameter", "Diameter", 30),
         _cm("drop_length", "Drop length", 120), _a("shade_material", "Shade material", "Glass"),
         _a("bulb_fitting", "Bulb fitting", "E27")),
        _each(59.0, "Brass", "Matte Black"),
        params=_p(kind="pendant", lights="1", finish="brass"), size_key="finish"),
    Row("LTCPN3", "3 Light Cluster Pendant", "Lanternby", "Home", CEILING,
        "Ceiling Light", 99.0, "ceiling_light",
        "A pendant, 3 light, with metal shades. Takes an E27 bulb in each.",
        (BLACK, WHITE, MUSTARD),
        (_a("fixture_type", "Fixture type", "Pendant"), _lights(3), _cm("diameter", "Diameter", 45),
         _cm("drop_length", "Drop length", 100), _a("shade_material", "Shade material", "Metal"),
         _a("bulb_fitting", "Bulb fitting", "E27")),
        _each(99.0, "Brass", "Copper", "Chrome"),
        params=_p(kind="pendant", lights="3", finish="brass"), size_key="finish"),
    Row("LTCFLS", "Flush Ceiling Light", "Lanternby", "Home", CEILING,
        "Ceiling Light", 45.0, "ceiling_light",
        "A flush ceiling light, 2 light, with a glass diffuser. Takes an E27 bulb in each.",
        (WHITE, CREAM),
        (_a("fixture_type", "Fixture type", "Flush"), _lights(2), _cm("diameter", "Diameter", 35),
         _a("shade_material", "Shade material", "Glass"),
         _a("bulb_fitting", "Bulb fitting", "E27")),
        _each(45.0, "Chrome", "Satin Nickel", "Brass"),
        params=_p(kind="flush", lights="2", finish="chrome"), size_key="finish"),
    Row("LTCSMF", "Semi-Flush Ceiling Light, 3 Light", "Calderby & Lune", "Home", CEILING,
        "Ceiling Light", 79.0, "ceiling_light",
        "A semi-flush ceiling light, 3 light, with a linen bowl shade. Takes an E14 bulb in "
        "each.",
        (WHITE, GREY, NATURAL),
        (_a("fixture_type", "Fixture type", "Semi-Flush"), _lights(3),
         _cm("diameter", "Diameter", 45), _a("shade_material", "Shade material", "Linen"),
         _a("bulb_fitting", "Bulb fitting", "E14")),
        _each(79.0, "Antique Brass", "Matte Black"),
        params=_p(kind="semi-flush", lights="3", finish="antique brass"), size_key="finish"),
    Row("LTCCHD", "5 Light Chandelier with Fabric Shades", "Harbour & Pine", "Home", CEILING,
        "Ceiling Light", 189.0, "ceiling_light",
        "A chandelier, 5 light, with fabric shades. Takes an E14 bulb in each.",
        (WHITE, BLACK),
        (_a("fixture_type", "Fixture type", "Chandelier"), _lights(5),
         _cm("diameter", "Diameter", 60), _a("shade_material", "Shade material", "Fabric"),
         _a("bulb_fitting", "Bulb fitting", "E14")),
        (("Antique Brass", 199.0), ("Chrome", 189.0), ("Matte Black", 189.0)),
        params=_p(kind="chandelier", lights="5", finish="antique brass"), size_key="finish"),
    Row("LTCSPT", "4 Light Spotlight Bar", "Brackenmere Home", "Home", CEILING,
        "Ceiling Light", 55.0, "ceiling_light",
        "A spotlight bar, 4 light, with metal heads. Takes a GU10 bulb in each.",
        (WHITE, BLACK),
        (_a("fixture_type", "Fixture type", "Spotlight Bar"), _lights(4),
         _a("shade_material", "Shade material", "Metal"),
         _a("bulb_fitting", "Bulb fitting", "GU10")),
        _each(55.0, "Chrome", "Matte Black", "Brass"),
        params=_p(kind="spotlight bar", lights="4", finish="chrome"), size_key="finish"),
)

# --------------------------------------------------------------------------
# Wall lights: one shade color x finish
# --------------------------------------------------------------------------

WALL_LIGHTS = (
    Row("LTWSCN", "Bathroom Wall Light, IP44", "Brackenmere Home", "Home", WALL,
        "Wall Light", 49.0, "wall_light",
        "A sconce with an opal glass shade, rated IP44 for a bathroom wall near a basin. It "
        "is hardwired.",
        (WHITE,),
        (_a("fixture_type", "Fixture type", "Sconce"), _a("power", "Power", "Hardwired"),
         _a("switch", "Switch", "Wall Switch"), _a("ip_rating", "IP rating", "IP44")),
        _each(49.0, "Chrome", "Satin Nickel", "Brass"),
        params=_p(kind="sconce", power="hardwired", finish="chrome"), size_key="finish"),
    Row("LTWSWG", "Plug-In Swing Arm Wall Light", "Lanternby", "Home", WALL,
        "Wall Light", 59.0, "wall_light",
        "A swing arm wall light. It is plug-in.",
        (BLACK,),
        (_a("fixture_type", "Fixture type", "Swing Arm"), _a("power", "Power", "Plug-In"),
         _a("switch", "Switch", "Inline"), _a("ip_rating", "IP rating", "IP20")),
        _each(59.0, "Matte Black", "Brass", "Antique Brass"),
        params=_p(kind="swing arm", power="plug-in", finish="matte black"), size_key="finish"),
    Row("LTWPIC", "LED Picture Light", "Calderby & Lune", "Home", WALL,
        "Wall Light", 69.0, "wall_light",
        "A picture light with a warm LED lamp. It is hardwired.",
        (BRASS,),
        (_a("fixture_type", "Fixture type", "Picture Light"), _a("power", "Power", "Hardwired"),
         _a("switch", "Switch", "Wall Switch"), _a("ip_rating", "IP rating", "IP20")),
        _each(69.0, "Antique Brass", "Brass"),
        params=_p(kind="picture light", power="hardwired", finish="antique brass"),
        size_key="finish"),
    Row("LTWRCH", "Rechargeable Wall Light with Touch Dimmer", "Harbour & Pine", "Home", WALL,
        "Wall Light", 39.0, "wall_light",
        "A sconce. It is rechargeable.",
        (WHITE,),
        (_a("fixture_type", "Fixture type", "Sconce"), _a("power", "Power", "Rechargeable"),
         _a("switch", "Switch", "Touch"), _a("ip_rating", "IP rating", "IP20")),
        _each(39.0, "Matte Black", "Brass", "Matte White"),
        params=_p(kind="sconce", power="rechargeable", finish="matte black"), size_key="finish"),
)

# --------------------------------------------------------------------------
# Lampshades: color or pattern x diameter
# --------------------------------------------------------------------------

LAMPSHADES = (
    Row("LTSDRM", "Linen Drum Lampshade", "Brackenmere Home", "Home", SHADES,
        "Lampshade", 22.0, "lampshade",
        "A straight-sided drum shade in natural linen. A reversible ring fits it to a ceiling "
        "or lamp.",
        (NATURAL, WHITE, GREY, NAVY),
        (_a("shape", "Shape", "Drum"), _a("fitting", "Fitting", "Ceiling or Lamp"),
         _a("fabric", "Fabric", "Linen"), _a("pattern", "Pattern", "Plain")),
        (("30", 22.0), ("40", 28.0), ("50", 35.0)),
        params=_p(form="drum", diameter_cm="30"), size_key="diameter_cm"),
    Row("LTSEMP", "Striped Empire Lampshade", "Lanternby", "Home", SHADES,
        "Lampshade", 18.0, "lampshade",
        "A classic empire shade, narrow at the top and flared at the hem, in a ticking stripe "
        "cotton. For a table or floor lamp.",
        (_stripe("Blue Stripe", "#3a5f8f"), _stripe("Green Stripe", "#4f7a55"),
         _stripe("Red Stripe", "#b0413e")),
        (_a("shape", "Shape", "Empire"), _a("fitting", "Fitting", "Lamp"),
         _a("fabric", "Fabric", "Cotton"), _a("pattern", "Pattern", "Stripe")),
        (("25", 18.0), ("30", 22.0), ("35", 26.0)),
        params=_p(form="empire", diameter_cm="25"), size_key="diameter_cm"),
    Row("LTSTAP", "Tapered Velvet Lampshade", "Calderby & Lune", "Home", SHADES,
        "Lampshade", 29.0, "lampshade",
        "A tapered shade in soft velvet with a plain lining that warms the light. Fits a "
        "ceiling or lamp.",
        (BLUSH, FOREST, MUSTARD),
        (_a("shape", "Shape", "Tapered"), _a("fitting", "Fitting", "Ceiling or Lamp"),
         _a("fabric", "Fabric", "Velvet"), _a("pattern", "Pattern", "Plain")),
        (("30", 29.0), ("40", 36.0)),
        params=_p(form="tapered", diameter_cm="30"), size_key="diameter_cm"),
    Row("LTSSCL", "Scalloped Gingham Lampshade", "Harbour & Pine", "Home", SHADES,
        "Lampshade", 24.0, "lampshade",
        "A scalloped shade in a cotton gingham check, with a wavy hem. For a table lamp.",
        (_gingham("Red Gingham", "#b0413e"), _gingham("Blue Gingham", "#3a5f8f"),
         _gingham("Green Gingham", "#4f7a55")),
        (_a("shape", "Shape", "Scalloped"), _a("fitting", "Fitting", "Lamp"),
         _a("fabric", "Fabric", "Cotton"), _a("pattern", "Pattern", "Gingham")),
        (("20", 24.0), ("25", 28.0), ("30", 32.0)),
        params=_p(form="scalloped", diameter_cm="25"), size_key="diameter_cm"),
    Row("LTSPLT", "Pleated Silk Dupion Lampshade", "Brackenmere Home", "Home", SHADES,
        "Lampshade", 32.0, "lampshade",
        "A pleated shade in silk dupion, gathered at the top. Made for a ceiling pendant.",
        (CREAM, BLUSH, TEAL),
        (_a("shape", "Shape", "Pleated"), _a("fitting", "Fitting", "Ceiling"),
         _a("fabric", "Fabric", "Silk Dupion"), _a("pattern", "Pattern", "Plain")),
        (("30", 32.0), ("40", 39.0)),
        params=_p(form="pleated", diameter_cm="30"), size_key="diameter_cm"),
)

#: Every lighting row, by type, in build order.
ROWS = (*FLOOR_LAMPS, *TABLE_LAMPS, *DESK_LAMPS, *CEILING_LIGHTS, *WALL_LIGHTS, *LAMPSHADES)


def docs() -> list[dict]:
    """Every lighting row's catalog document."""
    return [r.doc() for r in ROWS]


#: The forms that hang, and the only ones with a ``drop_length`` (gen#237).
HANGING_FORMS = frozenset({"Pendant", "Chandelier"})

#: Title words that belong to the pendant template's own form (a dome shade, a cluster of lights).
_PENDANT_QUALIFIERS = re.compile(r"\s+(?:Dome|Cluster)\b")


def fit_ceiling_form(rec: dict) -> None:
    """Make a derived ceiling light's attributes and title fit the form it ended up with.

    :func:`scale.derive` copies a template's attributes and swaps only the values that changed,
    so a pendant derived to a flush fitting kept its ``drop_length`` and its "Dome" beside the
    new form word. A form that does not hang loses ``drop_length``; a form other than a pendant
    loses the pendant's qualifier words.
    """
    if rec["product_type"] != "Ceiling Light":
        return
    form = next((a["value"] for a in rec["attributes"] if a["key"] == "fixture_type"), None)
    if form not in HANGING_FORMS:
        rec["attributes"] = [a for a in rec["attributes"] if a["key"] != "drop_length"]
    if form != "Pendant":
        rec["title"] = _PENDANT_QUALIFIERS.sub("", rec["title"])
