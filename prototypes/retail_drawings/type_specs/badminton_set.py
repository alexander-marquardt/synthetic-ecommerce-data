"""Badminton Set (gen#368, moved to a spec by gen#351): the second Sports & Outdoors increment.

The styles are templates only (``derivable`` False): the department grows by authored rows.
:mod:`kit_sports` draws them.
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from sports_helpers import _L, _NEUTRAL, _PRIMARY, _TEAM, _W, _a, _axis, _row
from type_registry import TypeSpec

SPEC = TypeSpec(
    key="badminton_set",
    department="Sports & Outdoors",
    product_type="Badminton Set",
    rows=(
        _row("BDMTWO", "Badminton Set for Two Players", _L, (*_TEAM, "Badminton Sets"), "Badminton Set", 18.0,
             "badminton_set", "Two steel-framed rackets and shuttlecocks in a carry bag, for the garden or the beach.",
             _PRIMARY, (_a("material", "Material", "Steel"), _a("net_included", "Net included", "No")),
             _axis((2, 18.0)), "players", (("players", "2"),)),
        _row("BDMFOU", "Badminton Set with Net for Four Players", _W, (*_TEAM, "Badminton Sets"), "Badminton Set", 42.0,
             "badminton_set", "Four aluminum rackets, a portable net with posts and a tube of shuttlecocks.",
             _NEUTRAL, (_a("material", "Material", "Aluminum"), _a("net_included", "Net included", "Yes")),
             _axis((4, 42.0)), "players", (("players", "4"),)),
    ),
)  # fmt: skip
