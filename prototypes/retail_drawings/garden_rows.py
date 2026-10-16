"""Lawn mower, robot mower, grass trimmer and barbecue templates for the scaled catalog (gen#203), and the garden hose's decoys.

The Garden department sold plants and growing kits only. This is the garden machines' first
increment: **Garden > Lawn Care** (lawn mowers with cordless, petrol and electric kinds, robot
mowers, grass trimmers) and **Garden > Barbecues & Grills** (kettle, barrel, kamado, portable and
gas barbecues). Each type has its own drawing (:mod:`kit_garden`), its shopper attributes as
structured entries, and SKUs over its color and its own axis: a mower's or trimmer's cutting width,
a robot mower's lawn area, a kettle's diameter, a gas barbecue's burners.

Every type offers the six main colors across its styles (gen#275). Not done yet (gen#203): hedge
trimmers, garden furniture sets and parasols. The garden hoses are a type spec
(``type_specs/garden_hose.py``, gen#292); their decoys are here, with the machines', copied from
the spec's two styles.

**Text-match decoys (gen#294).** Each type carries at least three of each of five classes: a sibling
product whose title holds the type word (a cushion, an apron), a real product of the type whose
title names a power source or fuel it does not use ("Electric Lawn Mower, Petrol Free"), a short
title or a scent with an incidental word ("Red Kite Lawn Mower", "Freshly Mown Lawn"), a title that
names a part's color beside the product's own, and a description that names another color. Their
fields tell the truth. :func:`decoy_ids` is what :func:`scale.derivable` and :mod:`main_colors`
leave alone.

All names are invented. Rows are templates only: :func:`scale.derivable` leaves them out, so the
department grows by authored rows.
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

import re
from dataclasses import replace

import kit_garden  # registers lawn_mower, robot_mower, grass_trimmer, bbq
from breadth_rows import Row
from type_specs import garden_hose
from variants import cw

from synthetic_ecommerce_data.core.entry import canonical

DEPARTMENT = "Garden"
_V, _M = "Thistle & Wren", "Fenwold Nursery"
_W, _H, _L = "Wrenfield", "Harbour & Pine", "Larkmoor"
_E = _W
_LAWN = (DEPARTMENT, "Lawn Care")
_MOW = (*_LAWN, "Lawn Mowers")
_TRIM = (*_LAWN, "Grass Trimmers")
_BBQ = (DEPARTMENT, "Barbecues & Grills")

_HEX = kit_garden.ACCENT_HEX
RED = cw("Red", _HEX["red"])
BLUE = cw("Blue", _HEX["blue"])
GREEN = cw("Green", _HEX["green"])
YELLOW = cw("Yellow", _HEX["yellow"])
BLACK = cw("Black", _HEX["black"])
WHITE = cw("White", _HEX["white"], "solid", "#9a9ca0")


def _a(key: str, name: str, v: str) -> tuple[str, str, str]:
    return (key, name, v)


def _u(key: str, name: str, v: int, unit: str) -> tuple[str, str, str, str, float]:
    """A measured attribute with its unit: the canonical value is the core's."""
    return (key, name, str(v), unit, float(canonical(str(v), unit)))


def _axis(*pairs: tuple[float, float]) -> tuple[tuple[str, float], ...]:
    """SKU values of a measured axis and the price at each."""
    return tuple((f"{v:g}", p) for v, p in pairs)


def _row(code: str, title: str, brand: str, path: tuple[str, ...], ptype: str, price: float,
         shape: str, description: str, colors: tuple, attrs: tuple, sizes: tuple = (),
         size_key: str = "size", params: tuple = ()) -> Row:  # fmt: skip
    return Row(code, title, brand, DEPARTMENT, path, ptype, price, shape, description, colors,
               attrs, sizes, size_key=size_key, params=params)  # fmt: skip


def _mower(power: str, drive: str, box_l: int, heights: int, volts: int = 0) -> tuple:
    """The attributes every lawn mower states; a cordless one adds its battery."""
    source = {"cordless": "Cordless Battery", "petrol": "Petrol", "electric": "Corded Electric"}[power]
    out = (_a("power_source", "Power source", source),
           _a("drive", "Drive", "Self-Propelled" if drive == "self" else "Push"),
           _u("grass_box_capacity", "Grass box capacity", box_l, "LTR"),
           _a("cutting_heights", "Cutting heights", str(heights)))  # fmt: skip
    if power == "cordless":
        out += (_u("battery_voltage", "Battery voltage", volts, "VLT"), _a("battery_included", "Battery included", "Yes"))
    return out


