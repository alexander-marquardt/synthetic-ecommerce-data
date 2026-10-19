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

A file yields :class:`Row` (the name is completed to ``"<PREFIX>: <name>"``) or, for the older
area files ``mutation_rows_area_<area>.py`` (#363), :class:`Mutation` (the name is already whole,
so ``PREFIX`` only labels the file). Both are planted the same way.
"""

from __future__ import annotations

import importlib
from dataclasses import dataclass
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


@dataclass(frozen=True)
class Mutation:
    name: str
    #: Path relative to ``root``.
    file: str
    old: str
    new: str
    #: The test selector expected to go red, or a TUPLE of them when one
    #: mutation is expected to red more than one test.
    #:
    #: A tuple rather than one ``-k "a or b"`` filter, and the difference is
    #: the whole point: this harness's verdict is "pytest went red", so a
    #: disjunction is satisfied by EITHER test and prints ``[ok]`` on the
    #: other one's back. Ten rows were written that way and five of them were
    #: riding on a sibling. Every selector in the tuple is run and judged on
    #: its own, and the row is caught only when ALL of them red.
    tests: str | tuple[str, ...]

    @property
    def selectors(self) -> tuple[str, ...]:
        return (self.tests,) if isinstance(self.tests, str) else tuple(self.tests)

    #: "A" and "B" label the two directions of one property.
    direction: str = ""
    property_name: str = ""
    #: Path relative to the REPO root that ``file`` hangs off. Defaults to the
    #: generator package; the PRISM customization is a second package, and the
    #: committed field map has to be mutable from here too -- a drift test that
    #: is only ever proven from the DERIVATION side is not proven at all.
    root: str = "src/synthetic_ecommerce_data"


def as_mutation(prefix: str, row: Row | Mutation) -> Mutation:
    """The :class:`Mutation` the harness plants for ``row`` of a file whose prefix is ``prefix``."""
    if isinstance(row, Mutation):
        return row
    return Mutation(
        f"{prefix}: {row.name}",
        row.file,
        row.old,
        row.new,
        row.tests,
        row.direction,
        row.property_name,
        row.root,
    )


def rows_files() -> list[Path]:
    """Every mutant-row file, found by glob and in a fixed order."""
    return sorted(HERE.glob("mutation_rows_*.py"))


def discover() -> list[tuple[str, Row | Mutation]]:
    """``(prefix, row)`` for every row of every mutant-row file.

    A file that lacks ``PREFIX`` or ``rows()``, whose prefix another file already uses, or whose
    ``rows()`` yields something that is neither a :class:`Row` nor a :class:`Mutation`, raises
    ``ValueError`` naming the file: a row that is skipped is a defect nobody plants.
    """
    found: list[tuple[str, Row | Mutation]] = []
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
            if not isinstance(row, Row | Mutation):
                raise ValueError(
                    f"{path.name}: rows() yielded a {type(row).__name__}, not a Row or a Mutation"
                )
            found.append((prefix, row))
    return found
