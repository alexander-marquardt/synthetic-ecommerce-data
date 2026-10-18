"""Water gun (gen#424): pistols, blasters and backpack water guns in the six main colors.

**Toys > Outdoor Toys > Water Toys**: four styles from three invented brands, drawn by
:func:`kit_toys_play.water_gun`. The tank capacity in millilitres, the range in metres and the
age range are structured entries; the SKUs are the colors (the six main ones and two more).
Not derivable: authored rows only.
"""

from __future__ import annotations

import kit_toys_play  # noqa: F401 -- registers water_gun
from toys_play_common import (
    BLUE,
    EIGHT,
    FERNBY,
    GREEN,
    MATERIAL_CLAIM,
    PINK,
    PIPWICK,
    PUDDLE,
    YELLOW,
    age,
    kind,
    measured,
    style,
    toy_decoy,
)
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
            measured("water_range", "Water range", metres, "MTR"),
            age(years),
        ),
        price,
        params=(("kind", shape_kind),),
    )


_ROWS = (
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
)  # fmt: skip
_BRAND = "Dolls House Row"

SPEC = TypeSpec(
    key="water_gun",
    department="Toys",
    product_type="Water Gun",
    rows=_ROWS,
    decoys=(
        toy_decoy(6, "kite", "generic", _ROWS[0], 28, "Kite Ridge Water Gun",
                  "From the Kite Ridge range, named after a windy ridge; it is a water gun and "
                  "does not fly.", color=PINK),
        toy_decoy(6, "play kitchen", "generic", _ROWS[1], 29, "Play Kitchen Quay Water Gun",
                  "From the Play Kitchen Quay range, named after a harbour wall; it is a "
                  "pistol, not a kitchen.", color=GREEN),
        toy_decoy(4, "neon water gun", MATERIAL_CLAIM, _ROWS[2], 30, "Neon-Look Water Gun",
                  "A blaster in a plain finish printed to look neon; it does not glow.",
                  color=YELLOW),
        toy_decoy(7, "dolls house", "generic", _ROWS[3], 31, "Dolls House Row Water Gun",
                  "A backpack tank gun from Dolls House Row; the name is the maker's, not a "
                  "house.", brand=_BRAND, color=BLUE),
    ),
    owners=((_BRAND, "own"),),
)  # fmt: skip
