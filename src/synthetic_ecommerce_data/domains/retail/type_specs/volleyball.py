"""Volleyball (gen#959, slice 2): Sports & Outdoors > Team & Racket Sports > Volleyballs.

A breadth type: ``derivable`` True, so the scaled build draws more volleyballs by the values the titles
show (the cover and where it is played). The panel bands are the SKU's color; a beach ball draws stitched seams (:func:`kit_fitness_team.volleyball`). Each SKU is a color in a ball size.
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.fitness_team_rows import VOLLEYBALLS
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
    _axis,
    _row,
)
from synthetic_ecommerce_data.domains.retail.type_registry import Option, TypeSpec


def _attrs(cover: str, play: str, grade: str) -> tuple[tuple, ...]:
    return (_a("cover", "Cover", cover), _a("play", "Play", play), _a("ball_grade", "Ball grade", grade))


SPEC = TypeSpec(
    key="volleyball",
    department="Sports & Outdoors",
    product_type="Volleyball",
    derivable=True,
    options=(Option("ball_size", "ball_size", "Ball size", "C62"),),
    rows=(
        _row("VLBSYI", "Training Synthetic Indoor Volleyball", _W, VOLLEYBALLS, "Volleyball", 22.0, "volleyball",
             "Synthetic indoor volleyball with glued panels and a soft touch, for school and club games.",
             (WHITE, BLUE, YELLOW, RED), _attrs("Synthetic", "Indoor", "Training"),
             _axis((4, 20.0), (5, 22.0)), "ball_size", (("play", "indoor"),)),
        _row("VLBMFI", "Official Microfiber Indoor Volleyball", _H, VOLLEYBALLS, "Volleyball", 54.0, "volleyball",
             "Microfiber indoor volleyball with a dimpled cover for a true flight, for league matches.",
             (WHITE, YELLOW, BLUE, GREEN), _attrs("Microfiber", "Indoor", "Official"),
             _axis((4, 50.0), (5, 54.0)), "ball_size", (("play", "indoor"),)),
        _row("VLBSYB", "Official Synthetic Beach Volleyball", _L, VOLLEYBALLS, "Volleyball", 19.0, "volleyball",
             "Synthetic beach volleyball with stitched panels that shrug off sand, sun and water.",
             (YELLOW, RED, GREEN, BLACK), _attrs("Synthetic", "Beach", "Official"),
             _axis((4, 17.0), (5, 19.0)), "ball_size", (("play", "beach"),)),
        _row("VLBRBB", "Recreational Rubber Beach Volleyball", _W, VOLLEYBALLS, "Volleyball", 12.0, "volleyball",
             "Rubber beach volleyball, light and bright, for the park, the pool and the sand.",
             (RED, GREEN, BLUE, WHITE), _attrs("Rubber", "Beach", "Recreational"),
             _axis((4, 11.0), (5, 12.0)), "ball_size", (("play", "beach"),)),
    ),
)  # fmt: skip
