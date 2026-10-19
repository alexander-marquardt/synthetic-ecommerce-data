"""Mutation rows for the retail department floor (gen#234), kept out of ``mutation_check.py``.

Each row plants one defect in ``breadth_rows.DEPARTMENT_FLOOR`` and names the test that must go
red. ``mutation_check.py`` turns them into ``Mutation`` rows named ``department floor: ...``
(``--only "department floor:"`` re-runs them). A row is
``(name, file, old, new, test, property, root)``.
"""

from __future__ import annotations

from mutation_row import Row

ROWS: list[tuple[str, str, str, str, str, str, str]] = [
    (
        "the floor is switched off",
        "breadth_rows.py",
        "DEPARTMENT_FLOOR = 150",
        "DEPARTMENT_FLOOR = 0",
        "tests/test_retail_scale.py -k test_the_department_floor_is_not_lowered",
        "the department floor is not lowered below the pinned minimum",
        "prototypes/retail_drawings",
    ),
    (
        "the floor is lowered by one",
        "breadth_rows.py",
        "DEPARTMENT_FLOOR = 150",
        "DEPARTMENT_FLOOR = 149",
        "tests/test_retail_scale.py -k test_the_department_floor_is_not_lowered",
        "the department floor is not lowered below the pinned minimum",
        "prototypes/retail_drawings",
    ),
]

# Found by ``mutation_row.discover``: the prefix of the rows' names and the rows in one shape.
PREFIX = "department floor"


def rows() -> list[Row]:
    return [Row(*r) for r in ROWS]
