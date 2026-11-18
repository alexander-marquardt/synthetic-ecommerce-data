"""Table Tennis Bat (gen#959, slice 2): Sports & Outdoors > Team & Racket Sports > Table Tennis Bats.

A breadth type: ``derivable`` True, so the scaled build draws more table tennis bats by the values the titles
show (the blade and the play style). The rubber is the SKU's color; the blade draws a wood grain or a carbon layer on the handle (:func:`kit_fitness_team.table_tennis_bat`). Each SKU is a color in a handle shape.
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.fitness_team_rows import TABLE_TENNIS_BATS
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


def _attrs(blade: str, play_style: str) -> tuple[tuple, ...]:
    return (_a("blade", "Blade", blade), _a("play_style", "Play style", play_style))


SPEC = TypeSpec(
    key="table_tennis_bat",
    department="Sports & Outdoors",
    product_type="Table Tennis Bat",
    derivable=True,
    options=(Option("handle_shape", "handle_shape", "Handle shape"),),
    rows=(
        _row("TTBWDC", "Control Table Tennis Bat with Wood Blade", _W, TABLE_TENNIS_BATS, "Table Tennis Bat", 19.0, "table_tennis_bat",
             "Control table tennis bat with a wood blade and soft rubbers that keep the ball on the table.",
             (RED, BLACK, BLUE, GREEN), _attrs("Wood", "Control"),
             _words(("Flared", 19.0), ("Straight", 19.0)), "handle_shape", (("blade", "wood"),)),
        _row("TTBWDA", "Allround Table Tennis Bat with Wood Blade", _H, TABLE_TENNIS_BATS, "Table Tennis Bat", 34.0, "table_tennis_bat",
             "Allround table tennis bat with a wood blade and grippy rubbers, for spin and a steady rally.",
             (RED, BLACK, WHITE, YELLOW), _attrs("Wood", "Allround"),
             _words(("Flared", 34.0), ("Straight", 34.0), ("Anatomic", 34.0)), "handle_shape", (("blade", "wood"),)),
        _row("TTBCBO", "Offensive Table Tennis Bat with Carbon Blade", _L, TABLE_TENNIS_BATS, "Table Tennis Bat", 69.0, "table_tennis_bat",
             "Offensive table tennis bat with a carbon blade and fast rubbers, for loops and smashes.",
             (BLACK, RED, BLUE, GREEN), _attrs("Carbon", "Offensive"),
             _words(("Flared", 69.0), ("Straight", 69.0), ("Anatomic", 69.0)), "handle_shape", (("blade", "carbon"),)),
        _row("TTBCBA", "Allround Table Tennis Bat with Carbon Blade", _L, TABLE_TENNIS_BATS, "Table Tennis Bat", 54.0, "table_tennis_bat",
             "Allround table tennis bat with a carbon blade and medium rubbers, quick but easy to control.",
             (RED, BLACK, YELLOW, WHITE), _attrs("Carbon", "Allround"),
             _words(("Flared", 54.0), ("Straight", 54.0)), "handle_shape", (("blade", "carbon"),)),
    ),
)  # fmt: skip