def _trimmer(power: str, head: str, telescopic: bool, volts: int = 0) -> tuple:
    source = {"cordless": "Cordless Battery", "petrol": "Petrol", "electric": "Corded Electric"}[power]
    out = (_a("power_source", "Power source", source),
           _a("cutting_head", "Cutting head", "Line" if head == "line" else "Blade"),
           _a("telescopic", "Telescopic", "Yes" if telescopic else "No"))  # fmt: skip
    if power == "cordless":
        out += (_u("battery_voltage", "Battery voltage", volts, "VLT"),)
    return out


def _bbq(fuel: str, kind: str, lid: bool, shelves: bool, *more: tuple) -> tuple:
    return (_a("fuel", "Fuel", fuel), _a("bbq_kind", "Barbecue kind", kind),
            _a("lid", "Lid", "Yes" if lid else "No"),
            _a("side_shelves", "Side shelves", "Yes" if shelves else "No"), *more)  # fmt: skip


# --------------------------------------------------------------------------
# Lawn mowers: the cutting width and color are SKUs; the power source is the style.
# --------------------------------------------------------------------------

LAWN_MOWERS = (
    _row("MWRCLP", "Cordless Push Lawn Mower", _V, (*_MOW, "Cordless Lawn Mowers"), "Lawn Mower", 149.0,
         "lawn_mower", "A lightweight mower that runs on a rechargeable battery, with a folding "
         "handle and a rear grass bag, for small and medium lawns.",
         (GREEN, RED, BLACK, YELLOW), _mower("cordless", "push", 40, 5, 36),
         _axis((32, 149.0), (37, 179.0), (42, 219.0)), "cutting_width_cm",
         (("power", "cordless"), ("drive", "push"))),
    _row("MWRCSP", "Cordless Self-Propelled Lawn Mower", _M, (*_MOW, "Cordless Lawn Mowers"), "Lawn Mower",
         329.0, "lawn_mower", "A battery mower that drives its own wheels, so a long lawn is a "
         "steady walk, with a large grass bag and seven cutting heights.",
         (RED, BLUE, BLACK, WHITE), _mower("cordless", "self", 55, 7, 40),
         _axis((41, 329.0), (46, 389.0)), "cutting_width_cm",
         (("power", "cordless"), ("drive", "self"))),
    _row("MWRPET", "Petrol Self-Propelled Lawn Mower", _H, (*_MOW, "Petrol Lawn Mowers"), "Lawn Mower",
         299.0, "lawn_mower", "A four-stroke engine mower with a pull-start and a driven rear "
         "axle, built for large lawns and long grass.",
         (RED, GREEN, YELLOW, BLUE), _mower("petrol", "self", 60, 7),
         _axis((46, 299.0), (51, 349.0), (53, 399.0)), "cutting_width_cm",
         (("power", "petrol"), ("drive", "self"))),
    _row("MWRELC", "Corded Electric Lawn Mower", _W, (*_MOW, "Electric Lawn Mowers"), "Lawn Mower", 79.0,
         "lawn_mower", "A mains mower with a ten metre cable, a push handle and a rear grass "
         "bag, light enough to lift over a step.",
         (BLUE, YELLOW, WHITE, GREEN), _mower("electric", "push", 35, 3),
         _axis((32, 79.0), (34, 89.0), (38, 109.0)), "cutting_width_cm",
         (("power", "electric"), ("drive", "push"))),
)

# --------------------------------------------------------------------------
# Robot mowers: the lawn area it covers is the SKU.
# --------------------------------------------------------------------------


def _robot(boundary: str, app: bool, slope: int) -> tuple:
    return (_a("boundary", "Boundary", "Wire" if boundary == "wire" else "Wire-Free GPS"),
            _a("app_control", "App control", "Yes" if app else "No"),
            _a("max_slope", "Maximum slope (%)", str(slope)))  # fmt: skip


