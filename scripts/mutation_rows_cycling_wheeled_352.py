"""Mutation rows for the cycling, wheeled and kayak types (gen#352), kept out of ``mutation_check.py``.

Each row plants one defect in a spec, a drawing or a decoy and names the test that must go red.
``mutation_check.py`` turns them into ``Mutation`` rows named ``cycling: ...``
(``--only "cycling:"`` re-runs them). A row is ``(name, file, old, new, test, property, root)``.
"""

# ruff: noqa: E501 -- a row's old and new text are spec lines, quoted whole.

from __future__ import annotations

from mutation_row import Row

_R = "prototypes/retail_drawings"
_T = "tests/test_retail_cycling_wheeled_352.py"

ROWS: list[tuple[str, str, str, str, str, str, str]] = [
    (
        "cycling: a two-seat kayak is drawn with one seat",
        "kit_sports.py",
        'count = 2 if str(seats) == "2" else 1',
        "count = 1",
        f'{_T} -k "param_changes_the_drawing"',
        "the seats param changes the kayak drawing",
        _R,
    ),
    (
        "cycling: a bike helmet is sold in S and M only",
        "type_specs/bike_helmet.py",
        'return _words(("S", price), ("M", price), ("L", price))',
        'return _words(("S", price), ("M", price))',
        f'{_T} -k "sold_in_the_sizes"',
        "a bike helmet is sold in S, M and L",
        _R,
    ),
    (
        "cycling: no skateboard is yellow",
        "type_specs/skateboard.py",
        "(YELLOW, GREEN, BLUE, BLACK)",
        "(GREEN, GREEN, BLUE, BLACK)",
        f'{_T} -k "six_main_colors"',
        "every type offers the six main colors across its styles",
        _R,
    ),
    (
        "cycling: a kids bike is sold by a size that is not its wheel",
        "type_specs/bicycle.py",
        '"wheel_size_in", (("style", "kids"),)',
        '"size", (("style", "kids"),)',
        f'{_T} -k "sold_in_the_sizes"',
        "a kids bike is sold by wheel size in inches",
        _R,
    ),
    (
        "cycling: a kayak decoy misleads another type",
        "feature_decoys/cycling_wheeled.py",
        '"Green", "kayak", "kayak", True, "Kayak")',
        '"Green", "kayak", "kayak", True, "Kayak Paddle")',
        f'{_T} -k "two_class_8_decoys and Kayak"',
        "every type carries two class 8 decoys of other departments",
        _R,
    ),
]

# Found by ``mutation_row.discover``: the prefix of the rows' names and the rows in one shape.
PREFIX = "cycling"


def rows() -> list[Row]:
    return [Row(*r) for r in ROWS]
