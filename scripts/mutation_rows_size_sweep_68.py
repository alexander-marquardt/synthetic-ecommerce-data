"""Mutation rows for the thread-size sweep over the lock nut (gen#68).

Kept out of ``mutation_check.py``.
Each row drops a row from a lock nut table, or stops the sweep reading ``thread_size``, and names
the test that must go red. ``mutation_check.py`` turns them into ``Mutation`` rows named
``size sweep: ...`` (``--only "size sweep:"`` re-runs them). A row is
``(name, file, old, new, property, root)``; every row runs the same sweep test.
"""

from __future__ import annotations

from mutation_row import GENERATOR, Row

LOCK_NUT = "domains/industrial/product_types/fasteners/lock_nuts_nylon_insert.py"
SWEEP = 'tests/test_catalog_coverage.py -k "every_size and generated"'
PROPERTY = "a lock nut size in a table reaches a document"

ROWS: list[tuple[str, str, str, str, str]] = [
    (
        "drop the ISO 7040 M24 row from the lock nut table",
        LOCK_NUT,
        '("M24x3", 36.0, 27.1), ("M30x3.5", 46.0, 32.6), ("M36x4", 55.0, 38.9),',
        '("M30x3.5", 46.0, 32.6), ("M36x4", 55.0, 38.9),',
        GENERATOR,
    ),
    (
        "drop the ISO 10512 M10x1 fine row from the lock nut table",
        LOCK_NUT,
        '(("M10x1", 16.0, 11.9), ("M12x1.25", 18.0, 14.9)),',
        '(("M12x1.25", 18.0, 14.9),),',
        GENERATOR,
    ),
    (
        "drop the 1-12 row from the lock nut's unified threads (_UNF) selection",
        LOCK_NUT,
        '["#10", "1/4", "5/16", "3/8", "7/16", "1/2", "9/16", "5/8", "3/4", "7/8", "1"]'
        "\n    )\n)\n#: The thin",
        '["#10", "1/4", "5/16", "3/8", "7/16", "1/2", "9/16", "5/8", "3/4", "7/8"]'
        "\n    )\n)\n#: The thin",
        GENERATOR,
    ),
    (
        "stop reading thread_size, so the lock nut is unswept again",
        "tests/test_catalog_coverage.py",
        '        values += facets.get("thread_size", [])',
        "        pass",
        ".",
    ),
]

# Found by ``mutation_row.discover``: the prefix of the rows' names and the rows in one shape.
PREFIX = "size sweep"


def rows() -> list[Row]:
    return [Row(n, f, o, w, SWEEP, PROPERTY, root, "A") for n, f, o, w, root in ROWS]