ROBOT_MOWERS = (
    _row("ROBWIR", "Wire Guided Robot Mower", _V, (*_MOW, "Robot Mowers"), "Robot Mower", 449.0,
         "robot_mower", "A quiet robot that mows by itself inside a boundary wire and returns to "
         "its charging station, controlled from a phone.",
         (GREEN, WHITE, BLACK), _robot("wire", True, 35),
         _axis((300, 449.0), (500, 549.0), (800, 699.0)), "lawn_area_m2", (("boundary", "wire"),)),
    _row("ROBGPS", "Wire Free GPS Robot Mower", _M, (*_MOW, "Robot Mowers"), "Robot Mower", 899.0,
         "robot_mower", "A satellite-guided robot that maps the lawn so there is nothing to bury, "
         "steers round obstacles and climbs steep banks.",
         (BLUE, RED, YELLOW, WHITE), _robot("gps", True, 45),
         _axis((500, 899.0), (1000, 1099.0), (1500, 1399.0)), "lawn_area_m2", (("boundary", "gps"),)),
    _row("ROBCMP", "Compact Robot Mower for Small Lawns", _H, (*_MOW, "Robot Mowers"), "Robot Mower", 279.0,
         "robot_mower", "A small, light robot for a town lawn, set up with a boundary wire and "
         "a dial on its back.",
         (YELLOW, BLACK, GREEN), _robot("wire", False, 25),
         _axis((150, 279.0), (250, 329.0)), "lawn_area_m2", (("boundary", "wire"),)),
)

# --------------------------------------------------------------------------
# Grass trimmers: the cutting width and color are SKUs.
# --------------------------------------------------------------------------

GRASS_TRIMMERS = (
    _row("TRMCRD", "Cordless Line Grass Trimmer", _V, (*_TRIM, "Cordless Grass Trimmers"), "Grass Trimmer",
         69.0, "grass_trimmer", "A battery trimmer with a nylon line head that feeds as you tap "
         "it, for edging a lawn and tidying round beds.",
         (GREEN, RED, BLACK, YELLOW), _trimmer("cordless", "line", True, 18),
         _axis((25, 69.0), (30, 79.0), (33, 95.0)), "cutting_width_cm",
         (("head", "line"), ("power", "cordless"))),
    _row("TRMPET", "Petrol Blade Grass Trimmer", _H, (*_TRIM, "Petrol Grass Trimmers"), "Grass Trimmer",
         159.0, "grass_trimmer", "A two-stroke trimmer with a metal blade for brambles, nettles "
         "and rough ground, with a shoulder strap.",
         (RED, BLUE, BLACK), _trimmer("petrol", "blade", False),
         _axis((40, 159.0), (43, 189.0)), "cutting_width_cm", (("head", "blade"), ("power", "petrol"))),
    _row("TRMELC", "Corded Electric Grass Trimmer", _W, (*_TRIM, "Electric Grass Trimmers"), "Grass Trimmer",
         34.0, "grass_trimmer", "A mains trimmer with a telescopic shaft and a pivoting head, "
         "light for trimming along walls and borders.",
         (BLUE, YELLOW, WHITE, GREEN), _trimmer("electric", "line", True),
         _axis((26, 34.0), (30, 42.0)), "cutting_width_cm", (("head", "line"), ("power", "electric"))),
)

# --------------------------------------------------------------------------
# Barbecues: fuel and kind are the style; the size or the burners are the SKU.
# --------------------------------------------------------------------------

BBQS = (
    _row("BBQKET", "Kettle Charcoal BBQ", _L, (*_BBQ, "Charcoal Barbecues"), "BBQ", 69.0, "bbq",
         "A round bowl and a domed lid with vents, on three legs, for grilling and slow roasting "
         "over coals.",
         (BLACK, RED, GREEN, WHITE), _bbq("Charcoal", "Kettle", True, False),
         _axis((47, 69.0), (57, 99.0), (67, 139.0)), "diameter_cm", (("kind", "kettle"),)),
    _row("BBQBRL", "Barrel Charcoal BBQ with Chimney", _E, (*_BBQ, "Charcoal Barbecues"), "BBQ", 129.0,
         "bbq", "A horizontal drum with a side firebox and a tall chimney, for smoking joints "
         "low and slow.",
         (BLACK, BLUE, YELLOW), _bbq("Charcoal", "Barrel", True, False),
         _axis((90, 129.0), (110, 179.0)), "length_cm", (("kind", "barrel"),)),
    _row("BBQKAM", "Ceramic Kamado Charcoal BBQ", _H, (*_BBQ, "Charcoal Barbecues"), "BBQ", 349.0,
         "bbq", "An egg-shaped ceramic cooker that holds its heat for hours, for baking, "
         "roasting and searing.",
         (RED, BLACK, GREEN), _bbq("Charcoal", "Kamado", True, False),
         _axis((40, 349.0), (53, 549.0)), "diameter_cm", (("kind", "kamado"),)),
    _row("BBQPRT", "Portable Charcoal BBQ", _E, (*_BBQ, "Charcoal Barbecues"), "BBQ", 24.0, "bbq",
         "A small bowl grill with a carry handle and folding legs, for a picnic or a camping trip.",
         (YELLOW, BLACK, BLUE, WHITE), _bbq("Charcoal", "Portable", True, False),
         _axis((33, 24.0), (38, 34.0)), "diameter_cm", (("kind", "portable"),)),
    _row("BBQGAS", "Three Burner Gas BBQ with Side Shelves", _L, (*_BBQ, "Gas Barbecues"), "BBQ", 279.0, "bbq",
         "A cabinet barbecue with a hooded lid, a burner for every knob and a shelf either "
         "side for plates and tools.",
         (BLACK, RED, WHITE, BLUE), _bbq("Gas", "Gas", True, True, _u("burners", "Burners", 3, "C62")),
         params=(("kind", "gas"), ("burners", "3"))),
    _row("BBQGSB", "Four Burner Gas BBQ with Side Burner", _H, (*_BBQ, "Gas Barbecues"), "BBQ", 449.0, "bbq",
         "A cabinet with a separate side burner for a pan, a warming rack and a thermometer "
         "in the lid.",
         (BLACK, GREEN, RED), _bbq("Gas", "Gas", True, True, _u("burners", "Burners", 4, "C62"), _a("side_burner", "Side burner", "Yes")),
         params=(("kind", "gas"), ("burners", "4"), ("side_burner", "yes"))),
)

