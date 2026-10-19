"""Mutation rows for the retail lighting drawings (gen#238), kept out of ``mutation_check.py``.

Each row plants one defect in ``kit_lighting.py`` and names the test that must go red.
``mutation_check.py`` turns them into ``Mutation`` rows named ``lighting drawings: ...``
(``--only "lighting drawings:"`` re-runs them). A row is
``(name, file, old, new, test, property)``; every row's root is ``prototypes/retail_drawings``.
"""

from __future__ import annotations

from mutation_row import Row

ROWS: list[tuple[str, str, str, str, str, str]] = [
    (
        "the task lamp's pole is lowered while its joints stay put",
        "kit_lighting.py",
        '_rod("M150,350 L150,110 L232,64", metal, 7)',
        '_rod("M150,350 L150,176 L232,118", metal, 7)',
        "tests/test_retail_lighting_197.py -k reaches_as_high_as_an_arc_one",
        "a task floor lamp's pole reaches as high as its head joint, above y 100",
    ),
    (
        "the task lamp's pole runs past its head joint",
        "kit_lighting.py",
        '_rod("M150,350 L150,110 L232,64", metal, 7)',
        '_rod("M150,350 L150,110 L232,50", metal, 7)',
        "tests/test_retail_lighting_197.py -k pole_ends_at_its_head_joint",
        "a task floor lamp's pole ends at its head joint",
    ),
]

# Found by ``mutation_row.discover``: the prefix of the rows' names and the rows in one shape.
PREFIX = "lighting drawings"


def rows() -> list[Row]:
    return [Row(*r, "prototypes/retail_drawings") for r in ROWS]
