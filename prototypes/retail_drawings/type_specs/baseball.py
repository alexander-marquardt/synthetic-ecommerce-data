"""Baseball (gen#368, moved to a spec by gen#351): the second Sports & Outdoors increment.

The styles are templates only (``derivable`` False): the department grows by authored rows.
:mod:`kit_sports` draws them.
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from sports_helpers import _BASEBALL, _L, _NEUTRAL, _PRIMARY, _W, _a, _row
from type_registry import TypeSpec

SPEC = TypeSpec(
    key="baseball",
    department="Sports & Outdoors",
    product_type="Baseball",
    rows=(
        _row("BBLLTH", "Leather Match Baseball", _W, (*_BASEBALL, "Baseballs"), "Baseball", 6.0, "baseball",
             "A cork-centered ball in a stitched leather cover, for match play and hard batting practice.",
             _NEUTRAL, (_a("cover", "Cover", "Leather"), _a("level", "Level", "Match"), _a("sold_as", "Sold as", "Single")),
             (), "size", (("cover", "leather"),)),
        _row("BBLPRC", "Soft Synthetic Practice Baseballs", _L, (*_BASEBALL, "Baseballs"), "Baseball", 14.0, "baseball",
             "A pack of six soft-core practice balls with a synthetic cover that is kind to hands and windows.",
             _PRIMARY, (_a("cover", "Cover", "Synthetic"), _a("level", "Level", "Practice"), _a("sold_as", "Sold as", "Pack of 6")),
             (), "size", (("cover", "synthetic"),)),
    ),
)  # fmt: skip