# --------------------------------------------------------------------------
# Text-match decoys (gen#294): the words match a garden query, the fields do not.
# --------------------------------------------------------------------------

_CUSH = ("Home", "Soft Furnishings", "Cushions")
_APRON = ("Home", "Kitchen & Dining", "Aprons")
_CANDLE = ("Gifts", "Home Fragrance", "Scented Candles")
_HEARTH, _LANTERN = "Hearth & Table", "Lanternby"
_CREAM = cw("Cream", "#efe8d8")
_SAGE = cw("Sage", "#9bb08f")
_SMOKE = cw("Smoke", "#6f6a66")


def _cushion(code: str, title: str, desc: str) -> Row:
    return Row(code, title, _HEARTH, "Home", _CUSH, "Cushion", 16.0, "cushion", desc, (_CREAM, _SAGE),
               (("fabric", "Fabric", "Cotton"),), (("45 x 45cm", 16.0),))


def _apron(code: str, title: str, desc: str) -> Row:
    return Row(code, title, _HEARTH, "Home", _APRON, "Apron", 12.0, "apron", desc, (_CREAM, _SAGE),
               (("fabric", "Fabric", "Cotton"),))


def _candle(code: str, title: str, desc: str, scent: str) -> Row:
    return Row(code, title, _LANTERN, "Gifts", _CANDLE, "Scented Candle", 12.0, "jar", desc, (_SMOKE,),
               (("fragrance", "Fragrance", scent),), label="Candle")


#: code -> (the class, the query it targets, the type word it misleads on). The classes: ``type``
#: (a sibling product holds the type word), ``absent`` (a real product names a fuel or power
#: source it lacks), ``incidental`` (a scent or a short title holds a word of the query),
#: ``secondary`` (the title names a part's color) and ``shade`` (only the description names a color).
DECOY_TABLE = {
    "DCMCSH": ("type", "lawn mower", "Lawn Mower"), "DCMELC": ("absent", "petrol lawn mower", "Lawn Mower"),
    "DCMCND": ("incidental", "lawn mower", "Lawn Mower"),
    "DCRCSH": ("type", "robot mower", "Robot Mower"), "DCRWIR": ("absent", "gps robot mower", "Robot Mower"),
    "DCRCND": ("incidental", "robot mower", "Robot Mower"),
    "DCTAPR": ("type", "grass trimmer", "Grass Trimmer"), "DCTELC": ("absent", "cordless grass trimmer", "Grass Trimmer"),
    "DCTCND": ("incidental", "grass trimmer", "Grass Trimmer"),
    "DCBAPR": ("type", "bbq", "BBQ"), "DCBCHR": ("absent", "gas bbq", "BBQ"),
    "DCBCND": ("incidental", "bbq", "BBQ"),
    "DCHCSH": ("type", "garden hose", "Garden Hose"), "DCHCND": ("incidental", "garden hose", "Garden Hose"),
}  # fmt: skip

