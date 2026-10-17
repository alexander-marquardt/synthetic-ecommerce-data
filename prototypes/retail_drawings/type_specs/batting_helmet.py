"""Batting Helmet (gen#368, moved to a spec by gen#351): the second Sports & Outdoors increment.

The styles are templates only (``derivable`` False): the department grows by authored rows.
:mod:`kit_sports` draws them.
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from sports_helpers import _BASEBALL, _H, _NEUTRAL, _PRIMARY, _W, _a, _axis, _row
from type_registry import TypeSpec

SPEC = TypeSpec(
    key="batting_helmet",
    department="Sports & Outdoors",
    product_type="Batting Helmet",
    rows=(
        _row("BHLSNG", "Batting Helmet with Single Ear Flap", _H, (*_BASEBALL, "Batting Helmets"), "Batting Helmet", 29.0,
             "batting_helmet", "A hard-shell batting helmet with a flap over the ear facing the pitcher and a vented crown.",
             _NEUTRAL, (_a("material", "Material", "ABS Shell"), _a("ear_flaps", "Ear flaps", "Single")),
             _axis((54, 29.0), (57, 29.0), (60, 31.0)), "head_cm", (("flaps", "single"),)),
        _row("BHLDBL", "Batting Helmet with Double Ear Flaps", _W, (*_BASEBALL, "Batting Helmets"), "Batting Helmet", 34.0,
             "batting_helmet", "A batting helmet with flaps over both ears and a foam liner, for youth leagues that require them.",
             _PRIMARY, (_a("material", "Material", "ABS Shell"), _a("ear_flaps", "Ear flaps", "Double")),
             _axis((52, 34.0), (55, 34.0), (58, 36.0)), "head_cm", (("flaps", "double"),)),
    ),
)  # fmt: skip
