"""Mutation rows for the wheel that publishes no pack (#357), kept out of ``mutation_check.py``.

Each row plants one defect in how the depressed-center wheel drops its pack and names the test that
must go red. ``mutation_check.py`` turns them into ``Mutation`` rows named ``wheel pack: ...``
(``--only "wheel pack:"`` re-runs them). A row is
``(name, file, old, new, test, direction, property, root)``, turned into a ``Row`` by ``rows()``.
"""

from __future__ import annotations

from mutation_row import Row

SRC = "src/synthetic_ecommerce_data"

ROWS: list[tuple[str, str, str, str, str, str, str, str]] = [
    (
        "the wheel's retired pack still tells two wheels apart",
        "domains/industrial/newtypes.py",
        "            distinguishes=False,\n",
        "            distinguishes=True,\n",
        "tests/test_wheel_pack_357.py -k no_two_wheels_of_a_brand",
        "A",
        "two wheels that differed only by the pack are made once",
        SRC,
    ),
    (
        "the already-made key keeps a retired attribute that no longer distinguishes",
        "domains/industrial/finishing.py",
        "                if not (isinstance(a, RetiredAttribute) and not a.distinguishes)\n",
        "",
        "tests/test_catalog_golden.py -k flat.jsonl",
        "A",
        "the committed catalog is what the build makes: a retired pack is not part of a spec",
        SRC,
    ),
    (
        "the already-made subset check counts the retired pack a draw kept",
        "domains/industrial/finishing.py",
        "            retired = [a for a in (*line_ghosts, *sku_ghosts) if a.distinguishes]\n",
        "            retired = [*line_ghosts, *sku_ghosts]\n",
        "tests/test_wheel_pack_357.py -k no_two_wheels_of_a_brand",
        "A",
        "two wheels that differed only by the pack are made once",
        SRC,
    ),
    (
        "the wheel vocabulary lists a pack again",
        "domains/industrial/vocab.py",
        '    _spec("Application", "line", 0.6),\n    _spec("Grit", "sku", kind="count"),',
        '    _spec("Application", "line", 0.6),\n'
        '    _spec("Units per Pack", "line", 0.8, kind="count"),\n'
        '    _spec("Grit", "sku", kind="count"),',
        "tests/test_wheel_pack_357.py -k wheel_vocabulary_has_no_pack_row",
        "A",
        "the wheel vocabulary names no pack",
        SRC,
    ),
]

# Found by ``mutation_row.discover``: the prefix of the rows' names and the rows in one shape.
PREFIX = "wheel pack"


def rows() -> list[Row]:
    return [
        Row(name, file, old, new, test, prop, root, direction)
        for name, file, old, new, test, direction, prop, root in ROWS
    ]