DECOYS = (
    _cushion("DCMCSH", "Vintage Lawn Mower Cushion", "A cotton cushion printed with an old push mower on a striped lawn."),
    _row("DCMELC", "Petrol Free Electric Lawn Mower", _W, (*_MOW, "Electric Lawn Mowers"), "Lawn Mower", 89.0,
         "lawn_mower", "A mains mower with no petrol to buy or oil to change, so it starts at the press of a switch.",
         (GREEN,), _mower("electric", "push", 35, 3), _axis((34, 89.0),), "cutting_width_cm",
         (("power", "electric"), ("drive", "push"))),
    _candle("DCMCND", "Freshly Mown Lawn Candle", "The smell of a lawn after the mower has been round, in a glass jar.", "Cut Lawn"),
    _cushion("DCRCSH", "Robot Mower Print Cushion", "A cotton cushion with a little round robot mower printed on it."),
    _row("DCRWIR", "Wire Robot Mower, No GPS", _H, (*_MOW, "Robot Mowers"), "Robot Mower", 299.0, "robot_mower",
         "A wire-guided robot that needs no satellite signal or subscription.",
         (WHITE,), _robot("wire", False, 30), _axis((250, 299.0),), "lawn_area_m2", (("boundary", "wire"),)),
    _candle("DCRCND", "Garden Robot Moss Candle", "A mossy scent in a glass jar, for a shelf by the garden door.", "Moss"),
    _apron("DCTAPR", "Grass Trimmer Dad Apron", "A cotton apron with a pocket, printed with a grass trimmer and a joke about the lawn."),
    _row("DCTELC", "Corded Grass Trimmer, Not Cordless", _W, (*_TRIM, "Electric Grass Trimmers"), "Grass Trimmer",
         29.0, "grass_trimmer", "A mains trimmer on a long cable, with no battery to charge.",
         (YELLOW,), _trimmer("electric", "line", False), _axis((26, 29.0),), "cutting_width_cm",
         (("head", "line"), ("power", "electric"))),
    _candle("DCTCND", "Fresh Cut Grass Candle", "A cut-grass scent in a glass jar, as a trimmer leaves the verge.", "Cut Grass"),
    _apron("DCBAPR", "BBQ Master Apron", "A cotton apron with a pocket and a bottle opener loop, for the one who mans the grill."),
    _row("DCBCHR", "Charcoal BBQ, Not Gas", _L, (*_BBQ, "Charcoal Barbecues"), "BBQ", 39.0, "bbq",
         "A bowl grill that burns charcoal, with no gas bottle or hose to fit.",
         (BLACK,), _bbq("Charcoal", "Portable", True, False), _axis((38, 39.0),), "diameter_cm", (("kind", "portable"),)),
    _candle("DCBCND", "Smoky Garden BBQ Candle", "A smoky wood scent in a glass jar, as the barbecue dies down.", "Wood Smoke"),
    _cushion("DCHCSH", "Garden Hose Print Cushion", "A cotton cushion printed with a coiled garden hose on a striped lawn."),
    _candle("DCHCND", "Garden Rain Mist Candle", "A damp paving scent in a glass jar, as the hose is turned off after dusk.", "Rain on Stone"),
)


# The decoys added for the gen#294 minimum (three of each class per type): real products of the
# type are copies of one of its styles with one main color, a title or a description that
# misleads, and the first size only.
_MAIN = ("red", "blue", "green", "yellow", "black", "white")
_BASE = {r.code: r for r in (*LAWN_MOWERS, *ROBOT_MOWERS, *GRASS_TRIMMERS, *BBQS, *garden_hose.SPEC.rows)}
_COLOR = {c[0].lower(): c for c in (RED, BLUE, GREEN, YELLOW, BLACK, WHITE)}
_QUERY = {"Lawn Mower": "lawn mower", "Robot Mower": "robot mower", "Grass Trimmer": "grass trimmer", "BBQ": "bbq", "Garden Hose": "garden hose"}
_ABSENT = {"Lawn Mower": "petrol", "Robot Mower": "gps", "Grass Trimmer": "cordless", "BBQ": "gas", "Garden Hose": "latex"}


_NAMED_PART = re.compile(r"\bwith (\w+) ([\w ]+)$")
_FIRST_WORD = re.compile(r"^(red|blue|green|yellow|black|white)\b", re.I)


