"""Resistance Band (gen#368, moved to a spec by gen#351): the second Sports & Outdoors increment.

The styles are templates only (``derivable`` False): the department grows by authored rows.
:mod:`kit_sports` draws them.
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from sports_helpers import _FIT, _L, _NEUTRAL, _PRIMARY, _W, _a, _row, _words
from type_registry import Option, TypeSpec

SPEC = TypeSpec(
    key="resistance_band",
    department="Sports & Outdoors",
    product_type="Resistance Band",
    options=(Option("resistance", "resistance_level", "Resistance level"),),
    rows=(
        _row("RSBLOP", "Fabric Loop Resistance Band", _L, (*_FIT, "Resistance Bands"), "Resistance Band", 8.0,
             "resistance_band", "A wide woven loop band that stays put on the thighs for glute and hip work.",
             _PRIMARY, (_a("band_type", "Band type", "Loop"), _a("material", "Material", "Cotton blend")),
             _words(("Light", 8.0), ("Medium", 9.0), ("Heavy", 10.0)), "resistance", (("form", "loop"),)),
        _row("RSBTUB", "Tube Resistance Band with Handles", _W, (*_FIT, "Resistance Bands"), "Resistance Band", 12.0,
             "resistance_band", "A latex tube band with a handle at each end for rows, presses and curls anywhere.",
             _NEUTRAL, (_a("band_type", "Band type", "Tube"), _a("material", "Material", "Latex")),
             _words(("Light", 12.0), ("Medium", 14.0), ("Heavy", 16.0)), "resistance", (("form", "tube"),)),
    ),
)  # fmt: skip
