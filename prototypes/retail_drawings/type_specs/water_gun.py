"""Water gun (gen#424): pistols, blasters and backpack water guns in the six main colors.

**Toys > Outdoor Toys > Water Toys**: four styles from three invented brands, drawn by
:func:`kit_toys_play.water_gun`. The tank capacity in millilitres, the range in metres and the
age range are structured entries; the SKUs are the colors (the six main ones and two more).
Not derivable: authored rows only.
"""

from __future__ import annotations

import kit_toys_play  # noqa: F401 -- registers water_gun
from toys_play_common import EIGHT, FERNBY, PIPWICK, PUDDLE, age, kind, measured, style
from type_registry import Row, TypeSpec

_PATH = ("Toys", "Outdoor Toys", "Water Toys")


def _gun(code: str, title: str, brand: str, shape_kind: str, ml: float, metres: float,
         years: str, desc: str, price: float) -> Row:  # fmt: skip
    return style(
        code,
        title,
        brand,
        _PATH,
        "Water Gun",
        "water_gun",
        desc,
        EIGHT,
        (
            kind(f"{shape_kind.title()} Water Gun"),
            measured("tank_capacity", "Tank capacity", ml, "MLT"),
            measured("water_range", "Range", metres, "MTR"),
            age(years),
        ),
        price,
        params=(("kind", shape_kind),),
    )


SPEC = TypeSpec(
    key="water_gun",
    department="Toys",
    product_type="Water Gun",
    rows=(
        _gun("WGNPIS", "Water Gun Pistol", PIPWICK, "pistol", 250, 6, "4+ years",
             "A small squirt pistol with a 250 ml tank and a 6 m range. For ages 4 and up.", 4.0),
        _gun("WGNPIM", "Mini Water Gun, 8 m Range", PUDDLE, "pistol", 400, 8, "5+ years",
             "A pistol with a 400 ml tank that shoots a 8 m range stream. For ages 5 and up.",
             6.0),
        _gun("WGNBLA", "Pump Action Water Gun Blaster", FERNBY, "blaster", 800, 10, "6+ years",
             "Pump the grip and fire a stream with a 10 m range from an 800 ml tank. For ages "
             "6 and up.", 12.0),
        _gun("WGNBPK", "Backpack Water Gun, Long Range", PIPWICK, "backpack", 2000, 12, "7+ years",
             "A 2 litre backpack tank and a nozzle on a hose for a 12 m range. For ages 7 "
             "and up.", 18.0),
    ),
)  # fmt: skip
