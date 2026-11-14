"""Remote-Control Vehicle (Toys), a breadth type of gen#960 (slice 3).

**Toys > Vehicles > Remote-Control Vehicles.** Each title shows the vehicle's theme and its kind
("Dune Storm Remote-Control Truck"), so the scaled build draws more vehicles by those two
values, and the drawing follows them (:func:`kit_toys_learning.rc_vehicle`: a car, a truck, a
boat or a helicopter with its handset, the theme on the panel). Every template is sold in the
six main colors of the body (ruling 2026-10-13, gen#275) and is for ages 6 and up, so a derived
style keeps its age. Every theme is invented (ruling 2026-10-30, gen#720).
"""

# ruff: noqa: E501 -- data rows read better whole (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail import (
    kit_toys_learning,  # noqa: F401 -- registers rc_vehicle
)
from synthetic_ecommerce_data.domains.retail.toys_play_common import (
    BLACK,
    BLUE,
    FERNBY,
    GREEN,
    MATERIAL_CLAIM,
    PUDDLE,
    RED,
    WHITE,
    YELLOW,
    age,
    kind,
    style,
    toy_decoy,
)
from synthetic_ecommerce_data.domains.retail.type_registry import Row, TypeSpec, a

_PATH = ("Toys", "Vehicles", "Remote-Control Vehicles")
CALDERBY, LANTERNBY, THISTLE = "Calderby & Lune", "Lanternby", "Thistle & Wren"
SIX = (RED, BLUE, GREEN, YELLOW, BLACK, WHITE)

#: The opening sentences: each names the theme and nothing that holds for one vehicle only.
_LEADS = (
    "The {t} model is quick off the mark and easy to steer.",
    "Take the {t} model out for a race with friends.",
    "The {t} model has a handset sized for small hands.",
    "Charge the {t} model by cable and it runs for twenty minutes.",
)


def _vehicle(code: str, theme: str, vehicle: str, brand: str, lead: str, price: float) -> Row:
    """A remote-control vehicle: "<theme> Remote-Control <vehicle>", in the six main colors."""
    toy_type = f"Remote-Control {vehicle}"
    desc = (f"{lead.format(t=theme)} This {toy_type.lower()} comes with a rechargeable "
            f"battery and its handset. For ages 6 and up.")  # fmt: skip
    return style(
        code,
        f"{theme} {toy_type}",
        brand,
        _PATH,
        "Remote-Control Vehicle",
        "rc_vehicle",
        desc,
        SIX,
        (a("theme", "Theme", theme), kind(toy_type), age("6+ years")),
        price,
        params=(("kind", toy_type.lower()), ("theme", theme.lower())),
    )


ROWS = (
    _vehicle("RCVDES", "Dune Storm", "Truck", CALDERBY, _LEADS[0], 32.0),
    _vehicle("RCVTUR", "Turbo Comet", "Car", LANTERNBY, _LEADS[1], 26.0),
    _vehicle("RCVHAR", "Harbour Patrol", "Boat", THISTLE, _LEADS[2], 29.0),
    _vehicle("RCVSKY", "Sky Ranger", "Helicopter", FERNBY, _LEADS[3], 34.0),
    _vehicle("RCVMUD", "Mud Crawler", "Truck", PUDDLE, _LEADS[0], 30.0),
    _vehicle("RCVTRK", "Track Blazer", "Car", CALDERBY, _LEADS[1], 24.0),
    _vehicle("RCVLAK", "Lake Racer", "Boat", LANTERNBY, _LEADS[2], 27.0),
    _vehicle("RCVHAW", "Storm Hawk", "Helicopter", THISTLE, _LEADS[3], 36.0),
    _vehicle("RCVCAN", "Canyon Climber", "Truck", FERNBY, _LEADS[0], 35.0),
    _vehicle("RCVDRI", "Drift Fox", "Car", PUDDLE, _LEADS[1], 22.0),
    _vehicle("RCVREE", "Reef Runner", "Boat", CALDERBY, _LEADS[2], 31.0),
    _vehicle("RCVRES", "Rescue Hopper", "Helicopter", LANTERNBY, _LEADS[3], 33.0),
    _vehicle("RCVBOU", "Boulder Basher", "Truck", THISTLE, _LEADS[0], 38.0),
    _vehicle("RCVNIT", "Night Sprinter", "Car", FERNBY, _LEADS[1], 25.0),
    _vehicle("RCVWAV", "Wave Dasher", "Boat", PUDDLE, _LEADS[2], 28.0),
    _vehicle("RCVBRE", "Breeze Rotor", "Helicopter", CALDERBY, _LEADS[3], 30.0),
    _vehicle("RCVTUN", "Tundra Tracker", "Truck", LANTERNBY, _LEADS[0], 34.0),
    _vehicle("RCVPIT", "Pit Lane Pro", "Car", THISTLE, _LEADS[1], 28.0),
    _vehicle("RCVLAG", "Lagoon Skipper", "Boat", FERNBY, _LEADS[2], 26.0),
    _vehicle("RCVSUM", "Cloud Spinner", "Helicopter", PUDDLE, _LEADS[3], 37.0),
)  # fmt: skip

SPEC = TypeSpec(
    key="remote_control_vehicle",
    department="Toys",
    product_type="Remote-Control Vehicle",
    rows=ROWS,
    derivable=True,
    decoys=(
        toy_decoy(
            6,
            "kite",
            "generic",
            ROWS[3],
            62,
            "Kite Chaser Remote-Control Helicopter",
            "Named for the kites it races past at the park; it is a helicopter, not a kite.",
            color=RED,
        ),
        toy_decoy(
            4,
            "metal remote control car",
            MATERIAL_CLAIM,
            ROWS[1],
            63,
            "Metal-Look Remote-Control Car",
            "A remote-control car painted to look like brushed steel; the body is plastic.",
            color=BLACK,
        ),
    ),
)
