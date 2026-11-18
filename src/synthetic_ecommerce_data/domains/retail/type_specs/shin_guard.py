"""Shin Guard (gen#959, slice 2): Sports & Outdoors > Team & Racket Sports > Shin Guards.

A breadth type: ``derivable`` True, so the scaled build draws more shin guards by the values the titles
show (the shell and the guard type). The shell is the SKU's color; the guard type adds ankle cups or a sleeve (:func:`kit_fitness_team.shin_guard`). Each SKU is a color in a size.
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.fitness_team_rows import SHIN_GUARDS
from synthetic_ecommerce_data.domains.retail.sports_helpers import (
    _H,
    _L,
    _W,
    BLACK,
    BLUE,
    GREEN,
    RED,
    WHITE,
    YELLOW,
    _a,
    _row,
    _words,
)
from synthetic_ecommerce_data.domains.retail.type_registry import TypeSpec


def _attrs(shell: str, guard_type: str, profile: str) -> tuple[tuple, ...]:
    return (_a("shell", "Shell", shell), _a("guard_type", "Guard type", guard_type), _a("guard_profile", "Profile", profile))


SPEC = TypeSpec(
    key="shin_guard",
    department="Sports & Outdoors",
    product_type="Shin Guard",
    derivable=True,
    rows=(
        _row("SHGPLS", "Low-Profile Plastic Slip-In Shin Guards", _W, SHIN_GUARDS, "Shin Guard", 9.0, "shin_guard",
             "Plastic slip-in shin guards with a foam backing, worn under the sock for training and matches.",
             (BLACK, WHITE, RED, BLUE), _attrs("Plastic", "Slip-In", "Low-Profile"),
             _words(("XS", 9.0), ("S", 9.0), ("M", 9.0), ("L", 9.0)), "size", (("guard_type", "slip-in"),)),
        _row("SHGPLA", "Reinforced Plastic Ankle Shin Guards", _H, SHIN_GUARDS, "Shin Guard", 14.0, "shin_guard",
             "Plastic ankle shin guards with padded ankle cups and a strap under the foot, for young players.",
             (BLUE, BLACK, YELLOW, GREEN), _attrs("Plastic", "Ankle", "Reinforced"),
             _words(("XS", 14.0), ("S", 14.0), ("M", 14.0), ("L", 14.0)), "size", (("guard_type", "ankle"),)),
        _row("SHGFBS", "Low-Profile Fiberglass Sleeve Shin Guards", _L, SHIN_GUARDS, "Shin Guard", 29.0, "shin_guard",
             "Fiberglass sleeve shin guards held in a stretch sleeve, light and firm for match play.",
             (WHITE, BLACK, GREEN, RED), _attrs("Fiberglass", "Sleeve", "Low-Profile"),
             _words(("S", 29.0), ("M", 29.0), ("L", 29.0), ("XL", 29.0)), "size", (("guard_type", "sleeve"),)),
        _row("SHGCBS", "Reinforced Carbon Slip-In Shin Guards", _L, SHIN_GUARDS, "Shin Guard", 45.0, "shin_guard",
             "Carbon slip-in shin guards, thin and light, with a shaped foam back that sits close to the leg.",
             (BLACK, YELLOW, RED, WHITE), _attrs("Carbon", "Slip-In", "Reinforced"),
             _words(("S", 45.0), ("M", 45.0), ("L", 45.0), ("XL", 45.0)), "size", (("guard_type", "slip-in"),)),
    ),
)  # fmt: skip