def _named(cls: str, title: str, shape: str) -> tuple[tuple[str, str], ...]:
    """The part a decoy's title names and its color, as the drawing's params (a ``secondary``
    title ends "with Red Wheels"; an ``incidental`` short title starts with the color word and
    colors the shape's first part), so the picture shows what the title says."""
    if cls == "secondary":
        m = _NAMED_PART.search(title)
        assert m, title
        return (("part", m.group(2).lower().replace(" ", "-")), ("part_color", m.group(1).lower()))
    if cls == "incidental":
        m = _FIRST_WORD.match(title)
        assert m, title
        return (("part", kit_garden.PARTS[shape][0]), ("part_color", m.group(1).lower()))
    return ()


def _copy(code: str, cls: str, title: str, base: str, color: str, desc: str) -> Row:
    b = _BASE[base]
    sizes = b.sizes[:1]
    return replace(b, code=code, title=title, description=desc, colors=(_COLOR[color],), sizes=sizes,
                   price=sizes[0][1] if sizes else b.price,
                   params=(*b.params, *_named(cls, title, b.shape)))  # fmt: skip


#: (code, class, title, base style, own main color, description) for each added real product,
#: and (code, class, title, description) for each added sibling product (a cushion or an apron).
_REAL = {
    "Lawn Mower": (
        ("DCMA01", "absent", "Petrol Free Cordless Lawn Mower", "MWRCLP", "blue", "A battery mower with no fuel mix to buy and no pull cord, ready after a charge."),
        ("DCMA02", "absent", "Corded Lawn Mower, Not Petrol", "MWRELC", "yellow", "A mains mower on a long cable, quiet and light, with nothing to refuel."),
        ("DCMI01", "incidental", "Red Kite Lawn Mower", "MWRELC", "black", "A mains mower with a rear grass bag, named for the kites over the lawn."),
        ("DCMI02", "incidental", "Blue Moon Lawn Mower", "MWRPET", "green", "A four-stroke mower with a driven rear axle, for long grass."),
        ("DCMS01", "secondary", "Green Lawn Mower with Red Wheels", "MWRELC", "green", "A mains mower with a ten metre cable and a rear grass bag."),
        ("DCMS02", "secondary", "Yellow Cordless Lawn Mower with Black Handle", "MWRCLP", "yellow", "A battery mower with a folding handle and a rear grass bag."),
        ("DCMS03", "secondary", "Red Petrol Lawn Mower with White Grass Box", "MWRPET", "red", "A pull-start mower with a driven rear axle, for large lawns."),
        ("DCMH01", "shade", "Light Corded Lawn Mower", "MWRELC", "blue", "A mains mower with a bright red start switch and a rear grass bag."),
        ("DCMH02", "shade", "Folding Cordless Lawn Mower", "MWRCLP", "black", "A battery mower with a lime yellow grass bag that folds flat for the shed."),
        ("DCMH03", "shade", "Heavy Duty Petrol Lawn Mower", "MWRPET", "blue", "A four-stroke mower with a white pull cord handle and a wide deck."),
    ),
    "Robot Mower": (
        ("DCRA01", "absent", "Robot Mower, No GPS Needed", "ROBWIR", "yellow", "A robot that follows a boundary wire, with no satellite signal to lose under trees."),
        ("DCRA02", "absent", "GPS Free Robot Mower for Terraces", "ROBCMP", "black", "A small wire-guided robot for a narrow terraced lawn."),
        ("DCRI01", "incidental", "Black Pearl Robot Mower", "ROBWIR", "white", "A wire-guided robot that mows by night, named for the color of its range."),
        ("DCRI02", "incidental", "Blue Moon Robot Mower", "ROBCMP", "yellow", "A small robot for a town lawn, with a dial on its back."),
        ("DCRS01", "secondary", "White Robot Mower with Red Bumper", "ROBWIR", "white", "A wire-guided robot with a domed cover and a rain sensor."),
        ("DCRS02", "secondary", "Yellow Robot Mower with Black Wheels", "ROBCMP", "yellow", "A compact robot that returns to its dock by itself."),
        ("DCRS03", "secondary", "Green Robot Mower with White Button", "ROBWIR", "green", "A wire-guided robot for a medium lawn, set from its dial."),
        ("DCRH01", "shade", "Quiet Robot Mower for Small Lawns", "ROBCMP", "white", "A small robot with a red stop button on its top and a boundary wire."),
        ("DCRH02", "shade", "Rain Sensing Robot Mower", "ROBWIR", "black", "A robot with a bright yellow charging dock that sends it home in a shower."),
        ("DCRH03", "shade", "Night Time Robot Mower", "ROBCMP", "green", "A robot that mows after dark, with a blue status light on its cover."),
    ),
    "Grass Trimmer": (
        ("DCTA01", "absent", "Not Cordless: Petrol Grass Trimmer", "TRMPET", "yellow", "A two-stroke trimmer with a metal blade, which starts on a pull cord."),
        ("DCTA02", "absent", "Mains Grass Trimmer, Never Cordless", "TRMELC", "red", "A trimmer on a long cable, with a telescopic shaft."),
        ("DCTI01", "incidental", "Red Kite Grass Trimmer", "TRMELC", "black", "A mains trimmer with a pivoting head, from the Kite range."),
        ("DCTI02", "incidental", "Blue Moon Grass Trimmer", "TRMCRD", "yellow", "A battery trimmer with a line head that feeds as you tap it."),
        ("DCTS01", "secondary", "Green Cordless Grass Trimmer with Black Handle", "TRMCRD", "green", "A battery trimmer for edging a lawn and tidying round beds."),
        ("DCTS02", "secondary", "Yellow Grass Trimmer with Red Shaft", "TRMELC", "yellow", "A mains trimmer for trimming along walls and borders."),
        ("DCTS03", "secondary", "Blue Petrol Grass Trimmer with White Engine", "TRMPET", "blue", "A two-stroke trimmer for brambles and rough ground."),
        ("DCTH01", "shade", "Light Edging Grass Trimmer", "TRMCRD", "black", "A battery trimmer with a red trigger and a line head."),
        ("DCTH02", "shade", "Heavy Duty Grass Trimmer", "TRMPET", "white", "A trimmer with a bright yellow shoulder strap and a metal blade."),
        ("DCTH03", "shade", "Telescopic Border Grass Trimmer", "TRMELC", "red", "A mains trimmer with a green guard and a pivoting head."),
    ),
    "BBQ": (
        ("DCBA01", "absent", "Gas Free Kettle BBQ", "BBQKET", "red", "A charcoal kettle with a vented lid, with no bottle or hose to fit."),
        ("DCBA02", "absent", "Kamado BBQ, No Gas Needed", "BBQKAM", "green", "A ceramic cooker that holds its heat on charcoal alone."),
        ("DCBI01", "incidental", "Red Kite BBQ", "BBQKET", "black", "A charcoal kettle from the Kite range, with a vented lid."),
        ("DCBI02", "incidental", "Blue Moon BBQ", "BBQPRT", "white", "A small bowl grill with a carry handle and folding legs."),
        ("DCBS01", "secondary", "Black Kettle BBQ with Red Lid Handle", "BBQKET", "black", "A charcoal kettle with a vented lid, on three legs."),
        ("DCBS02", "secondary", "Red Portable BBQ with Black Legs", "BBQPRT", "red", "A small bowl grill for a picnic or a camping trip."),
        ("DCBS03", "secondary", "Blue Gas BBQ with White Shelves", "BBQGAS", "blue", "A cabinet barbecue with a hooded lid and a shelf each side."),
        ("DCBH01", "shade", "Family Kettle BBQ", "BBQKET", "white", "A charcoal kettle with a red vent dial and a thermometer in the lid."),
        ("DCBH02", "shade", "Folding Portable BBQ", "BBQPRT", "blue", "A bowl grill with a yellow carry strap and folding legs."),
        ("DCBH03", "shade", "Smoker Kamado BBQ", "BBQKAM", "yellow", "A ceramic cooker with a green felt seal and a heavy lid."),
    ),
    "Garden Hose": (
        ("DCHA01", "absent", "Latex Free Garden Hose", "GHSREIN", "blue", "A four-layer PVC hose with no latex tube to perish in the sun, fitted to a standard outdoor tap."),
        ("DCHA02", "absent", "Garden Hose, Not Latex", "GHSREIN", "black", "A PVC hose that stays flexible in the cold, with nothing to stretch or shrink."),
        ("DCHA03", "absent", "Latex Free Reinforced Garden Hose", "GHSREIN", "green", "A reinforced PVC hose for a standard outdoor tap, with no latex to smell or split."),
        ("DCHI01", "incidental", "Red Kite Garden Hose", "GHSREIN", "black", "A reinforced hose from the Kite range, coiled for storage."),
        ("DCHI02", "incidental", "Blue Moon Garden Hose", "GHSEXPN", "yellow", "A light hose that shrinks to store, named for the moon over the lawn."),
        ("DCHS01", "secondary", "Black Garden Hose with Green Connectors", "GHSREIN", "black", "A four-layer hose that resists kinks, coiled for storage."),
        ("DCHS02", "secondary", "Red Expandable Garden Hose with Yellow Connectors", "GHSEXPN", "red", "A light hose that grows under water pressure and shrinks back to store."),
        ("DCHS03", "secondary", "Green Garden Hose with White Connectors", "GHSREIN", "green", "A reinforced hose for a standard outdoor tap, coiled for storage."),
        ("DCHH01", "shade", "Heavy Duty Garden Hose", "GHSREIN", "blue", "A four-layer hose, with a red hanging strap in the box and a standard tap fitting."),
        ("DCHH02", "shade", "Lightweight Garden Hose", "GHSEXPN", "green", "A light hose that grows under water pressure, supplied with a yellow spray gun."),
        ("DCHH03", "shade", "Compact Garden Hose", "GHSEXPN", "white", "A hose that shrinks back to store in a small space, sold in a bag with a black carry handle."),
    ),
}
def _hose_candle(code: str, title: str, desc: str) -> Row:
    return _candle(code, title, desc, "Fresh Grass")


