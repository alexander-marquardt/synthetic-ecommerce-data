"""Door stops (gen#217, a spec by gen#351): Home > Home Accessories > Door Stops.

Three styles from three brands, drawn by :func:`kit_decor.door_stop`: the kind (wedge or weighted)
changes the drawing. The material, the weight and the stop type are structured entries; a style is
a color. Every name here is invented.
"""

# ruff: noqa: E501 -- authored descriptions read better whole (prototype only).

from __future__ import annotations

import kit_decor  # noqa: F401 -- registers the shapes
from decor_rows import (
    BLACK,
    BLUE,
    COBBLE,
    GREEN,
    HARBOUR,
    RED,
    STOPS,
    THISTLE,
    WHITE,
    YELLOW,
    kg,
    row,
)
from type_registry import TypeSpec, a

ROWS = (
    row("DRSWDG", "Rubber Wedge Door Stop", HARBOUR, STOPS, "Door Stop", 3.0, "door_stop",
         "A rubber wedge that grips the floor and holds a door open.",
         (BLACK, WHITE, RED, BLUE),
         (a("material", "Material", "Rubber"), kg("weight", "Weight", 0.2),
          a("stop_type", "Stop type", "Wedge")),
         params=(("kind", "wedge"),)),
    row("DRSCST", "Cast Iron Weighted Door Stop", COBBLE, STOPS, "Door Stop", 14.0, "door_stop",
         "A heavy cast iron door stop with a carrying handle, for a door that swings shut.",
         (BLACK, GREEN, YELLOW),
         (a("material", "Material", "Cast Iron"), kg("weight", "Weight", 1.8),
          a("stop_type", "Stop type", "Weighted")),
         params=(("kind", "weighted"),)),
    row("DRSFBR", "Fabric Weighted Door Stop", THISTLE, STOPS, "Door Stop", 9.0, "door_stop",
         "A cotton door stop filled with sand, which sits behind a door and holds it open.",
         (BLUE, RED, WHITE),
         (a("material", "Material", "Cotton"), kg("weight", "Weight", 1.2),
          a("stop_type", "Stop type", "Weighted")),
         params=(("kind", "weighted"),)),
)


SPEC = TypeSpec(
    key="door_stop",
    department="Home",
    product_type="Door Stop",
    rows=ROWS,
)
