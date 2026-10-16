"""Parasol (gen#203, a spec by gen#351): a center pole parasol, a tilting one with a base and a cantilever.

**Garden > Garden Furniture** holds three styles from three invented brands, one leaf per kind
(center pole and cantilever parasols), drawn by :func:`kit_outdoor.parasol`. The kind, whether
the canopy tilts and whether a base comes with it are structured entries; the SKUs are a color
times a canopy diameter in metres. The six main colors are offered across the type (gen#275).
Not derivable: the department grows by authored rows. The type's text-match decoys (gen#294)
are in :mod:`garden_rows`, with the other machines'.
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

import kit_outdoor  # noqa: F401 -- registers parasol
from outdoor_helpers import BLACK, BLUE, GREEN, RED, WHITE, YELLOW, H, V, W, a, axis, row
from type_registry import TypeSpec

_ROOT = ("Garden", "Garden Furniture")
_PT = "Parasol"


def _attrs(kind: str, tilt: bool, base: bool) -> tuple:
    return (a("parasol_kind", "Parasol kind", kind), a("tilt", "Tilt", "Yes" if tilt else "No"),
            a("base_included", "Base included", "Yes" if base else "No"))  # fmt: skip


SPEC = TypeSpec(
    key="parasol",
    department="Garden",
    product_type=_PT,
    rows=(
        row("PRSCTR", "Center Pole Parasol", W, (*_ROOT, "Center Pole Parasols"), _PT, 29.0, "parasol",
            "A polyester parasol on a center pole that pushes up with a slide, for a patio table "
            "with a hole in the middle.",
            (GREEN, YELLOW, WHITE), _attrs("Center Pole", False, False),
            axis((2, 29.0), (2.5, 39.0), (3, 49.0)), "canopy_m",
            (("kind", "center"), ("tilt", "no"), ("base", "no"))),
        row("PRSTLT", "Tilting Center Pole Parasol with Base", V, (*_ROOT, "Center Pole Parasols"), _PT, 79.0,
            "parasol", "A crank-lift parasol whose canopy tilts to follow the sun, sold with a "
            "filled base that stays put without being fixed to the ground.",
            (BLUE, RED, BLACK, GREEN), _attrs("Center Pole", True, True),
            axis((2.5, 79.0), (3, 99.0)), "canopy_m",
            (("kind", "center"), ("tilt", "yes"), ("base", "yes"))),
        row("PRSCNT", "Cantilever Parasol with Cross Base", H, (*_ROOT, "Cantilever Parasols"), _PT, 199.0,
            "parasol", "A side-arm parasol that shades a whole table with the pole out of the way, "
            "with a tilting canopy and a cross base for paving slabs.",
            (BLACK, WHITE, RED, BLUE), _attrs("Cantilever", True, True),
            axis((3, 199.0), (3.5, 249.0)), "canopy_m",
            (("kind", "cantilever"), ("tilt", "yes"), ("base", "yes"))),
    ),
)  # fmt: skip