_SIBLINGS = (
    ("DCMT01", "Lawn Mower", _apron, "Lawn Mower Racing Apron", "A cotton apron printed with a mower and a joke about stripes."),
    ("DCMT02", "Lawn Mower", _cushion, "Striped Lawn Mower Cushion", "A cotton cushion printed with a mower on a striped lawn."),
    ("DCRT01", "Robot Mower", _apron, "Robot Mower Chef Apron", "A cotton apron with a pocket, printed with a little round robot mower."),
    ("DCRT02", "Robot Mower", _cushion, "Robot Mower Garden Cushion", "A cotton cushion with a robot mower on a green lawn."),
    ("DCTT01", "Grass Trimmer", _cushion, "Grass Trimmer Joke Cushion", "A cotton cushion printed with a trimmer and a joke about hedges."),
    ("DCTT02", "Grass Trimmer", _apron, "Grass Trimmer Workshop Apron", "A cotton apron with two pockets, printed with a trimmer."),
    ("DCBT01", "BBQ", _cushion, "BBQ Night Cushion", "A cotton cushion printed with a grill and a string of lights."),
    ("DCBT02", "BBQ", _apron, "BBQ Grill Pro Apron", "A cotton apron with a pocket and a bottle opener loop."),
    ("DCHT01", "Garden Hose", _apron, "Garden Hose Pro Apron", "A cotton apron with a pocket, printed with a coiled hose and a joke about the lawn."),
    ("DCHT02", "Garden Hose", _hose_candle, "Garden Hose Fresh Candle", "A fresh-cut grass scent in a glass jar, for a shelf by the garden door."),
)
_CLASS_QUERY = {"type": "{q}", "absent": "{a} {q}", "incidental": "{c} {q}", "secondary": "{c} {q}", "shade": "{c} {q}"}
_COLOR_WORD = re.compile(r"\b(red|blue|green|yellow|black|white)\b", re.I)


