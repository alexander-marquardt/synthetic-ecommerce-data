"""Garden hose (gen#292, a spec by gen#351): a reinforced hose and an expandable one.

The Garden department held plants, bulbs, grow-your-own kits and (gen#203) machines, and no
garden hose, so the demo replay ``green garden hose`` filtered to Garden and Green and found
nothing. This is **Garden > Watering > Garden Hoses**: two styles from two brands, drawn by
:func:`kit_garden.garden_hose`. A hose's diameter and material are structured entries, and its
SKUs are a color times a length in metres, the measured axis the export states with its unit
(``export.OPTIONS``). The six main colors are offered across the type (gen#275), green on both.
Not derivable: the department grows by authored rows. Every name here is invented.
"""

from __future__ import annotations

from fractions import Fraction

import kit_garden  # noqa: F401 -- registers garden_hose
from type_registry import Option, Row, TypeSpec, a, cw

_PATH = ("Garden", "Watering", "Garden Hoses")
_W, _F = "Wrenfield", "Fenwold Nursery"

RED = cw("Red", "#c8312e")
BLUE = cw("Blue", "#3f6fb5")
GREEN = cw("Green", "#4f8a3a")
YELLOW = cw("Yellow", "#f2c230")
BLACK = cw("Black", "#2d2d33")
WHITE = cw("White", "#f4f1ea", "solid", "#9a9ca0")


def _in(key: str, name: str, v: str) -> tuple[str, str, str, str, float]:
    """A diameter in inches (``1/2``); the canonical value is in millimetres, as the core's
    ``INH`` says."""
    return (key, name, v, "INH", float(Fraction(v) * Fraction(127, 5)))


def _lengths(*pairs: tuple[float, float]) -> tuple[tuple[str, float], ...]:
    """SKU lengths in metres and the price at each: a longer hose costs more."""
    return tuple((f"{m:g}", p) for m, p in pairs)


SPEC = TypeSpec(
    key="garden_hose",
    department="Garden",
    product_type="Garden Hose",
    options=(Option("length_m", "item_length", "Item length", "MTR"),),
    rows=(
        Row("GHSREIN", "Reinforced Garden Hose", _W, "Garden", _PATH, "Garden Hose", 14.0,
            "garden_hose", "A four-layer reinforced garden hose that resists kinks and splits, "
            "with brass connectors that fit a standard outdoor tap.",
            (GREEN, BLACK, BLUE),
            (_in("diameter", "Diameter", "1/2"), a("material", "Material", "PVC")),
            _lengths((10, 14.0), (15, 19.0), (25, 29.0)), size_key="length_m",
            params=(("style", "coiled"),)),
        Row("GHSEXPN", "Expandable Garden Hose", _F, "Garden", _PATH, "Garden Hose", 22.0,
            "garden_hose", "A light garden hose that grows to three times its length under "
            "water pressure and shrinks back to store in a small space, with brass connectors.",
            (GREEN, RED, YELLOW, WHITE),
            (_in("diameter", "Diameter", "3/4"), a("material", "Material", "Latex")),
            _lengths((7.5, 22.0), (15, 32.0), (22.5, 42.0)), size_key="length_m",
            params=(("style", "expandable"),)),
    ),
)  # fmt: skip
