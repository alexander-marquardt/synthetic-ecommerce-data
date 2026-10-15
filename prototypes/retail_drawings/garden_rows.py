"""Lawn mower, robot mower, grass trimmer and barbecue templates for the scaled catalog (gen#203): data only.

The Garden department sold plants and growing kits only. This is the garden machines' first
increment: **Garden > Lawn Care** (lawn mowers with cordless, petrol and electric kinds, robot
mowers, grass trimmers) and **Garden > Barbecues & Grills** (kettle, barrel, kamado, portable and
gas barbecues). Each type has its own drawing (:mod:`kit_garden`), its shopper attributes as
structured entries, and SKUs over its color and its own axis: a mower's or trimmer's cutting width,
a robot mower's lawn area, a kettle's diameter, a gas barbecue's burners.

Every type offers the six main colors across its styles (gen#275). Not done yet (gen#203): hedge
trimmers, garden furniture sets and parasols; garden hoses are gen#292's.

**Text-match decoys (gen#294).** Each type carries three: a sibling product whose title holds the
type word (a cushion, an apron), a real product of the type whose title names a power source or
fuel it does not use ("Electric Lawn Mower, Petrol Free"), and a candle whose scent holds an
incidental word ("Freshly Mown Lawn"). Their fields tell the truth. :func:`decoy_ids` is what
:func:`scale.derivable` and :mod:`main_colors` leave alone.

All names are invented. Rows are templates only: :func:`scale.derivable` leaves them out, so the
department grows by authored rows.
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

import kit_garden  # noqa: F401 -- registers lawn_mower, robot_mower, grass_trimmer, bbq
from breadth_rows import Row
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

RED = cw("Red", "#c8312e")
BLUE = cw("Blue", "#3f6fb5")
GREEN = cw("Green", "#4f8a3a")
YELLOW = cw("Yellow", "#f2c230")
BLACK = cw("Black", "#2d2d33")
WHITE = cw("White", "#f4f1ea", "solid", "#9a9ca0")


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
         (BLACK, BLUE, YELLOW), _bbq("Charcoal", "Barrel", True, True),
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
         params=(("kind", "gas"), ("burners", "4"))),
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
#: source it lacks) and ``incidental`` (a scent holds a word of the query).
DECOY_TABLE = {
    "DCMCSH": ("type", "lawn mower", "Lawn Mower"), "DCMELC": ("absent", "petrol lawn mower", "Lawn Mower"),
    "DCMCND": ("incidental", "lawn mower", "Lawn Mower"),
    "DCRCSH": ("type", "robot mower", "Robot Mower"), "DCRWIR": ("absent", "gps robot mower", "Robot Mower"),
    "DCRCND": ("incidental", "robot mower", "Robot Mower"),
    "DCTAPR": ("type", "grass trimmer", "Grass Trimmer"), "DCTELC": ("absent", "cordless grass trimmer", "Grass Trimmer"),
    "DCTCND": ("incidental", "grass trimmer", "Grass Trimmer"),
    "DCBAPR": ("type", "bbq", "BBQ"), "DCBCHR": ("absent", "gas bbq", "BBQ"),
    "DCBCND": ("incidental", "bbq", "BBQ"),
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
    _candle("DCRCND", "Garden Robot Moss Candle", "A mossy green scent in a glass jar, for a shelf by the garden door.", "Moss"),
    _apron("DCTAPR", "Grass Trimmer Dad Apron", "A cotton apron with a pocket, printed with a grass trimmer and a joke about the lawn."),
    _row("DCTELC", "Corded Grass Trimmer, Not Cordless", _W, (*_TRIM, "Electric Grass Trimmers"), "Grass Trimmer",
         29.0, "grass_trimmer", "A mains trimmer on a long cable, with no battery to charge.",
         (YELLOW,), _trimmer("electric", "line", False), _axis((26, 29.0),), "cutting_width_cm",
         (("head", "line"), ("power", "electric"))),
    _candle("DCTCND", "Fresh Cut Grass Candle", "A green, grassy scent in a glass jar, as a trimmer leaves the verge.", "Cut Grass"),
    _apron("DCBAPR", "BBQ Master Apron", "A cotton apron with a pocket and a bottle opener loop, for the one who mans the grill."),
    _row("DCBCHR", "Charcoal BBQ, Not Gas", _L, (*_BBQ, "Charcoal Barbecues"), "BBQ", 39.0, "bbq",
         "A bowl grill that burns charcoal, with no gas bottle or hose to fit.",
         (BLACK,), _bbq("Charcoal", "Portable", True, False), _axis((38, 39.0),), "diameter_cm", (("kind", "portable"),)),
    _candle("DCBCND", "Smoky Garden BBQ Candle", "A smoky wood scent in a glass jar, as the barbecue dies down.", "Wood Smoke"),
)

ROWS = (*LAWN_MOWERS, *ROBOT_MOWERS, *GRASS_TRIMMERS, *BBQS, *DECOYS)


def decoy_ids() -> frozenset[str]:
    """The decoys' product ids: derivation and color completion leave them as authored."""
    return frozenset(f"BRD-{r.code}" for r in DECOYS)


def docs() -> list[dict]:
    """Every row's catalog document."""
    return [r.doc() for r in ROWS]