def _query_color(cls: str, title: str, desc: str, own: str) -> str:
    """The color a decoy's text names that its own is not: the query it answers."""
    words = [w.lower() for w in _COLOR_WORD.findall(desc if cls == "shade" else title)]
    return next((w for w in words if w != own), "")


for _ptype, _items in _REAL.items():
    for _code, _cls, _title, _base, _own, _desc in _items:
        _query = _CLASS_QUERY[_cls].format(q=_QUERY[_ptype], a=_ABSENT[_ptype], c=_query_color(_cls, _title, _desc, _own))
        DECOY_TABLE[_code] = (_cls, _query, _ptype)
for _code, _ptype, *_ in _SIBLINGS:
    DECOY_TABLE[_code] = ("type", _QUERY[_ptype], _ptype)

DECOYS = (
    *DECOYS,
    *(_copy(c, k, t, b, col, d) for items in _REAL.values() for c, k, t, b, col, d in items),
    *(make(c, t, d) for c, _p, make, t, d in _SIBLINGS),
)

ROWS = (*LAWN_MOWERS, *ROBOT_MOWERS, *GRASS_TRIMMERS, *BBQS, *DECOYS)


def decoy_ids() -> frozenset[str]:
    """The decoys' product ids: derivation and color completion leave them as authored."""
    return frozenset(f"BRD-{r.code}" for r in DECOYS)


def docs() -> list[dict]:
    """Every row's catalog document."""
    return [r.doc() for r in ROWS]
