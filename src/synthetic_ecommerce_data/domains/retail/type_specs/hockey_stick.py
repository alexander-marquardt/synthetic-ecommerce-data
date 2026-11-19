"""Hockey Stick (gen#959, slice 2): Sports & Outdoors > Team & Racket Sports > Hockey Sticks.

A breadth type: ``derivable`` True, so the scaled build draws more hockey sticks by the values the titles
show (the material and the game). The shaft is the SKU's color; the game draws an ice blade with tape or a wide street blade (:func:`kit_fitness_team.hockey_stick`). Each SKU is a color in a hand.
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.fitness_team_rows import HOCKEY_STICKS
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
from synthetic_ecommerce_data.domains.retail.type_registry import Option, TypeSpec


def _attrs(material: str, hockey_type: str, curve: str) -> tuple[tuple, ...]:
    return (_a("material", "Material", material), _a("hockey_type", "Game", hockey_type), _a("blade_curve", "Curve", curve))


SPEC = TypeSpec(
    key="hockey_stick",
    department="Sports & Outdoors",
    product_type="Hockey Stick",
    derivable=True,
    options=(Option("handedness", "handedness", "Handedness"),),
    rows=(
        _row("HKSCPI", "Composite Ice Hockey Stick with Mid Curve", _W, HOCKEY_STICKS, "Hockey Stick", 89.0, "hockey_stick",
             "Composite ice hockey stick with a mid kick point and a curved blade, for quick wrist shots.",
             (BLACK, WHITE, RED, BLUE), _attrs("Composite", "Ice", "Mid Curve"),
             _words(("Left Handed", 89.0), ("Right Handed", 89.0)), "handedness", (("hockey_type", "ice"),)),
        _row("HKSWDI", "Wood Ice Hockey Stick with Heel Curve", _H, HOCKEY_STICKS, "Hockey Stick", 34.0, "hockey_stick",
             "Wood ice hockey stick with a laminated shaft and a curved blade, a sturdy first stick.",
             (BLACK, YELLOW, GREEN, WHITE), _attrs("Wood", "Ice", "Heel Curve"),
             _words(("Left Handed", 34.0), ("Right Handed", 34.0)), "handedness", (("hockey_type", "ice"),)),
        _row("HKSCPS", "Composite Street Hockey Stick with Toe Curve", _L, HOCKEY_STICKS, "Hockey Stick", 39.0, "hockey_stick",
             "Composite street hockey stick with a wide moulded blade that stands up to asphalt.",
             (RED, BLUE, GREEN, YELLOW), _attrs("Composite", "Street", "Toe Curve"),
             _words(("Left Handed", 39.0), ("Right Handed", 39.0)), "handedness", (("hockey_type", "street"),)),
        _row("HKSFGS", "Fiberglass Street Hockey Stick with Mid Curve", _W, HOCKEY_STICKS, "Hockey Stick", 29.0, "hockey_stick",
             "Fiberglass street hockey stick with a wide moulded blade, for driveway and park games.",
             (BLACK, BLUE, YELLOW, RED), _attrs("Fiberglass", "Street", "Mid Curve"),
             _words(("Left Handed", 29.0), ("Right Handed", 29.0)), "handedness", (("hockey_type", "street"),)),
    ),
)  # fmt: skip
