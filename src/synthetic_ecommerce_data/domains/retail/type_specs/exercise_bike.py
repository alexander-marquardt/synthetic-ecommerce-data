"""Exercise Bike (gen#959, slice 2): Sports & Outdoors > Yoga & Fitness > Exercise Bikes.

A breadth type: ``derivable`` True, so the scaled build draws more exercise bikes by the values the titles
show (the resistance and the style). The frame is the SKU's color; the style draws an upright bike, a recumbent one with a backrest or a folding X frame (:func:`kit_fitness_team.exercise_bike`). Each SKU is a color in a maximum user weight.
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.fitness_team_rows import EXERCISE_BIKES
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


def _attrs(resistance_type: str, bike_style: str) -> tuple[tuple, ...]:
    return (_a("resistance_type", "Resistance", resistance_type), _a("bike_style", "Style", bike_style))


SPEC = TypeSpec(
    key="exercise_bike",
    department="Sports & Outdoors",
    product_type="Exercise Bike",
    derivable=True,
    options=(Option("max_load_kg", "max_load_kg", "Maximum load", "KGM"),),
    rows=(
        _row("EXBMAG", "Magnetic Upright Exercise Bike", _W, EXERCISE_BIKES, "Exercise Bike", 249.0, "exercise_bike",
             "Magnetic upright exercise bike with eight resistance levels, a heavy flywheel and a padded saddle that slides and rises.",
             (BLACK, WHITE, RED, BLUE), _attrs("Magnetic", "Upright"),
             _axis((100, 249.0), (120, 279.0), (136, 319.0)), "max_load_kg", (("bike_style", "upright"),)),
        _row("EXBREC", "Magnetic Recumbent Exercise Bike", _H, EXERCISE_BIKES, "Exercise Bike", 329.0, "exercise_bike",
             "Magnetic recumbent exercise bike with a step-through frame, a backrest and a wide seat for long, easy rides.",
             (WHITE, BLACK, GREEN, YELLOW), _attrs("Magnetic", "Recumbent"),
             _axis((100, 329.0), (120, 359.0), (136, 399.0)), "max_load_kg", (("bike_style", "recumbent"),)),
        _row("EXBFLD", "Friction Folding Exercise Bike", _L, EXERCISE_BIKES, "Exercise Bike", 129.0, "exercise_bike",
             "Friction folding exercise bike that folds flat to store beside a wall, with a tension dial and a small display.",
             (RED, BLUE, BLACK, WHITE), _attrs("Friction", "Folding"),
             _axis((100, 129.0), (110, 139.0), (120, 149.0)), "max_load_kg", (("bike_style", "folding"),)),
        _row("EXBAIR", "Air Upright Exercise Bike", _W, EXERCISE_BIKES, "Exercise Bike", 399.0, "exercise_bike",
             "Air upright exercise bike whose resistance rises the harder you pedal, with moving handles for a full-body ride.",
             (YELLOW, BLACK, GREEN, RED), _attrs("Air", "Upright"),
             _axis((120, 399.0), (136, 439.0), (150, 479.0)), "max_load_kg", (("bike_style", "upright"),)),
    ),
)  # fmt: skip
