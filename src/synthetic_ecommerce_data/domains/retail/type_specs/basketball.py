"""Basketball (gen#959, slice 2): Sports & Outdoors > Team & Racket Sports > Basketballs.

A breadth type: ``derivable`` True, so the scaled build draws more basketballs by the values the titles
show (the cover and the court). The cover is the SKU's color; the cover draws deep, medium or thin channels (:func:`kit_fitness_team.basketball`). Each SKU is a color in a ball size.
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.fitness_team_rows import BASKETBALLS
from synthetic_ecommerce_data.domains.retail.sports_helpers import (
    _H,
    _L,
    _W,
    BLACK,
    BLUE,
    GREEN,
    ORANGE,
    RED,
    WHITE,
    YELLOW,
    _a,
    _axis,
    _row,
)
from synthetic_ecommerce_data.domains.retail.type_registry import Option, TypeSpec


def _attrs(cover: str, court: str, grade: str) -> tuple[tuple, ...]:
    return (_a("cover", "Cover", cover), _a("court", "Court", court), _a("ball_grade", "Grade", grade))


SPEC = TypeSpec(
    key="basketball",
    department="Sports & Outdoors",
    product_type="Basketball",
    derivable=True,
    options=(Option("ball_size", "ball_size", "Ball size", "C62"),),
    rows=(
        _row("BKBRBO", "Recreational Rubber Outdoor Basketball", _W, BASKETBALLS, "Basketball", 14.0, "basketball",
             "Rubber outdoor basketball with a pebbled grip and eight channels, for game play and practice.",
             (ORANGE, RED, YELLOW, BLUE, GREEN), _attrs("Rubber", "Outdoor", "Recreational"),
             _axis((5, 12.0), (6, 13.0), (7, 14.0)), "ball_size", (("cover", "rubber"),)),
        _row("BKBCPI", "Official Composite Indoor Basketball", _H, BASKETBALLS, "Basketball", 32.0, "basketball",
             "Composite indoor basketball with a soft, tacky cover that holds its grip through a whole game.",
             (ORANGE, BLACK, WHITE, RED), _attrs("Composite", "Indoor", "Official"),
             _axis((6, 30.0), (7, 32.0)), "ball_size", (("cover", "composite"),)),
        _row("BKBFGI", "Official Full-Grain Leather Indoor Basketball", _L, BASKETBALLS, "Basketball", 79.0, "basketball",
             "Full-grain leather indoor basketball that breaks in with play, for league games on a wooden court.",
             (ORANGE, BLACK, WHITE, GREEN), _attrs("Full-Grain Leather", "Indoor", "Official"),
             _axis((6, 75.0), (7, 79.0)), "ball_size", (("cover", "full-grain leather"),)),
        _row("BKBCPO", "Training Composite Outdoor Basketball", _L, BASKETBALLS, "Basketball", 26.0, "basketball",
             "Composite outdoor basketball with a deep pebble and a tough cover for asphalt and concrete.",
             (ORANGE, YELLOW, GREEN, BLACK), _attrs("Composite", "Outdoor", "Training"),
             _axis((5, 22.0), (6, 24.0), (7, 26.0)), "ball_size", (("cover", "composite"),)),
    ),
)  # fmt: skip
