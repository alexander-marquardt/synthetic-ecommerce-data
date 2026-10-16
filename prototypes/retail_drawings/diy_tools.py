"""Shared pieces of the DIY drill family's type specs (gen#191): colors, brands, attributes, decoys.

The nine types (Drill Driver, Combi Drill, Hammer Drill, Corded Drill, Impact Driver, SDS Hammer
Drill, Drill Bit Set, Tool Kit, Step Ladder) each live in ``type_specs/<key>.py`` and draw their
own shape (:mod:`kit_drills`). Every product type names its tool: none is a plain "Drill", so the
retail types never collide with the industrial drill bits and bushings on a merged index.

Colors: a type's styles pair up as (red, black), (blue, white) and (green, yellow), so a type
offers the six main colors across its styles (gen#275) with no exception.

Decoys (gen#294): each type carries three; see :func:`decoys` and :mod:`diy_decoy_rows`. All brand
names are invented; only text, no logos.
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from dataclasses import replace

import kit_drills  # noqa: F401 -- registers the shapes
from breadth_rows import Row
from type_registry import Decoy, a, cw

HOME = "Home"
DIY = (HOME, "DIY & Tools")
DRILLS = (*DIY, "Drills")
TOOL_SETS = (*DIY, "Tool Sets")

RED = cw("Red", "#c8312e")
BLUE = cw("Blue", "#3f6fb5")
GREEN = cw("Green", "#4f8a3a")
YELLOW = cw("Yellow", "#f2c230")
BLACK = cw("Black", "#2d2d33")
WHITE = cw("White", "#f4f1ea", "solid", "#9a9ca0")
#: A type's three color pairs: each style takes one, the first color leading.
PAIRS = ((RED, BLACK), (BLUE, WHITE), (GREEN, YELLOW))

CAL, TOR, BRI, HAR, STO = (
    "Calderby & Lune",
    "Torvane Tools",
    "Brindlecote",
    "Harkwell Power",
    "Stonemarsh",
)
#: Brands this family states: invented houses, text only.
OWNERS = ((TOR, "third_party"), (BRI, "own"), (HAR, "third_party"), (STO, "third_party"))


def volts(v: int) -> tuple[str, str, str, str, float]:
    """A battery voltage: the unit is in the key (``_v``), the canonical value in volts."""
    return ("voltage_v", "Voltage", str(v), "VLT", float(v))


def watts(w: int) -> tuple[str, str, str]:
    """A mains power: a plain number whose name carries its unit, as the appliances do."""
    return ("wattage", "Wattage (W)", str(w))


def cordless(v: int, motor: str = "Brushed", **extra: str) -> tuple:
    return (a("power_source", "Power source", "Cordless"), volts(v), a("battery_type", "Battery type", "Lithium-Ion"), a("motor_type", "Motor type", motor),
            *(a(k, k.replace("_", " ").capitalize(), v2) for k, v2 in extra.items()))  # fmt: skip


def corded(w: int, motor: str = "Brushed", **extra: str) -> tuple:
    return (a("power_source", "Power source", "Corded"), watts(w), a("motor_type", "Motor type", motor),
            *(a(k, k.replace("_", " ").capitalize(), v2) for k, v2 in extra.items()))  # fmt: skip


def impact(torque: int, kit: str) -> tuple:
    """An impact driver's torque (Nm), its quarter-inch hex bit holder and its battery kit."""
    return (
        a("bit_holder", "Bit holder", "1/4 in hex"),
        a("torque_nm", "Torque (Nm)", str(torque)),
        a("battery_kit", "Battery kit", kit),
    )


def sds(joules: float) -> tuple:
    """An SDS hammer drill's chuck, impact energy (J) and modes."""
    return (
        a("chuck_type", "Chuck type", "SDS-plus"),
        a("impact_energy_j", "Impact energy (J)", f"{joules:g}"),
        a("modes", "Modes", "Drill, hammer and chisel"),
    )


def styles(spec: tuple, ptype: str, shape: str, path: tuple[str, ...]) -> tuple[Row, ...]:
    """Rows from ``(code, title, brand, price, description, attrs, params)`` tuples: the n-th
    style takes the n-th color pair of :data:`PAIRS`."""
    return tuple(
        Row(
            code,
            title,
            brand,
            HOME,
            path,
            ptype,
            price,
            shape,
            desc,
            PAIRS[i % 3],
            attrs,
            params=params,
        )
        for i, (code, title, brand, price, desc, attrs, params) in enumerate(spec)
    )


# --------------------------------------------------------------------------
# Decoys
# --------------------------------------------------------------------------


def decoys(base: Row, words: str, absent: tuple[str, str, str]) -> tuple[Decoy, ...]:
    """The type's absent-feature decoy (class 4): its own row under a title naming a feature it
    lacks. ``absent`` is ``(code, title, query)``. The type's cross-department decoys are in
    :mod:`diy_decoy_rows`."""
    code, title, query = absent
    real = replace(
        base,
        code=code,
        title=title,
        description=f"A {words} sold on its own, with the fittings the title names.",
        colors=base.colors[:1],
    )
    return (Decoy(4, query, "category", real),)
