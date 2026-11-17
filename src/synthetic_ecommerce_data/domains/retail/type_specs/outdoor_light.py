"""Outdoor light (gen#961, slice 1): Garden > Outdoor Lighting > Path Lights and Wall Lights.

A breadth type: ``derivable`` True, so the scaled build draws more lights from these by the values
their titles show (the power source and the style). The scale pools values per leaf, so a path
light never takes a wall light's style. The style draws the head, the power source a solar
panel, a cable or a battery box, and the mounting a ground stake or a wall plate
(:func:`kit_patio.outdoor_light`). Each SKU is a color in a single or a pack, and every style
offers the six main colors (gen#275). The type's text-match decoys (gen#294) are in
:mod:`garden_rows`.
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail import (
    kit_patio,  # noqa: F401 -- registers outdoor_light
)
from synthetic_ecommerce_data.domains.retail.outdoor_helpers import (
    BLACK,
    BLUE,
    GREEN,
    RED,
    WHITE,
    YELLOW,
    H,
    L,
    M,
    V,
    W,
    a,
    packs,
    row,
)
from synthetic_ecommerce_data.domains.retail.type_registry import Home, TypeSpec

_ROOT = ("Garden", "Outdoor Lighting")
PATH_LIGHTS = (*_ROOT, "Path Lights")
WALL_LIGHTS = (*_ROOT, "Wall Lights")
_PT = "Outdoor Light"
SIX = (RED, BLUE, GREEN, YELLOW, BLACK, WHITE)
_KIND = {"Ground Stake": "Path Light", "Wall": "Wall Light"}


def _light(
    code: str, power: str, style: str, mounting: str, brand: str, desc: str, sizes: tuple
) -> object:
    path = PATH_LIGHTS if mounting == "Ground Stake" else WALL_LIGHTS
    attrs = (a("power_source", "Power source", power), a("style", "Style", style),
             a("mounting", "Mounting", mounting))  # fmt: skip
    params = (
        ("style", style.lower()),
        ("power_source", power.lower()),
        ("mounting", mounting.lower()),
    )
    return row(code, f"{power} {style} {_KIND[mounting]}", brand, path, _PT, sizes[0][1], "outdoor_light",
               desc, SIX, attrs, sizes, "pack_size", params)  # fmt: skip


ROWS = (
    _light(
        "OLTSLP",
        "Solar",
        "Lantern",
        "Ground Stake",
        V,
        "A solar lantern on a ground stake, whose panel charges by day and lights a path from dusk.",
        packs((1, 14.0), (2, 25.0), (4, 45.0)),
    ),
    _light(
        "OLTPBL",
        "Plug-In",
        "Bollard",
        "Ground Stake",
        W,
        "A plug-in bollard on a ground stake, with a low-voltage cable for lighting a drive or a path.",
        packs((1, 29.0), (2, 54.0), (4, 99.0)),
    ),
    _light(
        "OLTBGL",
        "Battery-Powered",
        "Globe",
        "Ground Stake",
        H,
        "A battery globe on a ground stake, with a timer that lights a border for six hours each night.",
        packs((1, 12.0), (2, 22.0), (4, 39.0)),
    ),
    _light(
        "OLTSWL",
        "Solar",
        "Lantern",
        "Wall",
        L,
        "A solar lantern for a fence or a porch, with a motion sensor and a panel on its cap.",
        packs((1, 19.0), (2, 35.0), (4, 65.0)),
    ),
    _light(
        "OLTHWB",
        "Hardwired",
        "Bulkhead",
        "Wall",
        M,
        "A hardwired bulkhead for a porch or a side passage, sealed against rain and wired to the mains.",
        packs((1, 24.0), (2, 45.0), (4, 85.0)),
    ),
    _light(
        "OLTBWC",
        "Battery-Powered",
        "Cube",
        "Wall",
        V,
        "A battery cube for a fence or a shed door, with a motion sensor and no cable to run.",
        packs((1, 16.0), (2, 29.0), (4, 54.0)),
    ),
)

SPEC = TypeSpec(
    key="outdoor_light",
    homes=(Home("garden_rows", False),),
    department="Garden",
    product_type=_PT,
    derivable=True,
    rows=ROWS,
)
