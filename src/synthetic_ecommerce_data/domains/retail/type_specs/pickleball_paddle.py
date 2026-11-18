"""Pickleball Paddle (gen#959, slice 2): Sports & Outdoors > Team & Racket Sports > Pickleball Paddles.

A breadth type: ``derivable`` True, so the scaled build draws more pickleball paddles by the values the titles
show (the weight class and the face). The face is the SKU's color; the face draws a weave, a sheen or a wood grain (:func:`kit_fitness_team.pickleball_paddle`). Each SKU is a color in a grip size.
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.fitness_team_rows import PICKLEBALL_PADDLES
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


def _attrs(paddle_weight: str, face: str, shape: str) -> tuple[tuple, ...]:
    return (_a("paddle_weight", "Weight class", paddle_weight), _a("face", "Face", face), _a("paddle_shape", "Shape", shape))


SPEC = TypeSpec(
    key="pickleball_paddle",
    department="Sports & Outdoors",
    product_type="Pickleball Paddle",
    derivable=True,
    options=(Option("grip", "grip_size", "Grip size"),),
    rows=(
        _row("PKPLGR", "Lightweight Graphite Elongated Pickleball Paddle", _W, PICKLEBALL_PADDLES, "Pickleball Paddle", 59.0, "pickleball_paddle",
             "Lightweight graphite pickleball paddle with a polymer honeycomb core, quick at the kitchen line.",
             (BLACK, BLUE, RED, WHITE), _attrs("Lightweight", "Graphite", "Elongated"),
             _words(("Small", 59.0), ("Standard", 59.0), ("Large", 59.0)), "grip", (("face", "graphite"),)),
        _row("PKPMFG", "Midweight Fiberglass Widebody Pickleball Paddle", _H, PICKLEBALL_PADDLES, "Pickleball Paddle", 45.0, "pickleball_paddle",
             "Midweight fiberglass pickleball paddle with a polymer honeycomb core and a lively feel off the face.",
             (YELLOW, GREEN, BLUE, BLACK), _attrs("Midweight", "Fiberglass", "Widebody"),
             _words(("Small", 45.0), ("Standard", 45.0), ("Large", 45.0)), "grip", (("face", "fiberglass"),)),
        _row("PKPMCF", "Midweight Carbon Fiber Elongated Pickleball Paddle", _L, PICKLEBALL_PADDLES, "Pickleball Paddle", 99.0, "pickleball_paddle",
             "Midweight carbon fiber pickleball paddle with a textured face for spin and a cushioned grip.",
             (BLACK, RED, WHITE, GREEN), _attrs("Midweight", "Carbon Fiber", "Elongated"),
             _words(("Standard", 99.0), ("Large", 99.0)), "grip", (("face", "carbon fiber"),)),
        _row("PKPHWD", "Heavyweight Wood Widebody Pickleball Paddle", _L, PICKLEBALL_PADDLES, "Pickleball Paddle", 24.0, "pickleball_paddle",
             "Heavyweight wood pickleball paddle, a sturdy paddle for schools, clubs and a first game.",
             (RED, YELLOW, BLUE, GREEN), _attrs("Heavyweight", "Wood", "Widebody"),
             _words(("Small", 24.0), ("Standard", 24.0)), "grip", (("face", "wood"),)),
    ),
)  # fmt: skip
