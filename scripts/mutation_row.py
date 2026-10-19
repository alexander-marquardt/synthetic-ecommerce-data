"""The one row shape of a mutant-row file, and the glob that finds the files.

A file ``scripts/mutation_rows_<topic>.py`` holds the rows of one issue. It exposes two names:

``PREFIX``
    The text before ``": "`` in each row's name (``--only "<prefix>:"`` re-runs the file's rows).
    Unique across the files.
``rows()``
    The file's rows, each a :class:`Row`.

``mutation_check.py`` calls :func:`discover` and reads every file the glob finds. It names no
rows file, so a pull request that adds a mutant row adds a file and edits no line of
``mutation_check.py``, and two such pull requests branched from one ``main`` never conflict
(alexander-marquardt/synthetic-ecommerce-data#506). ``tests/test_mutation_rows_glob_506.py``
fails when a shared list names a rows file again.
"""

from __future__ import annotations

import importlib
from pathlib import Path
from typing import NamedTuple

HERE = Path(__file__).resolve().parent

#: Where the file that a row plants in hangs off, for the generator package and for the retail
#: drawing package. A row names its own ``root``; these are the two spellings in use.
GENERATOR = "src/synthetic_ecommerce_data"
RETAIL_DRAWINGS = "prototypes/retail_drawings"


class Row(NamedTuple):
    name: str
    #: Path relative to ``root``.
    file: str
    old: str
    new: str
    #: The test selector expected to go red, or a tuple of them (see ``Mutation.tests``).
    tests: str | tuple[str, ...]
    property_name: str
    #: Path relative to the repository root that ``file`` hangs off.
    root: str = GENERATOR
    #: "A" and "B" label the two directions of one property.
    direction: str = ""


def rows_files() -> list[Path]:
    """Every mutant-row file, found by glob and in a fixed order."""
    return sorted(HERE.glob("mutation_rows_*.py"))


def discover() -> list[tuple[str, Row]]:
    """``(prefix, row)`` for every row of every mutant-row file.

    A file that lacks ``PREFIX`` or ``rows()``, whose prefix another file already uses, or whose
    ``rows()`` yields something that is not a :class:`Row`, raises ``ValueError`` naming the
    file: a row that is skipped is a defect nobody plants.
    """
    found: list[tuple[str, Row]] = []
    owner: dict[str, str] = {}
    for path in rows_files():
        module = importlib.import_module(path.stem)
        prefix = getattr(module, "PREFIX", None)
        if not isinstance(prefix, str) or not prefix:
            raise ValueError(f"{path.name} has no PREFIX string")
        if not callable(getattr(module, "rows", None)):
            raise ValueError(f"{path.name} has no rows() function")
        if prefix in owner:
            raise ValueError(f"{path.name} and {owner[prefix]} share the prefix {prefix!r}")
        owner[prefix] = path.name
        for row in module.rows():
            if not isinstance(row, Row):
                raise ValueError(f"{path.name}: rows() yielded a {type(row).__name__}, not a Row")
            found.append((prefix, row))
    return found
